from django.db.models import Model
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters,status
from rest_framework.views import APIView
from django.http import HttpResponse

from .models import *
from .serializers import *
from rest_framework.decorators import action
from openpyxl import Workbook



# Create your views here.

class CategoryViewset(viewsets.ModelViewSet):
    queryset =Category.objects.all()
    serializer_class =CategorySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields= ['name']


class ProductViewset(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class= ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend,filters.SearchFilter, filters.OrderingFilter]
    filterset_fields=['narx']

    search_fields = ['name','=narx']
    ordering_fields= ['name','narx']



class CartItemViewset(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)




from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cart, CartItem, Product, Order, OrderItem
from .serializers import *



class CartVewset(viewsets.GenericViewSet):
    # O'ZGARDI: ModelViewSet emas, GenericViewSet. Cart ni to'g'ridan-to'g'ri
    # yaratish/o'chirish/o'zgartirish (PUT, DELETE) yo'llari ochilmaydi.
    serializer_class = CartSerializer
    permission_classes = [permissions.AllowAny]


    # O'ZGARDI: AllowAny emas

    def get_queryset(self):
        # O'ZGARDI: faqat shu foydalanuvchining savati
        return Cart.objects.filter(user=self.request.user)

    # ---------- yordamchi ----------
    def _cart_response(self, request, code=status.HTTP_200_OK):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart = (Cart.objects
                .prefetch_related('items__product__category')
                .get(pk=cart.pk))
        return Response(CartSerializer(cart, context={'request': request}).data,
                        status=code)

    # ---------- GET /api/cart/ ----------
    def list(self, request):
        return self._cart_response(request)

    # ---------- POST /api/cart/add/ ----------
    # Body: {"product_id": 44, "jami_mahsulot": 2}
    @action(detail=False, methods=['post'], url_path='add')
    def add(self, request):
        s = CartItemSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)

        product = s.validated_data['product']
        qty = s.validated_data.get('jami_mahsulot', 1)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item = CartItem.objects.filter(cart=cart, product=product).first()
        new_qty = (item.jami_mahsulot if item else 0) + qty

        if new_qty > product.qoldiq:
            return Response({'detail': "Omborda yetarli mahsulot yo'q."},
                            status=status.HTTP_400_BAD_REQUEST)

        if item:
            item.jami_mahsulot = new_qty
            item.save()
        else:
            CartItem.objects.create(cart=cart, product=product,
                                    jami_mahsulot=new_qty)
        return self._cart_response(request, status.HTTP_201_CREATED)

    # ---------- PATCH / DELETE /api/cart/items/44/ ----------
    # PATCH body: {"jami_mahsulot": 3}
    @action(detail=False, methods=['patch', 'delete'],
            url_path=r'items/(?P<product_id>\d+)')
    def item(self, request, product_id=None):
        cart = get_object_or_404(Cart, user=request.user)

        if request.method == 'DELETE':
            CartItem.objects.filter(cart=cart, product_id=product_id).delete()
            return self._cart_response(request)

        item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        try:
            qty = int(request.data.get('jami_mahsulot', 1))
        except (TypeError, ValueError):
            return Response({'detail': "Son noto'g'ri."}, status=400)

        if qty <= 0:
            item.delete()
        elif qty > item.product.qoldiq:
            return Response({'detail': "Omborda yetarli mahsulot yo'q."}, status=400)
        else:
            item.jami_mahsulot = qty
            item.save()
        return self._cart_response(request)

    # ---------- POST /api/cart/merge/ ----------
    # Body: {"items": [{"product_id": 5, "jami_mahsulot": 2}]}
    @action(detail=False, methods=['post'], url_path='merge')
    def merge(self, request):
        s = MergeCartSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        for row in s.validated_data['items']:
            product = Product.objects.filter(id=row['product_id']).first()
            if not product or product.qoldiq < 1:
                continue
            item, _ = CartItem.objects.get_or_create(
                cart=cart, product=product, defaults={'jami_mahsulot': 0})
            item.jami_mahsulot = min(item.jami_mahsulot + row['jami_mahsulot'],
                                     product.qoldiq)
            item.save()
        return self._cart_response(request)

    # ---------- POST /api/cart/checkout/ ----------
    # Body: {"address": "...", "phone": "..."}
    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        s = CheckoutSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        cart = get_object_or_404(Cart, user=request.user)
        items = list(cart.items.all())
        if not items:
            return Response({'detail': "Savat bo'sh."}, status=400)

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    address=s.validated_data['address'],
                    phone=s.validated_data['phone'],
                    total_price=0,
                )
                total = 0
                for item in items:
                    product = Product.objects.select_for_update().get(id=item.product_id)
                    if item.jami_mahsulot > product.qoldiq:
                        raise ValueError(f"{product.name} yetarli emas.")
                    OrderItem.objects.create(
                        order=order, product=product,
                        quantity=item.jami_mahsulot, price=product.narx)
                    product.qoldiq -= item.jami_mahsulot
                    product.save()
                    total += product.narx * item.jami_mahsulot
                order.total_price = total
                order.save()
                cart.items.all().delete()
        except ValueError as e:
            return Response({'detail': str(e)}, status=400)

        return Response(OrderSerializer(order, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

class OrderItemViewset(viewsets.ModelViewSet):

    serializer_class = OrderItemSerializer
    permission_classes = [permissions.AllowAny]


    def get_queryset(self):
            return CartItem.objects.filter(cart__user=self.request.user)




Model={
    'Category':Category,
    'OrderItem':OrderItem,
    'Product':Product,
    'Cart':Cart,
    'CartItem':CartItem,
    'Order':Order,

}


class ExsportViewset(APIView):
    permission_classes = [permissions.AllowAny]

    def get (self,request,model_name):
        lookup = {name.lower(): m for name, m in Model.items()}
        model = lookup.get(model_name)
        if model is None:
            return Response(
                {'detail':'Bunday model topilmadi',
                "mavjud_modellar": list(Model.keys())
                 },
                 status=status.HTTP_400_BAD_REQUEST,
            )
        fields=model._meta.fields
        exsel=Workbook()
        export=exsel.active
        export.title = model._meta.verbose_name_plural.title()[:31]

        export.append([f.name for f in fields])
        for obj in model.objects.all():
            row=[]
            for f in fields:
                value = f.value_from_object(obj)
                if value is not None and not isinstance(value, (int, float, str, bool)):
                    value = str(value)
                row.append(value)
            export.append(row)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{model_name}.xlsx"'
        exsel.save(response)
        return response




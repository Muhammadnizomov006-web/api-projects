# from rest_framework import serializers
# from .models import *
# from .models import Product
#
#
# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ('id', 'name_uz', 'name_ru', 'name_en', 'img')
#
#
#
#
# class ProductSerializer(serializers.ModelSerializer):
#
#     category_name = serializers.CharField(source="category.name", read_only=True)
#     class Meta:
#         model= Product
#         fields =('name','narx','text','surati','qoldiq','vaqti','category_name')
#
#
#
#
# class CartItemSerializer(serializers.ModelSerializer):
#     product = ProductSerializer(read_only=True)
#     product_id = serializers.PrimaryKeyRelatedField(
#         queryset=Product.objects.all(), source="product", write_only=True
#     )
#     total_price = serializers.SerializerMethodField()
#     class Meta:
#         model =CartItem
#         fields = ['id', 'cart', 'product', 'product_id', 'jami_mahsulot', 'total_price']  # ✅ ikkalasi ham qo'shildi
#
#     def get_total_price(self,obj):
#         return obj.product.narx*obj.jami_mahsulot
#
#
# class CartSerializer(serializers.ModelSerializer):
#     items= CartItemSerializer(many=True,read_only=True)
#     total_price = serializers.SerializerMethodField()
#     class Meta:
#         model= Cart
#         fields = ['id', 'user', 'items', 'total_price']
#     def get_total_price(self,obj):
#         return sum(item.product.narx * item.jami_mahsulot for item in obj.items.all())
#
#
#
#
#
#
#
#
# class OrderItemSerializer(serializers.ModelSerializer):
#         product = ProductSerializer(read_only=True)
#
#         # buyurtma tarixida mahsulotning to'liq ma'lumotini ko'rsatish uchun
#
#         class Meta:
#             model = OrderItem
#             fields = ["id", "product", "quantity", "price"]
#             # price — bu yerda modeldagi "xarid qilingan paytdagi narx",
#             # hozirgi Product.price bilan aralashtirilmaydi
#
#     # BUYURTMA SERIALIZERI
#     # Vazifasi: bitta buyurtmani, uning ichidagi barcha mahsulotlari bilan
#     # birga JSON ko'rinishida chiqaradi (buyurtmalar tarixi sahifasi uchun)
# class OrderSerializer(serializers.ModelSerializer):
#         items = OrderItemSerializer(many=True, read_only=True)
#
#         # shu buyurtmaga tegishli barcha OrderItem'lar ro'yxati
#
#         class Meta:
#             model = Order
#             fields = [
#                 "id",
#                 "user",
#                 "status",
#                 "address",
#                 "phone",
#                 "total_price",
#                 "created_at",
#                 "items",
#             ]
#             read_only_fields = ["total_price", "created_at"]
#             # bu maydonlar foydalanuvchi tomonidan qo'lda yuborilmaydi,
#             # avtomatik hisoblanadi yoki tizim tomonidan to'ldiriladi




















from django.contrib.auth.models import User          # YANGI: RegisterSerializer uchun kerak
from rest_framework import serializers
from .models import Category, Product, Cart, CartItem, Order, OrderItem
# O'ZGARDI: avval "from .models import *" va "from .models import Product" edi.
# "*" hamma narsani yashirin import qiladi va Product ikki marta yozilgan edi.
# Endi kerakli modellar aniq ko'rsatilgan.


# YANGI: ro'yxatdan o'tish uchun (avval yo'q edi, view shuni import qiladi)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        # create_user parolni xeshlab saqlaydi (oddiy create() ochiq matn saqlardi)
        return User.objects.create_user(**validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'name_uz', 'name_ru', 'name_en', 'img')
        # O'ZGARDI: 'name' qo'shildi (joriy tildagi nom shu orqali chiqadi)


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'narx', 'text', 'surati',
                  'qoldiq', 'vaqti', 'category', 'category_name')
        # O'ZGARDI: 'id' qo'shildi (frontend savatga qo'shishda product_id ni bilishi uchun)
        # O'ZGARDI: 'category' (id) qo'shildi (kategoriya bo'yicha filtrlash uchun)


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'jami_mahsulot', 'total_price']
        # OLIB TASHLANDI: 'cart'. Ochiq qolsa, foydalanuvchi boshqa odamning
        # savat id sini yuborib, o'sha savatga mahsulot qo'sha olardi (xavfsizlik teshigi).
        # Savatni view o'zi request.user orqali topadi.
        extra_kwargs = {'jami_mahsulot': {'min_value': 1, 'required': False}}
        # YANGI: son kamida 1 bo'lsin; yuborilmasa modeldagi default (1) ishlaydi

    def get_total_price(self, obj):
        return obj.product.narx * obj.jami_mahsulot


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
        # OLIB TASHLANDI: 'user'. Savat egasini javobda ko'rsatish shart emas,
        # yozish uchun ochiq bo'lishi esa xavfli edi.

    def get_total_price(self, obj):
        return sum(i.product.narx * i.jami_mahsulot for i in obj.items.all())


# YANGI: mehmon savatini login dan keyin bazaga ko'chirish uchun (3 ta klass)
class MergeItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    jami_mahsulot = serializers.IntegerField(min_value=1)


class MergeCartSerializer(serializers.Serializer):
    items = MergeItemSerializer(many=True)


class OrderItemSerializer(serializers.ModelSerializer):
    # O'ZGARDI: keraksiz ichkariga surilgan bo'sh joylar (indent) tuzatildi, mantiq o'sha
    product = ProductSerializer(read_only=True)
    # buyurtma tarixida mahsulotning to'liq ma'lumotini ko'rsatish uchun

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]
        # price: xarid paytidagi narx (Product.narx keyin o'zgarsa ham shu qoladi)
        # O'ZGARDI: izohdagi "Product.price" ni "Product.narx" ga to'g'rilandi


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    # shu buyurtmaga tegishli barcha OrderItem lar ro'yxati

    class Meta:
        model = Order
        fields = ["id", "status", "address", "phone",
                  "total_price", "created_at", "items"]
        # OLIB TASHLANDI: "user". Buyurtma egasini view request.user dan oladi,
        # foydalanuvchi boshqa odam nomidan buyurtma yarata olmasin.
        read_only_fields = ["status", "total_price", "created_at"]
        # O'ZGARDI: "status" qo'shildi. Avval ochiq edi, ya'ni foydalanuvchi
        # o'zi status: "delivered" deb yuborishi mumkin edi.


# YANGI: buyurtma berishda foydalanuvchidan faqat shu ikki maydon olinadi
class CheckoutSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=20)
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Setings.settings")  # <-- o'zingizning settings yo'li
django.setup()

from django.db.models import Sum, Count
from apps_1.models import CartItem

dups = (CartItem.objects
        .values('cart_id', 'product_id')
        .annotate(n=Count('id'), total=Sum('jami_mahsulot'))
        .filter(n__gt=1))

for d in list(dups):
    items = CartItem.objects.filter(
        cart_id=d['cart_id'], product_id=d['product_id']
    ).order_by('id')

    keep = items.first()
    keep.jami_mahsulot = min(d['total'], keep.product.qoldiq) or 1
    keep.save()
    items.exclude(id=keep.id).delete()
    print("Birlashtirildi:", d['cart_id'], d['product_id'])

print("Tayyor")

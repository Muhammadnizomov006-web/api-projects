import random
from django.contrib.auth.models import User
from apps_1.models import Category, Product, Cart, CartItem, Order, OrderItem

# 1. Kategoriyalar (10 ta)
categories = []
for name in ["Telefon", "Noutbuk", "Kiyim", "Oyoq kiyim", "Uy jihozlari",
             "Sport anjomlari", "Kitoblar", "O'yinchoqlar", "Kosmetika", "Elektronika"]:
    c = Category.objects.create(name=name)
    categories.append(c)
print(f"{len(categories)} ta kategoriya qo'shildi")

# 2. Mahsulotlar (150 ta)
products = []
for i in range(1, 151):
    p = Product.objects.create(
        category=random.choice(categories),
        name=f"Mahsulot {i}",
        narx=random.randint(10000, 5000000),
        text="Bu mahsulot haqida qisqacha ma'lumot",
        qoldiq=random.randint(0, 100),
    )
    products.append(p)
print(f"{len(products)} ta mahsulot qo'shildi")

# 3. Test foydalanuvchi
user, created = User.objects.get_or_create(
    username="testuser",
    defaults={"email": "test@example.com"}
)
if created:
    user.set_password("test12345")
    user.save()
print("Foydalanuvchi tayyor:", user.username)

# 4. Savat va savat elementlari
cart, _ = Cart.objects.get_or_create(user=user)
for _ in range(10):
    CartItem.objects.create(
        cart=cart,
        product=random.choice(products),
        jami_mahsulot=random.randint(1, 5),
    )
print("Savat elementlari qo'shildi")

# 5. Buyurtmalar (Order) - 20 ta
orders = []
for _ in range(20):
    product = random.choice(products)
    miqdor = random.randint(1, 5)
    o = Order.objects.create(
        user=user,
        product=product,
        jami_olindi=miqdor,
        narx=product.narx,
        status=random.choice(["new", "processing", "shipped", "delivered", "cancelled"]),
        address="Toshkent shahar, Chilonzor tumani",
        phone="+998901234567",
        total_price=product.narx * miqdor,
    )
    orders.append(o)
print(f"{len(orders)} ta buyurtma qo'shildi")

# 6. OrderItem
for order in orders:
    OrderItem.objects.create(
        order=order,
        product=order.product,
        quantity=order.jami_olindi,
        price=order.narx,
    )
print("OrderItem yozuvlari qo'shildi")

print("Barchasi tayyor!")
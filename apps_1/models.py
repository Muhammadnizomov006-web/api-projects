from django.db import models
from django.contrib.auth.models import User

# Create your models here.




class Category(models.Model):
    name= models.CharField(max_length=100)
    img=models.ImageField(upload_to='img')
    def __str__(self):
        return self.name



class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name=models.CharField(max_length=130)
    narx=models.IntegerField()
    text=models.TextField()
    surati=models.ImageField(upload_to='img')
    qoldiq=models.PositiveIntegerField(default=0)
    vaqti=models.DateField(auto_now_add=True)
    def __str__(self):
        return self.name



class Cart(models.Model):
    user=models.OneToOneField(User , on_delete=models.CASCADE)
    @property
    def total_price(self):
        # Savatdagi hamma mahsulotlar summasi
        return sum(item.subtotal for item in self.items.select_related('product'))



class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE, related_name="items")
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    jami_mahsulot=models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    @property
    def subtotal(self):
          # narx × son
           return self.product.narx * self.jami_mahsulot


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Yangi"),
        ("processing", "Jarayonda"),
        ("shipped", "Yuborilgan"),
        ("delivered", "Yetkazilgan"),
        ("cancelled", "Bekor qilingan"),
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    jami_olindi=models.PositiveIntegerField()
    narx=models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    # buyurtmaning hozirgi holati (hozircha "yangi" deb belgilanadi)

    address = models.CharField(max_length=255)  # yetkazib berish manzili

    phone = models.CharField(max_length=20)  # aloqa uchun telefon raqami

    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    # buyurtmaning umumiy summasi (barcha mahsulotlar narxi yig'indisi)

    created_at = models.DateTimeField(auto_now_add=True)




class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )  # bu qaysi buyurtmaga tegishli ekanini bildiradi

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # buyurtma qilingan aynan qaysi mahsulot ekanini ko'rsatadi

    quantity = models.PositiveIntegerField()
    # o'sha mahsulotdan nechta dona sotib olinganini saqlaydi

    price = models.DecimalField(max_digits=10, decimal_places=2)
    # mahsulotning XARID QILINGAN PAYTDAGI narxi
    # Nega alohida saqlanadi: kelajakda Product.price o'zgarishi mumkin,
    # lekin eski buyurtmada xaridor o'sha paytdagi narxda olganini
    # ko'rsatish uchun bu qiymat "muzlatib" saqlab qo'yiladi




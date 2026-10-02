from django.contrib import admin
from .models import *
from modeltranslation.admin import TabbedTranslationAdmin
# Register your models here.


admin.site.register(Category)
# admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)



@admin.register(Product)
class ProductAdmin(TabbedTranslationAdmin):
    list_display = ('name',)

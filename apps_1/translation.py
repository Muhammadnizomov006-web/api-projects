from modeltranslation.translator import register,TranslationOptions
from .models import *


@register(Category)
class CategoryTranslation(TranslationOptions):
    fields=('name',)






@register(Product)
class ProductTranslation(TranslationOptions):
    fields=('name','text',)








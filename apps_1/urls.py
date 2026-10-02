from rest_framework import serializers
from django.urls import path,include
from rest_framework import routers
from .views import *


router = routers.DefaultRouter()
router.register(r"category",CategoryViewset)
router.register(r"product",ProductViewset)
router.register(r"orderitem", OrderItemViewset, basename="orderitem")
router.register(r"cart", CartVewset, basename="cart")
router.register(r"cartitem", CartItemViewset, basename="cartitem")




urlpatterns = [
    path("", include(router.urls)),
    path("api-auth", include("rest_framework.urls")),
    path('export/<str:model_name>/',ExsportViewset.as_view(),name='export')
]
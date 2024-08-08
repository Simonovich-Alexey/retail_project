from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (RegisterUserViewSet, LoginViewSet, LogoutView,
                    ProfileViewSet, ContactsUserViewSet, ShopViewSet,
                    CategoryViewSet, LoadingGoods, ProductInfoViewSet, OrderItemViewSet)

router = DefaultRouter()

router.register('user/register', RegisterUserViewSet, basename='register')
router.register('user/login', LoginViewSet, basename='login')
router.register('user/profile', ProfileViewSet, basename='profile')
router.register('user/contacts', ContactsUserViewSet, basename='contacts')
router.register('shop', ShopViewSet)
router.register('categories', CategoryViewSet)
router.register('products', ProductInfoViewSet)
router.register('basket', OrderItemViewSet)

urlpatterns = [
    path('user/logout/', LogoutView.as_view()),
    path('shop/loading/', LoadingGoods.as_view()),
] + router.urls

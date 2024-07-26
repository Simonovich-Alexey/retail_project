from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (RegisterUserViewSet, LoginViewSet, LogoutView,
                    ProfileViewSet, ContactsUserViewSet, ShopViewSet,
                    CategoryViewSet, LoadingGoods)

router = DefaultRouter()

router.register('user/register', RegisterUserViewSet, basename='register')
router.register('user/login', LoginViewSet, basename='login')
router.register('user/profile', ProfileViewSet, basename='profile')
router.register('user/contacts', ContactsUserViewSet, basename='contacts')

router.register('shop', ShopViewSet)
router.register('shop/category', CategoryViewSet)

urlpatterns = [
    path('user/logout/', LogoutView.as_view()),
    path('shop/loading/', LoadingGoods.as_view()),
] + router.urls

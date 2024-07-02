from django.urls import path
from rest_framework.routers import DefaultRouter

from users.views import RegisterUserViewSet, LoginViewSet, LogoutView, ProfileViewSet, ContactsUserViewSet

router = DefaultRouter()
router.register('register', RegisterUserViewSet, basename='register')
router.register('login', LoginViewSet, basename='login')
router.register('profile', ProfileViewSet, basename='profile')
router.register('contacts', ContactsUserViewSet, basename='contacts')

urlpatterns = [
    path('logout/', LogoutView.as_view()),
] + router.urls

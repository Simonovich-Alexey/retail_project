from django.urls import path
from rest_framework.routers import DefaultRouter

from users.views import RegisterUserViewSet, LoginViewSet, LogoutViewSet, ProfileViewSet

router = DefaultRouter()
router.register('register', RegisterUserViewSet, basename='register')
router.register('login', LoginViewSet, basename='login')
router.register('logout', LogoutViewSet, basename='logout')
router.register('profile', ProfileViewSet, basename='profile')

# urlpatterns = [
#     path('register/', RegisterUserViewSet.as_view(), name='register'),
# ]
urlpatterns = router.urls
# urlpatterns += router.urls


# Регистрация POST запрос (автоматическая отправка почты после регистрации)
# Повторная отправка письма с подтверждением почты POST запрос
# Получение, изменение, удаление пользователя GET, PATCH, DELETE запрос.
# Вход и выход пользователя POST запрос.

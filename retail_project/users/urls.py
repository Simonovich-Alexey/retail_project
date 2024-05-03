from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet, LoginViewSet, LogoutViewSet

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('token/login', LoginViewSet, basename='login')
router.register('token/logout', LogoutViewSet, basename='logout')

urlpatterns = router.urls


# Регистрация POST запрос (автоматическая отправка почты после регистрации)
# Повторная отправка письма с подтверждением почты POST запрос
# Получение, изменение, удаление пользователя GET, PATCH, DELETE запрос.
# Вход и выход пользователя POST запрос.

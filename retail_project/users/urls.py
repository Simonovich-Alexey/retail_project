# from django.urls import path, include, re_path
# from rest_framework.routers import DefaultRouter
#
# from users.views import RegisterViewSet

# router = DefaultRouter()
# router.register('users', RegisterViewSet, basename='users')
#
# urlpatterns = router.urls

# from djoser.views import UserViewSet, TokenCreateView, TokenDestroyView
#
# urlpatterns = [
#     path('', UserViewSet.perform_create, name='users'),
#     path('activation/', UserViewSet.activation, name='activation'),
#     path('resend_activation/', UserViewSet.resend_activation, name='resend_activation'),
#     path('me/', UserViewSet.me, name='me'),
#     path('reset_password_confirm/', UserViewSet.reset_password_confirm, name='reset_password_confirm'),
#     path('reset_password/', UserViewSet.reset_password, name='reset_password'),
#     path('reset_password_confirm/', UserViewSet.reset_password_confirm, name='reset_password_confirm'),
#     path('login/', TokenCreateView.as_view(), name='login'),
#     path('logout/', TokenDestroyView.as_view(), name='logout'),
# ]

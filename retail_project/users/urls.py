from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from users.views import RegisterViewSet

# router = DefaultRouter()
# router.register('users', RegisterViewSet, basename='users')
#
# urlpatterns = router.urls

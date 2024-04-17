from django.urls import path
from rest_framework.routers import DefaultRouter

from users.views import RegisterViewSet

router = DefaultRouter()
router.register('register', RegisterViewSet)

urlpatterns = router.urls

# app_name = 'users'
#
# urlpatterns = [
#     path('register/', RegisterViewSet.as_view(), name='register'),
# ]

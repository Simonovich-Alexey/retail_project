from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['id', 'email', 'first_name', 'last_name', 'type_user', 'is_active']
    list_filter = ['email', 'first_name', 'last_name', 'type_user', 'is_active']

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CastomUser


@admin.register(CastomUser)
class CastomUserAdmin(UserAdmin):
    model = CastomUser
    list_display = ['id', 'email', 'first_name', 'last_name', 'type', 'is_active']
    list_filter = ['email', 'first_name', 'last_name', 'type', 'is_active']

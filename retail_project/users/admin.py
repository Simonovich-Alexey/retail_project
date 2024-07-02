from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ContactsUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = (
        (None, {'fields': ('email',)}),
        ('Информация о пользователе', {'fields': ('first_name', 'last_name', 'type_user', 'is_active')}),
    )
    list_display = ['id', 'email', 'phone', 'first_name', 'last_name',
                    'type_user', 'is_active', 'last_login', 'created_at']
    list_filter = ['type_user', 'is_active']
    list_display_links = ['id', 'email']
    ordering = ['-created_at']


@admin.register(ContactsUser)
class ContactsUserAdmin(admin.ModelAdmin):
    model = ContactsUser
    list_display = ['user', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'favorite']
    list_display_links = ['user']
    list_filter = ['user']
    ordering = ['user']

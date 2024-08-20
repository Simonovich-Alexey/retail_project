from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (CustomUser, ContactsUser, Shop, Category, Product,
                     ShopCategory, ProductInfo, Parameter, ProductParameter, Order, OrderItem)


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
    list_display = ['id', 'user', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'favorite']
    list_display_links = ['user']
    list_filter = ['user']
    ordering = ['user']


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    model = Shop
    list_display = ['id', 'name_shop', 'url_file', 'status_order', 'user']
    list_display_links = ['name_shop']
    list_filter = ['status_order']
    ordering = ['name_shop']


class ShopCategoryInline(admin.TabularInline):
    model = ShopCategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [ShopCategoryInline]
    model = Category
    list_display = ['id', 'name_category']
    list_display_links = ['name_category']
    ordering = ['name_category']


class ProductInfoInline(admin.TabularInline):
    model = ProductInfo


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductInfoInline]
    model = Product
    list_display = ['id', 'name_product', 'category_id']
    list_display_links = ['name_product']
    ordering = ['id']


class ProductParameterInline(admin.TabularInline):
    model = ProductParameter


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    inlines = [ProductParameterInline]
    model = ProductInfo
    list_display = ['id', 'name', 'product', 'shop', 'external_id', 'quantity', 'price', 'price_rrc']
    list_display_links = ['name', 'product']
    list_filter = ['shop']
    ordering = ['product']


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    model = Parameter
    list_display = ['name_parameter']
    list_display_links = ['name_parameter']
    ordering = ['name_parameter']


class OrderItemInline(admin.TabularInline):
    model = OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    model = Order
    list_display = ['id', 'user', 'created_at', 'contacts', 'total_cost']
    list_display_links = ['user']
    ordering = ['created_at']

    def total_cost(self, obj):
        return obj.get_total_cost()

    total_cost.short_description = 'Сумма заказа'

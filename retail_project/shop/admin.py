from django.contrib import admin
from .models import Shop, Category, Product, ShopCategory, ProductInfo, Parameter, ProductParameter


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    model = Shop
    list_display = ['name_shop', 'url_file', 'status_order', 'user']
    list_display_links = ['name_shop']
    list_filter = ['status_order']
    ordering = ['name_shop']


class ShopCategoryInline(admin.TabularInline):
    model = ShopCategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [ShopCategoryInline]
    model = Category
    list_display = ['name_category']
    list_display_links = ['name_category']
    ordering = ['name_category']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ['name_product']
    list_display_links = ['name_product']
    ordering = ['name_product']


class ProductParameterInline(admin.TabularInline):
    model = ProductParameter


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    inlines = [ProductParameterInline]
    model = ProductInfo
    list_display = ['name', 'product', 'shop', 'external_id', 'quantity', 'price', 'price_rrc']
    list_display_links = ['name', 'product']
    list_filter = ['shop']
    ordering = ['product']


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    model = Parameter
    list_display = ['name_parameter', 'unit']
    list_display_links = ['name_parameter']
    list_filter = ['unit']
    ordering = ['name_parameter']

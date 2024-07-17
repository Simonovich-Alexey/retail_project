from django.db import models

"""
1. Модель магазина
   1.1. Название магазина
   1.2. Пользователь (кто создал магазин)
   1.3. Статус (активен или нет)
   1.4. Ссылка на файл
   
2. Категории товара
   2.1. Название категории

3. Товар
   3.1. Название
   3.2. Категория

4. 
"""


class Shop(models.Model):
    name_shop = models.CharField(max_length=100, verbose_name='Название магазина')
    url_file = models.URLField(max_length=255, verbose_name='Ссылка на файл')
    status_order = models.BooleanField(default=True, verbose_name='Статус приема заказов')

    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE,
                             blank=True, null=True, verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ('-name_shop',)

    def __str__(self):
        return f'{self.name_shop} - status:{self.status_order}'


class Category(models.Model):
    name_category = models.CharField(max_length=100, verbose_name='Название категории')

    shop = models.ManyToManyField(Shop, related_name='category', verbose_name='Магазин', through='ShopCategory')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('-name_category',)

    def __str__(self):
        return self.name_category


class ShopCategory(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')

    class Meta:
        verbose_name = 'Магазин категория'
        verbose_name_plural = 'Магазины категории'
        ordering = ('-shop',)

    def __str__(self):
        return f'{self.shop.name_shop} - {self.category.name_category}'


class Product(models.Model):
    name_product = models.CharField(max_length=100, verbose_name='Название')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('name_product',)

    def __str__(self):
        return self.name_product


class ProductInfo(models.Model):
    name_model = models.CharField(max_length=100, verbose_name='Название')
    product = models.ForeignKey(Product, related_name='product_info', on_delete=models.CASCADE, verbose_name='Товар')
    shop = models.ForeignKey(ShopCategory, on_delete=models.CASCADE, verbose_name='Магазин')
    external_id = models.PositiveIntegerField(verbose_name='Внешний идентификатор')
    quantity = models.IntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Цена')
    price_rrc = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Розничная цена', default=0)

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информация о продуктах'

    def __str__(self):
        return self.name_model


class Parameter(models.Model):
    name_parameter = models.CharField(max_length=100, verbose_name='Название')
    unit = models.CharField(max_length=100, verbose_name='Единица измерения')

    product = models.ManyToManyField(ProductInfo, through='ProductParameter',
                                     related_name='parameter', verbose_name='Товар')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'
        ordering = ('name_parameter',)

    def __str__(self):
        return self.name_parameter


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, related_name='product_parameter',
                                     on_delete=models.CASCADE, verbose_name='Информация о продукте')
    parameter = models.ForeignKey(Parameter, related_name='parameter',
                                  on_delete=models.CASCADE, verbose_name='Параметр')
    value = models.CharField(max_length=100, verbose_name='Значение')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'
        ordering = ('product_info',)

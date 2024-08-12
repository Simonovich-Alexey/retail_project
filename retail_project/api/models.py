from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise gettext_lazy(ValueError('Users must have an email address'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        if not password:
            raise gettext_lazy(ValueError('We need a password'))
        if not email:
            raise gettext_lazy(ValueError('Users must have an email address'))

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        user = self._create_user(email, password, **extra_fields)
        return user


class CustomUser(AbstractUser, PermissionsMixin):
    """
    Пользовательская модель пользователя
    """

    # Определение выбора типа пользователя
    class UserType(models.TextChoices):
        buyer = 'buyer', 'Покупатель'
        supplier = 'supplier', 'Поставщик'

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(verbose_name='Имя пользователя', max_length=150, validators=[username_validator])
    email = models.EmailField(verbose_name='E-mail', unique=True, db_index=True)
    phone = models.CharField(verbose_name='Телефон', max_length=20, unique=True)
    company = models.CharField(verbose_name='Компания', max_length=100, blank=True)
    is_active = models.BooleanField(verbose_name='Активированный', default=False)

    type_user = models.CharField(verbose_name='Тип пользователя', choices=UserType.choices,
                                 max_length=10)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Дата обновления', auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)


class ContactsUser(models.Model):
    objects = models.Manager()

    user = models.ForeignKey(CustomUser, related_name='contacts', on_delete=models.CASCADE, verbose_name='Пользователь')
    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.IntegerField(verbose_name='Дом')
    structure = models.IntegerField(verbose_name='Корпус', blank=True, null=True)
    building = models.IntegerField(verbose_name='Строение', blank=True, null=True)
    apartment = models.IntegerField(verbose_name='Квартира', blank=True, null=True)
    favorite = models.BooleanField(default=False, verbose_name='Избранное')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = 'Список контактов пользователя'

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'


class Shop(models.Model):
    objects = models.Manager()

    name_shop = models.CharField(max_length=100, verbose_name='Название магазина')
    url_file = models.URLField(max_length=255, verbose_name='Ссылка на файл', blank=True, null=True)
    status_order = models.BooleanField(default=False, verbose_name='Статус приема заказов')

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             blank=True, null=True, verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ('-name_shop',)

    def __str__(self):
        return f'{self.name_shop} - status:{self.status_order}'


class Category(models.Model):
    objects = models.Manager()

    name_category = models.CharField(max_length=100, verbose_name='Название категории')

    shop = models.ManyToManyField(Shop, related_name='category', verbose_name='Магазин', through='ShopCategory')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('-name_category',)

    def __str__(self):
        return self.name_category


class ShopCategory(models.Model):
    objects = models.Manager()

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')

    class Meta:
        verbose_name = 'Магазин категория'
        verbose_name_plural = 'Магазины категории'
        ordering = ('-shop',)

    def __str__(self):
        return f'{self.shop.name_shop} - {self.category.name_category}'


class Product(models.Model):
    objects = models.Manager()

    name_product = models.CharField(max_length=100, verbose_name='Название')

    category_id = models.ForeignKey(Category, related_name='product',
                                    on_delete=models.CASCADE, verbose_name='Категория')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('name_product',)

    def __str__(self):
        return self.name_product


class ProductInfo(models.Model):
    objects = models.Manager()

    name = models.CharField(max_length=100, verbose_name='Название')
    external_id = models.PositiveIntegerField(verbose_name='Внешний идентификатор')
    quantity = models.IntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Цена')
    price_rrc = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Розничная цена', default=0)

    product = models.ForeignKey(Product, related_name='product_info', on_delete=models.CASCADE, verbose_name='Товар')
    shop = models.ForeignKey(Shop, related_name='product_info', on_delete=models.CASCADE, verbose_name='Магазин')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информация о продуктах'

    def __str__(self):
        return self.name


class Parameter(models.Model):
    objects = models.Manager()

    name_parameter = models.CharField(max_length=100, verbose_name='Название')

    product = models.ManyToManyField(ProductInfo, through='ProductParameter',
                                     related_name='parameter', verbose_name='Товар')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'
        ordering = ('name_parameter',)

    def __str__(self):
        return self.name_parameter


class ProductParameter(models.Model):
    objects = models.Manager()

    product_info = models.ForeignKey(ProductInfo, related_name='product_parameter',
                                     on_delete=models.CASCADE, verbose_name='Информация о продукте')
    parameter = models.ForeignKey(Parameter, related_name='parameter',
                                  on_delete=models.CASCADE, verbose_name='Параметр')
    value = models.CharField(max_length=100, verbose_name='Значение')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'
        ordering = ('product_info',)


class Order(models.Model):
    class StateChoices(models.TextChoices):
        basket = 'basket', 'Статус корзина'
        new = 'new', 'Новый'
        confirmed = 'confirmed', 'Подтвержден'
        assembled = 'assembled', 'Собран'
        sent = 'sent', 'Отправлен'
        delivered = 'delivered', 'Доставлен'
        canceled = 'canceled', 'Отменен'

    objects = models.Manager()

    user = models.ForeignKey(CustomUser, related_name='order', on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    status = models.CharField(max_length=15, verbose_name='Статус', choices=StateChoices.choices,
                              default=StateChoices.basket)
    contacts = models.ForeignKey(ContactsUser, related_name='contacts', on_delete=models.CASCADE,
                                 verbose_name='Контакты', null=True, blank=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(fields=['id', 'status'], name='unique_order')
        ]

    def __str__(self):
        return f'{self.user} - {self.status}'

    def get_total_quantity(self):
        return sum(list(map(lambda x: x.quantity, self.items.all())))

    def get_total_cost(self):
        return sum(list(map(lambda x: x.quantity * x.product_info.price, self.items.all())))


class OrderItem(models.Model):
    objects = models.Manager()

    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Заказ', blank=True)
    product_info = models.ForeignKey(ProductInfo, related_name='order_items', on_delete=models.CASCADE,
                                     verbose_name='Информация о продукте')
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
        ordering = ('-order',)

    def __str__(self):
        return f'{self.order} - {self.product_info}'

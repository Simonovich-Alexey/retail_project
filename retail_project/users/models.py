from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise gettext_lazy(ValueError('Users must have an email address'))
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        if not password:
            raise gettext_lazy(ValueError('We need a password'))
        if not email:
            raise gettext_lazy(ValueError('Users must have an email address'))

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        user = self.create_user(email, password, **extra_fields)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
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
    first_name = models.CharField(verbose_name='Имя', max_length=100)
    last_name = models.CharField(verbose_name='Фамилия', max_length=100)
    is_active = models.BooleanField(verbose_name='Активированный', default=False)
    is_staff = models.BooleanField(verbose_name='Сотрудник', default=False)
    type_user = models.CharField(verbose_name='Тип пользователя', choices=UserType.choices,
                            max_length=10)
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Дата обновления', auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.email}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

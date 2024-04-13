from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Пользовательская модель пользователя
    """
    # Определение выбора типа пользователя
    class UserType(models.TextChoices):
        buyer = 'buyer', 'Покупатель'
        supplier = 'supplier', 'Поставщик'
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(verbose_name='Имя пользователя', max_length=100, validators=[username_validator])
    email = models.EmailField(verbose_name='E-mail', unique=True)
    password = models.CharField(max_length=50)
    type = models.CharField(verbose_name='Тип пользователя', choices=UserType.choices,
                            default=UserType.buyer, max_length=10,
                            help_text=gettext_lazy('Укажите тип пользователя: покупатель или поставщик'))
    is_active = models.BooleanField(verbose_name='Активированный', default=False)

    objects = UserManager()

    def __str__(self):
        return f'{self.username} {self.email}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

from django.db import models

from users.models import CustomUser


class ContactsUser(models.Model):
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

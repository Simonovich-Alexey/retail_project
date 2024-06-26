# Generated by Django 5.0.4 on 2024-05-15 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContactsUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=50, verbose_name='Город')),
                ('street', models.CharField(max_length=100, verbose_name='Улица')),
                ('house', models.IntegerField(verbose_name='Дом')),
                ('structure', models.IntegerField(blank=True, null=True, verbose_name='Корпус')),
                ('building', models.IntegerField(blank=True, null=True, verbose_name='Строение')),
                ('apartment', models.IntegerField(blank=True, null=True, verbose_name='Квартира')),
                ('favorite', models.BooleanField(default=False, verbose_name='Избранное')),
            ],
            options={
                'verbose_name': 'Контакты пользователя',
                'verbose_name_plural': 'Список контактов пользователя',
            },
        ),
    ]

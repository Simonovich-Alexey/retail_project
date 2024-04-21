from typing import Type
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from users.models import CastomUser


# @receiver(post_save, sender=CastomUser)
# def new_user_registered_signal(sender: Type[CastomUser], instance: CastomUser, created: bool, **kwargs):
#     """
#      отправляем письмо с подтрердждением почты
#     """
#     if created and not instance.is_verified:
#         # send an e-mail to the user
#         token = Token.objects.create(user=instance)
#         print(token)
#         # msg = EmailMultiAlternatives(
#         #     # title:
#         #     f"Password Reset Token for {instance.email}",
#         #     # message:
#         #     token,
#         #     # from:
#         #     settings.EMAIL_HOST_USER,
#         #     # to:
#         #     [instance.email]
#         # )
#         # msg.send()
#

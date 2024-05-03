from typing import Type
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from rest_framework.authtoken.models import Token

from users.models import CustomUser
from django.conf import settings


# @receiver(post_save, sender=CustomUser)
# def new_user_registered_signal(sender: Type[CustomUser], instance: CustomUser, created: bool, **kwargs):
#     """
#      отправляем письмо с подтрердждением почты
#     """
#     if created and not instance.is_active:
#         # send an e-mail to the user
#
#
#         msg = EmailMultiAlternatives(
#             # title:
#             f"Password Reset Token for {instance.email}",
#             # message:
#             token.key,
#             # from:
#             settings.EMAIL_HOST_USER,
#             # to:
#             [instance.email]
#         )
#         msg.send()
# #

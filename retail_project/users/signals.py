from typing import Type

from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings
from users.models import User


@receiver(post_save, sender=User)
def new_user_registered_signal(sender: Type[User], instance: User, created: bool, **kwargs):
    """
     отправляем письмо с подтрердждением почты
    """
    if created and not instance.is_verified:
        # send an e-mail to the user
        token = 'sadafgsgd'
        print(token)
        # msg = EmailMultiAlternatives(
        #     # title:
        #     f"Password Reset Token for {instance.email}",
        #     # message:
        #     token,
        #     # from:
        #     settings.EMAIL_HOST_USER,
        #     # to:
        #     [instance.email]
        # )
        # msg.send()

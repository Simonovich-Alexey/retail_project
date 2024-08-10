import uuid
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives


def email_activation(user_email, sender_email):
    key = uuid.uuid4().hex
    cache.set(key, {'user_email': user_email}, timeout=600)
    print(key)
    msg = EmailMultiAlternatives(
        # title:
        f"Подтверждение email",
        # message:
        f"Ваш код для подтверждения регистрации:\n\n{key}",
        # from:
        sender_email,
        # to:
        [user_email]
    )
    # msg.send()


def password_reset(user_email, sender_email):
    key = uuid.uuid4().hex
    cache.set(key, {'user_email': user_email}, timeout=600)
    print(key)
    msg = EmailMultiAlternatives(
        # title:
        f"Смена пароля",
        # message:
        f"Ваш код для смены пароля:\n\n{key}",
        # from:
        sender_email,
        # to:
        [user_email]
    )
    msg.send()


def order_confirm(user_email, sender_email):
    key = uuid.uuid4().hex
    cache.set(key, {'user_email': user_email}, timeout=600)
    print(key)
    msg = EmailMultiAlternatives(
        # title:
        f"Подтверждение заказа",
        # message:
        f"Ваш код для подтверждения заказа:\n\n{key}",
        # from:
        sender_email,
        # to:
        [user_email]
    )
    msg.send()

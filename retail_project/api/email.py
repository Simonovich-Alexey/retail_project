import uuid
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives


def email_activation(user_email, sender_email):
    """
    Отправляет сообщение активации по электронной почте пользователю с уникальным ключом для подтверждения.
    :param user_email: Адрес электронной почты пользователя.
    :param sender_email: Адрес электронной почты, с которого отправляется письмо активации.
    """
    # Генерация уникального ключа для активации
    key = uuid.uuid4().hex
    print(key)

    # Сохранение ключа в кэше с user_email в качестве значения
    cache.set(key, {'user_email': user_email}, timeout=600)

    # Составление сообщения электронной почты
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
    msg.send()


def password_reset(user_email, sender_email):
    """
    Генерирует уникальный ключ, сохраняет его в кэше с адресом электронной почты пользователя и отправляет
    письмо с ключом для сброса пароля.
    :param user_email: Адрес электронной почты пользователя.
    :param sender_email: Адрес электронной почты, с которого отправляется письмо активации.
    """
    # Генерируем уникальный ключ для сброса пароля
    key = uuid.uuid4().hex
    print(key)

    # Сохраняем ключ в кэше с адресом электронной почты пользователя для дальнейшей верификации
    cache.set(key, {'user_email': user_email}, timeout=600)

    # Отправляем письмо с ключом для сброса пароля
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
    """
    Генерирует уникальный ключ, сохраняет его в кэше с email пользователя и отправляет email с ключом
    пользователю для подтверждения заказа.
    :param user_email: Адрес электронной почты пользователя.
    :param sender_email: Адрес электронной почты, с которого отправляется письмо активации.
    """
    # Генерация уникального ключа
    key = uuid.uuid4().hex
    print(key)

    # Сохранение ключа в кэше с email пользователя на 10 минут
    cache.set(key, {'user_email': user_email}, timeout=600)

    # Отправка письма с кодом для подтверждения
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

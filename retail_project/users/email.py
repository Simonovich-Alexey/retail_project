import uuid
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives


def email_activation(user, email):
    key = uuid.uuid4().hex
    cache.set(key, {'user_email': user.email}, timeout=300)
    print(key)
    msg = EmailMultiAlternatives(
        # title:
        f"Подтверждение email",
        # message:
        f"Ваш код для подтверждения регистрации:\n\n{key}",
        # from:
        email,
        # to:
        [user.email]
    )
    msg.send()

from django.contrib.auth import tokens, login
from django.core.cache import cache
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from retail_project import settings
from .models import CustomUser
from .permissions import CurrentUserOrAdmin
from .serializers import CustomUserSerializer, ActivationSerializer, LoginSerializer, LogoutSerializer
from .email import email_activation


class LoginViewSet(viewsets.ModelViewSet):
    serializer_class = LoginSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.email
        token, _ = Token.objects.get_or_create(user=user)

        return Response({"token": token.key}, status=status.HTTP_200_OK)


class LogoutViewSet(viewsets.ModelViewSet):
    serializer_class = LogoutSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [CurrentUserOrAdmin]

    def create(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [CurrentUserOrAdmin]

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [AllowAny]
        elif self.action == "resend_activation":
            self.permission_classes = [AllowAny]
        elif self.action == "activation":
            self.permission_classes = [AllowAny]
        elif self.action == "login":
            self.permission_classes = [AllowAny]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserSerializer
        if self.action == 'resend_activation' or self.action == 'activation':
            return ActivationSerializer
        if self.action == 'login':
            return LoginSerializer

        return self.serializer_class

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        try:
            email_activation(user, settings.EMAIL_HOST_USER)
        except Exception as e:
            print({'error': e})

    @action(methods=["post"], detail=False)
    def resend_activation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # email = serializer.validated_data["email"]

        user = serializer.email
        print(user.id)

        email_activation(user, settings.EMAIL_HOST_USER)
        return Response({'message': 'Письмо отправлено'}, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False)
    def activation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        key = serializer.validated_data["key"]

        user = serializer.email

        redis_key = cache.get(key)
        if redis_key and redis_key.get('user_email') == user.email:
            with transaction.atomic():
                user.is_active = True
                user.save()
                cache.delete(key)
                return Response({'message': 'Пользователь успешно активирован'}, status=status.HTTP_200_OK)

        return Response({'message': 'Неверный ключ активации'}, status=status.HTTP_400_BAD_REQUEST)

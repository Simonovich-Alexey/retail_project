from django.contrib.auth import login, logout
from django.core.cache import cache
from django.db import transaction

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from retail_project import settings
from .models import CustomUser
from .permissions import CurrentUserOrAdmin, CurrentUser
from .serializers import ActivationSerializer, LoginSerializer, LogoutSerializer, RegisterUserSerializer, \
    ResendActivationSerializer, ProfileSerializer, PasswordResetSerializer
from .email import email_activation, password_reset


class RegisterUserViewSet(viewsets.ModelViewSet):
    serializer_class = RegisterUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def get_serializer_class(self):
        if self.action == 'resend_activation':
            return ResendActivationSerializer
        elif self.action == 'activation':
            return ActivationSerializer

        return self.serializer_class

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        if settings.ACTIVATION_EMAIL:
            email_activation(user, settings.EMAIL_HOST_USER)

    @action(methods=['post'], detail=False)
    def resend_activation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_email = serializer.validated_data['email']

        if settings.ACTIVATION_EMAIL:
            email_activation(user_email, settings.EMAIL_HOST_USER)
            return Response({'message': 'Письмо отправлено'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Активация не требуется'}, status=status.HTTP_400_BAD_REQUEST)

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


class LoginViewSet(viewsets.ModelViewSet):
    serializer_class = LoginSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.email
        token, _ = Token.objects.get_or_create(user=user)
        if token:
            login(request, user)

        return Response({"token": token.key}, status=status.HTTP_200_OK)


class LogoutViewSet(viewsets.ModelViewSet):
    serializer_class = LogoutSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [CurrentUserOrAdmin]

    def create(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        logout(request)
        return Response(status=status.HTTP_200_OK)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [CurrentUser]
    http_method_names = ['get', 'patch', 'delete', 'post']

    def get_serializer_class(self):
        if self.action == 'destroy':
            return self.serializer_class
        elif self.action == 'password_reset':
            return PasswordResetSerializer

    def list(self, request, *args, **kwargs):
        user = self.queryset.get(id=request.user.id)
        return Response(self.get_serializer(user).data)

    def update(self, request, pk='me', *args, **kwargs):
        user = self.queryset.get(id=request.user.id)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        if email and email != user.email and settings.ACTIVATION_EMAIL:
            serializer.is_active = False
            Token.objects.filter(user=user).delete()
            email_activation(email, settings.EMAIL_HOST_USER)

        serializer.save()
        return Response(self.get_serializer(user).data)

    def destroy(self, request, pk='me', *args, **kwargs):
        user = self.queryset.get(id=request.user.id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False)
    def password_reset(self, request):
        user = self.queryset.get(id=request.user.id)
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user_email = serializer.validated_data['email']

        if settings.PASSWORD_RESET_EMAIL:
            Token.objects.filter(user=user).delete()
            password_reset(user_email, settings.EMAIL_HOST_USER)
            return Response({'message': 'Письмо для смены пароля отправлено'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Смена пароля не требуется'}, status=status.HTTP_400_BAD_REQUEST)

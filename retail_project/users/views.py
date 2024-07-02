from django.contrib.auth import login, logout
from django.core.cache import cache
from django.db import transaction

from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from retail_project import settings
from .models import CustomUser, ContactsUser
from .permissions import CurrentUserOrAdmin, CurrentUser
from .serializers import ActivationSerializer, LoginSerializer, RegisterUserSerializer, \
    ResendActivationSerializer, ProfileSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, \
    ContactUserSerializer
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
        email_activation(user.email, settings.EMAIL_HOST_USER)

    @action(methods=['post'], detail=False)
    def resend_activation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_email = serializer.validated_data['email']

        email_activation(user_email, settings.EMAIL_HOST_USER)
        return Response({'message': 'Письмо отправлено'}, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False)
    def activation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        key = serializer.validated_data["key"]

        user = serializer.validated_data["user"]

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
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        if token:
            login(request, user)

        return Response({"token": token.key}, status=status.HTTP_200_OK)


class LogoutView(views.APIView):
    permission_classes = [CurrentUserOrAdmin]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [CurrentUser]
    http_method_names = ['get', 'patch', 'delete', 'post']

    def get_serializer_class(self):
        if self.action == 'password_reset':
            return PasswordResetSerializer
        elif self.action == 'password_reset_confirm':
            return PasswordResetConfirmSerializer
        if self.action == 'contacts':
            return ContactUserSerializer

        return self.serializer_class

    def get_permissions(self):
        if self.action == 'password_reset_confirm':
            return [AllowAny()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        return Response({'message': 'Метод не поддерживается'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        user = self.queryset.get(id=request.user.id)
        return Response(self.get_serializer(user).data)

    def update(self, request, pk='me', *args, **kwargs):
        user = self.queryset.get(id=request.user.id)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')

        if email and email != user.email:
            serializer.is_active = False
            Token.objects.filter(user=user).delete()
            email_activation(email, settings.EMAIL_HOST_USER)

        serializer.save()
        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)

    def destroy(self, request, pk='me', *args, **kwargs):
        user = self.queryset.get(id=request.user.id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False)
    def password_reset(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_email = serializer.validated_data['email']
        password_reset(user_email, settings.EMAIL_HOST_USER)

        return Response({'message': 'Письмо для смены пароля отправлено'}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def password_reset_confirm(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        key = serializer.validated_data['key']
        user = serializer.validated_data['user']

        redis_key = cache.get(key)
        if redis_key and redis_key.get('user_email') == user.email:
            with transaction.atomic():
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                cache.delete(key)
                Token.objects.filter(user_id=user.id).delete()
                return Response({'message': 'Пароль успешно изменен'}, status=status.HTTP_200_OK)

        return Response({'message': 'Неверный ключ смены пароля'}, status=status.HTTP_400_BAD_REQUEST)


class ContactsUserViewSet(viewsets.ModelViewSet):
    serializer_class = ContactUserSerializer
    queryset = ContactsUser.objects.all()
    permission_classes = [CurrentUser]
    http_method_names = ['get', 'patch', 'delete', 'post']

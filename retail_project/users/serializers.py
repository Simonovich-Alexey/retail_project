from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'phone', 'first_name', 'last_name', 'password', 'type_user']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8, 'max_length': 64}}

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class ResendActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        user = CustomUser.objects.filter(email=attrs.get('email')).first()
        if user:
            if not user.is_active:
                return attrs

            raise ValidationError({'message': 'Пользователь уже активирован'})

        raise ValidationError({'message': 'Пользователь не найден'})


class ActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    key = serializers.CharField()

    def validate(self, attrs):
        user = CustomUser.objects.filter(email=attrs.get('email')).first()
        if user:
            if not user.is_active:
                self.email = user
                return attrs
            raise ValidationError({'message': 'Пользователь уже активирован'})
        raise ValidationError({'message': 'Пользователь не найден'})


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        self.email = CustomUser.objects.filter(email=email).first()
        if self.email:
            if self.email.is_active:
                if self.email.check_password(password):
                    attrs['user'] = self.email
                    return attrs
            raise ValidationError({'message': 'Пользователь не активирован'})
        raise ValidationError({'message': 'Неверная почта или пароль'})


class LogoutSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['email']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'first_name', 'last_name', 'type_user']


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        self.email = CustomUser.objects.filter(email=email).first()
        if not self.email:
            raise ValidationError({'message': 'Пользователь не найден'})

        return attrs


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    key = serializers.CharField(min_length=8, max_length=64)
    new_password = serializers.CharField(min_length=8, max_length=64)
    confirm_password = serializers.CharField(min_length=8, max_length=64)

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        user = CustomUser.objects.filter(email=attrs.get('email')).first()
        if not user:
            raise ValidationError({'message': 'Пользователь не найден'})
        if user.check_password(new_password):
            raise ValidationError({'message': 'Новый пароль совпадает с текущим'})
        if new_password != confirm_password:
            raise ValidationError({'message': 'Пароли не совпадают'})

        return attrs

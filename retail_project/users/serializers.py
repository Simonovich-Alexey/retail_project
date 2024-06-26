import re

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

    def validate(self, attrs):
        phone = attrs.get('phone')
        pattern_phone = r'[+]?[8,7]?[\s -]?(\d{3})[\s -]?(\d{3})[\s -]?(\d{2})[\s -]?(\d{2})'
        result_phone = re.sub(pattern_phone, r'+7 \1 \2-\3-\4', phone)
        attrs['phone'] = result_phone
        if CustomUser.objects.filter(phone=result_phone).exists():
            raise ValidationError({'message': 'Такой номер уже зарегистрирован'})
        return super().validate(attrs)


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
                attrs['user'] = user
                return attrs
            raise ValidationError({'message': 'Пользователь уже активирован'})
        raise ValidationError({'message': 'Пользователь не найден'})


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = CustomUser.objects.filter(email=email).first()
        if user:
            if user.is_active:
                if user.check_password(password):
                    attrs['user'] = user
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

    def validate(self, attrs):
        phone = attrs.get('phone')
        pattern_phone = r'[+]?[8,7]?[\s -]?(\d{3})[\s -]?(\d{3})[\s -]?(\d{2})[\s -]?(\d{2})'
        result_phone = re.sub(pattern_phone, r'+7 \1 \2-\3-\4', phone)
        attrs['phone'] = result_phone
        return super().validate(attrs)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        user = CustomUser.objects.filter(email=email).first()
        if user and user.email == email:
            attrs['user'] = user
            return attrs
        raise ValidationError({'message': 'Неверная почта'})


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
        attrs['user'] = user
        return attrs

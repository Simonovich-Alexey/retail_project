from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'type_user']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8, 'max_length': 64}}

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        email = super().validate(validated_data.get('email'))

        if email:
            instance.is_active = False

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.type_user = validated_data.get('type_user', instance.type_user)
        instance.save()
        return instance


class ActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    key = serializers.CharField(required=False)

    def validate(self, data):
        try:
            self.email = CustomUser.objects.get(email=data.get('email'))
        except CustomUser.DoesNotExist:
            raise ValidationError({'message': 'Пользователь не найден'})

        if not self.email.is_active:
            return data
        else:
            raise ValidationError({'message': 'Пользователь уже активирован'})


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        self.email = CustomUser.objects.filter(email=email).first()
        if self.email:
            if self.email.is_active:
                if self.email.check_password(password):
                    data['user'] = self.email
                    return data
            raise ValidationError({'message': 'Пользователь не активирован'})
        raise ValidationError({'message': 'Неверная почта или пароль'})


class LogoutSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = CustomUser
        fields = ['email']

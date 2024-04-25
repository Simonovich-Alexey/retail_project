from requests import Request
from rest_framework import serializers

from .models import CastomUser


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = CastomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'type']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8, 'max_length': 64}}

    def create(self, validated_data):
        return CastomUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.type = validated_data.get('type', instance.type)
        instance.save()
        return instance


class ChangeUserSerializer(serializers.Serializer):

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    type = serializers.CharField(max_length=10)
    password = serializers.CharField(min_length=8, max_length=64, write_only=True)
    email = serializers.EmailField(write_only=True)

    def validate(self, data):
        if data.get('password'):
            raise serializers.ValidationError('You cannot change password')
        if data.get('email'):
            raise serializers.ValidationError('You cannot change email')
        return data

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.type = validated_data.get('type', instance.type)
        instance.save()
        return instance

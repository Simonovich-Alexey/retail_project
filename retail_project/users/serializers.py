from rest_framework import serializers

from .models import CastomUser


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = CastomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'type']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8, 'max_length': 64}}

    def create(self, validated_data):
        return CastomUser.objects.create_user(**validated_data)

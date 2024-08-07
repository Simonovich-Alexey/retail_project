import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _

from .models import CustomUser, ContactsUser, Shop, Category, Product, ProductInfo


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'phone', 'company', 'first_name', 'last_name', 'password', 'type_user']
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


class ContactUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactsUser
        fields = ['id', 'city', 'street', 'house', 'apartment', 'favorite', 'structure', 'building']
        extra_kwargs = {
            'structure': {'required': False},
            'building': {'required': False},
        }
        ordering = ['favorite']

    def validate(self, attrs):
        contacts = ContactsUser.objects.filter(user=self.context['request'].user)
        attrs['user_id'] = self.context['request'].user.id
        if len(contacts) > 5:
            raise ValidationError({'message': 'Вы достигли максимального количества контактов (10)'})
        return super().validate(attrs)

    def create(self, validated_data):
        if validated_data.get('favorite'):
            favorite = ContactsUser.objects.filter(user=self.context['request'].user, favorite=True).first()
            if favorite:
                favorite.favorite = False
                favorite.save()

        return ContactsUser.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('favorite'):
            favorite = ContactsUser.objects.filter(user=self.context['request'].user, favorite=True).first()
            if favorite:
                favorite.favorite = False
                favorite.save()

        return super().update(instance, validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    contacts = ContactUserSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'first_name', 'last_name', 'type_user', 'company', 'contacts']

    def validate(self, attrs):
        if attrs.get('type_user'):
            raise ValidationError({'message': 'Тип пользователя не может быть изменен'})
        phone = attrs.get('phone')
        if attrs.get('phone'):
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


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name_shop', 'status_order']
        extra_kwargs = {'name_shop': {'required': False}}


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name_category']


class LoadingGoodsSerializer(serializers.Serializer):
    url_file = serializers.URLField()

    def update(self, instance, validated_data):
        instance.url_file = validated_data.get('url_file')
        instance.save()
        return instance


# class ProductInfoSerializer(serializers.ModelSerializer):
#     name_shop = serializers.CharField(source='shop.name_shop')
#
#     class Meta:
#         model = ProductInfo
#         fields = ['id', 'name', 'name_shop', 'quantity', 'price', 'price_rrc']
#
#
# class ProductSerializer(serializers.ModelSerializer):
#     product_info = ProductInfoSerializer(many=True, read_only=True)
#     name_category = serializers.CharField(source='category_id.name_category')
#
#     class Meta:
#         model = Product
#         fields = ['id', 'name_product', 'name_category', 'product_info']


class ProductSerializer(serializers.ModelSerializer):
    name_category = serializers.CharField(source='category_id.name_category')

    class Meta:
        model = Product
        fields = ['name_product', 'name_category', 'category_id']


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True, many=False)
    name_shop = serializers.CharField(source='shop.name_shop')

    class Meta:
        model = ProductInfo
        fields = ['id', 'name', 'name_shop', 'quantity', 'price', 'price_rrc', 'product']

from typing import Any, Dict, List

import yaml
import requests
from django.contrib.auth import login, logout
from django.core.cache import cache
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, generics, status, views
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from retail_project import settings
from .models import (CustomUser, ContactsUser, Shop, Category, Product, ProductInfo, Parameter, ProductParameter,
                     Order, OrderItem)
from .permissions import CurrentUserOrAdmin, CurrentUser
from .serializers import ActivationSerializer, LoginSerializer, RegisterUserSerializer, \
    ResendActivationSerializer, ProfileSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer, \
    ContactUserSerializer, ShopSerializer, CategorySerializer, LoadingGoodsSerializer, ProductInfoSerializer, \
    OrderSerializer, OrderItemSerializer
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
        if serializer.validated_data.get('type_user') == 'supplier':
            Shop.objects.create(name_shop=serializer.validated_data.get('company'),
                                user_id=user.id)
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
        if serializer.validated_data.get('company'):
            Shop.objects.filter(user_id=user.id).update(name_shop=serializer.validated_data.get('company'))

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

    def list(self, request, *args, **kwargs):
        contacts = self.queryset.filter(user_id=request.user.id)
        return Response(self.get_serializer(contacts, many=True).data)


class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get', 'patch']

    def get_permissions(self):
        if self.action == 'status_order':
            return [CurrentUser()]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        return Response({'error': 'Изменение магазина запрещено'}, status=405)

    @action(methods=['get', 'patch'], detail=False)
    def status_order(self, request):
        user = get_object_or_404(self.queryset, user_id=request.user.id)
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ['get']


class LoadingGoods(generics.UpdateAPIView):
    queryset = Shop.objects.all()
    serializer_class = LoadingGoodsSerializer
    permission_classes = [CurrentUser]

    @transaction.atomic
    def update(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """
        Обновление данных магазина пользователя.
        """
        # Получаем магазин пользователя
        shop = get_object_or_404(self.queryset, user_id=request.user.id)
        serializer = self.get_serializer(shop, data=request.data)
        serializer.is_valid(raise_exception=True)
        url = serializer.validated_data.get('url_file')
        serializer.save()

        # Получаем данные из файла по URL
        url_response = requests.get(url)

        if url_response.status_code != 200:
            return Response({'message': 'Неверный URL'}, status=status.HTTP_400_BAD_REQUEST)

        # Загружаем YAML данные
        data = yaml.safe_load(url_response.content)

        categories_data: List[Dict[str, Any]] = data.get('categories', [])
        products_data: List[Dict[str, Any]] = data.get('goods', [])

        if not categories_data or not products_data:
            return Response({'message': 'Неверные данные'}, status=status.HTTP_400_BAD_REQUEST)

        # Обработка категорий
        category_objs = {}
        for categories in categories_data:
            categories_obj, _ = Category.objects.get_or_create(name_category=categories['name'])
            category_objs[categories['id']] = categories_obj
            categories_obj.shop.add(shop)

        # Обработка продуктов
        for item in products_data:
            category = category_objs.get(item['category'])

            product, _ = Product.objects.get_or_create(
                name_product=item['name'],
                category_id=category
            )
            product_info, _ = ProductInfo.objects.update_or_create(
                product=product,
                shop=shop,
                external_id=item['id'],
                defaults={
                    'name': item['name'],
                    'price': item['price'],
                    'price_rrc': item['price_rrc'],
                    'quantity': item['quantity'],
                }
            )

            # Обработка параметров продукта
            for name, value in item['parameters'].items():
                parameter_obj, _ = Parameter.objects.get_or_create(
                    name_parameter=name
                )

                ProductParameter.objects.get_or_create(
                    product_info=product_info,
                    parameter=parameter_obj,
                    value=value
                )

        return Response({'message': 'Товары загружены'}, status=status.HTTP_200_OK)


class ProductInfoViewSet(viewsets.ModelViewSet):
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['shop']
    search_fields = ['name', 'shop__name_shop', 'product__name_product', 'product__category_id__name_category']
    ordering_fields = ['shop', 'product', 'price', 'quantity']
    http_method_names = ['get']


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [CurrentUser]

    def create(self, request, *args, **kwargs):
        user = get_object_or_404(CustomUser, id=request.user.id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order, _ = Order.objects.get_or_create(user=user)
        quantity = serializer.validated_data['quantity']
        product_info = serializer.validated_data['product_info']

        order_item, _ = OrderItem.objects.update_or_create(product_info=product_info,
                                                           order=order,
                                                           defaults={
                                                               'quantity': quantity
                                                           })
        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [CurrentUser]
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

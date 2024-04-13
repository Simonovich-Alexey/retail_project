from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User


class RegisterUser(APIView):
    def post(self, request, *args, **kwargs):
        create_user = User.objects.create_user()
        return Response({'message': 'OK'})

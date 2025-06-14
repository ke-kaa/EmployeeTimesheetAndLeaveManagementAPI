from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import EmployeeModel
from .serializers import EmployeeAccountCreationSerializer
from .permissions import IsManager


class EmployeeCreationView(generics.CreateAPIView):
    serializer_class = EmployeeAccountCreationSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser | IsManager]
    authentication_classes = [JWTAuthentication]
from django.shortcuts import render
from . import serializers as my_serializers
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from datetime import datetime
from rest_framework.utils import timezone
from rest_framework.permissions import IsAuthenticated


from . import models as my_models


class ClockInView(generics.CreateAPIView):
    serializer_class = my_serializers.ClockInSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        timesheet = serializer.save()

        return Response({
            'timesheet_id': timesheet.id,
            'clock_in_time': timesheet.clock_in_time,
        }, status=status.HTTP_201_CREATED)
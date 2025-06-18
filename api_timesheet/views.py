from django.shortcuts import render
from . import serializers as my_serializers
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model


from . import models as my_models
from . import permissions as my_permissions
from api_authentication.models import EmployeeModel


User = get_user_model()


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
    

class ClockOutView(generics.UpdateAPIView):
    serializer_class = my_serializers.ClockOutSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        timesheet = serializer.save()

        return Response({
            'timesheet_id': timesheet.id,
            'clock_in_time': timesheet.clock_in_time,
            'clock_out_time': timesheet.clock_out_time,
        }, status=status.HTTP_200_OK)
    

class EmployeeTimesheetView(generics.ListAPIView):
    serializer_class = my_serializers.EmployeeTimesheetSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    page_size = 15
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['clock_in_time', 'clock_out_time', 'working_hours']
    ordering = ['-clock_in_time', '-clock_out_time']
    
    def get_queryset(self):
        return my_models.TimesheetModel.objects.filter(user=self.request.user)


class TeamEmployeeTimesheetView(generics.ListAPIView):
    serializer_class = my_serializers.TeamEmployeeTimesheetSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, my_permissions.IsManager]

    pagination_class = PageNumberPagination
    page_size = 10

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['clock_in_time', 'clock_out_time', 'working_hours']
    ordering = ['-clock_in_time']

    def get_queryset(self):
        current_employee = EmployeeModel.objects.get(user=self.request.user)
        team_employees = EmployeeModel.objects.filter(manager=current_employee).values_list('user', flat=True)
        return my_models.TimesheetModel.objects.filter(user__in=team_employees)

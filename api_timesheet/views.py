from django.shortcuts import render
from . import serializers as my_serializers
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination



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
    serializer_class = my_serializers.EmployeeTimesheet
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    page_size = 15
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['clock_in_time', 'clock_out_time', 'working_hours']
    ordering = ['-clock_in_time', '-clock_out_time']
    
    def get_queryset(self):
        return my_models.TimesheetModel.objects.filter(user=self.request.user)
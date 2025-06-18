from django.shortcuts import render
from rest_framework import generics, permissions, status, pagination, filters
from rest_framework_simplejwt import authentication
from rest_framework.response import Response


from . import models as my_models, serializers as my_serializers, permissions as my_permissions, pagination as my_pagination
from api_authentication.models import EmployeeModel


class EmployeeLeaveRequestCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.JWTAuthentication]
    serializer_class = my_serializers.EmployeeLeaveRequestCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leave_request = serializer.save()

        return Response(
            {
                'leave_request_id': leave_request.id,
                'start_date': leave_request.start_date,
                'end_date': leave_request.end_date,
                'reason': leave_request.reason,
                'status': leave_request.status,
                'approved_by': leave_request.approved_by.get_full_name() if leave_request.approved_by else None,
            },
            status=status.HTTP_201_CREATED
        )
    

class EmployeeLeaveRequestListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.JWTAuthentication]
    serializer_class = my_serializers.EmployeeLeaveRequestListSerializer
    pagination_class = my_pagination.LeaveRequestPagination

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['start_date', 'end_date', 'status']
    ordering = ['-start_date', '-end_date']

    def get_queryset(self):
        return my_models.LeaveRequestModel.objects.filter(user=self.request.user)


class TeamLeaveRequestView(generics.ListAPIView):
    serializer_class = my_serializers.TeamLeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser | my_permissions.IsManager]
    pagination_class = my_pagination.LeaveRequestPagination
    authentication_classes = [authentication.JWTAuthentication]


    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['start_date', 'end_date', 'status']
    ordering = ['-start_date', '-end_date']

    def get_queryset(self):
        current_employee = EmployeeModel.objects.get(user=self.request.user)
        team_employee = EmployeeModel.objects.filter(manager=current_employee).values_list('user', flat=True)
        return my_models.LeaveRequestModel.objects.filter(user__in=team_employee)
    

class ApproveEmployeeLeaveRequestView(generics.UpdateAPIView):
    serializer_class = my_serializers.ApproveEmployeeLeaveRequestSerializer
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser | my_permissions.IsManager]
    queryset = my_models.LeaveRequestModel.objects.all()
    lookup_field = 'pk'

    
class RejectEmployeeLeaveRequestView(generics.UpdateAPIView):
    serializer_class = my_serializers.RejectEmployeeLeaveRequestSerializer
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser | my_permissions.IsManager]
    queryset = my_models.LeaveRequestModel.objects.all()
    lookup_field = 'pk'
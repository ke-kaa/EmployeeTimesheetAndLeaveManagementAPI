from rest_framework import serializers
from rest_framework.utils import timezone


from . import models as my_models
from api_authentication.models import EmployeeModel


class EmployeeLeaveRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = my_models.LeaveRequestModel
        fields = ['id', 'start_date', 'end_date', 'reason',]
    
    def validate(self, attrs):
        if attrs['start_date'] < timezone.now().date():
            raise serializers.ValidationError("Leave start date cannot be in the past.")
        
        if attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError("Leave start date cannot be after leave end date.")
        
        overlapping_requests = my_models.LeaveRequestModel.objects.filter(
            user=self.context['request'].user,
            start_data__lte=attrs['start_date'],
            end_date__gte=attrs['end_date']
            )
        
        if overlapping_requests.exists():
            raise serializers.ValidationError("You have an overlapping leave request")
        
        return attrs

    def create(self, validated_data):
        return my_models.LeaveRequestModel(
            user=self.context['request'].user,
            **validated_data
        )


class EmployeeLeaveRequestListSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    approved_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = my_models.LeaveRequestModel
        fields = ['id', 'start_date', 'end_date', 'reason', 'status', 'approved_by']
    
    def get_approved_by(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None


class EmployeeBasicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeModel
        fields = ['employee_id', 'department', 'job_title']


class TeamLeaveRequestSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = my_models.LeaveRequestModel
        fields = ['id', 'start_date', 'end_date', 'reason', 'status', 'approved_by', 'user']

    def get_user(self, obj):
        try:
            employee = EmployeeModel.objects.get(user=obj.user)
            return {
                'username': obj.user.username,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
                'employee_info': EmployeeBasicInfoSerializer(employee).data
            }
        except EmployeeModel.DoesNotExist:
            return {
                'username': obj.user.username,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
                'employee_info': None
            }
        

class ApproveEmployeeLeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = my_models.LeaveRequestModel
        fields = ['id', 'start_date', 'end_date', 'reason', 'status', 'approved_by']
        read_only_fields = ['id', 'start_date', 'end_date', 'reason']

    
    def update(self, instance, validated_data):
        if instance.status != my_models.LeaveRequestModel.Status.PENDING:
            raise serializers.ValidationError("Only pending leave request can be approved.")
        
        instance.status = my_models.LeaveRequestModel.Status.APPROVED
        instance.approved_by = self.context['request'].user
        instance.save()

        return instance


class RejectEmployeeLeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = my_models.LeaveRequestModel
        fields = ['id', 'start_date', 'end_date', 'reason', 'status', 'approved_by']
        read_only_fields = ['id', 'start_date', 'end_date', 'reason']
    
    def update(self, instance, validated_data):
        if instance.status != my_models.LeaveRequestModel.Status.PENDING:
            raise serializers.ValidationError("Only pending leave request can be rejected.")
        
        instance.status = my_models.LeaveRequestModel.Status.REJECTED
        instance.approved_by = self.context['request'].user
        instance.save()

        return instance    
from rest_framework import serializers
from rest_framework.utils import timezone


from . import models as my_models


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

from rest_framework import serializers
from . import models as my_models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.http import JsonResponse


User = get_user_model()


class ClockInSerializer(serializers.ModelSerializer):
    clock_in_time = serializers.DateTimeField(required=False)

    class Meta:
        model = my_models.TimesheetModel
        fields = ['clock_in_time']
    
    def validate(self, data):
        request = self.context['request']
        user = request.user
        today = timezone.now().date()

        if my_models.TimesheetModel.filter(user=user, clock_in_time=today):
            raise serializers.ValidationError("You have already clocked in today.")
        
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user

        my_models.TimesheetModel.objects.create(
            user=user, 
            clock_in_time=validated_data.get('clock_in_time', timezone.now()),
        )
    
    
from rest_framework import serializers
from . import models as my_models
from django.utils import timezone
from django.contrib.auth import get_user_model


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

        return my_models.TimesheetModel.objects.create(
            user=user, 
            clock_in_time=validated_data.get('clock_in_time', timezone.now()),
        )
    

class ClockOutSerializer(serializers.ModelSerializer):
    clock_out_time = serializers.DateTimeField(required=False)

    class Meta:
        model = my_models.TimesheetModel
        fields = ['clock_out_time']
    
    def validate(self, data):
        user = self.context['request'].user

        try:
            self.timesheet = my_models.TimesheetModel.objects.filter(
                user=user,
                clock_in_time__isnull=False,
                clock_out_time__isnull=True,
            ).latest('clock_in_time')
        except my_models.TimesheetModel.DoesNotExist as e:
            raise serializers.ValidationError("No active clock-in found.")
        
        clock_out_time = data.get('clock_out_time', timezone.now())

        if clock_out_time < self.timesheet.clock_in_time:
            raise serializers.ValidationError("Clock-out time must be after clock-in time.")
        
        self.validated_clock_out_time = clock_out_time

        return data
    
    def save(self, **kwargs):
        self.timesheet.clock_out_time = self.validated_clock_out_time
        self.timesheet.save()
        return self.timesheet
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class TimesheetModel(models.Model):
    """
    Model to track employee timesheets, including clock-in and clock-out times,
    and automatically calculates the total working hours for each shift.

    Fields:
        user (ForeignKey): Reference to the User who owns the timesheet entry.
        clock_in_time (DateTimeField): The datetime when the employee clocks in.
        clock_out_time (DateTimeField): The datetime when the employee clocks out.
        working_hours (DurationField): The duration between clock-in and clock-out, auto-calculated.

    Methods:
        save(): Calculates and stores working_hours before saving.
        clean(): Validates that clock_out_time is not before clock_in_time.

    Meta:
        Adds an index on user and clock_in_time for efficient querying.
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True,)
    clock_in_time = models.DateTimeField(null=True, blank=True,db_index=True)
    clock_out_time = models.DateTimeField(null=True, blank=True, db_index=True)
    working_hours = models.DurationField(null=True, blank=True, editable=False, db_index=True)

    def save(self, *args, **kwargs):
        if self.clock_in_time and self.clock_out_time:
            self.working_hours = self.clock_out_time - self.clock_in_time    
        else:
            self.working_hours = None

        super().save(*args, **kwargs)
    
    def clean(self):
        if self.clock_out_time < self.clock_in_time:
            raise ValidationError("Clock in time cannot be before Clock out time.")
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'clock_in_time'])
        ]

        ordering = ['-clock_in_time']
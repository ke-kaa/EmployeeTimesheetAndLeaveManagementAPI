from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class LeaveRequestModel(models.Model):
    """
    Model to represent an employee's leave request.

    Fields:
        user (ForeignKey): The user requesting leave.
        start_date (DateField): The start date of the leave period.
        end_date (DateField): The end date of the leave period.
        reason (CharField): The reason for the leave request.
        status (CharField): The current status of the leave request (Pending, Approved, Rejected).
        approved_by (ForeignKey): The user (typically a manager or admin) who approved or rejected the request.

    Methods:
        clean(): Validates 
                        that the leave request does not overlap with existing requests,
                        that the start date is not in the past, and
                        that the start date is not after the end date.
        __str__(): Returns a human-readable representation of the leave request.

    Meta:
        Adds an index on user and start_date for efficient querying.
    """
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"


    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='leave_requests', 
        db_index=True
    )
    start_date = models.DateField(db_index=True)
    end_date = models.DateField()
    reason = models.CharField(max_length=2500)
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING, 
        db_index=True,
    )
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_leaves'
    )

    def clean(self):
        overlapping_requests = LeaveRequestModel.objects.filter(
            user=self.user, 
            start_date__lte=self.end_date, 
            end_date__gte=self.start_date
        )
        if self.pk:
            overlapping_requests = overlapping_requests.exclude(pk=self.pk)
        if overlapping_requests.exists():
            raise ValidationError("You have an overlapping leave request.")
        if self.start_date < timezone.now().date():
            raise ValidationError("Leave start date cannot be in the past.")
        if self.start_date > self.end_date:
            raise ValidationError("Leave start date cannot be after leave end date.")
        return super().clean()
        
    def __str__(self):
        return f'Name: {self.user.get_full_name() or self.user.first_name or self.user.last_name}\nLeave Start Date: {self.start_date}\nLeave End Date: {self.end_date}\nStatus: {self.get_status_display()}'
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'start_date'])
        ]

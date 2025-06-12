from django.db import models
from django.contrib.auth.models import User
import uuid

# let user to login using both email and username
# default User model - for login
# use employee model for registration 
# Separate Work Schedule class for user workshecule FK to Employee
class Employee(models.Model):
    GENDER_CHOICE = (
        ("Male", "Male"),
        ("Female", "Female"),
    )
    ROLE_CHOICES = (
        ("EMPLOYEE", "EMPLOYEE"),
        ("MANAGER", "MANAGER"),
        ("ADMIN", "ADMIN"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.UUIDField(uuid.uuid4, editable=False, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True, choices=GENDER_CHOICE)
    phone_number_one = models.CharField(max_length=20, null=True, blank=True)
    phone_number_two = models.CharField(max_length=20, null=True, blank=True)
    department = models.CharField(max_length=250, null=True, blank=True)
    job_title =  models.CharField(max_length=250, null=True, blank=True)
    hire_date = models.DateField()
    leave_balance = models.FloatField(null=True, blank=True)
    manager = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    roles = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_CHOICES[0])
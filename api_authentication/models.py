from django.db import models
from django.contrib.auth.models import User
import uuid

# let user to login using both email and username
# default User model - for login, registration 
# use employee model for users extra profile
# Separate Work Schedule class for user workshecule FK to Employee
class EmployeeModel(models.Model):
    """
    Model to store additional employee information linked to a Django User.

    Fields:
        user (OneToOneField): The associated Django User account.
        employee_id (UUIDField): Unique identifier for the employee.
        date_of_birth (DateField): The employee's date of birth.
        gender (CharField): The employee's gender (Male/Female).
        phone_number_one (CharField): Primary phone number.
        phone_number_two (CharField): Secondary phone number (optional).
        department (CharField): Department where the employee works.
        job_title (CharField): Employee's job title.
        hire_date (DateField): Date the employee was hired.
        leave_balance (FloatField): Remaining leave balance for the employee.
        manager (ForeignKey): Reference to the employee's manager (self-referential).
        role (CharField): Role of the employee (EMPLOYEE, MANAGER, ADMIN).

    Notes:
        - Used for employee registration and profile management.
        - Supports linking to a separate Work Schedule model via a foreign key.
    """

    GENDER_CHOICE = (
        ("Male", "Male"),
        ("Female", "Female"),
    )
    ROLE_CHOICES = (
        ("EMPLOYEE", "EMPLOYEE"),
        ("MANAGER", "MANAGER"),
        ("ADMIN", "ADMIN"),
    )

    password_reset_required = models.BooleanField(default=True)
    temp_password = models.CharField(max_length=128)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.UUIDField(uuid.uuid4, editable=False, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True, choices=GENDER_CHOICE)
    phone_number_one = models.CharField(max_length=20, null=True, blank=True)
    phone_number_two = models.CharField(max_length=20, null=True, blank=True)
    department = models.CharField(max_length=250, null=True, blank=True)
    job_title =  models.CharField(max_length=250, null=True, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    leave_balance = models.FloatField(null=True, blank=True)
    manager = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_CHOICES[0])
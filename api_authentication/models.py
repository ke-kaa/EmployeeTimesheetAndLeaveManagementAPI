from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class CustomUser(User):
    ROLE_CHOICES = (
        ("EMPLOYEE", "EMPLOYEE"),
        ("MANAGER", "MANAGER"),
        ("ADMIN", "ADMIN"),
    )

    roles = models.CharField(choices=ROLE_CHOICES, default=ROLE_CHOICES[0])
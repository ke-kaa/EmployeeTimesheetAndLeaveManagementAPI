from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import EmployeeModel
from django.core import cache

@receiver(post_save, sender=EmployeeModel)
@receiver(post_delete, sender=EmployeeModel)
def clear_employee_cache(sender, instance, **kwargs):
    # Clear department cache
    cache.delete(f"user_{instance.user.id}_department")
    # Clear manager validation cache
    cache.delete_pattern(f"manager_validation_{instance.user.email}*")
    cache.delete_pattern(f"manager_validation_{instance.user.username}*")
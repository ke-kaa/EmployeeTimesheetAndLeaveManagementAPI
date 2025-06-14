from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import secrets
from .models import EmployeeModel
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
import logging
import smtplib
from .utils import SMTP_ERROR_CODES
from django.db import transaction

logger = logging.getLogger(__name__)

class EmployeeAccountCreationSerializer(serializers.ModelSerializer):
    ROLE_CHOICES = (
        ("EMPLOYEE", "EMPLOYEE"),
        ("MANAGER", "MANAGER"),
        ("ADMIN", "ADMIN"),
    )
    role = serializers.CharField(required=True, choices=ROLE_CHOICES)
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    manager_email_or_username = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'manager_email_or_username',]
    
    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})
        if 'manager_email_or_username' in data:
            manager = self._get_manager_by_email_or_username(data['manager_email_or_username'])
            if not manager:
                raise serializers.ValidationError(
                    {"manager_email_or_username": "No valid manager found with this email/username"}
                )

        return data
    
    def create(self, validated_data):
        with transaction.atomic():
            temp_password = secrets.token_urlsafe(12)

            user = User.objects.create(
                username=validated_data['username'],
                email=validated_data['email'],
                password=make_password(temp_password),
                is_active=True
            )

            EmployeeModel.objects.create(
                user=user,
                temp_password=temp_password,
                role=validated_data['role'],
                manager=self._get_manager_by_email_or_username(validated_data['manager_email_or_username']),
            )

            self._send_credentials_email(username=validated_data['username'], temp_password=temp_password, recipient=validated_data['email'])

    def _send_credentials_email(self, username, temp_password, recipient,):
        subject = "Your Employee Account Credentials"
        message = f'''
        Hello, 

        Your account has been created. Please log in using:
        Username: {username}
        Password: {temp_password}

        Reset your password on first login.
        Login here: {reverse_lazy('password-reset-view-name')} 
        '''
        # View and url or password reset will be created later.
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
        except smtplib.SMTPResponseException as e:
            error_code = e.smtp_code  # Fix variable name
            error_message = SMTP_ERROR_CODES.get(error_code, f"Unknown error ({error_code})")
            logger.error(f"Failed to send email to {recipient}: {error_message.format(e.smtp_error)}")
        except Exception as e:
            logger.error(f"Unexpected error sending email to {recipient}: {str(e)}")        

    def _get_manager_by_email_or_username(self, value):
        ROLES = ('ADMIN', 'MANAGER')
        if not value:
            return None
        user = (User.objects.filter(email__iexact=value) | User.objects.filter(username__exact=value)).first()
        if user and hasattr(user, 'employee'):
            if user.employee.role in ['ADMIN', 'MANAGER']:
                return user.employee
        return None
    
    def validate_email(self, value):
        norm_email = value.lower()
        if User.objects.filter(email=norm_email).exists():
            raise serializers.ValidationError("This email is already registered.")
        return norm_email
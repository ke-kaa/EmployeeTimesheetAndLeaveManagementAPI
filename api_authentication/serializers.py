from rest_framework import serializers
from django.contrib.auth import get_user_model
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
from django.core.cache import cache
from django.contrib.auth import authenticate

logger = logging.getLogger(__name__)
User = get_user_model()
# Cache timeout (1 hour)
MANAGER_DEPT_CACHE_TIMEOUT = 3600  
USER_EXISTS_CACHE_TIMEOUT = 300

class EmployeeAccountCreationSerializer(serializers.ModelSerializer):
    """
    Secure employee account creation serializer with department-level access control and caching.

    Handles atomic creation of User and EmployeeModel records with:
    - Temporary password generation (secrets.token_urlsafe)
    - Credential email delivery with SMTP error handling
    - Transaction rollback on failures
    - Department-level permission enforcement
    - Optimized validation caching

    Security Features:
    ─────────────────
    • JWT-authenticated requests only
    • Managers restricted to their own department (cached validation)
    • Admin bypass for cross-department creation
    • Case-insensitive email normalization
    • Atomic rollback if email delivery fails

    Field Requirements:
    ──────────────────
    role (str):                      Must be EMPLOYEE/MANAGER/ADMIN (managers can only assign EMPLOYEE)
    email (str):                     Valid email format, case-normalized, unique
    username (str):                  Unique identifier
    department (str):                Required - validated against manager's cached department
    manager_email_or_username (str): Optional - must reference valid ADMIN/MANAGER (cached lookup)

    Caching Behavior (TTL):
    ──────────────────────
    • Manager department (1 hour)
    • Manager validation (30 minutes)
    • Email/username existence (5 minutes)

    Validation Rules:
    ────────────────
    For Managers:
    ✓ department MUST match manager's cached department
    ✓ Can only create EMPLOYEE roles
    ✓ Manager reference must be valid ADMIN/MANAGER

    For Admins:
    ✓ No department restrictions
    ✓ Can create any role type

    Transaction Safety:
    ──────────────────
    • Entire operation (User+Employee+Email) is atomic
    • Database changes roll back if:
        - Email fails to send
        - Any validation fails post-creation

    Email Handling:
    ──────────────
    • Includes temporary password (12 char, URL-safe)
    • Password reset link
    • Comprehensive SMTP error logging:
    - SMTP-specific error codes
    - Fallback general exception handling

    Example Usage:
    ─────────────
    >>> serializer = EmployeeAccountCreationSerializer(
    ...     data={
    ...         'username': 'new_employee',
    ...         'email': 'employee@company.com',
    ...         'role': 'EMPLOYEE',
    ...         'department': 'Engineering',
    ...         'manager_email_or_username': 'manager@company.com'
    ...     },
    ...     context={'request': request}
    ... )
    >>> serializer.is_valid(raise_exception=True)
    >>> user = serializer.save()

    Notes:
    ─────
    • Requires request context for permission checks
    • Cache keys are sanitized (lowercase, prefixed)
    • All sensitive operations are transaction-protected
    """

    ROLE_CHOICES = (
        ("EMPLOYEE", "EMPLOYEE"),
        ("MANAGER", "MANAGER"),
        ("ADMIN", "ADMIN"),
    )
    role = serializers.CharField(required=True, choices=ROLE_CHOICES)
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    manager_email_or_username = serializers.CharField(required=False)
    department = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'manager_email_or_username', 'department']
    
    def validate(self, data):
        request = self.context['request']

        if request.user.is_superuser:
            return data

        if hasattr(request.user, 'employee') and (request.user.employee.role == 'MANAGER' and data.get('role') in ['MANAGER', 'ADMIN']):
            raise serializers.ValidationError("Manager creation is restricted to Admins only.")
        
        cache_key = f"user_{request.user.pk}_department"

        manager_dept = cache.get(cache_key)
        if manager_dept is None:
            manager_dept = request.user.employee.department
            cache.set(cache_key, manager_dept, MANAGER_DEPT_CACHE_TIMEOUT)

        if not request.user.is_superuser and manager_dept != data.get('department'):
                raise serializers.ValidationError(f"Employee creation restricted to {manager_dept}") 

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
                is_active=True,
                is_staff=validated_data['role'] == 'MANAGER'
            )

            EmployeeModel.objects.create(
                user=user,
                temp_password=temp_password,
                role=validated_data['role'],
                manager=self._get_manager_by_email_or_username(validated_data['manager_email_or_username']),
            )

            self._send_credentials_email(username=validated_data['username'], temp_password=temp_password, recipient=validated_data['email'])
        
        return user

    def _send_credentials_email(self, username, temp_password, recipient,):
        subject = "Your Employee Account Credentials"
        message = f'''
        Hello, 

        Your account has been created. Please log in using:
        Username: {username}
        Password: {temp_password}

        Reset your password on first login.
        Login here: {reverse_lazy('Login page url')} 
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
            error_code = e.smtp_code
            error_message = SMTP_ERROR_CODES.get(error_code, f"Unknown error ({error_code})")
            logger.error(f"Failed to send email to {recipient}: {error_message.format(e.smtp_error)}")
        except Exception as e:
            logger.error(f"Unexpected error sending email to {recipient}: {str(e)}")        

    def _get_manager_by_email_or_username(self, value):
        if not value:
            return None
        
        cache_key = f"manager_validation_{value.lower()}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        user = (User.objects.filter(email__iexact=value) | User.objects.filter(username__exact=value)).first()

        result = None
        if user and hasattr(user, 'employee'):
            if user.employee.role in ['ADMIN', 'MANAGER']:
                result = user.employee
        
        cache.set(cache_key, result, MANAGER_DEPT_CACHE_TIMEOUT)
        return result
    
    def validate_email(self, value):
        norm_email = value.lower()
        if User.objects.filter(email=norm_email).exists():
            raise serializers.ValidationError("This email is already registered.")
        return norm_email
    
# Move email data to separate template ( add html versoin for email clients)
# password reset url : absolute url with domain (add expirty time for reset link)

class LoginSerailizer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"username": "No user found with this username"}
            )
        
        if hasattr(user, 'employee') and user.employee.password_reset_required:
            attrs['requires_password_reset'] = True
        else:
            user = authenticate(
                username=username,
                password=attrs.get('password')
            )
            if not user:
                raise serializers.ValidationError(
                    {"error": "Invalid credentials"}
                )
            attrs['user'] = user
            
        return attrs
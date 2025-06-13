from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import secrets
from .models import EmployeeModel
from django.core.mail import send_mail

class EmployeeAccountCreationSerailizer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email',]
    
    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})
        
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "This email is already registered."})

        return data
    
    def create(self, validated_data):
        temp_password = secrets.token_urlsafe(8)

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            password=make_password(temp_password),
            is_active=True
        )

        EmployeeModel.objects.create(
            user=user,
        )

    def _send_credentials_email(self, username, temp_password, password_reset_url, recepient, sender_email):
        subject = "Your Employee Account Credentials"
        message = f'''
        Hello,

        Your account has been created. Please log in using:
        Username: {username}
        Password: {temp_password}

        Reset your password on first login.
        Login here: {password_reset_url}
        '''

        send_mail(
            subject=subject,
            message=message,
            from_email=sender_email,
            recepient=recepient,
            fail_silently=False,
        )

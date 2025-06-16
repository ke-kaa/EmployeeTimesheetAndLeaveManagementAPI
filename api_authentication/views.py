from rest_framework.response import Response
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from rest_framework import serializers


from . import serializers as my_serializers
from .permissions import IsManager
from . import models as my_models
User = get_user_model()

# The following views with their respective serializers can be added to expand the project:
#   LogoutView
#   PasswordResetView
#   EmployeeList/Detail 
#   Employee Activation/Deactivation

class EmployeeCreationView(generics.CreateAPIView):
    serializer_class = my_serializers.EmployeeAccountCreationSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser | IsManager]
    authentication_classes = [JWTAuthentication]


class LoginView(TokenObtainPairView):
    serializer_class = my_serializers.CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            if e.get_codes().get('non_field_errors') == ['password_reset_required']:
                redirect_url = e.detail.get('redirect')

                if redirect_url:
                    return Response({
                        "detail": "Password reset required.",
                        "redirect": redirect_url
                    }, status=status.HTTP_403_FORBIDDEN)
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        
        return super().post(request, *args, **kwargs)
    

class InitialPasswordResetView(APIView):
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        serializer = my_serializers.InitialPasswordResetSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        new_password = serializer.validated_data['password']

        user.set_password(new_password) 
        user.save()

        if hasattr(user, 'employee'):
            user.employee.password_reset_required = False  
            user.employee.save()  
        
        return Response(
            {"detail": "Password successfully reset",
            "next": "/employee/me/"},
            status=status.HTTP_200_OK
        )
    

class EmployeeProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = my_serializers.EmployeeProfileSerializer
    
    def get_object(self):
        return my_models.EmployeeModel.objects.get(user=self.request.user)
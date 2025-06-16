from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views as my_views

urlpatterns = [
    path('/token/', my_views.LoginView.as_view(), name='token-obtain-pair'),
    path('/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('/create/account/', my_views.EmployeeCreationView.as_view(), name='account-create'),
    path('/reset-initial-password/',my_views.InitialPasswordResetView.as_view(), name='password-reset'),
    path('/employee/me/', my_views.EmployeeProfileRetrieveUpdateView.as_view(), name='employee-self-profile')
]
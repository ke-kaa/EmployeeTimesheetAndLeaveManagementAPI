from django.urls import path

from . import views as my_views


urlpatterns = [
    path('api/timesheet/clock-in/', my_views.ClockInView.as_view(), name='clock-in'),
    path('api/timesheet/clock-out/', my_views.ClockOutView.as_view(), name='clock-out'),
    path('api/timesheet/me/', my_views.EmployeeTimesheetView.as_view(), name='my-timesheet'),
    path('api/timesheet/team/', my_views.TeamEmployeeTimesheetView.as_view(), name='team-timesheet'),
]
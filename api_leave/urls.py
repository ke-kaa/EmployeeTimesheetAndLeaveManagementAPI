from django.urls import path


from . import views as my_views


urlpatterns = [
    path('/api/leave-request/', my_views.EmployeeLeaveRequestCreateView.as_view(), name='create-leave-request'),
    path('/api/leave-request/me/', my_views.EmployeeLeaveRequestListView.as_view(), name='list-leave-request'),
    path('/api/leave-request/team/', my_views.TeamLeaveRequestView.as_view(), name='team-leave-request'),
    path('/api/leave-request/<id>/approve/', my_views.ApproveEmployeeLeaveRequestView.as_view(), name='approve-leave-request'),
    path('/api/leave-request/<id>/reject/', my_views.RejectEmployeeLeaveRequestView.as_view(), name='reject-leave-request')
]
from rest_framework.pagination import PageNumberPagination

class LeaveRequestPagination(PageNumberPagination):
    page_size = 15
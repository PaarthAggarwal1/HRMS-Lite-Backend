from django.urls import path
from . import views

urlpatterns = [
    path('csrf-token/', views.csrf_token, name='csrf_token'),
    
    path("employees/", views.employees_view, name="employees"),

    path("attendance/", views.attendance_view, name="attendance"),
]

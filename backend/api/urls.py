from django.urls import path
from . import views

urlpatterns = [    
    path("employees/", views.employees_view, name="employees"),

    path("attendance/", views.attendance_view, name="attendance"),
]

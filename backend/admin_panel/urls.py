from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('create-admin/', views.create_admin_user, name='create_admin'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('students/', views.student_applications, name='student_applications'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/<int:student_id>/update-status/', views.update_student_status, name='update_student_status'),
]


from django.urls import path
from . import views
from . import tests

app_name = 'students'

urlpatterns = [
    path('register/', views.student_registration, name='registration'),
    path('registration-success/<int:student_id>/', views.registration_success, name='registration_success'),
    path('check-status/', views.check_registration_status, name='check_status'),
    path('toggle-batch-schedule/', views.toggle_batch_schedule, name='toggle_batch_schedule'),

    path('test-email/', tests.test_email_config, name='test_email_config'),
    path('debug-email/', tests.debug_email_config, name='debug_email'),  # Add this
]


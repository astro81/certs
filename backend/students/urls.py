from django.urls import path
from .views import StudentCreateView
from django.views.generic import TemplateView

urlpatterns = [
    path('', StudentCreateView.as_view(), name='student_register'),
    path('success/', TemplateView.as_view(template_name="students/success.html"), name='student_success'),
]

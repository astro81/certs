# certificates/urls.py
from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('', views.certificate_list, name='certificate_list'),
    path('<int:certificate_id>/', views.certificate_detail, name='certificate_detail'),
    path('<int:certificate_id>/download/', views.download_certificate, name='download_certificate'),
    path('verify/<str:certificate_number>/', views.view_certificate_public, name='view_certificate_public'),

    path('preview/<str:verification_code>/', views.certificate_preview, name='certificate_preview'),
    path('download/<str:verification_code>/', views.download_certificate, name='download_certificate'),

]


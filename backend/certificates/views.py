# certificates/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from students.models import Student
from .models import Certificate
from .services import CertificateService


@login_required
def certificate_list(request):
    """View all certificates (admin only)"""
    certificates = Certificate.objects.all().select_related('student')
    return render(request, 'certificates/certificate_list.html', {
        'certificates': certificates
    })


@login_required
def certificate_detail(request, certificate_id):
    """View certificate details"""
    certificate = get_object_or_404(Certificate, id=certificate_id)
    return render(request, 'certificates/certificate_detail.html', {
        'certificate': certificate
    })


@login_required
def download_certificate(request, certificate_id):
    """Download certificate PDF"""
    certificate = get_object_or_404(Certificate, id=certificate_id)

    if certificate.certificate_file:
        response = HttpResponse(certificate.certificate_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{certificate.certificate_file.name}"'
        return response
    else:
        # Regenerate if file doesn't exist
        CertificateService.regenerate_certificate(certificate)
        response = HttpResponse(certificate.certificate_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{certificate.certificate_file.name}"'
        return response


def view_certificate_public(request, certificate_number):
    """Public view for certificate verification"""
    certificate = get_object_or_404(Certificate, certificate_number=certificate_number)
    return render(request, 'certificates/certificate_public.html', {
        'certificate': certificate
    })


# certificates/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from students.models import Student
from .models import Certificate
from .services import CertificateService
import base64


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


def view_certificate_public(request, certificate_number):
    """Public view for certificate verification"""
    certificate = get_object_or_404(Certificate, certificate_number=certificate_number)
    return render(request, 'certificates/certificate_public.html', {
        'certificate': certificate
    })


def certificate_preview(request, verification_code):
    """View for certificate preview and download"""
    certificate = get_object_or_404(Certificate, verification_code=verification_code)

    # Generate QR code as base64 for embedding in HTML
    qr_buffer = certificate.generate_qr_code()
    qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()

    context = {
        'certificate': certificate,
        'student': certificate.student,
        'qr_code_base64': qr_base64,
    }

    return render(request, 'certificates/preview.html', context)


def download_certificate(request, verification_code):
    """View for downloading certificate"""
    certificate = get_object_or_404(Certificate, verification_code=verification_code)

    if certificate.certificate_file:
        response = HttpResponse(certificate.certificate_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="certificate_{certificate.certificate_number}.pdf"'
        return response
    else:
        return HttpResponse("Certificate file not found", status=404)

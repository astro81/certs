# certificates/models.py
from django.db import models
from students.models import Student
import os
from django.core.validators import FileExtensionValidator
from django.utils import timezone
import random
import string
import qrcode
from io import BytesIO
from django.core.files import File
import secrets
from django.urls import reverse
from django.conf import settings


def certificate_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"certificate.{ext}"
    return os.path.join('certificates', instance.student.full_name.replace(' ', '_'), filename)


class Certificate(models.Model):
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='certificate'
    )
    certificate_number = models.CharField(max_length=50, unique=True)
    issued_date = models.DateField(default=timezone.now)
    certificate_file = models.FileField(
        upload_to=certificate_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    verification_code = models.CharField(
        max_length=32,
        unique=True,
        blank=True,
        help_text="Unique code for certificate verification"
    )


    class Meta:
        ordering = ['-issued_date']
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'

    def __str__(self):
        return f"Certificate {self.certificate_number} - {self.student.full_name}"

    def generate_certificate_number(self):
        """Generate a unique certificate number"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"CERT-{timestamp}-{random_chars}"

    def generate_verification_code(self):
        """Generate a unique verification code"""
        return secrets.token_urlsafe(24)

    def get_certificate_url(self):
        """Generate the certificate preview URL"""
        if not hasattr(settings, 'SITE_URL'):
            # Fallback if SITE_URL is not set
            site_url = 'http://localhost:8000'  # Adjust to domain
        else:
            site_url = settings.SITE_URL

        return f"{site_url}{reverse('certificates:certificate_preview', kwargs={'verification_code': self.verification_code})}"

    def generate_qr_code(self):
        """Generate QR code for the certificate"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.get_certificate_url())
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer


    def save(self, *args, **kwargs):
        # Generate certificate number if it doesn't exist
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()

        # Set issued_date if it doesn't exist
        if not self.issued_date:
            self.issued_date = timezone.now().date()

        # Generate verification code if it doesn't exist
        if not self.verification_code:
            self.verification_code = self.generate_verification_code()


        super().save(*args, **kwargs)


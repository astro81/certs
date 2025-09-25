# certificates/models.py
from django.db import models
from students.models import Student
import os
from django.core.validators import FileExtensionValidator
from django.utils import timezone
import random
import string


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
    issued_date = models.DateField(default=timezone.now)  # Fix: use default instead of auto_now_add
    certificate_file = models.FileField(
        upload_to=certificate_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    def save(self, *args, **kwargs):
        # Generate certificate number if it doesn't exist
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()

        # Set issued_date if it doesn't exist
        if not self.issued_date:
            self.issued_date = timezone.now().date()

        super().save(*args, **kwargs)


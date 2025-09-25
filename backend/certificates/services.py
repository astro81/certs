# certificates/services.py
from .models import Certificate
from .utils import generate_certificate_pdf
from django.core.files.base import ContentFile
import os


class CertificateService:
    @staticmethod
    def create_certificate_for_student(student):
        """Create and generate certificate for a student"""

        # Check if certificate already exists
        if hasattr(student, 'certificate'):
            return student.certificate

        # Create and save certificate first to generate certificate number and issued_date
        certificate = Certificate(student=student)
        certificate.save()  # This will generate certificate number and set issued_date

        try:
            # Generate PDF content
            pdf_content = generate_certificate_pdf(certificate)

            # Save PDF to certificate file field
            filename = f"certificate_{certificate.certificate_number}.pdf"
            certificate.certificate_file.save(filename, ContentFile(pdf_content))

            # Save again to update the file field
            certificate.save()
            return certificate

        except Exception as e:
            # If PDF generation fails, delete the certificate and re-raise the exception
            certificate.delete()
            raise e

    @staticmethod
    def regenerate_certificate(certificate):
        """Regenerate certificate PDF"""
        pdf_content = generate_certificate_pdf(certificate)

        # Delete old file if exists
        if certificate.certificate_file:
            if os.path.isfile(certificate.certificate_file.path):
                os.remove(certificate.certificate_file.path)

        # Save new PDF
        filename = f"certificate_{certificate.certificate_number}.pdf"
        certificate.certificate_file.save(filename, ContentFile(pdf_content))
        certificate.save()

        return certificate


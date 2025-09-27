from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
import os

from .email_messages import (
    format_registration_message,
    format_status_update_message,
    REGISTRATION_EMAIL_SUBJECT,
    get_status_update_subject
)


def send_registration_email(student):
    """Send email notification when student registers successfully"""

    # HTML message
    html_message = render_to_string('students/emails/registration_received.html', {
        'student': student,
    })

    try:
        send_mail(
            subject=REGISTRATION_EMAIL_SUBJECT,
            message=format_registration_message(student),
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email_address],
            fail_silently=False,
        )
        print(f"Registration email sent to: {student.email_address}")
        return True
    except Exception as e:
        print(f"Error sending registration email to {student.email_address}: {e}")
        return False


def send_status_update_email(student, old_status, new_status):
    """Send email notification when application status changes"""

    # HTML message
    html_message = render_to_string('students/emails/status_updated.html', {
        'student': student,
        'old_status': old_status,
        'new_status': new_status,
    })

    try:
        email = EmailMessage(
            subject=get_status_update_subject(student.get_approve_status_display()),
            body=format_status_update_message(student, old_status, new_status),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[student.email_address],
        )

        # Set HTML content
        email.content_subtype = "html"
        email.body = html_message

        # Attach certificate PDF if status is accepted and certificate exists
        if new_status == 'accepted' and hasattr(student, 'certificate'):
            certificate = student.certificate

            # Attach certificate file
            if certificate.certificate_file and os.path.exists(certificate.certificate_file.path):
                email.attach_file(certificate.certificate_file.path)

            # Generate and attach QR code
            qr_buffer = certificate.generate_qr_code()
            email.attach(
                f'certificate_qr_{certificate.certificate_number}.png',
                qr_buffer.getvalue(),
                'image/png'
            )

        # Send email
        email.send(fail_silently=False)

        print(f"Status update email sent to: {student.email_address}")
        return True
    except Exception as e:
        print(f"Error sending status update email to {student.email_address}: {e}")
        return False


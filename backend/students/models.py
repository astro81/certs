from django.db import models
from django.core.validators import FileExtensionValidator
import os
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def student_photo_upload_path(instance, filename):
    # This will create a path like: student_photos/full_name/filename
    ext = filename.split('.')[-1]
    filename = f"photo.{ext}"
    return os.path.join('student_photos', instance.full_name.replace(' ', '_'), filename)


class Student(models.Model):
    APPROVAL_STATUS = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    MODE_OF_LEARNING = [
        ('physical', 'Physical'),
        ('online', 'Online'),
    ]

    COURSE_CHOICES = [
        ('web_development', 'Web Development'),
        ('data_science', 'Data Science'),
        ('digital_marketing', 'Digital Marketing'),
        ('graphic_design', 'Graphic Design'),
        ('mobile_app_development', 'Mobile App Development'),
        ('python_programming', 'Python Programming'),
        ('java_programming', 'Java Programming'),
        ('cyber_security', 'Cyber Security'),
    ]

    # Required Fields
    full_name = models.CharField(max_length=100)
    fathers_name = models.CharField(max_length=100)
    address = models.TextField()
    enrolled_date = models.DateField()
    course_name = models.CharField(max_length=50, choices=COURSE_CHOICES)
    course_duration = models.CharField(max_length=50, help_text="e.g., 3 months, 6 months, etc.")
    mode_of_learning = models.CharField(max_length=10, choices=MODE_OF_LEARNING)
    instructor_name = models.CharField(max_length=100)
    student_photo = models.ImageField(
        upload_to=student_photo_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Upload a JPG or PNG image"
    )
    email_address = models.EmailField()

    # Conditional Field
    batch_schedule = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Only required for physical mode (e.g., Mon-Wed-Fri 10:00 AM)"
    )

    # Admin-only Field
    approve_status = models.CharField(
        max_length=10,
        choices=APPROVAL_STATUS,
        default='pending'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        return f"{self.full_name} - {self.get_course_name_display()} - {self.approve_status}"

    def get_status_badge(self):
        status_colors = {
            'pending': 'warning',
            'accepted': 'success',
            'rejected': 'danger'
        }
        return f'<span class="badge bg-{status_colors[self.approve_status]}">{self.get_approve_status_display()}</span>'


    def send_registration_email(self):
        """Send email notification when student registers successfully"""
        subject = 'Registration Received - Student Portal'

        # HTML message
        html_message = render_to_string('students/emails/registration_received.html', {
            'student': self,
        })

        # Proper plain text message (manually created, not using strip_tags)
        plain_message = f"""
    Dear {self.full_name},

    Thank you for submitting your application to the Student Portal. We have successfully received your registration for the following course:

    APPLICATION DETAILS:
    - Course: {self.get_course_name_display()}
    - Duration: {self.course_duration}
    - Mode of Learning: {self.get_mode_of_learning_display()}
    - Enrollment Date: {self.enrolled_date}
    - Reference ID: STU{self.id:06d}
    - Current Status: Pending Review

    WHAT HAPPENS NEXT?
    - Our administration team will review your application
    - You will receive another email once your application is processed
    - The review process typically takes 1-3 business days

    You can check your application status at any time by visiting our website and using your email address.

    Need help? If you have any questions, please don't hesitate to contact our support team.

    This is an automated message. Please do not reply to this email.

    © 2024 Student Portal. All rights reserved.
    """

        try:
            send_mail(
                subject=subject,
                message=plain_message.strip(),
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.email_address],
                fail_silently=False,
            )
            print(f"Registration email sent to: {self.email_address}")
            return True
        except Exception as e:
            print(f"Error sending registration email to {self.email_address}: {e}")
            return False

    def send_status_update_email(self, old_status, new_status):
        """Send email notification when application status changes"""
        subject = f'Application Status Update - {self.get_approve_status_display()}'

        # HTML message
        html_message = render_to_string('students/emails/status_updated.html', {
            'student': self,
            'old_status': old_status,
            'new_status': new_status,
        })

        # Proper plain text message
        plain_message = f"""
    Dear {self.full_name},

    Your application for {self.get_course_name_display()} has been reviewed by our administration team.

    APPLICATION DECISION:
    - Status: {self.get_approve_status_display().upper()}
    - Course: {self.get_course_name_display()}
    - Reference ID: STU{self.id:06d}
    - Review Date: {self.updated_at.strftime('%B %d, %Y')}
    """

        if self.approve_status == 'accepted':
            plain_message += """
    🎉 CONGRATULATIONS! Your application has been accepted!

    NEXT STEPS:
    - You will receive a welcome package within 2 business days
    - Course orientation will be scheduled for the coming week
    - Check your email for further instructions regarding course materials
    - Prepare for your first class as per the schedule provided

    We're excited to have you join our learning community!
    """
        elif self.approve_status == 'rejected':
            plain_message += """
    APPLICATION REVIEW NOTE:

    We regret to inform you that your application could not be approved at this time. 
    This decision may be due to course capacity limitations, prerequisite requirements, or schedule conflicts.

    Contact our admissions office to discuss alternative options or future opportunities.
    """
        else:
            plain_message += """
    Your application is currently being processed. We appreciate your patience during this time.
    You will receive another notification once the review is complete.
    """

        plain_message += f"""

    IMPORTANT NOTES:
    - This decision is based on your submitted application materials
    - All decisions are final but may be appealed by contacting admissions
    - Keep your reference ID for all future communications

    This is an automated message. Please do not reply to this email.

    © 2024 Student Portal. All rights reserved.
    """

        try:
            send_mail(
                subject=subject,
                message=plain_message.strip(),
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.email_address],
                fail_silently=False,
            )
            print(f"Status update email sent to: {self.email_address}")
            return True
        except Exception as e:
            print(f"Error sending status update email to {self.email_address}: {e}")
            return False





    def save(self, *args, **kwargs):
        # Check if this is a new student (registration)
        is_new = self._state.adding

        # Get old status if updating
        if not is_new:
            try:
                old_student = Student.objects.get(pk=self.pk)
                old_status = old_student.approve_status
            except Student.DoesNotExist:
                old_status = 'pending'
        else:
            old_status = 'pending'

        # Clear batch_schedule if mode is online
        if self.mode_of_learning == 'online':
            self.batch_schedule = None

        # Save the student
        super().save(*args, **kwargs)

        # Send emails based on the operation
        if is_new:
            # New registration - send welcome/confirmation email
            self.send_registration_email()
        else:
            # Status changed - send notification
            if old_status != self.approve_status:
                self.send_status_update_email(old_status, self.approve_status)


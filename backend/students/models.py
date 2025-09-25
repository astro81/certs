from django.db import models
from django.core.validators import FileExtensionValidator
import os
from .emails import send_registration_email, send_status_update_email

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
            send_registration_email(self)
        else:
            # Status changed - send notification
            if old_status != self.approve_status:
                send_status_update_email(self, old_status, self.approve_status)

                # Generate certificate when status changes to accepted
                if self.approve_status == 'accepted' and old_status != 'accepted':
                    from certificates.services import CertificateService
                    CertificateService.create_certificate_for_student(self)



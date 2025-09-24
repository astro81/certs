from django.db import models


class Student(models.Model):
    MODE_CHOICES = [
        ('Physical', 'Physical'),
        ('Online', 'Online'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    full_name = models.CharField(max_length=255)
    fathers_name = models.CharField(max_length=255)
    address = models.TextField()
    enrolled_date = models.DateField()
    course_name = models.CharField(max_length=255)
    course_duration = models.CharField(max_length=255)
    mode_of_learning = models.CharField(max_length=10, choices=MODE_CHOICES)
    batch_schedule = models.CharField(max_length=255, blank=True, null=True)
    instructor_name = models.CharField(max_length=255)
    student_photo = models.ImageField(upload_to='student_photos/')
    email_address = models.EmailField()
    approval_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return self.full_name

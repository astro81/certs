from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email_address', 'course_name', 'mode_of_learning', 'approve_status', 'created_at']
    list_filter = ['approve_status', 'course_name', 'mode_of_learning', 'created_at']
    search_fields = ['full_name', 'email_address', 'fathers_name']
    list_editable = ['approve_status']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'fathers_name', 'address', 'email_address', 'student_photo')
        }),
        ('Course Information', {
            'fields': ('enrolled_date', 'course_name', 'course_duration', 'mode_of_learning', 'batch_schedule')
        }),
        ('Administrative', {
            'fields': ('approve_status', 'instructor_name', 'created_at', 'updated_at')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('enrolled_date', 'course_name')
        return self.readonly_fields
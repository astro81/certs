from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        # Exclude approval_status from the form
        exclude = ['approval_status']

        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'fathers_name': forms.TextInput(attrs={'placeholder': 'Father’s Name'}),
            'address': forms.Textarea(attrs={'placeholder': 'Address', 'rows': 3}),
            'enrolled_date': forms.DateInput(attrs={'type': 'date'}),
            'course_name': forms.TextInput(attrs={'placeholder': 'Course Name'}),
            'course_duration': forms.TextInput(attrs={'placeholder': 'Course Duration'}),
            'mode_of_learning': forms.RadioSelect(),
            'batch_schedule': forms.TextInput(attrs={'placeholder': 'Batch Schedule'}),
            'instructor_name': forms.TextInput(attrs={'placeholder': 'Instructor Name'}),
            'student_photo': forms.ClearableFileInput(),
            'email_address': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        mode = cleaned_data.get("mode_of_learning")
        batch = cleaned_data.get("batch_schedule")
        if mode == "Physical" and not batch:
            self.add_error("batch_schedule", "Batch Schedule is required for Physical mode.")
        return cleaned_data


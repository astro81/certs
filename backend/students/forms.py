from django import forms
from .models import Student
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Field


class StudentForm(forms.ModelForm):
    enrolled_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Select the enrollment date"
    )

    class Meta:
        model = Student
        fields = [
            'full_name', 'fathers_name', 'address', 'enrolled_date',
            'course_name', 'course_duration', 'mode_of_learning',
            'batch_schedule', 'instructor_name', 'student_photo',
            'email_address'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('full_name', css_class='form-group col-md-6'),
                Column('fathers_name', css_class='form-group col-md-6'),
            ),
            'address',
            Row(
                Column('enrolled_date', css_class='form-group col-md-6'),
                Column('email_address', css_class='form-group col-md-6'),
            ),
            Row(
                Column('course_name', css_class='form-group col-md-6'),
                Column('course_duration', css_class='form-group col-md-6'),
            ),
            'mode_of_learning',
            Div(
                'batch_schedule',
                css_id='batch-schedule-field',
                css_class='form-group'
            ),
            'instructor_name',
            'student_photo',
        )

    def clean(self):
        cleaned_data = super().clean()
        mode_of_learning = cleaned_data.get('mode_of_learning')
        batch_schedule = cleaned_data.get('batch_schedule')

        # Validate batch_schedule for physical mode
        if mode_of_learning == 'physical' and not batch_schedule:
            raise forms.ValidationError({
                'batch_schedule': 'Batch schedule is required for physical mode of learning.'
            })

        # Ensure batch_schedule is empty for online mode
        if mode_of_learning == 'online' and batch_schedule:
            self.cleaned_data['batch_schedule'] = None

        return cleaned_data


class StudentApprovalForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['approve_status']
        widgets = {
            'approve_status': forms.RadioSelect(choices=Student.APPROVAL_STATUS),
        }


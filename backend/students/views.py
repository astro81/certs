from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import Student
from .forms import StudentForm

class StudentCreateView(CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_success')

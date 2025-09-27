from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Student
from .forms import StudentForm, StudentApprovalForm


def student_registration(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()  # The email will be sent automatically via the model's save method

            messages.success(request,
                             'Your registration has been submitted successfully! We will review your application and contact you soon.')
            return redirect('students:registration_success', student_id=student.id)
    else:
        form = StudentForm()

    return render(request, 'students/registration.html', {'form': form})


def registration_success(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'students/registration_success.html', {'student': student})


def check_registration_status(request):
    if request.method == 'POST':
        # email = request.POST.get('email')
        reference_id = request.POST.get('reference_id')
        try:
            # Remove any non-numeric characters and convert to integer
            clean_reference_id = ''.join(filter(str.isdigit, reference_id))
            if clean_reference_id:
                student_id = int(clean_reference_id)
                student = Student.objects.get(id=student_id)
                return render(request, 'students/status_result.html', {'student': student})
            else:
                messages.error(request, 'Please enter a valid reference ID.')
        except Student.DoesNotExist:
            messages.error(request, 'No registration found with this reference ID. Please check your email and try again.')

    return render(request, 'students/check_status.html')


# AJAX view to handle batch schedule field visibility
@csrf_exempt
def toggle_batch_schedule(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        mode = request.POST.get('mode_of_learning')
        is_physical = (mode == 'physical')
        return JsonResponse({'show_batch_schedule': is_physical})
    return JsonResponse({'error': 'Invalid request'}, status=400)


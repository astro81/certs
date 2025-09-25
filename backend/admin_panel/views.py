from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from students.forms import StudentApprovalForm
from students.models import Student
from .forms import AdminUserCreationForm, EmailAuthenticationForm
from django.contrib.auth import get_user_model
from django.http import JsonResponse

User = get_user_model()


def create_admin_user(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Admin user {user.username} created successfully!')
            return redirect('admin_panel:login')
    else:
        form = AdminUserCreationForm()

    return render(request, 'admin_panel/create_admin.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_panel:dashboard')

    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('admin_panel:dashboard')
            else:
                messages.error(request, 'Invalid credentials or not an admin user.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmailAuthenticationForm()

    return render(request, 'admin_panel/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('admin_panel:login')


@login_required
def dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('admin_panel:login')

    total_users = User.objects.count()
    admin_users = User.objects.filter(is_staff=True).count()
    total_students = Student.objects.count()
    pending_students = Student.objects.filter(approve_status='pending').count()
    accepted_students = Student.objects.filter(approve_status='accepted').count()
    rejected_students = Student.objects.filter(approve_status='rejected').count()

    context = {
        'total_users': total_users,
        'admin_users': admin_users,
        'total_students': total_students,
        'pending_students': pending_students,
        'accepted_students': accepted_students,
        'rejected_students': rejected_students,
    }

    return render(request, 'admin_panel/dashboard.html', context)


@login_required
def student_applications(request):
    if not request.user.is_staff:
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('admin_panel:login')

    status_filter = request.GET.get('status', 'all')

    if status_filter == 'pending':
        students = Student.objects.filter(approve_status='pending')
    elif status_filter == 'accepted':
        students = Student.objects.filter(approve_status='accepted')
    elif status_filter == 'rejected':
        students = Student.objects.filter(approve_status='rejected')
    else:
        students = Student.objects.all()

    context = {
        'students': students,
        'status_filter': status_filter,
        'total_count': Student.objects.count(),
        'pending_count': Student.objects.filter(approve_status='pending').count(),
        'accepted_count': Student.objects.filter(approve_status='accepted').count(),
        'rejected_count': Student.objects.filter(approve_status='rejected').count(),
    }

    return render(request, 'admin_panel/student_applications.html', context)


@login_required
def student_detail(request, student_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        form = StudentApprovalForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Status updated successfully!',
                'new_status': student.get_approve_status_display(),
                'status_class': student.approve_status
            })

    form = StudentApprovalForm(instance=student)

    context = {
        'student': student,
        'form': form,
    }

    return render(request, 'admin_panel/student_detail.html', context)


@login_required
def update_student_status(request, student_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        student = get_object_or_404(Student, id=student_id)
        new_status = request.POST.get('approve_status')

        if new_status in dict(Student.APPROVAL_STATUS):
            # The email will be sent automatically via the model's save method
            student.approve_status = new_status
            student.save()  # This will trigger the status update email

            return JsonResponse({
                'success': True,
                'message': 'Status updated successfully! Email notification sent to student.',
                'new_status': student.get_approve_status_display(),
                'status_class': student.approve_status
            })
        else:
            return JsonResponse({'success': False, 'error': 'Invalid status'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


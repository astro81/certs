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


# def student_registration(request):
#     if request.method == 'POST':
#         form = StudentForm(request.POST, request.FILES)
#         if form.is_valid():
#             student = form.save(commit=False)
#             student.save()
#
#             # Send confirmation email (optional)
#             try:
#                 send_mail(
#                     'Student Registration Received',
#                     f'Dear {student.full_name},\n\nYour registration for {student.get_course_name_display()} has been received and is under review.\n\nWe will notify you once your application is processed.\n\nThank you!',
#                     settings.DEFAULT_FROM_EMAIL,
#                     [student.email_address],
#                     fail_silently=True,
#                 )
#             except Exception as e:
#                 # Email failure shouldn't break the registration
#                 pass
#
#             messages.success(request,
#                              'Your registration has been submitted successfully! We will review your application and contact you soon.')
#             return redirect('students:registration_success', student_id=student.id)
#     else:
#         form = StudentForm()
#
#     return render(request, 'students/registration.html', {'form': form})


def registration_success(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'students/registration_success.html', {'student': student})


def check_registration_status(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            student = Student.objects.get(email_address=email)
            return render(request, 'students/status_result.html', {'student': student})
        except Student.DoesNotExist:
            messages.error(request, 'No registration found with this email address.')

    return render(request, 'students/check_status.html')


# AJAX view to handle batch schedule field visibility
@csrf_exempt
def toggle_batch_schedule(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        mode = request.POST.get('mode_of_learning')
        is_physical = (mode == 'physical')
        return JsonResponse({'show_batch_schedule': is_physical})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def test_email_config(request):
    """Test email configuration"""
    from django.core.mail import send_mail
    from django.http import HttpResponse
    from django.conf import settings

    # Only allow in development
    if not settings.DEBUG:
        return HttpResponse("Not available in production")

    test_email = "caien873@gmail.com"  # Change to a real email address for testing

    try:
        send_mail(
            subject='Test Email from Student Portal',
            message='This is a test email to verify your email configuration is working correctly.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        return HttpResponse(f"Test email sent successfully to {test_email}! Check your inbox.")
    except Exception as e:
        return HttpResponse(f"Error sending email: {str(e)}")


def debug_email_config(request):
    """Detailed email configuration debug view"""
    from django.http import HttpResponse
    from django.conf import settings
    import smtplib
    import logging

    logger = logging.getLogger(__name__)

    debug_info = []
    debug_info.append("=== EMAIL CONFIGURATION DEBUG ===")

    # Check current settings
    debug_info.append(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Not set')}")
    debug_info.append(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    debug_info.append(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    debug_info.append(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
    debug_info.append(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    debug_info.append(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")
    debug_info.append(
        f"EMAIL_HOST_PASSWORD: {'*' * len(getattr(settings, 'EMAIL_HOST_PASSWORD', ''))} ({len(getattr(settings, 'EMAIL_HOST_PASSWORD', ''))} chars)")

    # Test SMTP connection
    try:
        debug_info.append("\n=== TESTING SMTP CONNECTION ===")
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
        server.ehlo()
        if settings.EMAIL_USE_TLS:
            server.starttls()
            debug_info.append("TLS started successfully")
        server.ehlo()

        # Try to login
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        debug_info.append("SMTP Login successful!")

        # Test email sending
        test_message = f"""Subject: Debug Test Email
From: {settings.DEFAULT_FROM_EMAIL}
To: {settings.EMAIL_HOST_USER}

This is a debug test email."""

        server.sendmail(settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER], test_message)
        debug_info.append("Test email sent via raw SMTP!")

        server.quit()

    except smtplib.SMTPAuthenticationError as e:
        debug_info.append(f"SMTP AUTHENTICATION ERROR: {e}")
        debug_info.append("Check your App Password and 2FA settings")

    except Exception as e:
        debug_info.append(f"SMTP ERROR: {e}")

    # Test Django's send_mail
    try:
        debug_info.append("\n=== TESTING DJANGO send_mail ===")
        from django.core.mail import send_mail

        result = send_mail(
            subject='Django Debug Test Email',
            message='This is a test from Django send_mail function.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        debug_info.append(f"Django send_mail result: {result}")

    except Exception as e:
        debug_info.append(f"DJANGO SEND_MAIL ERROR: {e}")

    debug_info.append("\n=== TROUBLESHOOTING TIPS ===")
    debug_info.append("1. Check that 2-Factor Authentication is ENABLED on your Gmail")
    debug_info.append("2. Verify you're using an App Password (16 chars), not your regular password")
    debug_info.append("3. Check your Gmail spam folder")
    debug_info.append("4. Make sure 'Less secure app access' is NOT enabled (use App Passwords instead)")
    debug_info.append("5. Try sending to a different email address")

    return HttpResponse('<pre>' + '\n'.join(debug_info) + '</pre>')
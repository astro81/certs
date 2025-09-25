from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
import smtplib


def test_email_config(request):
    """Test email configuration"""
    # Only allow in development
    if not settings.DEBUG:
        return HttpResponse("Not available in production")

    test_email = settings.TEST_MAIL  # Change to a real email address for testing

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


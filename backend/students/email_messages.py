"""
Email message templates for student notifications
"""

# Registration email template
REGISTRATION_EMAIL_PLAIN = """
Dear {full_name},

Thank you for submitting your application to the Student Portal. We have successfully received your registration for the following course:

APPLICATION DETAILS:
- Course: {course_name}
- Duration: {course_duration}
- Mode of Learning: {mode_of_learning}
- Enrollment Date: {enrolled_date}
- Reference ID: {reference_id}
- Current Status: Pending Review

WHAT HAPPENS NEXT?
- Our administration team will review your application
- You will receive another email once your application is processed
- The review process typically takes 1-3 business days

You can check your application status at any time by visiting our website and using your email address.

Need help? If you have any questions, please don't hesitate to contact our support team.

This is an automated message. Please do not reply to this email.

© 2024 Student Portal. All rights reserved.
"""

# Status update email templates
STATUS_UPDATE_BASE = """
Dear {full_name},

Your application for {course_name} has been reviewed by our administration team.

APPLICATION DECISION:
- Status: {status_display}
- Course: {course_name}
- Reference ID: {reference_id}
- Review Date: {review_date}
"""

STATUS_ACCEPTED_MESSAGE = """
🎉 CONGRATULATIONS! Your application has been accepted!

NEXT STEPS:
- You will receive a welcome package within 2 business days
- Course orientation will be scheduled for the coming week
- Check your email for further instructions regarding course materials
- Prepare for your first class as per the schedule provided

We're excited to have you join our learning community!
"""

STATUS_REJECTED_MESSAGE = """
APPLICATION REVIEW NOTE:

We regret to inform you that your application could not be approved at this time. 
This decision may be due to course capacity limitations, prerequisite requirements, or schedule conflicts.

Contact our admissions office to discuss alternative options or future opportunities.
"""

STATUS_OTHER_MESSAGE = """
Your application is currently being processed. We appreciate your patience during this time.
You will receive another notification once the review is complete.
"""

STATUS_UPDATE_FOOTER = """

IMPORTANT NOTES:
- This decision is based on your submitted application materials
- All decisions are final but may be appealed by contacting admissions
- Keep your reference ID for all future communications

This is an automated message. Please do not reply to this email.

© 2024 Student Portal. All rights reserved.
"""



# Email subjects
REGISTRATION_EMAIL_SUBJECT = 'Registration Received - Student Portal'


def get_status_update_subject(status_display):
    """Generate status update email subject"""
    return f'Application Status Update - {status_display}'


def format_registration_message(student):
    """Format registration email message"""
    return REGISTRATION_EMAIL_PLAIN.format(
        full_name=student.full_name,
        course_name=student.get_course_name_display(),
        course_duration=student.course_duration,
        mode_of_learning=student.get_mode_of_learning_display(),
        enrolled_date=student.enrolled_date,
        reference_id=f"STU{student.id:06d}"
    ).strip()


def format_status_update_message(student, old_status, new_status):
    """Format status update email message"""
    # Base message
    message = STATUS_UPDATE_BASE.format(
        full_name=student.full_name,
        course_name=student.get_course_name_display(),
        status_display=student.get_approve_status_display().upper(),
        reference_id=f"STU{student.id:06d}",
        review_date=student.updated_at.strftime('%B %d, %Y')
    )

    # Add status-specific message
    if student.approve_status == 'accepted':
        message += STATUS_ACCEPTED_MESSAGE
    elif student.approve_status == 'rejected':
        message += STATUS_REJECTED_MESSAGE
    else:
        message += STATUS_OTHER_MESSAGE

    # Add footer
    message += STATUS_UPDATE_FOOTER

    return message.strip()
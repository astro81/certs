# certificates/utils.py
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from django.utils import timezone
from datetime import datetime


def generate_certificate_pdf(certificate):
    """Generate PDF certificate for a student"""

    # Create buffer for PDF
    buffer = BytesIO()

    # Create PDF canvas in landscape mode
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Draw border
    c.setStrokeColor(colors.gold)
    c.setLineWidth(3)
    c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

    # Title
    c.setFont('Helvetica-Bold', 36)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 2 * inch, "CERTIFICATE OF COMPLETION")

    # Subtitle
    c.setFont('Helvetica', 18)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 3 * inch, "This certifies that")

    # Student name (prominent)
    c.setFont('Helvetica-Bold', 32)
    c.setFillColor(colors.darkred)
    c.drawCentredString(width / 2, height - 4.5 * inch, certificate.student.full_name.upper())

    # Completion text
    c.setFont('Helvetica', 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 6 * inch, "has successfully completed the course")

    # Course name
    c.setFont('Helvetica-Bold', 20)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 7 * inch, certificate.student.get_course_name_display())

    # Course details
    c.setFont('Helvetica', 14)
    c.setFillColor(colors.black)

    details_y = height - 8.5 * inch
    c.drawCentredString(width / 2, details_y, f"Course Duration: {certificate.student.course_duration}")
    c.drawCentredString(width / 2, details_y - 0.5 * inch,
                        f"Mode of Learning: {certificate.student.get_mode_of_learning_display()}")
    c.drawCentredString(width / 2, details_y - 1 * inch, f"Instructor: {certificate.student.instructor_name}")

    # Dates - FIX: Handle possible None values
    enrolled_date = certificate.student.enrolled_date.strftime(
        '%B %d, %Y') if certificate.student.enrolled_date else "N/A"
    issued_date = certificate.issued_date.strftime(
        '%B %d, %Y') if certificate.issued_date else timezone.now().date().strftime('%B %d, %Y')

    c.drawCentredString(width / 2, details_y - 2 * inch, f"Enrolled: {enrolled_date}")
    c.drawCentredString(width / 2, details_y - 2.5 * inch, f"Certificate Issued: {issued_date}")

    # Certificate number
    c.setFont('Helvetica-Oblique', 12)
    c.setFillColor(colors.gray)
    c.drawString(1 * inch, 1 * inch, f"Certificate Number: {certificate.certificate_number}")

    # Signatures area
    signature_y = 2 * inch
    c.setFont('Helvetica', 12)
    c.setFillColor(colors.black)

    # Instructor signature line
    c.line(1.5 * inch, signature_y, 3 * inch, signature_y)
    c.drawString(1.5 * inch, signature_y - 0.3 * inch, certificate.student.instructor_name)
    c.drawString(1.5 * inch, signature_y - 0.6 * inch, "Instructor")

    # Director signature line
    c.line(width - 3 * inch, signature_y, width - 1.5 * inch, signature_y)
    c.drawString(width - 3 * inch, signature_y - 0.3 * inch, "Director")
    c.drawString(width - 3 * inch, signature_y - 0.6 * inch, "Learning Institute")

    # Save the PDF
    c.showPage()
    c.save()

    # Get PDF content from buffer
    pdf_content = buffer.getvalue()
    buffer.close()

    return pdf_content


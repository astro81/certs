# certificates/utils.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, black, white, lightgrey
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Frame
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import Table, TableStyle
from django.utils import timezone
from django.conf import settings
from datetime import datetime
import os


def get_asset_path(filename):
    """Get absolute path to asset file"""
    assets_dir = os.path.join(settings.BASE_DIR, 'certificates', 'assets')
    return os.path.join(assets_dir, filename)


def draw_header(c, page_width, page_height):
    """Draw header image at the top of the page."""
    header_image_path = get_asset_path('header.jpeg')

    # Check if header image exists, if not, skip drawing
    if not os.path.exists(header_image_path):
        print(f"Header image not found at: {header_image_path}")
        return

    header_img_width, header_img_height = 600, 120
    x_top = (page_width - header_img_width) / 2
    y_top = page_height - header_img_height - 2  # 30px margin from top
    c.drawImage(header_image_path, x_top, y_top, header_img_width, header_img_height)


def draw_footer(c, page_width):
    """Draw footer image at the bottom of the page."""
    footer_image_path = get_asset_path('footer.jpeg')

    # Check if footer image exists, if not, skip drawing
    if not os.path.exists(footer_image_path):
        print(f"Footer image not found at: {footer_image_path}")
        return

    footer_img_width, footer_img_height = 600, 30
    x_bottom = (page_width - footer_img_width) / 2
    y_bottom = 2  # margin from bottom
    c.drawImage(footer_image_path, x_bottom, y_bottom, footer_img_width, footer_img_height)


def draw_top_sub_container(c, certificate, container_x, top_sub_y, container_width, top_sub_height):
    """Draws the top sub-container with date and student image."""

    # Draw rectangle
    c.setFillColor(white)
    c.rect(container_x, top_sub_y, container_width, top_sub_height, fill=0, stroke=0)

    # Date text at top-left
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(black)
    date_str = certificate.issued_date.strftime(
        "%d-%m-%Y") if certificate.issued_date else timezone.now().date().strftime("%d-%m-%Y")
    date_text = f"Date: {date_str}"
    text_x = container_x
    text_y = top_sub_y + top_sub_height - 10
    c.drawString(text_x, text_y, date_text)

    # Student image (right side)
    student = certificate.student
    default_image_path = get_asset_path('profile.jpg')

    # Try to get student photo path if it exists
    if student.student_photo and hasattr(student.student_photo, 'path') and os.path.exists(student.student_photo.path):
        top_image_path = student.student_photo.path
    else:
        top_image_path = default_image_path

    img_height = top_sub_height
    img_width = 120
    img_x = container_x + container_width - img_width + 30
    img_y = top_sub_y

    if os.path.exists(top_image_path):
        try:
            c.drawImage(top_image_path, img_x, img_y, img_width, img_height,
                        preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"Error drawing student image: {e}")
            # Draw placeholder text if image fails
            c.setFont("Helvetica", 10)
            c.drawString(img_x, img_y + img_height / 2, "Student Photo")
    else:
        print(f"Warning: Image not found at {top_image_path}")
        # Draw placeholder text
        c.setFont("Helvetica", 10)
        c.drawString(img_x, img_y + img_height / 2, "Student Photo")


def draw_title_container(c, container_x, container_y, container_width, top_y):
    """
    Draws the title container at the top of the mid sub-container.
    """
    title_text = "CERTIFICATE OF COMPLETION"
    title_font = "Helvetica-Bold"
    title_size = 18
    padding = 1

    # Set font and calculate text width
    c.setFont(title_font, title_size)
    text_width = c.stringWidth(title_text, title_font, title_size)

    # Center the text horizontally
    text_x = container_x + (container_width - text_width) / 2
    text_y = top_y - title_size - padding

    # Draw the text
    c.setFillColor(black)
    c.drawString(text_x, text_y, title_text)

    # Draw underline matching text width
    underline_y = text_y - 2
    c.setLineWidth(1.5)
    c.line(text_x, underline_y, text_x + text_width, underline_y)


def draw_paragraph_container(c, text, container_x, container_y, container_width, top_y):
    """Draws a justified paragraph container (for intro or message)."""
    try:
        style = ParagraphStyle(
            name="ParagraphStyle",
            fontName="Helvetica",
            fontSize=13,
            leading=16,
            alignment=TA_JUSTIFY,
        )

        paragraph = Paragraph(text, style)
        frame_height = top_y - container_y - 10
        frame = Frame(container_x - 5, container_y + 10, container_width + 10, frame_height, showBoundary=0)
        frame.addFromList([paragraph], c)
    except Exception as e:
        print(f"Error drawing paragraph: {e}")
        # Fallback: draw simple text
        c.setFont("Helvetica", 13)
        c.setFillColor(black)
        # Simple text drawing as fallback
        c.drawString(container_x, container_y + 50, text[:100] + "..." if len(text) > 100 else text)


def draw_body_container(c, certificate, container_x, container_y, container_width, top_y):
    """Draws the course details table."""
    student = certificate.student

    data = [
        ["Course Title", ":", student.get_course_name_display()],
        ["Duration", ":", student.course_duration],
        ["Total Hours", ":", "5 Hours per day"],  # Default value
        ["Mode of Learning", ":", student.get_mode_of_learning_display()],
        ["Batch Schedule", ":", student.batch_schedule or "N/A"],
        ["Instructor/Trainer", ":", student.instructor_name],
    ]

    # Set column widths
    col_widths = [120, 10, container_width - 130]

    try:
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # First column bold
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            # Other columns normal
            ("FONTNAME", (1, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 13),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),  # Labels
            ("ALIGN", (1, 0), (1, -1), "CENTER"),  # Colon
            ("ALIGN", (2, 0), (2, -1), "LEFT"),  # Values
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))

        # Draw the table at specified position
        frame_height = top_y - container_y - 10
        table.wrapOn(c, container_width + 10, frame_height)
        table.drawOn(c, container_x - 5, container_y + 100)
    except Exception as e:
        print(f"Error drawing table: {e}")
        # Fallback: draw simple text for each row
        c.setFont("Helvetica", 13)
        c.setFillColor(black)
        y_pos = container_y + 100
        for label, _, value in data:
            c.drawString(container_x, y_pos, f"{label}: {value}")
            y_pos -= 20


def draw_mid_sub_container(c, certificate, container_x, container_y, container_width, mid_sub_height,
                           bottom_sub_height):
    """Draws the middle sub-container with 4 stacked inner containers."""
    student = certificate.student

    # Base rectangle (background of mid sub-container)
    c.setFillColor(white)
    c.rect(container_x, container_y + bottom_sub_height, container_width, mid_sub_height, fill=0, stroke=0)

    # Top Y of mid-sub container
    top_y = container_y + bottom_sub_height + mid_sub_height

    # Title container
    draw_title_container(c, container_x, container_y, container_width, top_y)
    title_bottom_y = top_y - 30  # Spacing below title

    # Intro container
    enrolled_date = student.enrolled_date.strftime("%B %d, %Y") if student.enrolled_date else "N/A"
    intro_text = (
        f"This is to certify that Mr./Ms. {student.full_name}, Son/Daughter of {student.fathers_name}, "
        f"Resident of {student.address}, has been officially enrolled as a student of Digital "
        f"Pathshala on {enrolled_date} for the following academic and professional training program:"
    )
    draw_paragraph_container(c, intro_text, container_x, container_y + bottom_sub_height, container_width,
                             title_bottom_y)

    # Body container
    body_bottom_y = title_bottom_y - 160  # Adjust based on content height
    draw_body_container(c, certificate, container_x, container_y + bottom_sub_height, container_width, body_bottom_y)

    # Message container
    message_text = (
        "Upon successful completion of the program and fulfillment of all academic and disciplinary "
        "requirements, the student has been awarded a Certificate of Completion by Digital Pathshala."
    )
    message_bottom_y = body_bottom_y - 80  # Adjust based on content height
    draw_paragraph_container(c, message_text, container_x, container_y + bottom_sub_height, container_width,
                             message_bottom_y)


def draw_bottom_sub_container(c, container_x, container_y, container_width, bottom_sub_height):
    """Draws the bottom sub-container."""
    c.setFillColor(white)
    c.rect(container_x, container_y, container_width, bottom_sub_height, fill=0, stroke=0)

    # Signature square container
    sig_size = bottom_sub_height  # Square: width = height
    sig_x = container_x  # left side
    sig_y = container_y  # bottom of bottom container

    # Draw square border
    c.setStrokeColor(black)
    c.setFillColor(white)
    c.rect(sig_x, sig_y, sig_size, sig_size, fill=0, stroke=0)

    # Set text color to black
    c.setFillColor(black)

    # Signature text lines
    sig_lines = ["Authorized Signature", "Mahesh Basnet", "Director"]
    line_font = "Helvetica-Bold"
    line_size = 12
    line_spacing = 24  # vertical spacing between lines

    # Calculate starting Y to vertically center all lines
    total_text_height = len(sig_lines) * line_spacing
    start_y = sig_y + (sig_size + total_text_height) / 2 - line_spacing

    c.setFont(line_font, line_size)
    for i, text in enumerate(sig_lines):
        text_width = c.stringWidth(text, line_font, line_size)
        text_x = sig_x + (sig_size - text_width) / 2
        text_y = start_y - i * line_spacing
        c.drawString(text_x, text_y, text)

        # Draw line above "Authorized Signature" only
        if i == 0:
            line_y = text_y + 20  # slightly above first line
            c.setLineWidth(1.2)
            c.line(text_x, line_y, text_x + text_width, line_y)


def draw_main_container(c, certificate, container_x, container_y, container_width, container_height):
    """Draws the main container and delegates sub-containers."""

    # Draw main container
    c.setFillColor(white)
    c.rect(container_x, container_y, container_width, container_height, fill=1, stroke=0)

    # Sub-container heights
    top_sub_height = 120
    bottom_sub_height = 150
    mid_sub_height = container_height - (top_sub_height + bottom_sub_height)

    # Y positions
    top_sub_y = container_y + container_height - top_sub_height

    # Draw sub-containers
    draw_top_sub_container(c, certificate, container_x, top_sub_y, container_width, top_sub_height)
    draw_mid_sub_container(c, certificate, container_x, container_y, container_width, mid_sub_height, bottom_sub_height)
    draw_bottom_sub_container(c, container_x, container_y, container_width, bottom_sub_height)


def generate_certificate_pdf(certificate):
    """
    Generate a PDF certificate in the format similar to the provided sample.

    Args:
        certificate: Certificate model instance

    Returns:
        bytes: PDF content as bytes
    """
    from io import BytesIO

    # Create canvas in memory buffer
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Draw header (with error handling)
    try:
        draw_header(c, width, height)
    except Exception as e:
        print(f"Error drawing header: {e}")
        # Continue without header

    # Main container dimensions
    margin_x = 70
    container_x = margin_x
    container_y = 90
    container_width = width - 2 * margin_x
    container_height = height - 220  # Adjusted height

    # Draw main container
    try:
        draw_main_container(c, certificate, container_x, container_y, container_width, container_height)
    except Exception as e:
        print(f"Error drawing main container: {e}")
        # Draw simple fallback certificate
        c.setFont("Helvetica-Bold", 20)
        c.drawString(100, height / 2, "CERTIFICATE OF COMPLETION")
        c.setFont("Helvetica", 12)
        c.drawString(100, height / 2 - 30, f"This certifies that {certificate.student.full_name}")
        c.drawString(100, height / 2 - 50, f"has successfully completed the course.")

    # Draw footer (with error handling)
    try:
        draw_footer(c, width)
    except Exception as e:
        print(f"Error drawing footer: {e}")
        # Continue without footer

    # Add certificate number at the bottom
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(lightgrey)
    c.drawString(70, 50, f"Certificate Number: {certificate.certificate_number}")

    # Save the PDF
    c.save()

    # Get PDF content from buffer
    pdf_content = buffer.getvalue()
    buffer.close()

    return pdf_content
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

def generate_pdf(text, path="ScannedBook.pdf"):
    try:
        doc = SimpleDocTemplate(path, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()

        # Create custom style for better text formatting
        custom_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=12,
            leading=14,
            spaceAfter=6,
        )

        story = []

        # Clean and process text
        if not text or not text.strip():
            text = "No text could be extracted from the video."

        # Split text into lines and create paragraphs
        lines = text.split('\n')
        current_paragraph = []

        for line in lines:
            line = line.strip()
            if line:
                current_paragraph.append(line)
            elif current_paragraph:
                # Create paragraph from accumulated lines
                para_text = ' '.join(current_paragraph)
                if para_text.strip():
                    p = Paragraph(para_text, custom_style)
                    story.append(p)
                    story.append(Spacer(1, 6))  # Small space between paragraphs
                current_paragraph = []

        # Handle any remaining paragraph
        if current_paragraph:
            para_text = ' '.join(current_paragraph)
            if para_text.strip():
                p = Paragraph(para_text, custom_style)
                story.append(p)

        # If no paragraphs were created, add a default message
        if not story:
            p = Paragraph("No readable text was found in the video.", custom_style)
            story.append(p)

        doc.build(story)
        return path

    except Exception as e:
        print(f"PDF generation error: {e}")
        # Fallback to simple canvas method
        try:
            c = canvas.Canvas(path, pagesize=letter)
            width, height = letter

            # Simple text rendering
            c.setFont("Helvetica", 12)
            y_position = height - 50

            for line in text.split('\n'):
                if y_position < 50:  # New page if needed
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y_position = height - 50

                c.drawString(50, y_position, line[:80])  # Limit line length
                y_position -= 15

            c.save()
            return path
        except Exception as e2:
            print(f"Fallback PDF generation also failed: {e2}")
            raise e

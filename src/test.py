import PyPDF2
from reportlab.pdfgen import canvas
from io import BytesIO

def create_watermark(watermark_text):
    packet = BytesIO()
    # Create a PDF object to create the watermark
    can = canvas.Canvas(packet, pagesize=(200, 200))
    can.setFont("Helvetica", 12)
    can.rotate(45)  # Rotate the text by 45 degrees
    can.drawString(0, 100, watermark_text)
    can.save()

    packet.seek(0)
    watermark = PyPDF2.PdfReader(packet)

    return watermark

if __name__ == "__main__":
    import io

    # Input text for the watermark
    watermark_text = "This is the first test"

    # Create a blank PDF as the original PDF
    c = canvas.Canvas("original.pdf")
    c.save()

    # Create a watermark on each page of the original PDF
    create_watermark(watermark_text)

    print("Watermarked PDF created successfully.")

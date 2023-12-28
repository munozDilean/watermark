# app.py
from flask import Flask
from flask import request, render_template
from flask import make_response
from flask import send_file
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
import os
import math

from spire.pdf import *
from spire.pdf.common import *

# Constatns
ORIGINAL_VIDEO_PATH='original_videos'
ORIGINAL_PDF_PATH='original_pdfs'
RESULT_VIDEO_PATH='watermark_videos'
RESULT_PDF_PATH='watermark_pdfs'
VIDEO_FONTSIZE = 40

# for deletion later
PDF_FILE_PATH = "examples/sample_pdf_1.pdf"
WATERMARK_TEXT= "[RECEIVER EMAIL RECEIVER COMPANY | SENDER EMAIL SENDER COMPANY YYYY-MM-DD]"



app = Flask(__name__)
app.config['ORIGINAL_VIDEO_PATH'] = ORIGINAL_VIDEO_PATH
app.config['ORIGINAL_PDF_PATH'] = ORIGINAL_PDF_PATH
app.config['RESULT_VIDEO_PATH'] = RESULT_VIDEO_PATH
app.config['RESULT_PDF_PATH'] = RESULT_PDF_PATH



@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/pdf", methods=['POST', 'GET'])
def add_pdf_watermark():
    if not os.path.isdir(ORIGINAL_PDF_PATH):
        os.mkdir(ORIGINAL_PDF_PATH)
    if not os.path.isdir(RESULT_PDF_PATH):
        os.mkdir(RESULT_PDF_PATH)

    if request.method == "POST":
        # Get and save the file to the original_videos folder
        uploaded_file = request.files['fileInput']
        uploaded_file.save(os.path.join(app.config['ORIGINAL_PDF_PATH'], secure_filename(uploaded_file.filename)))
        # get file path 
       
        data = request.form
        sender_email = data['senderEmail'] or "SENDER EMAIL"
        sender_company = data['senderCompany'] or "SENDER_COMPANY"
        reciever_email= data['receiverEmail'] or "RECEIVER EMAIL"
        reciever_company = data['receiverCompany'] or "RECEIVER COMPANY"
        date = datetime.today().strftime('%Y-%m-%d')
        text = f"{sender_email} {sender_company} {reciever_email} {reciever_company} {date}"
        makeWatermark(text)
        tmp = uploaded_file.filename.split('.')
        tmp.insert(1, '_wm.')
        result_file_name = ''.join(tmp)
        makepdf(uploaded_file.filename,result_file_name)
        # spirePDFmethod()
        return "we will add the pdf watermark"
    else:
        file_name=request.args["fileName"]
        if os.path.isfile(f'{RESULT_PDF_PATH}/{file_name}'):
            return send_file(f'{RESULT_PDF_PATH}/{file_name}')
        else:
            return 'File does not exist', 400

@app.route("/video",methods = ['POST', 'GET'])
def add_video_watermark():
    if not os.path.isdir(ORIGINAL_VIDEO_PATH):
        os.mkdir(ORIGINAL_VIDEO_PATH)
    if not os.path.isdir(RESULT_VIDEO_PATH):
        os.mkdir(RESULT_VIDEO_PATH)
    # Handle making a new video Watermark
    if request.method == "POST":
        data = request.form
        sender_email = data['senderEmail'] or "SENDER EMAIL"
        sender_company = data['senderCompany'] or "SENDER_COMPANY"
        reciever_email= data['receiverEmail'] or "RECEIVER EMAIL"
        reciever_company = data['receiverCompany'] or "RECEIVER COMPANY"
        date = datetime.today().strftime('%Y-%m-%d')
        # Get and save the file to the original_videos folder
        uploaded_file = request.files['fileInput']
        uploaded_file.save(os.path.join(app.config['ORIGINAL_VIDEO_PATH'], secure_filename(uploaded_file.filename)))
        # get file path 
        filename = f"{app.config['ORIGINAL_VIDEO_PATH']}/{uploaded_file.filename}"
        # make the file name result
        tmp = uploaded_file.filename.split('.')
        tmp.insert(1, '_wm.')
        result_file_name = ''.join(tmp)
        # execute the command
        result = -1
        if (filename.endswith(".mp4")): #or .avi, .mpeg, whatever.
            result = os.system(f"ffmpeg -i {filename} -y -vf \"drawtext=text='{sender_email} {sender_company}':x=(w-text_w)/2:y=(h-text_h)/2:fontsize={VIDEO_FONTSIZE}:fontcolor=white@0.2, drawtext=text='{reciever_email} {reciever_company}':x=(w-text_w)/2:y=((h-text_h)/2)+{VIDEO_FONTSIZE+5}:fontsize={VIDEO_FONTSIZE}:fontcolor=white@0.2, drawtext=text='{date}':x=(w-text_w)/2:y=((h-text_h)/2)+{(VIDEO_FONTSIZE+5)*2}:fontsize={VIDEO_FONTSIZE}:fontcolor=white@0.2\" {RESULT_VIDEO_PATH}/{result_file_name}")

        if result == 0:
            response = make_response("Success", 200)
        else:
            response = make_response("Failed", 400)
        return response
    # Handle retriving a file
    else:
        file_name=request.args["fileName"]
        if os.path.isfile(f'{RESULT_VIDEO_PATH}/{file_name}'):
            return send_file(f'{RESULT_VIDEO_PATH}/{file_name}')
        else:
            return 'File does not exist', 400

# FOR PDF WATERMARK
def makeWatermark(watermark_text):
    text = watermark_text
    pdf = canvas.Canvas("watermark.pdf", pagesize=A4)
    pdf.translate(inch, inch)
    pdf.setFillColor(colors.grey, alpha=0.6)
    pdf.setFont("Helvetica", 17)
    pdf.rotate(45)
    pdf.drawCentredString(400, 100, text)
    pdf.save()

def makepdf(original_file_name,result_file_name):
    pdf_file = f"{ORIGINAL_PDF_PATH}/{original_file_name}"
    watermark = 'watermark.pdf'
    merged = result_file_name

    with open(pdf_file, "rb") as input_file, open(watermark, "rb") as watermark_file:
        input_pdf = PdfReader(input_file)
        watermark_pdf = PdfReader(watermark_file)
        watermark_page = watermark_pdf.pages[0]
        output = PdfWriter()

        for i in range(len(input_pdf.pages)):
            pdf_page = input_pdf.pages[i]
            pdf_page.merge_page(watermark_page)
            output.add_page(pdf_page)

        with open(merged, "wb") as merged_file:
            output.write(merged_file)

def spirePDFmethod():
    # Create a PdfDocument object
    pdf = PdfDocument()
    # Load a PDF file
    pdf.LoadFromFile("examples/sample_pdf_1.pdf")

    # Create a PdfTrueTypeFont object
    font = PdfTrueTypeFont("Arial", 20.0, 0, True)

    # Specify the watermark text
    text = WATERMARK_TEXT

    offset1 = float (font.MeasureString(text).Width * math.sqrt(2) / 4)
    offset2 = float (font.MeasureString(text).Height * math.sqrt(2) / 4)

    # Loop through the pages of the document
    for i in range(pdf.Pages.Count):
        # Get the current page
        page = pdf.Pages.get_Item(i)
        # Create a tile brush
        brush = PdfTilingBrush(SizeF(page.ActualSize.Width / float(3), page.ActualSize.Height / float(4)))
        # Set the transparency of the brush
        brush.Graphics.SetTransparency(0.3)
        brush.Graphics.Save()
        # Translate the coordinate system of the tile brush to a specified position
        brush.Graphics.TranslateTransform(brush.Size.Width / float(2) - offset1 - offset2, brush.Size.Height / float(2) + offset1 - offset2)
        # Rotate the coordinate system 45 degrees counterclockwise
        brush.Graphics.RotateTransform(-45.0)
        # Draw the watermark text on the tile brush
        brush.Graphics.DrawString(text, font, PdfBrushes.get_Violet(), 0.0, 0.0)
        brush.Graphics.Restore()
        brush.Graphics.SetTransparency(1.0)
        # Draw a rectangle that covers the whole page using the tile brush
        page.Canvas.DrawRectangle(brush, RectangleF(PointF(0.0, 0.0), page.ActualSize))

    # Save the resulting PDF file
    pdf.SaveToFile(f"{RESULT_PDF_PATH}/sample_pdf_1_wm.pdf")
    pdf.Close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
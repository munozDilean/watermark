# app.py
from flask import Flask
from flask import request
from flask import make_response
from flask import send_from_directory
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
import os

# Constatns
ORIGINAL_VIDEO_PATH='./original_videos'
ORIGINAL_PDF_PATH='./original_pdfs'
RESULT_VIDEO_PATH='./watermark_videos'
RESULT_PDF_PATH='./watermark_pdfs'
VIDEO_FONTSIZE = 40

# for deletion later
PDF_FILE_RESULT_NAME = "./output/result.pdf"
PDF_FILE_PATH = "examples/sample_pdf_1.pdf"
WATERMARK_TEXT= "[RECEIVER EMAIL RECEIVER COMPANY | SENDER EMAIL SENDER COMPANY YYYY-MM-DD]"



app = Flask(__name__)
app.config['ORIGINAL_VIDEO_PATH'] = ORIGINAL_VIDEO_PATH
app.config['ORIGINAL_PDF_PATH'] = ORIGINAL_PDF_PATH
app.config['RESULT_VIDEO_PATH'] = RESULT_VIDEO_PATH
app.config['RESULT_PDF_PATH'] = RESULT_PDF_PATH



@app.route("/")
def hello_world():
    return "<h1>Starter Flask App</h1>"

@app.route("/pdf")
def add_pdf_watermark():
    makeWatermark()
    makepdf()
    return "we will add the pdf watermark"

@app.route("/video",methods = ['POST', 'GET'])
def add_video_watermark():
    if not os.path.exists(ORIGINAL_VIDEO_PATH):
        os.mkdir(ORIGINAL_VIDEO_PATH)
    if not os.path.exists(RESULT_VIDEO_PATH):
        os.mkdir(RESULT_VIDEO_PATH)
    # Handle making a new video Watermark
    if request.method == "POST":
        data = request.form
        sender_email = data['senderEmail'] or "SENDER EMAIL"
        sender_company = data['senderCompany'].capitalize() or "SENDER_COMPANY"
        reciever_email= data['receiverEmail'] or "RECEIVER EMAIL"
        reciever_company = data['receiverCompany'].capitalize() or "RECEIVER COMPANY"
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
        if (filename.endswith(".mp4")): #or .avi, .mpeg, whatever.
            os.system(f"ffmpeg -i {filename} -y -vf \"drawtext=text='{sender_email} {sender_company}':x=(w-text_w)/2:y=(h-text_h)/2:fontsize={VIDEO_FONTSIZE}:fontcolor=white@0.2, drawtext=text='{reciever_email} {reciever_company}':x=(w-text_w)/2:y=((h-text_h)/2)+{VIDEO_FONTSIZE+5}:fontsize={VIDEO_FONTSIZE}:fontcolor=white@0.2, drawtext=text='{date}':x=(w-text_w)/2:y=((h-text_h)/2)+{(VIDEO_FONTSIZE+5)*2}:fontsize={VIDEO_FONTSIZE}:fontcolor=white@0.2\" {RESULT_VIDEO_PATH}/{result_file_name}")
        
        response = make_response("Success", 200)
        return response
    # Handle retriving a file
    else:
        file_name=request.args["fileName"]
        if os.path.exists(f'{RESULT_VIDEO_PATH}/{file_name}'):
            return send_from_directory(RESULT_VIDEO_PATH, file_name)
        else:
            return 'File does not exist', 400

# FOR PDF WATERMARK
def makeWatermark():
    text = WATERMARK_TEXT
    pdf = canvas.Canvas("watermark.pdf", pagesize=A4)
    pdf.translate(inch, inch)
    pdf.setFillColor(colors.grey, alpha=0.6)
    pdf.setFont("Helvetica", 17)
    pdf.rotate(45)
    pdf.drawCentredString(400, 100, text)
    pdf.save()


def makepdf():
    pdf_file = PDF_FILE_PATH
    watermark = 'watermark.pdf'
    merged = PDF_FILE_RESULT_NAME

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
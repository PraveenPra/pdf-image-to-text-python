import os
from flask import Flask, request, render_template, send_from_directory
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'E:\CustumInstallPrograms\OrcTesseractInstall\tesseract.exe'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def pdf_to_images(pdf_path, output_dir):
    pdf_document = fitz.open(pdf_path)
    pages_data = []

    for i in range(len(pdf_document)):
        page = pdf_document.load_page(i)
        image = page.get_pixmap()
        image_path = os.path.join(output_dir, f'page_{i}.png')
        image.save(image_path)
        text = ocr_image(image_path)
        text_path = os.path.join(output_dir, f'page_{i}.txt')
        save_text(text, text_path)
        pages_data.append((f'page_{i}.png', text))

    return pages_data

def ocr_image(image_path):
    return pytesseract.image_to_string(Image.open(image_path), lang='hin')

def save_text(text, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        pages_data = pdf_to_images(file_path, OUTPUT_FOLDER)
        return render_template('upload.html', pages_data=pages_data)

@app.route('/output/<filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)





'''
Filename: app.py
'''

import os
from flask import Flask, render_template, request, redirect, url_for
import PyPDF2
import docx # For .docx files
from werkzeug.utils import secure_filename

# Define a folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
# Define the file types we'll accept
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Checks if the file's extension is in our list of allowed extensions."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(filepath, filename):
    """Extracts text content based on file extension."""
    ext = filename.rsplit('.', 1)[1].lower()
    text = ''
    try:
        if ext == 'pdf':
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ''
        elif ext in ['doc', 'docx']:
            doc = docx.Document(filepath)
            for para in doc.paragraphs:
                text += para.text + '\n'
        elif ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        
        if not text:
            return "Successfully uploaded, but no text could be extracted from this file."
        return text

    except Exception as e:
        return f"An error occurred while processing the file: {e}"

@app.route('/')
def home():
    """Renders the home page."""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    """Handles the file upload and analysis."""
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url) # Or show an error
        
        file = request.files['file']
        
        if file.filename == '':
            return redirect(request.url) # Or show an error

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Extract text using our new function
            analysis_result = extract_text_from_file(filepath, filename)

            # Render the results page
            return render_template('results.html', filename=filename, analysis_result=analysis_result)

    # For a GET request, just display the upload page
    return render_template('upload.html')

if __name__ == '__main__':
    # Using debug=False is recommended for production environments
    app.run(host='0.0.0.0', port=5000)



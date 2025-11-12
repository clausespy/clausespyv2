
# Filename: app.py

import os
from flask import Flask, render_template, request, redirect, url_for
# NOTE: You will need to add PyPDF2 to your requirements.txt
import PyPDF2
from werkzeug.utils import secure_filename

# Define a folder to store uploaded files
UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        # Check if the file part is in the request
        if 'file' not in request.files:
            return redirect(request.url) # Or show an error
        
        file = request.files['file']
        
        # If the user does not select a file, the browser submits an empty file
        if file.filename == '':
            return redirect(request.url) # Or show an error

        if file:
            # It's good practice to secure the filename
            filename = secure_filename(file.filename)
            # Ensure the upload folder exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # --- AI Analysis Placeholder ---
            # This section extracts text from a PDF.
            # In your final app, you'll send this text to an AI model.
            analysis_result = ''
            try:
                if filename.lower().endswith('.pdf'):
                    with open(filepath, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages:
                            analysis_result += page.extract_text() or ''
                    if not analysis_result:
                        analysis_result = "Successfully uploaded, but no text could be extracted from this PDF."
                else:
                    analysis_result = "File is not a PDF. For now, only PDF text extraction is supported."
            except Exception as e:
                analysis_result = f"An error occurred while processing the file: {e}"
            # --- End of Placeholder ---

            return render_template('results.html', filename=filename, analysis_result=analysis_result)

    # For a GET request, just display the upload page
    return render_template('upload.html')

if __name__ == '__main__':
    # Using debug=False is recommended for production environments
    app.run(host='0.0.0.0', port=5000)


'''
This script runs a Flask web application that allows users to upload documents
(TXT, PDF, or DOCX) for legal analysis. The analysis is performed by the
OpenAI GPT-4 Turbo model, which returns a structured JSON response detailing
the contract's overall risk, opportunities, and a breakdown of potential risks.

Key functionalities:
- File upload with extension validation.
- Text extraction from various document formats.
- Interaction with the OpenAI API for text analysis.
- Structured JSON parsing for consistent output.
- Display of the analysis results on a web page.

To run this application:
1.  Ensure you have a virtual environment set up and activated.
2.  Install the required packages: `pip install Flask openai PyPDF2 python-docx`
3.  Set your OpenAI API key as an environment variable:
    -   On macOS/Linux: `export OPENAI_API_KEY='your_api_key_here'`
    -   On Windows: `set OPENAI_API_KEY=your_api_key_here`
4.  Run the script: `python app.py`
'''

import os
import json
from flask import Flask, render_template, request, redirect, url_for
import PyPDF2
import docx
from werkzeug.utils import secure_filename
import openai

# Initialize the OpenAI Client
# The API key is loaded from the environment variables.
# Ensure 'OPENAI_API_KEY' is set in your environment.
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Flask Application Configuration
UPLOAD_FOLDER = 'uploads'
# Removed 'doc' as it is not supported by the python-docx library.
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload folder if it does not exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Checks if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(filepath, filename):
    """
    Extracts text content from the uploaded file based on its extension.
    Supports TXT, PDF, and DOCX formats.
    """
    ext = filename.rsplit('.', 1)[1].lower()
    text = ''
    try:
        if ext == 'pdf':
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                if not reader.pages:
                    print(f"Warning: PDF file {filename} has no pages.")
                    return None
                for page in reader.pages:
                    text += page.extract_text() or ''
        elif ext == 'docx':
            doc = docx.Document(filepath)
            for para in doc.paragraphs:
                text += para.text + '\n'
        elif ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        # Return None if text is empty or just whitespace
        return text if text.strip() else None
    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")
        return None

def analyze_text_with_openai_json(text, filename):
    """
    Sends the extracted text to OpenAI's GPT-4 Turbo model for analysis and
    requests a structured JSON response.
    """
    if not text:
        return {
            "error": "The document appears to be empty or no text could be extracted.",
            "original_filename": filename
        }

    system_prompt = '''
    You are an expert legal assistant. Analyze the provided contract text and return your analysis
    in a structured JSON format. The JSON object must have the following keys:
    - "original_filename": A string containing the original name of the file.
    - "overall_risk": A string with one of three values: "High", "Medium", or "Low".
    - "opportunities_found": An integer representing the number of opportunities or positive clauses you found.
    - "risk_breakdown": An array of objects, where each object represents a specific risk and has these keys:
        - "risk_level": A string, either "High", "Medium", or "Low".
        - "title": A short, descriptive title for the risk (e.g., "Unlimited Liability").
        - "description": A 1-2 sentence explanation of the risk and its location.
    
    Ensure your output is a single, valid JSON object and nothing else.
    '''
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            response_format={"type": "json_object"},  # Force JSON output
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze the following document named '{filename}':\n\n{text}"}
            ]
        )
        analysis_data = json.loads(completion.choices[0].message.content)
        return analysis_data
    except Exception as e:
        print(f"Error with OpenAI API or JSON parsing: {e}")
        return {
            "original_filename": filename,
            "overall_risk": "Error",
            "opportunities_found": 0,
            "risk_breakdown": [{"risk_level": "Error", "title": "Analysis Failed", "description": str(e)}]
        }

@app.route('/')
def home():
    """Renders the main upload page (index.html)."""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    """Handles the file upload, processing, and renders the result."""
    if request.method == 'POST':
        # Check if a file was submitted
        if 'file' not in request.files or not request.files['file'].filename:
            return redirect(request.url)
        
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(filepath)
                extracted_text = extract_text_from_file(filepath, filename)
                analysis_data = analyze_text_with_openai_json(extracted_text, filename)
            finally:
                # Ensure the uploaded file is removed after processing
                if os.path.exists(filepath):
                    os.remove(filepath)

            return render_template('result.html', analysis=analysis_data)
            
    # For a GET request or if the file is not allowed, show the main upload page
    return render_template('index.html')

if __name__ == '__main__':
    # Note: debug=True is for development. Set to False in production.
    app.run(debug=True)

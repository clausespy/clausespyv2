import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
import PyPDF2
import docx
from werkzeug.utils import secure_filename
import openai

# Load environment variables from a .env file for local development
load_dotenv()

# --- Initialize the OpenAI Client ---
# This securely reads the API key from the environment.
# On your live server, you will set this as an environment variable.
# On your local machine, it will be read from your .env file.
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define a folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
# Define the file types we'll accept
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
                if not reader.pages:
                    return None # Handle empty PDF
                for page in reader.pages:
                    text += page.extract_text() or ''
        elif ext in ['doc', 'docx']:
            doc = docx.Document(filepath)
            for para in doc.paragraphs:
                text += para.text + '\n'
        elif ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        
        return text if text else None

    except Exception as e:
        print(f"An error occurred while processing the file: {e}")
        return None

def analyze_text_with_openai(text):
    """Sends the extracted text to OpenAI for analysis."""
    if not text:
        return "The document appears to be empty or no text could be extracted."
    try:
        completion = client.chat.completions.create(
            model="gpt-4-turbo",  # Or whichever model you prefer
            messages=[
                {"role": "system", "content": "You are an expert legal assistant specializing in contract analysis. Analyze the following document and highlight key clauses, potential risks, and obligations."},
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred while communicating with OpenAI: {e}"

@app.route('/')
def home():
    """Renders the home page."""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    """Handles the file upload and analysis."""
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Extract text from the saved file
            extracted_text = extract_text_from_file(filepath, filename)

            # Analyze the text with OpenAI
            analysis_result = analyze_text_with_openai(extracted_text)
            
            # Clean up the uploaded file
            os.remove(filepath)

            # Render the result page with the analysis
            return render_template('result.html', analysis=analysis_result)
            
    # If a GET request or there was an issue, show the upload page again.
    return render_template('index.html')

# This is needed to run the app locally for testing
if __name__ == '__main__':
    app.run(debug=True)

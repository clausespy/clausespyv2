import os
import json
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
import PyPDF2
import docx
from werkzeug.utils import secure_filename
import openai

# Load environment variables
load_dotenv()

# Initialize OpenAI Client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Flask App Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(filepath, filename):
    # (This function is unchanged)
    ext = filename.rsplit('.', 1)[1].lower()
    text = ''
    try:
        if ext == 'pdf':
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                if not reader.pages: return None
                for page in reader.pages: text += page.extract_text() or ''
        elif ext in ['doc', 'docx']:
            doc = docx.Document(filepath)
            for para in doc.paragraphs: text += para.text + '\n'
        elif ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f: text = f.read()
        return text if text else None
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

def analyze_text_with_openai_json(text, filename):
    """
    NEW: Sends text to OpenAI and requests a structured JSON response.
    """
    if not text:
        return {"error": "The document appears to be empty or no text could be extracted."}

    # This is the new, more detailed prompt that tells the AI exactly how to format the JSON.
    system_prompt = """
    You are an expert legal assistant. Analyze the provided contract text and return your analysis
    in a structured JSON format. The JSON object must have the following keys:
    - "original_filename": A string containing the original name of the file.
    - "overall_risk": A string with one of three values: "High", "Medium", or "Low".
    - "opportunities_found": An integer representing the number of opportunities or positive clauses you found.
    - "risk_breakdown": An array of objects, where each object represents a specific risk and has the following keys:
        - "risk_level": A string, either "High", "Medium", or "Low".
        - "title": A short, descriptive title for the risk (e.g., "Unlimited Liability").
        - "description": A 1-2 sentence explanation of the risk and its location.
    
    Do not include any text outside of the JSON object itself.
    """
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            response_format={"type": "json_object"}, # NEW: Force the model to return JSON
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze the following document named '{filename}':\n\n{text}"}
            ]
        )
        # The response content is a JSON string, so we parse it into a Python dictionary
        analysis_data = json.loads(completion.choices[0].message.content)
        return analysis_data
    except Exception as e:
        print(f"Error with OpenAI or JSON parsing: {e}")
        # Return a default error structure if something goes wrong
        return {
            "original_filename": filename,
            "overall_risk": "Error",
            "opportunities_found": 0,
            "risk_breakdown": [{"risk_level": "Error", "title": "Analysis Failed", "description": str(e)}]
        }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            extracted_text = extract_text_from_file(filepath, filename)
            
            # NEW: Call the JSON version of the analysis function
            analysis_data = analyze_text_with_openai_json(extracted_text, filename)
            
            os.remove(filepath)

            # NEW: Pass the entire dictionary to the template
            return render_template('result.html', analysis=analysis_data)
            
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

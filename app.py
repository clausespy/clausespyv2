'''
This script runs a Flask web application that provides AI-powered legal analysis.
It is a membership-based application requiring users to log in.

User Flow:
1. Visitor sees the landing page.
2. Clicks "Get Started" -> Goes to the login page.
3. After login/registration -> Redirected to the upload form.

Key Features:
- Landing page for new visitors.
- User registration, login, and session management.
- Protected route for document analysis, accessible only to logged-in users.
- File upload (TXT, PDF, DOCX) and text extraction with error handling.
- AI analysis using GPT-4o mini with a structured JSON response.
- Database for storing user information (using SQLite).
'''

import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import PyPDF2
import docx
import openai

# --- App Initialization and Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize OpenAI Client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

# --- Database Model ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Helper Functions (File Processing & AI) ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(filepath, filename):
    ext = filename.rsplit('.', 1)[1].lower()
    text = ''
    try:
        if ext == 'pdf':
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                if reader.is_encrypted:
                    return None, f"The PDF file '{filename}' is encrypted and cannot be processed."
                if not reader.pages:
                    return None, f"The PDF file '{filename}' contains no pages."
                for page in reader.pages:
                    text += page.extract_text() or ''
        elif ext == 'docx':
            doc = docx.Document(filepath)
            for para in doc.paragraphs:
                text += para.text + '\n'
        elif ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        
        if not text.strip():
            return None, f"No text could be extracted from '{filename}'. The file may be empty or contain only images."
        
        return text, None
    except Exception as e:
        return None, f"An error occurred while trying to read '{filename}': {str(e)}"

def analyze_text_with_openai_json(text, filename):
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
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze the following document named '{filename}':\n\n{text}"}
            ]
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"original_filename": filename, "error": f"The AI model failed to analyze the document. Error: {str(e)}"}

# --- Routes ---
@app.route('/')
def home():
    """Renders the main marketing landing page."""
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('upload_form'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('upload_form'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('upload_form'))
    if request.method == 'POST':
        if User.query.filter_by(email=request.form['email']).first():
            flash('Email address already registered.')
            return redirect(url_for('register'))
        new_user = User(username=request.form['username'], email=request.form['email'])
        new_user.set_password(request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        flash('Thanks for registering! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/upload-form')
@login_required
def upload_form():
    """Displays the page with the file upload form."""
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
@login_required
def handle_upload():
    if 'file' not in request.files or not request.files['file'].filename:
        flash('No file part selected.')
        return redirect(url_for('upload_form'))
    
    file = request.files['file']
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload a TXT, PDF, or DOCX file.')
        return redirect(url_for('upload_form'))
        
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    analysis_data = None
    
    try:
        file.save(filepath)
        extracted_text, error = extract_text_from_file(filepath, filename)
        
        if error:
            analysis_data = {"original_filename": filename, "error": error}
        else:
            analysis_data = analyze_text_with_openai_json(extracted_text, filename)
    except Exception as e:
        analysis_data = {"original_filename": filename, "error": f"A server error occurred: {str(e)}"}
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

    return render_template('result.html', analysis=analysis_data)

# --- Main Execution ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

import os
import uuid
import json # Import the json library
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import fitz  # PyMuPDF
import openai

# --- App and Database Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-super-secret-key-that-you-should-change'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- OpenAI API Key ---
# IMPORTANT: Replace "your-openai-api-key" with your actual OpenAI API key
openai.api_key = "your-openai-api-key"

# --- User Model ---
class User(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('upload_page'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))
        
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload')
@login_required
def upload_page():
    return render_template('upload.html')

analysis_results = {}

@app.route('/analyze', methods=['POST'])
@login_required
def analyze_contract():
    if 'contract_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['contract_file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('upload_page'))
    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()

            system_prompt = '''
            You are a legal contract analyzer. Analyze the provided contract text and return a JSON object with the following structure:
            {
              "overall_risk": "Low", "Medium", or "High",
              "opportunities_found": "A brief summary of any opportunities or benefits for the user.",
              "risk_breakdown": [
                {
                  "title": "Clause Title",
                  "risk_level": "Low", "Medium", or "High",
                  "description": "A summary of the clause and why it represents that level of risk."
                }
              ]
            }
            Do not include any text outside of the JSON object.
            '''
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo-1106", # A model that supports JSON mode
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ]
            )
            
            analysis_data = json.loads(response.choices[0].message.content)
            analysis_data['original_filename'] = filename
            
            task_id = str(uuid.uuid4())
            analysis_results[task_id] = analysis_data
            
            return redirect(url_for('results_page', task_id=task_id))

        except Exception as e:
            task_id = str(uuid.uuid4())
            analysis_results[task_id] = {
                "error": f"An error occurred during analysis: {e}",
                "original_filename": filename
            }
            return redirect(url_for('results_page', task_id=task_id))

@app.route('/results/<task_id>')
@login_required
def results_page(task_id):
    analysis = analysis_results.get(task_id, {"error": "Analysis not found.", "original_filename": "Unknown"})
    return render_template('results.html', analysis=analysis)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='leigh').first():
            admin_user = User(username='leigh')
            admin_user.set_password('your_password') # Change this password
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)

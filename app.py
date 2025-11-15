import os
import uuid
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import fitz  # PyMuPDF
import openai
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# --- App and Database Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-default-secret-key-for-development')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Flask-Migrate Initialization ---
migrate = Migrate(app, db)

# --- OpenAI API Key ---
openai.api_key = os.environ.get("OPENAI_API_KEY")

# --- User Model ---
class User(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    # New 'role' column to distinguish admins from regular users
    role = db.Column(db.String(20), nullable=False, default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Property to easily check if a user is an admin
    @property
    def is_admin(self):
        return self.role == 'admin'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# --- Admin Setup ---
# Custom ModelView to protect admin pages from non-admin users
class AdminView(ModelView):
    def is_accessible(self):
        # Only allow access if the user is logged in and has the 'admin' role
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # Redirect non-admins to the login page if they try to access /admin
        flash('You must be an admin to access this page.', 'danger')
        return redirect(url_for('login'))

# Initialize Flask-Admin
admin = Admin(app, name='ClauseSpy Admin', template_mode='bootstrap3')

# Add the User model to the admin interface, protected by our custom AdminView
admin.add_view(AdminView(User, db.session))

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('upload_page'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            # After login, check if the user is an admin and redirect them
            if user.is_admin:
                return redirect(url_for('admin.index'))
            # Otherwise, redirect to the standard upload page
            return redirect(url_for('upload_page'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('upload_page'))
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
            You are a legal contract analyzer. Analyze the provided contract text and return a JSON object...
            '''
            
            # This is a placeholder for the actual OpenAI call
            # In a real app, you'd handle the API call here
            analysis_data = {
                "overall_risk": "Medium",
                "opportunities_found": "Sample analysis result.",
                "risk_breakdown": []
            }
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

# --- CLI command to create an admin user ---
@app.cli.command("create-admin")
def create_admin():
    """Creates or updates a user to have the admin role."""
    username = input("Enter username for admin: ")
    password = input("Enter password for admin: ")
    
    user = User.query.filter_by(username=username).first()
    if user:
        print(f"User '{username}' already exists. Updating role to admin and setting new password.")
        user.role = 'admin'
        user.set_password(password)
    else:
        print(f"Creating new admin user: '{username}'.")
        user = User(username=username, role='admin')
        user.set_password(password)
        db.session.add(user)
    
    db.session.commit()
    print(f"Admin user '{username}' successfully created/updated.")

if __name__ == '__main__':
    app.run(debug=True)

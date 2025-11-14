from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import uuid
import os

# --- App and Login Manager Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-super-secret-key-that-you-should-change'
# Create a folder to store uploads
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

# --- User Model and In-Memory Database ---
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

users_db = {}

# --- User Loader ---
@login_manager.user_loader
def load_user(user_id):
    return users_db.get(user_id)

# --- Main Routes ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Auth Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users_db.values() if u.username == username), None)
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
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
        if any(u.username == username for u in users_db.values()):
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))
        new_id = str(uuid.uuid4())
        new_user = User(id=new_id, username=username, password=password)
        users_db[new_id] = new_user
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- App Functionality Routes ---
@app.route('/upload')
@login_required
def upload_page():
    """Renders the file upload page."""
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
@login_required
def analyze_contract():
    """Handles the contract file upload and initiates analysis."""
    if 'contract_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['contract_file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('upload_page'))
    if file:
        # In a real app, you'd secure the filename
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Here is where you would trigger your AI analysis on the file at file_path
        
        # For now, we'll just flash a success message
        flash(f'Successfully uploaded "{filename}". Analysis is in progress...')
        return redirect(url_for('upload_page'))

if __name__ == '__main__':
    app.run(debug=True)

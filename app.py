from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import uuid

# --- App and Login Manager Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-super-secret-key-that-you-should-change' 

login_manager = LoginManager()
login_manager.init_app(app)
# If a user tries to access a page that requires a login, redirect them to the 'login' page
login_manager.login_view = 'login' 

# --- User Model and In-Memory Database ---
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Using a dictionary to act as a simple in-memory database
users_db = {}

# --- User Loader ---
@login_manager.user_loader
def load_user(user_id):
    """Loads a user from our 'database'"""
    return users_db.get(user_id)

# --- Routes ---
@app.route('/')
def index():
    """Renders the main landing page."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login on its own page."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = None
        for u in users_db.values():
            if u.username == username:
                user = u
                break
            
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user registration on its own page."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username already exists
        if any(u.username == username for u in users_db.values()):
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))

        # Create new user and add to our 'database'
        new_id = str(uuid.uuid4())
        new_user = User(id=new_id, username=username, password=password)
        users_db[new_id] = new_user
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Logs the current user out."""
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload')
@login_required
def upload_form():
    """A protected page for logged-in users."""
    # This corresponds to your 'Get Started' button's action for logged-in users.
    # You will need to create 'upload.html' for this to be useful.
    return "<h1>Upload Your Contract</h1><p>You are logged in as {{ current_user.username }}.</p>"

if __name__ == '__main__':
    app.run(debug=True)

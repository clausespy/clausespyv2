from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

# 1. Initialize the Flask App
app = Flask(__name__)
# You must set a secret key for session management
app.config['SECRET_KEY'] = 'a-super-secret-key-that-you-should-change' 

# 2. Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
# If a user tries to access a page that requires a login, redirect them here
login_manager.login_view = 'index' 

# 3. Create a User Model
# This is a simple User class. In a real app, this would come from a database.
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Simple in-memory user database.
users_db = {
    "1": User(id="1", username="testuser", password="password123")
}

# 4. Create a user_loader function
@login_manager.user_loader
def load_user(user_id):
    """Loads a user object from the user ID stored in the session."""
    return users_db.get(user_id)

# 5. Update Routes
@app.route('/')
def index():
    """Renders the home/login page."""
    # The template now handles showing the login form or the welcome message
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Handles the user login form submission."""
    username = request.form['username']
    password = request.form['password']
    
    # Find the user
    user = None
    for u in users_db.values():
        if u.username == username:
            user = u
            break
            
    # Check if user exists and password is correct
    if user and user.password == password:
        login_user(user) # This function handles the session
        return redirect(url_for('index'))
    else:
        # If login fails, you can redirect back to index or show an error
        return redirect(url_for('index')) 

@app.route('/register')
def register():
    """Renders the registration page."""
    # This route just shows the registration page. You would add POST logic
    # to handle the form submission and add a new user to your database.
    return render_template('register.html')

@app.route('/logout')
@login_required # Ensures only logged-in users can access this
def logout():
    """Logs the current user out."""
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload')
@login_required # Protect this page so only logged-in users can see it
def upload_form():
    """Shows the file upload page."""
    # You would create an 'upload.html' template for this.
    return "<h1>Upload Page</h1><p>Welcome, you are logged in!</p>"

if __name__ == '__main__':
    app.run(debug=True)

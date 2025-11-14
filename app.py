from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# This is a simple in-memory user store for demonstration.
# In a real application, you would use a database.
users = {}

@app.route('/')
def index():
    """Renders the home page."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        # In a real app, you would verify username and password
        username = request.form['username']
        if username in users:
            # Logic to check password would go here
            return redirect(url_for('index'))
        else:
            # Handle failed login
            return 'Invalid login', 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user registration."""
    if request.method == 'POST':
        username = request.form['username']
        # In a real app, you would hash the password
        password = request.form['password']
        if username not in users:
            users[username] = password
            return redirect(url_for('login'))
        else:
            # Handle case where user already exists
            return 'User already exists', 409
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)


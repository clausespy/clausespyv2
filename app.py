# Change 1: Simplify the main home() route
@app.route('/')
def home():
    """Renders the main marketing landing page."""
    return render_template('landing.html')


# Change 2: Update the login() function to redirect to the upload form
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # If user is already logged in, send them to the upload form
        return redirect(url_for('upload_form')) 
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            # This is the crucial change: redirect to 'upload_form' after login
            return redirect(url_for('upload_form'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html')


# Change 3: Rename the upload form route to prevent conflicts
@app.route('/upload-form')
@login_required
def upload_form():
    """Displays the page with the file upload form."""
    return render_template('upload.html')


# The function that handles the file submission is now at /upload
@app.route('/upload', methods=['POST'])
@login_required
def handle_upload():
    # ... (The rest of this function remains unchanged)
    # ...

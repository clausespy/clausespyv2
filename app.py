
# Filename: app.py

# 1. Initialize the Flask Application
from flask import Flask, render_template

# The 'app' object is the core of your web application.
# Gunicorn, the server used by Render, will look for this variable to start your app.
app = Flask(__name__)

# 2. Define the Application's Routes
# A route connects a URL to a specific Python function.
@app.route('/')
def home():
    """
    This function handles requests to the root URL ('/').
    It renders and returns the 'index.html' file from the 'templates' directory.
    """
    return render_template('index.html')

# 3. Entry point for Local Development
# This part of the code runs ONLY when you execute 'python app.py' on your local machine.
# It is not used by the Gunicorn server on Render.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


### Why This Code Works

*   **App Initialization**: The line `app = Flask(__name__)` correctly creates your Flask application.
*   **Routing**: The `@app.route('/')` decorator properly maps the main URL of your site to the `home()` function.
*   **Rendering Template**: The `home()` function correctly returns your `index.html` page.
*   **Gunicorn Compatibility**: Render's server (Gunicorn) will automatically find and use the `app` object, ignoring the `if __name__ == '__main__':` block, which is the correct behavior.

It seems you have already fixed the original problem. The previous issue may have been an accidental commenting out of the entire file, but the code you've provided now is correct.


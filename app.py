


'''
# Filename: app.py

from flask import Flask, render_template

# 1. Initialize the Flask Application
# This 'app' variable is the central object that Gunicorn will use to run the application.

app = Flask(__name__)
# Forcing a fresh deployment yes

# 2. Define the Routes
# A route maps a URL to a Python function. When a user visits the URL,
# Flask executes the function and returns its output to the browser.

@app.route('/')
def home():
    """
    This function handles all web requests to the main URL ('/').
    It tells Flask to find and return the 'index.html' file from the 'templates' folder.
    """
    return render_template('index.html')


# 3. Local Development Server
# This block of code is only executed when you run 'python app.py' directly on your own computer.
# The Gunicorn server on Render does not use this part.
if __name__ == '__main__':
    # The host='0.0.0.0' makes the server accessible on your local network.
    # The port=5000 is a standard port for development.
    # debug=True will automatically reload the server when you save changes.
    app.run(host='0.0.0.0', port=5000, debug=True)

'''





# Filename: app.py

import os
from flask import Flask, render_template

app = Flask(__name__)

# --- Debugging ---
print(f"Current working directory: {os.getcwd()}")
print(f"Flask root_path: {app.root_path}")
print(f"Flask template_folder: {app.template_folder}")
# Let's see what Flask sees in its root path
try:
    print(f"Contents of root_path ({app.root_path}): {os.listdir(app.root_path)}")
except Exception as e:
    print(f"Error listing contents of root_path: {e}")
# And the contents of the current working directory
try:
    print(f"Contents of CWD ({os.getcwd()}): {os.listdir(os.getcwd())}")
except Exception as e:
    print(f"Error listing contents of CWD: {e}")
# --- End Debugging ---

@app.route('/', methods=['GET', 'HEAD'])
def home():
    """
    This function handles requests to the root URL ('/').
    It now explicitly handles both GET and HEAD requests.
    """
    return render_template('index.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# Filename: app.py

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'HEAD'])
def home():
    """
    This function handles requests to the root URL ('/').
    It now explicitly handles both GET and HEAD requests.
    """
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

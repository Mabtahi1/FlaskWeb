"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
from datetime import datetime
from flask import render_template
from flask import Flask
app = Flask(__name__ , template_folder="templates")

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


@app.route('/')
def hello():
    """Renders a sample page."""
    # return "Hello World!"
    
    return render_template('index.html')

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)

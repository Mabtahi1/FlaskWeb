"""
Prolexis Analytics - Flask Web Application
"""
from datetime import datetime
from flask import render_template, url_for
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def hello():
    """Renders the home page."""
    return render_template('index.html')

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template('contact.html')

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template('about.html')

@app.route('/TrendSummarizer')
def TrendSummarizer():
    """Renders the trend summarizer page."""
    return render_template('TrendSummarizer.html')

@app.route('/DataHelp')
def DataHelp():
    """Renders the data help page."""
    return render_template('DataHelp.html')

@app.route('/signin')
def signin():
    """Renders the signin page."""
    return render_template('signin.html')

@app.route('/signup')
def signup():
    """Renders the signup page."""
    return render_template('signup.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'service': 'Prolexis Analytics'}

@app.route('/tools')
def tools():
    return render_template('tools.html')
    
if __name__ == '__main__':
    # For Heroku deployment
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

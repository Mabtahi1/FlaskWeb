"""
Prolexis Analytics - Flask Web Application
"""
from datetime import datetime
from flask import render_template, url_for, redirect, jsonify
from flask import Flask
import subprocess
import threading
import time
import requests
import os

app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

# Global variable to track Streamlit process
streamlit_process = None

def start_streamlit():
    """Start Streamlit app in background"""
    global streamlit_process
    try:
        # Start Streamlit on port 8501
        streamlit_process = subprocess.Popen([
            'streamlit', 'run', 'streamlit_app.py', 
            '--server.port=8501',
            '--server.headless=true',
            '--server.enableXsrfProtection=false',
            '--server.enableCORS=false'
        ])
        print("✅ Streamlit BI Analyzer started on port 8501")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

def check_streamlit_health():
    """Check if Streamlit is running"""
    try:
        response = requests.get("http://localhost:8501/healthz", timeout=5)
        return response.status_code == 200
    except:
        return False

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

@app.route('/business-intelligence')
def business_intelligence():
    """Renders the Business Intelligence Analyzer page."""
    # Check if Streamlit is running, start if needed
    if not check_streamlit_health():
        threading.Thread(target=start_streamlit, daemon=True).start()
        time.sleep(3)  # Wait for Streamlit to start
    
    return render_template('business_intelligence.html')

@app.route('/bi-app')
def bi_app_redirect():
    """Direct redirect to Streamlit app"""
    return redirect("http://localhost:8501")

@app.route('/health')
def health():
    """Health check endpoint"""
    streamlit_status = check_streamlit_health()
    return jsonify({
        'flask': 'running',
        'streamlit': 'running' if streamlit_status else 'stopped'
    })

if __name__ == '__main__':
    # Start Streamlit in background
    print("🚀 Starting Prolexis Analytics Platform...")
    threading.Thread(target=start_streamlit, daemon=True).start()
    
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    
    print(f"🌐 Flask website running on http://{HOST}:{PORT}")
    print(f"📊 BI Analyzer available on http://localhost:8501")
    print(f"🔗 Access BI through: http://{HOST}:{PORT}/business-intelligence")
    
    app.run(HOST, PORT, debug=True)

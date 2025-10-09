"""
Prolexis Analytics - Flask Web Application
"""
from datetime import datetime
from flask import render_template, url_for, request, redirect, jsonify
from flask import Flask
import os
import stripe
import pyrebase

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_no_cache(response):
    response.cache_control.no_store = True
    response.cache_control.no_cache = True
    response.cache_control.must_revalidate = True
    response.cache_control.max_age = 0
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Stripe configuration (replace with your actual keys)
# Instead of hardcoded keys:
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')

# Firebase configuration (same as your Streamlit)
firebase_config = {
    "apiKey": "AIzaSyDt6y7YRFVF_zrMTYPn4z4ViHjLbmfMsLQ",
    "authDomain": "trend-summarizer-6f28e.firebaseapp.com",
    "projectId": "trend-summarizer-6f28e",
    "storageBucket": "trend-summarizer-6f28e.firebasestorage.app",
    "messagingSenderId": "655575726457",
    "databaseURL": "https://trend-summarizer-6f28e-default-rtdb.firebaseio.com",
    "appId": "1:655575726457:web:9ae1d0d363c804edc9d7a8",
    "measurementId": "G-HHY482GQKZ"
}

try:
    firebase = pyrebase.initialize_app(firebase_config)
    db = firebase.database()
except Exception as e:
    print(f"Firebase error: {e}")
    db = None

# Your existing routes
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
@app.route('/app')
def legal_app():
    return render_template('legal_app.html')  # or whatever template name you're using
# NEW: Payment routes
@app.route('/payment/<plan_type>')
def payment(plan_type):
    """Handle payment for different plans"""
    
    plans = {
        'basic': {'price': 1000, 'name': 'Basic Plan', 'description': '5 summaries/month'},
        'pro': {'price': 4900, 'name': 'Pro Plan', 'description': 'Unlimited summaries + competitor tracking'},
        'onetime': {'price': 2500, 'name': 'One-time Plan', 'description': 'PDF from up to 3 sources'},
        'starter': {'price': 49900, 'name': 'Starter Plan', 'description': 'Dashboard + Data cleanup'},
        'premium': {'price': 99900, 'name': 'Premium Plan', 'description': 'Automation + Forecasting + $100/mo'}
    }
    
    if plan_type not in plans:
        return "Invalid plan", 400
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': plans[plan_type]['name'],
                        'description': plans[plan_type]['description'],
                    },
                    'unit_amount': plans[plan_type]['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'https://prolexisanalytics.com/payment-success?session_id={{CHECKOUT_SESSION_ID}}&plan={plan_type}',
            cancel_url='https://prolexisanalytics.com/',
            metadata={
                'plan_type': plan_type
            },
            # Add this to collect customer email
            customer_email=request.args.get('email'),  # We'll pass this from the frontend
            billing_address_collection='required'
        )
        return redirect(session.url)
    except Exception as e:
        return f"Error creating payment session: {str(e)}", 400

@app.route('/payment-success')
def payment_success():
    """Handle successful payment"""
    session_id = request.args.get('session_id')
    plan_type = request.args.get('plan')
    
    if not session_id:
        return "Missing session ID", 400
    
    try:
        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            # Get customer email from the session
            customer_email = session.customer_details.email if session.customer_details else None
            
            # Store payment info (we'll add Firebase later)
            payment_info = {
                'email': customer_email,
                'plan': plan_type,
                'amount': session.amount_total,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # For now, just log it (we'll add Firebase integration next)
            print(f"Payment successful: {payment_info}")
            
            return render_template('payment_success.html', 
                                 plan=plan_type, 
                                 session_id=session_id,
                                 email=customer_email)
        else:
            return "Payment not completed", 400
            
    except Exception as e:
        return f"Error verifying payment: {str(e)}", 400

@app.route('/upgrade-user', methods=['POST'])
def upgrade_user():
    """API endpoint to upgrade user after payment"""
    data = request.get_json()
    email = data.get('email')
    plan_type = data.get('plan_type')
    
    if not email or not plan_type:
        return jsonify({'error': 'Missing email or plan_type'}), 400
    
    try:
        # Update user in Firebase
        update_user_subscription(email, plan_type)
        return jsonify({'success': True, 'message': 'User upgraded successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def update_user_subscription(email, plan_type):
    """Update user subscription in Firebase"""
    user_key = email.replace(".", "_")
    
    # Define plan limits
    plans = {
        "basic": {
            "summaries_per_month": 5,
            "sources_limit": 3,
            "has_competitor_tracking": False,
            "has_automation": False,
            "has_forecasting": False
        },
        "pro": {
            "summaries_per_month": "unlimited",
            "sources_limit": "unlimited", 
            "has_competitor_tracking": True,
            "has_automation": False,
            "has_forecasting": False
        },
        "onetime": {
            "summaries_per_month": 3,
            "sources_limit": 3,
            "has_competitor_tracking": False,
            "has_automation": False,
            "has_forecasting": False
        },
        "starter": {
            "summaries_per_month": 10,
            "sources_limit": 5,
            "has_competitor_tracking": False,
            "has_automation": True,
            "has_forecasting": False
        },
        "premium": {
            "summaries_per_month": "unlimited",
            "sources_limit": "unlimited",
            "has_competitor_tracking": True,
            "has_automation": True,
            "has_forecasting": True
        }
    }
    
    update_data = {
        "subscription_type": plan_type,
        "subscription_status": "active",
        "payment_date": datetime.now().isoformat(),
        "usage_limits": plans.get(plan_type, plans["basic"]),
        # Reset usage count for new subscription
        "current_usage": {
            "summaries_this_month": 0,
            "last_reset_date": datetime.now().replace(day=1).isoformat()
        }
    }
    
    db.child("users").child(user_key).update(update_data)

if __name__ == '__main__':
    # For Heroku deployment
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)





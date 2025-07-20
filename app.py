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

# Stripe configuration (replace with your actual keys)
stripe.api_key = "sk_test_YOUR_STRIPE_SECRET_KEY"  # Replace with your secret key
STRIPE_PUBLISHABLE_KEY = "pk_test_YOUR_STRIPE_PUBLISHABLE_KEY"  # Replace with your publishable key

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

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

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

# NEW: Payment routes
@app.route('/payment/<plan_type>')
def payment(plan_type):
    """Handle payment for different plans"""
    
    # Define plan details
    plans = {
        'basic': {
            'price': 1000,  # $10.00 in cents
            'name': 'Basic Plan',
            'description': '5 summaries/month'
        },
        'pro': {
            'price': 4900,  # $49.00 in cents
            'name': 'Pro Plan', 
            'description': 'Unlimited summaries + competitor tracking'
        },
        'onetime': {
            'price': 2500,  # $25.00 in cents
            'name': 'One-time Plan',
            'description': 'PDF from up to 3 sources'
        },
        'starter': {
            'price': 49900,  # $499.00 in cents
            'name': 'Starter Plan',
            'description': 'Dashboard + Data cleanup'
        },
        'premium': {
            'price': 99900,  # $999.00 in cents
            'name': 'Premium Plan',
            'description': 'Automation + Forecasting + $100/mo'
        }
    }
    
    if plan_type not in plans:
        return "Invalid plan", 400
    
    try:
        # Create Stripe checkout session
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
            }
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
            # Payment was successful
            return render_template('payment_success.html', 
                                 plan=plan_type, 
                                 session_id=session_id)
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
    app.run(host='0.0.0.0', port=port, debug=False)

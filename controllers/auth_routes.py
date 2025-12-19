from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.db import create_user, find_user_by_email, get_db, find_user_by_phone
from utils.auth import hash_password, check_password, create_session, clear_session
import json
import os
import re

auth_bp = Blueprint('auth', __name__)

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Get database connection
        db = get_db()
        
        # Find user WITH password for authentication
        if hasattr(db, 'users'):
            users = db.users
            user_with_password = users.find_one({'email': email})
        else:
            # Handle mock database
            user_with_password = find_user_by_email(email)
        
        if user_with_password and check_password(password, user_with_password['password']):
            # Create session with user data (excluding password)
            session['user_id'] = str(user_with_password['_id'])
            session['user_name'] = user_with_password['name']
            session['user_email'] = user_with_password['email']
            session['user_phone'] = user_with_password.get('phone', 'Not provided')
            session['user_state'] = user_with_password.get('state', 'Not provided')
            session['user_district'] = user_with_password.get('district', 'Not provided')
            
            flash('🎉 Login successful! Welcome back, ' + user_with_password['name'] + '!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('❌ Invalid email or password. Please try again.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Load states and districts
    try:
        # Try to load from current directory (production)
        if os.path.exists('states_districts.json'):
            with open('states_districts.json', 'r', encoding='utf-8') as f:
                states_districts = json.load(f)
        else:
            # Try to load from script directory (fallback)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(script_dir, '..', 'states_districts.json')
            with open(filepath, 'r', encoding='utf-8') as f:
                states_districts = json.load(f)
    except FileNotFoundError as e:
        print(f"Warning: states_districts.json not found: {e}")
        # Fallback states and districts
        states_districts = {
            "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik"],
            "Karnataka": ["Bangalore", "Mysore", "Mangalore", "Hubli"],
            "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem"]
        }
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        state = request.form['state']
        district = request.form['district']
        
        # Check if user already exists by email
        if find_user_by_email(email):
            flash('⚠️ Email already registered! Please use a different email or login.', 'warning')
            return render_template('register.html', states_districts=states_districts)
        
        # Check if phone number is already registered
        if find_user_by_phone(phone):
            flash('⚠️ Phone number already registered! Please use a different phone number or login.', 'warning')
            return render_template('register.html', states_districts=states_districts)
        
        # Validate password strength
        is_strong, message = validate_password_strength(password)
        if not is_strong:
            flash(f'🔒 {message}', 'warning')
            return render_template('register.html', states_districts=states_districts)
        
        # Hash password and create user
        hashed_password = hash_password(password)
        create_user(name, email, hashed_password, phone, state, district)
        
        flash('✅ Registration successful! Welcome to Smart Farming Assistant. Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', states_districts=states_districts)

@auth_bp.route('/logout')
def logout():
    user_name = session.get('user_name', 'User')
    clear_session()
    flash(f'👋 Goodbye {user_name}! You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.db import create_user, find_user_by_email, get_db
from utils.auth import hash_password, check_password, create_session, clear_session
import json
import os

auth_bp = Blueprint('auth', __name__)

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
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid email or password!', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Load states and districts
    try:
        with open('states_districts.json', 'r') as f:
            states_districts = json.load(f)
    except FileNotFoundError:
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
        
        # Check if user already exists
        if find_user_by_email(email):
            flash('Email already registered!', 'error')
            return render_template('register.html', states_districts=states_districts)
        
        # Hash password and create user
        hashed_password = hash_password(password)
        create_user(name, email, hashed_password, phone, state, district)
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', states_districts=states_districts)

@auth_bp.route('/logout')
def logout():
    clear_session()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

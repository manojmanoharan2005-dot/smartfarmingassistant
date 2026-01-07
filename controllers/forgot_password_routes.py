"""
Forgot Password Routes
Handles password reset flow with OTP verification
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import re
from utils.otp_manager import OTPManager
from utils.sms_gateway import SMSGateway
from functools import wraps
from pymongo import MongoClient
import os

forgot_password_bp = Blueprint('forgot_password', __name__)

# Rate limiting storage (in production, use Redis)
otp_request_tracker = {}

def rate_limit_otp(mobile_number, max_requests=3, time_window_minutes=15):
    """
    Rate limit OTP requests
    Returns (allowed, message)
    """
    now = datetime.utcnow()
    
    if mobile_number in otp_request_tracker:
        requests = otp_request_tracker[mobile_number]
        # Remove old requests outside time window
        requests = [req_time for req_time in requests 
                   if now - req_time < timedelta(minutes=time_window_minutes)]
        
        if len(requests) >= max_requests:
            return False, f"Too many OTP requests. Please try again after {time_window_minutes} minutes."
        
        requests.append(now)
        otp_request_tracker[mobile_number] = requests
    else:
        otp_request_tracker[mobile_number] = [now]
    
    return True, None

def validate_mobile_number(mobile):
    """Validate Indian mobile number format"""
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, mobile) is not None

def validate_password_strength(password):
    """
    Validate password strength
    Returns (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None

@forgot_password_bp.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    """Display forgot password page"""
    return render_template('forgot_password.html')

@forgot_password_bp.route('/api/forgot-password/request-otp', methods=['POST'])
def request_otp():
    """
    Step 1: Request OTP for password reset
    """
    try:
        data = request.get_json()
        mobile_number = data.get('mobile_number', '').strip()
        
        # Validate mobile number format
        if not validate_mobile_number(mobile_number):
            return jsonify({
                'success': False,
                'message': 'Invalid mobile number format'
            }), 400
        
        # Rate limiting
        allowed, rate_limit_msg = rate_limit_otp(mobile_number)
        if not allowed:
            return jsonify({
                'success': False,
                'message': rate_limit_msg
            }), 429
        
        # Get database connection
        from app import get_db
        db = get_db()
        
        # Check if user exists (without revealing existence)
        user = db.users.find_one({'mobile_number': mobile_number})
        
        # Always return success to prevent user enumeration
        # But only send OTP if user exists
        if user:
            # Invalidate any previous OTPs
            OTPManager.invalidate_previous_otps(db, mobile_number)
            
            # Generate new OTP
            otp = OTPManager.generate_otp()
            
            # Create OTP record
            otp_record = OTPManager.create_otp_record(mobile_number, otp)
            
            # Store in database
            db.otps.insert_one(otp_record)
            
            # Send OTP via SMS
            success, sms_message = SMSGateway.send_otp(mobile_number, otp)
            
            if not success:
                return jsonify({
                    'success': False,
                    'message': 'Failed to send OTP. Please try again.'
                }), 500
        
        # Always return success message
        return jsonify({
            'success': True,
            'message': 'If this mobile number is registered, you will receive an OTP shortly.',
            'mobile_number': mobile_number
        }), 200
        
    except Exception as e:
        print(f"Error in request_otp: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500

@forgot_password_bp.route('/verify-otp', methods=['GET'])
def verify_otp_page():
    """Display OTP verification page"""
    mobile_number = request.args.get('mobile')
    if not mobile_number:
        flash('Invalid request', 'error')
        return redirect(url_for('forgot_password.forgot_password_page'))
    
    return render_template('verify_otp.html', mobile_number=mobile_number)

@forgot_password_bp.route('/api/forgot-password/verify-otp', methods=['POST'])
def verify_otp():
    """
    Step 2: Verify OTP
    """
    try:
        data = request.get_json()
        mobile_number = data.get('mobile_number', '').strip()
        otp_entered = data.get('otp', '').strip()
        
        if not mobile_number or not otp_entered:
            return jsonify({
                'success': False,
                'message': 'Mobile number and OTP are required'
            }), 400
        
        # Get database connection
        from app import get_db
        db = get_db()
        
        # Get latest OTP record for this mobile number
        otp_record = db.otps.find_one(
            {'mobile_number': mobile_number, 'used': False},
            sort=[('created_at', -1)]
        )
        
        # Validate OTP record
        is_valid, error_message = OTPManager.is_otp_valid(otp_record)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'message': error_message
            }), 400
        
        # Verify OTP
        if OTPManager.verify_otp(otp_entered, otp_record['otp_hash']):
            # OTP is correct - mark as used
            OTPManager.mark_otp_used(db, mobile_number)
            
            # Create session token for password reset
            session['reset_token'] = mobile_number
            session['reset_token_expiry'] = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
            
            return jsonify({
                'success': True,
                'message': 'OTP verified successfully',
                'redirect_url': url_for('forgot_password.reset_password_page', mobile=mobile_number)
            }), 200
        else:
            # Increment attempts
            OTPManager.increment_attempts(db, mobile_number)
            
            attempts_left = otp_record['max_attempts'] - (otp_record['attempts'] + 1)
            
            return jsonify({
                'success': False,
                'message': f'Invalid OTP. {attempts_left} attempts remaining.'
            }), 400
            
    except Exception as e:
        print(f"Error in verify_otp: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500

@forgot_password_bp.route('/reset-password', methods=['GET'])
def reset_password_page():
    """Display password reset page"""
    mobile_number = request.args.get('mobile')
    
    # Verify session token
    if session.get('reset_token') != mobile_number:
        flash('Invalid or expired session. Please request a new OTP.', 'error')
        return redirect(url_for('forgot_password.forgot_password_page'))
    
    # Check token expiry
    expiry_str = session.get('reset_token_expiry')
    if expiry_str:
        expiry = datetime.fromisoformat(expiry_str)
        if datetime.utcnow() > expiry:
            session.pop('reset_token', None)
            session.pop('reset_token_expiry', None)
            flash('Session expired. Please request a new OTP.', 'error')
            return redirect(url_for('forgot_password.forgot_password_page'))
    
    return render_template('reset_password.html', mobile_number=mobile_number)

@forgot_password_bp.route('/api/forgot-password/reset-password', methods=['POST'])
def reset_password():
    """
    Step 3: Reset password
    """
    try:
        data = request.get_json()
        mobile_number = data.get('mobile_number', '').strip()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Verify session token
        if session.get('reset_token') != mobile_number:
            return jsonify({
                'success': False,
                'message': 'Invalid session. Please request a new OTP.'
            }), 401
        
        # Check passwords match
        if new_password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'Passwords do not match'
            }), 400
        
        # Validate password strength
        is_valid, validation_message = validate_password_strength(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': validation_message
            }), 400
        
        # Get database connection
        from app import get_db
        db = get_db()
        
        # Hash new password
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        
        # Update user password
        result = db.users.update_one(
            {'mobile_number': mobile_number},
            {
                '$set': {
                    'password': hashed_password,
                    'password_updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Clear session
        session.pop('reset_token', None)
        session.pop('reset_token_expiry', None)
        
        # Invalidate all OTPs for this mobile number
        OTPManager.invalidate_previous_otps(db, mobile_number)
        
        return jsonify({
            'success': True,
            'message': 'Password reset successfully. You can now login with your new password.',
            'redirect_url': url_for('auth.login')
        }), 200
        
    except Exception as e:
        print(f"Error in reset_password: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500

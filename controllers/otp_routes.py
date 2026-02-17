"""
OTP Routes for Phone Verification
Handles OTP sending and verification for registration
"""
from flask import Blueprint, request, jsonify
from utils.db import find_user_by_phone
from utils.otp_manager import OTPManager
from utils.sms_gateway import SMSGateway
import os
import re
from datetime import datetime, timedelta

otp_bp = Blueprint('otp', __name__)

# Store OTPs temporarily for registration (in production, use Redis)
registration_otp_store = {}


def is_phone_verified(phone):
    """Check if a phone number has been verified via OTP"""
    if phone in registration_otp_store:
        return registration_otp_store[phone].get('verified', False)
    return False


def clear_phone_verification(phone):
    """Clear verification data after successful registration"""
    if phone in registration_otp_store:
        del registration_otp_store[phone]


@otp_bp.route('/api/register/send-otp', methods=['POST'])
def send_registration_otp():
    """Send OTP for phone verification during registration"""
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        
        # Validate phone number
        if not phone or not re.match(r'^[0-9]{10}$', phone):
            return jsonify({'success': False, 'message': 'Please enter a valid 10-digit phone number'}), 400
        
        # Check if phone is already registered
        if find_user_by_phone(phone):
            return jsonify({'success': False, 'message': 'This phone number is already registered'}), 400
        
        # Check cooldown (30 seconds)
        if phone in registration_otp_store:
            last_sent = registration_otp_store[phone].get('sent_at')
            if last_sent and (datetime.now() - last_sent).total_seconds() < 30:
                remaining = 30 - int((datetime.now() - last_sent).total_seconds())
                return jsonify({'success': False, 'message': f'Please wait {remaining} seconds before requesting another OTP'}), 429
        
        # Generate OTP
        otp = OTPManager.generate_otp()
        
        # Store OTP (expires in 5 minutes)
        registration_otp_store[phone] = {
            'otp': otp,
            'sent_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(minutes=5),
            'attempts': 0,
            'verified': False
        }
        
        # Send OTP via SMS (tries Fast2SMS first, then Twilio)
        sms_success, sms_message = SMSGateway.send_otp(phone, otp)
        
        if sms_success:
            print(f"[Registration OTP] Sent to {phone}")
            return jsonify({'success': True, 'message': 'OTP sent successfully to your phone'})
        else:
            # Fallback: Show OTP in console for development
            print(f"[DEV MODE] Registration OTP for {phone}: {otp}")
            return jsonify({'success': True, 'message': 'OTP sent! (Check console in dev mode)', 'dev_otp': otp if os.getenv('FLASK_ENV') == 'development' else None})
            
    except Exception as e:
        print(f"[Error] send_registration_otp: {e}")
        return jsonify({'success': False, 'message': 'Failed to send OTP. Please try again.'}), 500


@otp_bp.route('/api/register/verify-otp', methods=['POST'])
def verify_registration_otp():
    """Verify OTP for phone verification during registration"""
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        otp = data.get('otp', '').strip()
        
        # Validate inputs
        if not phone or not otp:
            return jsonify({'success': False, 'message': 'Phone number and OTP are required'}), 400
        
        # Check if OTP exists
        if phone not in registration_otp_store:
            return jsonify({'success': False, 'message': 'No OTP found. Please request a new one.'}), 400
        
        otp_data = registration_otp_store[phone]
        
        # Check expiry
        if datetime.now() > otp_data['expires_at']:
            del registration_otp_store[phone]
            return jsonify({'success': False, 'message': 'OTP expired. Please request a new one.'}), 400
        
        # Check attempts
        if otp_data['attempts'] >= 3:
            del registration_otp_store[phone]
            return jsonify({'success': False, 'message': 'Too many failed attempts. Please request a new OTP.'}), 400
        
        # Verify OTP
        if otp_data['otp'] == otp:
            registration_otp_store[phone]['verified'] = True
            return jsonify({'success': True, 'message': 'Phone number verified successfully!'})
        else:
            registration_otp_store[phone]['attempts'] += 1
            remaining = 3 - registration_otp_store[phone]['attempts']
            return jsonify({'success': False, 'message': f'Invalid OTP. {remaining} attempts remaining.'}), 400
            
    except Exception as e:
        print(f"[Error] verify_registration_otp: {e}")
        return jsonify({'success': False, 'message': 'Verification failed. Please try again.'}), 500

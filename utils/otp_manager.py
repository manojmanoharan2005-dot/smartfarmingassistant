"""
OTP Manager for Forgot Password Flow
Handles OTP generation, hashing, validation, and expiry
"""
import random
import string
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os

class OTPManager:
    """Manages OTP lifecycle for password reset"""
    
    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 5
    MAX_ATTEMPTS = 3
    
    @staticmethod
    def generate_otp():
        """Generate a secure 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=OTPManager.OTP_LENGTH))
    
    @staticmethod
    def hash_otp(otp):
        """Hash OTP before storing in database"""
        return generate_password_hash(otp, method='pbkdf2:sha256')
    
    @staticmethod
    def verify_otp(plain_otp, hashed_otp):
        """Verify OTP against hashed version"""
        return check_password_hash(hashed_otp, plain_otp)
    
    @staticmethod
    def create_otp_record(mobile_number, otp):
        """
        Create OTP record for MongoDB
        Returns dict ready for insertion
        """
        return {
            'mobile_number': mobile_number,
            'otp_hash': OTPManager.hash_otp(otp),
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(minutes=OTPManager.OTP_EXPIRY_MINUTES),
            'attempts': 0,
            'used': False,
            'max_attempts': OTPManager.MAX_ATTEMPTS
        }
    
    @staticmethod
    def is_otp_valid(otp_record):
        """
        Check if OTP record is still valid
        Returns (is_valid, error_message)
        """
        if not otp_record:
            return False, "OTP not found"
        
        if otp_record.get('used', False):
            return False, "OTP already used"
        
        if datetime.utcnow() > otp_record.get('expires_at'):
            return False, "OTP expired"
        
        if otp_record.get('attempts', 0) >= otp_record.get('max_attempts', 3):
            return False, "Maximum attempts exceeded"
        
        return True, None
    
    @staticmethod
    def increment_attempts(db, mobile_number):
        """Increment OTP verification attempts"""
        db.otps.update_one(
            {'mobile_number': mobile_number, 'used': False},
            {'$inc': {'attempts': 1}}
        )
    
    @staticmethod
    def mark_otp_used(db, mobile_number):
        """Mark OTP as used after successful verification"""
        db.otps.update_one(
            {'mobile_number': mobile_number, 'used': False},
            {'$set': {'used': True, 'used_at': datetime.utcnow()}}
        )
    
    @staticmethod
    def cleanup_expired_otps(db):
        """Remove expired OTPs from database (maintenance task)"""
        result = db.otps.delete_many({
            'expires_at': {'$lt': datetime.utcnow()}
        })
        return result.deleted_count
    
    @staticmethod
    def invalidate_previous_otps(db, mobile_number):
        """Invalidate all previous OTPs for a mobile number"""
        db.otps.update_many(
            {'mobile_number': mobile_number, 'used': False},
            {'$set': {'used': True, 'invalidated_at': datetime.utcnow()}}
        )

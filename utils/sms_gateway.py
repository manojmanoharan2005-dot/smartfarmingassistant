"""
SMS Gateway Integration for OTP Delivery
Supports Fast2SMS and Twilio
"""
import os
import requests
from typing import Tuple

class SMSGateway:
    """Handle SMS sending via Fast2SMS or Twilio"""
    
    @staticmethod
    def send_otp_fast2sms(mobile_number: str, otp: str) -> Tuple[bool, str]:
        """
        Send OTP via Fast2SMS
        Returns (success, message)
        """
        api_key = os.environ.get('FAST2SMS_API_KEY')
        
        if not api_key:
            return False, "SMS API key not configured"
        
        # Fast2SMS API endpoint
        url = "https://www.fast2sms.com/dev/bulkV2"
        
        # Message template
        message = f"Your Smart Farming Assistant password reset OTP is: {otp}. Valid for 5 minutes. Do not share this OTP."
        
        payload = {
            'authorization': api_key,
            'route': 'v3',
            'sender_id': 'SMRTFM',  # Your sender ID
            'message': message,
            'language': 'english',
            'flash': 0,
            'numbers': mobile_number
        }
        
        try:
            response = requests.post(url, data=payload, timeout=10)
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('return'):
                return True, "OTP sent successfully"
            else:
                error_msg = response_data.get('message', 'Failed to send OTP')
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            return False, f"SMS service error: {str(e)}"
    
    @staticmethod
    def send_otp_twilio(mobile_number: str, otp: str) -> Tuple[bool, str]:
        """
        Send OTP via Twilio
        Returns (success, message)
        """
        try:
            from twilio.rest import Client
        except ImportError:
            return False, "Twilio library not installed. Run: pip install twilio"
        
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        from_number = os.environ.get('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, from_number]):
            return False, "Twilio credentials not configured"
        
        message_body = f"Your Smart Farming Assistant password reset OTP is: {otp}. Valid for 5 minutes. Do not share this OTP."
        
        try:
            client = Client(account_sid, auth_token)
            
            # Ensure mobile number has country code
            if not mobile_number.startswith('+'):
                mobile_number = f"+91{mobile_number}"  # India country code
            
            message = client.messages.create(
                body=message_body,
                from_=from_number,
                to=mobile_number
            )
            
            if message.sid:
                return True, "OTP sent successfully"
            else:
                return False, "Failed to send OTP"
                
        except Exception as e:
            return False, f"Twilio error: {str(e)}"
    
    @staticmethod
    def send_otp(mobile_number: str, otp: str) -> Tuple[bool, str]:
        """
        Send OTP using configured SMS gateway
        Tries Fast2SMS first, falls back to Twilio
        """
        # Validate mobile number format
        if not mobile_number or len(mobile_number) < 10:
            return False, "Invalid mobile number"
        
        # Remove any non-digit characters
        mobile_number = ''.join(filter(str.isdigit, mobile_number))
        
        # Try Fast2SMS first
        if os.environ.get('FAST2SMS_API_KEY'):
            success, message = SMSGateway.send_otp_fast2sms(mobile_number, otp)
            if success:
                return True, message
        
        # Fallback to Twilio
        if os.environ.get('TWILIO_ACCOUNT_SID'):
            return SMSGateway.send_otp_twilio(mobile_number, otp)
        
        # No SMS gateway configured - for development, just log
        print(f"[DEV MODE] OTP for {mobile_number}: {otp}")
        return True, "OTP sent (development mode)"

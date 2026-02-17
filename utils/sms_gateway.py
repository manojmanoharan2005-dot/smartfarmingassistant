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
        Send OTP via Fast2SMS using 'otp' route (DLT-free)
        Returns (success, message)
        """
        api_key = os.environ.get('FAST2SMS_API_KEY')
        
        if not api_key or 'your_' in api_key:
            return False, "Fast2SMS API key not configured"
        
        # Fast2SMS API endpoint
        url = "https://www.fast2sms.com/dev/bulkV2"
        
        # Use 'otp' route which bypasses DLT template scrubbing
        # It sends a default message: "Your OTP is {otp}"
        payload = {
            'authorization': api_key,
            'route': 'otp',
            'variables_values': otp,
            'flash': 0,
            'numbers': mobile_number
        }
        
        headers = {
            'cache-control': "no-cache"
        }
        
        try:
            print(f"[Fast2SMS] Sending OTP to {mobile_number}...")
            response = requests.post(url, data=payload, headers=headers, timeout=10)
            response_data = response.json()
            
            # Log response for debugging
            print(f"[Fast2SMS] Response: {response_data}")
            
            if response.status_code == 200 and response_data.get('return'):
                return True, "OTP sent successfully via SMS"
            else:
                error_msg = response_data.get('message', 'Failed to send OTP')
                print(f"[Fast2SMS Error] {error_msg}")
                return False, f"SMS Provider Error: {error_msg}"
                
        except requests.exceptions.RequestException as e:
            print(f"[Fast2SMS Exceptions] {str(e)}")
            return False, f"SMS Connection Error: {str(e)}"
                
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
        
        message_body = f"Your Smart Farming Assistant OTP is: {otp}. Valid for 5 minutes. Do not share this code."
        
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

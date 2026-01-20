# 🔐 FORGOT PASSWORD SYSTEM - COMPLETE DOCUMENTATION

## 📋 Overview
Production-ready email-based password reset system for the Farming Assistant web application.

---

## 🛠️ Tech Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, Bootstrap Icons
- **Database**: MongoDB Atlas
- **Authentication**: bcrypt (via werkzeug.security)
- **Email Service**: SMTP (Gmail)

---

## 🔄 Complete Flow

### **Step 1: Request Password Reset** (`/forgot-password`)

#### User Actions:
1. User clicks "Forgot Password?" link on login page
2. Enters registered email address
3. Clicks "Send Reset Link"

#### Backend Process:
1. ✅ **Email Validation**: Validates email format using regex
2. ✅ **Rate Limiting**: Max 3 requests per 15 minutes per email
3. ✅ **User Lookup**: Checks if email exists in MongoDB (without revealing)
4. ✅ **Token Generation**: Creates secure 256-bit token using `secrets.token_urlsafe(32)`
5. ✅ **Token Storage**: Stores in MongoDB `password_reset_tokens` collection:
   ```json
   {
     "email": "farmer@email.com",
     "token": "secure_random_token",
     "expiry": "2026-01-20T12:30:00",
     "used": false,
     "created_at": "2026-01-20T12:15:00"
   }
   ```
6. ✅ **Email Sending**: Sends HTML email with reset link via SMTP
7. ✅ **Generic Response**: Always shows success message (prevents user enumeration)

#### Security Features:
- ✅ Email format validation
- ✅ Rate limiting (3 requests / 15 min)
- ✅ No user enumeration (same message for existing/non-existing emails)
- ✅ 15-minute token expiry
- ✅ Secure random token generation

---

### **Step 2: Reset Password** (`/reset-password/<token>`)

#### User Actions:
1. User clicks reset link from email
2. Enters new password
3. Confirms new password
4. Clicks "Reset Password"

#### Backend Process:
1. ✅ **Token Validation**: Checks token exists in MongoDB and is unused
2. ✅ **Expiry Check**: Verifies token hasn't expired (15 minutes)
3. ✅ **Password Match**: Ensures password and confirm password match
4. ✅ **Password Strength**: Validates:
   - Minimum 8 characters
   - At least one uppercase letter (A-Z)
   - At least one lowercase letter (a-z)
   - At least one number (0-9)
   - At least one special character (!@#$%^&*)
5. ✅ **Password Hashing**: Hashes password using bcrypt (pbkdf2:sha256)
6. ✅ **Database Update**: Updates user password in MongoDB
7. ✅ **Token Cleanup**: Marks token as used and deletes old tokens
8. ✅ **Redirect**: Redirects to login page with success message

#### Security Features:
- ✅ Token expiration (15 minutes)
- ✅ One-time token usage
- ✅ Strong password enforcement
- ✅ bcrypt password hashing
- ✅ Automatic cleanup of old/used tokens

---

## 📁 File Structure

```
smartfarmingassitant/
├── controllers/
│   └── auth_routes.py              # Main authentication routes
├── templates/
│   ├── login.html                  # Login page with "Forgot Password?" link
│   ├── forgot_password.html        # Email input page
│   └── reset_password.html         # New password form
└── utils/
    ├── db.py                       # MongoDB connection & user functions
    └── auth.py                     # Password hashing utilities
```

---

## 🗄️ MongoDB Schema

### Users Collection
```json
{
  "_id": ObjectId("..."),
  "name": "Farmer Name",
  "email": "farmer@email.com",
  "password": "$pbkdf2-sha256$...",  // bcrypt hashed
  "phone": "9876543210",
  "state": "Maharashtra",
  "district": "Pune",
  "created_at": "2026-01-20T10:00:00"
}
```

### Password Reset Tokens Collection
```json
{
  "_id": ObjectId("..."),
  "email": "farmer@email.com",
  "token": "secure_random_token_32_bytes",
  "expiry": "2026-01-20T12:30:00",
  "used": false,
  "created_at": "2026-01-20T12:15:00",
  "used_at": null  // Set when token is used
}
```

---

## 📧 Email Configuration

### Environment Variables Required:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Gmail App Password, not regular password
```

### Gmail App Password Setup:
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Go to "App passwords"
4. Generate password for "Mail"
5. Use this password in `SMTP_PASSWORD`

### Email Template Features:
- ✅ Farmer-friendly green theme
- ✅ Responsive HTML design
- ✅ Large "Reset Password" button
- ✅ Security notice (15-min expiry)
- ✅ Alternative link for button failures
- ✅ Plain text fallback

---

## 🔒 Security Features

### 1. **Rate Limiting**
```python
# Max 3 reset requests per 15 minutes per email
rate_limit_reset_request(email, max_requests=3, time_window_minutes=15)
```

### 2. **Token Security**
- 256-bit secure random tokens
- 15-minute expiration
- One-time use only
- Stored in MongoDB (not in-memory)

### 3. **Password Validation**
```python
def validate_password_strength(password):
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
```

### 4. **User Enumeration Prevention**
- Same success message for existing/non-existing emails
- No indication if email is registered

### 5. **CSRF Protection**
- Flask's built-in session management
- Secure token validation

---

## 🎨 UI Features

### Forgot Password Page:
- ✅ Clean, farmer-friendly design
- ✅ Green agriculture theme
- ✅ Large input fields (touch-friendly)
- ✅ Email validation
- ✅ Security notice about expiry
- ✅ "Back to Login" link

### Reset Password Page:
- ✅ Password strength indicator
- ✅ Show/hide password toggle
- ✅ Real-time strength feedback
- ✅ Password requirements list
- ✅ Confirm password field
- ✅ Client-side validation

---

## 🧪 Testing Guide

### Test Scenario 1: Successful Password Reset
1. Go to `/login`
2. Click "Forgot Password?"
3. Enter registered email
4. Check email inbox for reset link
5. Click reset link
6. Enter new strong password
7. Confirm password
8. Click "Reset Password"
9. Login with new password

### Test Scenario 2: Non-Existent Email
1. Enter non-registered email
2. Should show same success message
3. No email should be sent

### Test Scenario 3: Expired Token
1. Request reset link
2. Wait 16 minutes
3. Click reset link
4. Should show "expired" error

### Test Scenario 4: Rate Limiting
1. Request reset 3 times quickly
2. 4th request should be blocked
3. Wait 15 minutes
4. Should work again

### Test Scenario 5: Weak Password
1. Try password: "weak"
2. Should show validation error
3. Try password: "StrongPass123!"
4. Should succeed

---

## 🐛 Error Handling

### Common Errors & Solutions:

**1. Email Not Sent**
```
Error: Email service not configured
Solution: Set SMTP_EMAIL and SMTP_PASSWORD environment variables
Dev Mode: Reset link printed in console
```

**2. Token Not Found**
```
Error: Invalid or expired reset link
Solution: Request new reset link
```

**3. Rate Limit Exceeded**
```
Error: Too many reset requests
Solution: Wait 15 minutes before trying again
```

**4. Password Too Weak**
```
Error: Password must contain uppercase, lowercase, number, special char
Solution: Create stronger password
```

---

## 📊 Monitoring & Logs

### Console Logs:
```python
[SUCCESS] Password reset email sent to farmer@email.com
[WARNING] Email not configured. Please set SMTP_EMAIL and SMTP_PASSWORD
[DEV MODE] Reset link: http://localhost:5000/reset-password/token123
[ERROR] Failed to create reset token: <error details>
[ERROR] Failed to reset password: <error details>
```

### MongoDB Queries for Monitoring:
```javascript
// Check active reset tokens
db.password_reset_tokens.find({ used: false, expiry: { $gt: new Date() } })

// Check expired tokens
db.password_reset_tokens.find({ expiry: { $lt: new Date() } })

// Clean up old tokens (run periodically)
db.password_reset_tokens.deleteMany({
  $or: [
    { expiry: { $lt: new Date() } },
    { used: true }
  ]
})
```

---

## 🚀 Deployment Checklist

- [ ] Set SMTP_EMAIL environment variable
- [ ] Set SMTP_PASSWORD environment variable (Gmail App Password)
- [ ] Test email sending in production
- [ ] Verify MongoDB connection
- [ ] Test rate limiting
- [ ] Test token expiration
- [ ] Test password validation
- [ ] Enable HTTPS for secure token transmission
- [ ] Set up automated token cleanup (cron job)
- [ ] Monitor email delivery rates
- [ ] Set up error logging/monitoring

---

## 🔧 Maintenance

### Periodic Tasks:

**1. Clean Up Old Tokens (Daily)**
```python
# Add to scheduled task
db.password_reset_tokens.delete_many({
    '$or': [
        {'expiry': {'$lt': datetime.now()}},
        {'used': True, 'used_at': {'$lt': datetime.now() - timedelta(days=7)}}
    ]
})
```

**2. Monitor Email Delivery**
- Check SMTP logs
- Monitor bounce rates
- Update email templates if needed

**3. Review Security**
- Check rate limiting effectiveness
- Review failed reset attempts
- Update password requirements if needed

---

## 📝 Code Comments

All code includes comprehensive comments explaining:
- Function purpose
- Security considerations
- Error handling
- Flow logic

---

## ✅ Production-Ready Features

- ✅ MongoDB token storage (not in-memory)
- ✅ Rate limiting
- ✅ Email validation
- ✅ Password strength enforcement
- ✅ Token expiration
- ✅ One-time token usage
- ✅ User enumeration prevention
- ✅ CSRF protection
- ✅ Comprehensive error handling
- ✅ Farmer-friendly UI
- ✅ Mobile responsive
- ✅ Email HTML template
- ✅ Security notices
- ✅ Logging and monitoring

---

## 📞 Support

For issues or questions:
1. Check console logs for errors
2. Verify environment variables
3. Test email configuration
4. Check MongoDB connection
5. Review this documentation

---

**Last Updated**: January 20, 2026  
**Status**: ✅ Production Ready

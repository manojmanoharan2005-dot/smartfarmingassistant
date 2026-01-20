# 🚀 QUICK START GUIDE - Forgot Password Feature

## ⚡ 3-Minute Setup

### Step 1: Configure Email (2 minutes)
```powershell
# Set these environment variables
$env:SMTP_EMAIL="your-email@gmail.com"
$env:SMTP_PASSWORD="your-gmail-app-password"
```

**Need App Password?** See [EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md)

### Step 2: Restart Flask (30 seconds)
```bash
# Stop current server (Ctrl+C)
# Start again
python app.py
```

### Step 3: Test It! (30 seconds)
1. Go to: http://localhost:5000/login
2. Click "Forgot password?"
3. Enter your email
4. Check your inbox
5. Click reset link
6. Set new password
7. Login! ✅

---

## 📋 What You Get

✅ **Email-based password reset** (not SMS)  
✅ **15-minute secure tokens**  
✅ **Rate limiting** (3 requests / 15 min)  
✅ **Beautiful farmer-friendly UI**  
✅ **Professional email templates**  
✅ **MongoDB token storage**  
✅ **Production-ready security**  

---

## 🔍 Files to Know

| File | Purpose |
|------|---------|
| `controllers/auth_routes.py` | Backend logic |
| `templates/forgot_password.html` | Email input page |
| `templates/reset_password.html` | Password reset form |
| `FORGOT_PASSWORD_DOCUMENTATION.md` | Full documentation |
| `EMAIL_SETUP_GUIDE.md` | Email setup help |

---

## 🐛 Troubleshooting

**Email not sending?**
- Check environment variables are set
- Restart Flask after setting variables
- Check console for reset link (dev mode)

**Token expired?**
- Tokens expire in 15 minutes
- Request a new reset link

**Password rejected?**
- Must be 8+ characters
- Need uppercase, lowercase, number, special char

---

## 📚 Full Documentation

For complete details, see:
- **[FORGOT_PASSWORD_DOCUMENTATION.md](FORGOT_PASSWORD_DOCUMENTATION.md)** - Complete system docs
- **[EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md)** - Gmail SMTP setup
- **[FORGOT_PASSWORD_DELIVERY.md](FORGOT_PASSWORD_DELIVERY.md)** - What was built

---

## ✅ Quick Test Checklist

- [ ] Environment variables set
- [ ] Flask restarted
- [ ] Can access /forgot-password
- [ ] Email received
- [ ] Reset link works
- [ ] New password accepted
- [ ] Can login with new password

---

**Status**: ✅ Production-Ready  
**Time to Setup**: ~3 minutes  
**Security Level**: Enterprise-grade

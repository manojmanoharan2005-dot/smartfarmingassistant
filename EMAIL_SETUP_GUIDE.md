# 📧 EMAIL SETUP GUIDE - GMAIL SMTP

## Quick Setup (5 Minutes)

### Step 1: Enable 2-Step Verification
1. Go to https://myaccount.google.com/security
2. Click "2-Step Verification"
3. Follow the setup process

### Step 2: Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" as the app
3. Select "Windows Computer" (or your device)
4. Click "Generate"
5. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

### Step 3: Set Environment Variables

#### Windows (PowerShell):
```powershell
$env:SMTP_EMAIL="your-email@gmail.com"
$env:SMTP_PASSWORD="your-16-char-app-password"
```

#### Windows (Command Prompt):
```cmd
set SMTP_EMAIL=your-email@gmail.com
set SMTP_PASSWORD=your-16-char-app-password
```

#### Linux/Mac:
```bash
export SMTP_EMAIL="your-email@gmail.com"
export SMTP_PASSWORD="your-16-char-app-password"
```

#### Permanent Setup (Windows):
1. Search "Environment Variables" in Windows
2. Click "Environment Variables" button
3. Under "User variables", click "New"
4. Add:
   - Variable name: `SMTP_EMAIL`
   - Variable value: `your-email@gmail.com`
5. Click "New" again
6. Add:
   - Variable name: `SMTP_PASSWORD`
   - Variable value: `your-16-char-app-password`
7. Click "OK" to save
8. **Restart your terminal/IDE**

### Step 4: Test Email Sending

Run your Flask app and test the forgot password feature:
```bash
python app.py
```

Visit: http://localhost:5000/forgot-password

---

## 🔧 Troubleshooting

### Error: "Username and Password not accepted"
**Solution**: Make sure you're using the **App Password**, not your regular Gmail password

### Error: "Email not configured"
**Solution**: Environment variables not set. Follow Step 3 again and restart terminal

### Email Not Received
**Possible Causes**:
1. Check spam/junk folder
2. Verify email address is correct
3. Check Gmail "Sent" folder to confirm email was sent
4. Try different email provider (not Gmail)

### Error: "SMTPAuthenticationError"
**Solution**: 
1. Regenerate App Password
2. Make sure 2-Step Verification is enabled
3. Use the exact 16-character password (no spaces)

---

## 🎯 Quick Test

1. Set environment variables
2. Restart terminal
3. Run: `python app.py`
4. Go to: http://localhost:5000/forgot-password
5. Enter your email
6. Check your inbox

---

## 📝 Notes

- **App Password** is different from your regular Gmail password
- App Password is 16 characters (4 groups of 4)
- Remove spaces when copying App Password
- Environment variables must be set before starting Flask
- For production, use environment variable management (e.g., `.env` file with python-dotenv)

---

## 🚀 Production Deployment

For production, use secure environment variable management:

1. **Heroku**: Use Config Vars in dashboard
2. **AWS**: Use AWS Secrets Manager
3. **Docker**: Use docker-compose environment variables
4. **VPS**: Use systemd environment files

**Never commit SMTP credentials to Git!**

---

## ✅ Verification Checklist

- [ ] 2-Step Verification enabled on Gmail
- [ ] App Password generated
- [ ] SMTP_EMAIL environment variable set
- [ ] SMTP_PASSWORD environment variable set
- [ ] Terminal restarted
- [ ] Flask app restarted
- [ ] Test email sent successfully
- [ ] Email received in inbox

---

**Need Help?** Check console logs for detailed error messages.

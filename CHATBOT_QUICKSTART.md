# 🚀 Quick Start: Gemini AI Chatbot

Your chatbot is now powered by **Google Gemini AI** instead of pattern matching!

## ⚡ Super Quick Setup (2 Minutes)

### 1️⃣ Install Gemini Package
```powershell
pip install google-generativeai
```

### 2️⃣ Get FREE API Key
Visit: **https://makersuite.google.com/app/apikey**
- Click "Create API Key"
- Copy the key (starts with `AIzaSy...`)

### 3️⃣ Add Your API Key

**Option A: Environment Variable (Recommended)**
```powershell
# Create .env file
copy .env.example .env

# Open .env and paste your key:
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Option B: Direct in Code**
Open `controllers/chat_routes.py` line 9, replace:
```python
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')
```

### 4️⃣ Test It!
```powershell
# Start your app
python app.py

# Visit test endpoint
http://localhost:5000/chat/test

# Or just use the chatbot!
# Click "🤖 Ask AI Assistant" in dashboard
```

## 🎉 What's New?

| Before | After |
|--------|-------|
| ❌ Pattern matching | ✅ Real AI (Gemini) |
| ❌ Fixed responses | ✅ Intelligent answers |
| ❌ Limited knowledge | ✅ Context-aware |
| ❌ No follow-ups | ✅ Conversations |

## 🎯 Try These Questions

- "How do I check my soil's NPK levels?"
- "What crops grow well in high humidity?"
- "Explain the expense calculator features"
- "How do I detect plant diseases?"
- "Tell me about PM-KISAN scheme"

## 🆓 Completely Free!

Gemini API Free Tier:
- ✅ 60 requests/minute
- ✅ 1,500 requests/day
- ✅ No credit card needed

## 📂 Files Changed

- ✅ `controllers/chat_routes.py` - New Gemini API backend
- ✅ `templates/dashboard.html` - Updated to call API
- ✅ `app.py` - Registered chat routes
- ✅ `requirements.txt` - Added google-generativeai
- ✅ `.env.example` - API key template
- ✅ `.gitignore` - Protects your API key

## 🔒 Security

Your API key is protected:
- ✅ Stored in `.env` (not committed to Git)
- ✅ `.gitignore` excludes `.env` files
- ✅ Only accessible server-side

## 🐛 Troubleshooting

**"Please configure your Gemini API key"**
→ Add key to `.env` or `chat_routes.py`

**"Module 'google.generativeai' not found"**
→ Run: `pip install google-generativeai`

**Chatbot not responding**
→ Check browser console (F12) for errors
→ Make sure you're logged in
→ Verify Flask server is running

**"API key not valid"**
→ Get new key from https://makersuite.google.com/app/apikey

## 💡 Pro Tips

1. **Test First**: Visit `/chat/test` to verify setup
2. **Use .env**: Safer than hardcoding API key
3. **Check Logs**: Flask console shows detailed errors
4. **Browser Console**: Press F12 to see frontend errors

## 📖 Full Documentation

For complete guide, see: `GEMINI_CHATBOT_SETUP.md`

## 🎊 You're All Set!

Your Smart Farming chatbot is now AI-powered! 

Start your Flask app and click **"🤖 Ask AI Assistant"** to try it out!

---

**Need Help?**
1. Check browser console (F12)
2. Check Flask server terminal
3. Visit: https://ai.google.dev/docs

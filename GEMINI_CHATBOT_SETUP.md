# 🤖 Gemini AI Chatbot Setup Guide

## Quick Setup (3 Steps)

### Step 1: Get Your Gemini API Key (FREE)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key" or "Create API Key"
3. Copy your API key (looks like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX`)

### Step 2: Configure API Key

**Option A: Using Environment Variable (Recommended)**
1. Create a `.env` file in the `smartfarming` folder:
   ```bash
   copy .env.example .env
   ```
2. Open `.env` and paste your API key:
   ```
   GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

**Option B: Direct Configuration**
1. Open `controllers/chat_routes.py`
2. Find line 8:
   ```python
   GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY_HERE')
   ```
3. Replace `'YOUR_GEMINI_API_KEY_HERE'` with your actual key:
   ```python
   GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX')
   ```

### Step 3: Install Gemini Library
```bash
pip install google-generativeai
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Testing Your Setup

1. Start your Flask app:
   ```bash
   python app.py
   ```

2. Test the API endpoint:
   - Visit: `http://localhost:5000/chat/test`
   - Should see: `"Gemini API is configured correctly!"`

3. Test the chatbot:
   - Login to your dashboard
   - Click "🤖 Ask AI Assistant" button
   - Type a message and see Gemini respond!

## Features

✅ **Real AI Responses** - Powered by Google's Gemini AI  
✅ **Context-Aware** - Remembers last 5 messages in conversation  
✅ **Farming Expertise** - Pre-trained with your platform knowledge  
✅ **Smart & Helpful** - Provides step-by-step guidance  
✅ **Free Tier** - 60 requests per minute (plenty for most users)  

## Troubleshooting

### Error: "Please configure your Gemini API key"
- Make sure your API key is set in `.env` or `chat_routes.py`
- Restart your Flask server after adding the key

### Error: "API key not valid"
- Check that you copied the full API key
- Generate a new key from Google AI Studio

### Error: "Module 'google.generativeai' not found"
- Run: `pip install google-generativeai`

### Chatbot not responding
- Check browser console (F12) for errors
- Verify Flask server is running
- Make sure you're logged in

## API Key Security

⚠️ **IMPORTANT**: Never commit your `.env` file to Git!

The `.gitignore` should include:
```
.env
*.env
```

## Cost & Limits

Gemini API Free Tier:
- ✅ 60 requests per minute
- ✅ 1,500 requests per day
- ✅ Completely FREE for personal/small projects

For production with many users, consider:
- Google Cloud paid tier (very affordable)
- Rate limiting per user
- Caching common responses

## Support

If you need help:
1. Check the error message in browser console (F12)
2. Check Flask server logs in terminal
3. Test the `/chat/test` endpoint
4. Review [Gemini API Documentation](https://ai.google.dev/docs)

## What Changed?

**Before**: Pattern-matching chatbot with pre-written responses  
**After**: Real AI chatbot using Google Gemini

The chatbot now:
- Understands natural language better
- Gives contextual, intelligent responses
- Can answer follow-up questions
- Provides personalized farming advice
- Remembers conversation history

Enjoy your AI-powered farming assistant! 🌾🤖

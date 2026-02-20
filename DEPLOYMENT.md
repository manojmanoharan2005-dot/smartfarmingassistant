# Smart Farming Assistant - Deployment Guide

This guide covers deploying the Smart Farming Assistant to both **Vercel** and **Render**.

## 📋 Prerequisites

Before deploying, ensure you have:
- A GitHub account (recommended for both platforms)
- Your code pushed to a GitHub repository
- MongoDB Atlas account (for database)
- Google API key (for AI chatbot feature)
- Twilio account (for SMS/OTP features) - Optional

---

## 🚀 Option 1: Deploy to Render (Recommended for Full Features)

Render is better suited for this application as it supports:
- Background workers and scheduled tasks
- File uploads with persistent storage
- Full PostgreSQL/MongoDB support
- Longer request timeouts for ML model predictions

### Steps to Deploy on Render:

1. **Sign up for Render**
   - Go to [render.com](https://render.com)
   - Sign up or log in with GitHub

2. **Create a New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your `smartfarmingassistant` repository

3. **Configure the Service**
   - **Name**: `smart-farming-assistant` (or your choice)
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

4. **Set Environment Variables**
   Go to "Environment" tab and add:
   ```
   FLASK_ENV=production
   SECRET_KEY=your-strong-secret-key-here
   MONGODB_URI=your-mongodb-atlas-connection-string
   GOOGLE_API_KEY=your-google-api-key
   TWILIO_ACCOUNT_SID=your-twilio-sid (optional)
   TWILIO_AUTH_TOKEN=your-twilio-token (optional)
   TWILIO_PHONE_NUMBER=your-twilio-number (optional)
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - You'll get a URL like: `https://smart-farming-assistant.onrender.com`

6. **Set Up MongoDB Atlas** (if not done)
   - Go to [mongodb.com/atlas](https://www.mongodb.com/atlas)
   - Create a free cluster
   - Get your connection string
   - Add it to Render environment variables as `MONGODB_URI`
   - Whitelist Render's IP (or use 0.0.0.0/0 for all IPs)

---

## ⚡ Option 2: Deploy to Vercel (Serverless)

Vercel is great for quick deployments but has limitations:
- 10-second timeout for serverless functions (may affect ML model inference)
- No persistent file system (uploads won't persist)
- No background workers/schedulers

### Steps to Deploy on Vercel:

1. **Install Vercel CLI** (Optional)
   ```bash
   npm install -g vercel
   ```

2. **Sign up for Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub

3. **Import Your Project**
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect it's a Python app

4. **Configure Environment Variables**
   In the project settings, add:
   ```
   FLASK_ENV=production
   SECRET_KEY=your-strong-secret-key-here
   MONGODB_URI=your-mongodb-atlas-connection-string
   GOOGLE_API_KEY=your-google-api-key
   TWILIO_ACCOUNT_SID=your-twilio-sid (optional)
   TWILIO_AUTH_TOKEN=your-twilio-token (optional)
   TWILIO_PHONE_NUMBER=your-twilio-number (optional)
   ```

5. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - You'll get a URL like: `https://your-project.vercel.app`

### Deploy from CLI (Alternative):
```bash
cd smartfarmingassistant
vercel
# Follow the prompts
# Add environment variables when asked or add them in dashboard
```

---

## 🗄️ Database Setup (MongoDB Atlas)

Both platforms need a cloud database:

1. **Create MongoDB Atlas Account**
   - Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
   - Sign up for free

2. **Create a Cluster**
   - Choose free tier (M0)
   - Select a region close to your deployment

3. **Create Database User**
   - Go to "Database Access"
   - Add new user with password
   - Remember credentials

4. **Network Access**
   - Go to "Network Access"
   - Add IP: `0.0.0.0/0` (allow from anywhere)
   - Or add specific IPs from Render/Vercel

5. **Get Connection String**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your actual password
   - Format: `mongodb+srv://username:password@cluster.mongodb.net/smartfarming?retryWrites=true&w=majority`

---

## 🔑 Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `FLASK_ENV` | Flask environment | Yes | `production` |
| `SECRET_KEY` | Flask secret key | Yes | `your-random-secret-key-123` |
| `MONGODB_URI` | MongoDB connection string | Yes | `mongodb+srv://user:pass@cluster...` |
| `GOOGLE_API_KEY` | Google Gemini API key for chatbot | Yes | `AIza...` |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID for SMS | Optional | `AC...` |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | Optional | `...` |
| `TWILIO_PHONE_NUMBER` | Twilio phone number | Optional | `+1234567890` |
| `PORT` | Server port (auto-set by platforms) | No | `5000` |

---

## 🧪 Testing Your Deployment

After deployment:

1. **Visit your URL**
   - Render: `https://your-app.onrender.com`
   - Vercel: `https://your-app.vercel.app`

2. **Test Key Features**
   - ✅ Homepage loads
   - ✅ User registration/login works
   - ✅ Dashboard accessible
   - ✅ Crop recommendation works
   - ✅ Market prices load
   - ✅ AI chatbot responds

3. **Check Logs**
   - **Render**: View logs in dashboard
   - **Vercel**: Check "Functions" tab for serverless logs

---

## 🐛 Common Issues & Solutions

### Issue: "Application error" on first load
**Solution**: Check logs for missing environment variables

### Issue: MongoDB connection fails
**Solution**: 
- Verify connection string
- Check IP whitelist in MongoDB Atlas
- Ensure username/password are correct

### Issue: ML models not loading
**Solution**: 
- Ensure `ml_models/` and `datasets/` are in repository
- Check file paths are relative, not absolute
- On Vercel, models may timeout (use Render instead)

### Issue: File uploads not persisting (Vercel)
**Solution**: Vercel has ephemeral storage. Use Render or add cloud storage (AWS S3, Cloudinary)

### Issue: Scheduler not running (Vercel)
**Solution**: Vercel doesn't support background tasks. Use Render or separate cron service

---

## 📊 Platform Comparison

| Feature | Render | Vercel |
|---------|--------|--------|
| **Best For** | Full web apps with workers | Static sites, APIs |
| **Timeout** | Up to 120s | 10s (serverless) |
| **File Storage** | Persistent | Ephemeral |
| **Background Jobs** | Yes (schedulers work) | No |
| **Cost** | Free tier available | Free tier available |
| **ML Models** | ✅ Suitable | ⚠️ May timeout |
| **Database** | All supported | All supported |
| **Auto-deploy** | ✅ Yes | ✅ Yes |

**Recommendation**: Use **Render** for this project due to ML models, schedulers, and file uploads.

---

## 🔄 Continuous Deployment

Both platforms support auto-deployment:
- Push to your GitHub repository
- Platform automatically detects changes
- Rebuilds and redeploys automatically

---

## 📞 Support Resources

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **MongoDB Atlas**: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)

---

## ✅ Quick Start Checklist

- [ ] Push code to GitHub
- [ ] Create MongoDB Atlas cluster
- [ ] Get Google API key
- [ ] Choose platform (Render recommended)
- [ ] Create new web service
- [ ] Set environment variables
- [ ] Deploy and test
- [ ] Monitor logs for errors

---

**Good luck with your deployment! 🚀🌱**

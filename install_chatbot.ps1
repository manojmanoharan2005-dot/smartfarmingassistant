# Gemini Chatbot Installation Script
# Run this after getting your API key from https://makersuite.google.com/app/apikey

Write-Host "🤖 Installing Gemini AI Chatbot Dependencies..." -ForegroundColor Cyan
Write-Host ""

# Install google-generativeai
Write-Host "📦 Installing google-generativeai package..." -ForegroundColor Yellow
pip install google-generativeai

Write-Host ""
Write-Host "✅ Installation Complete!" -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (Test-Path ".env") {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "📝 Please edit .env and add your Gemini API key" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Get your FREE Gemini API key from: https://makersuite.google.com/app/apikey" -ForegroundColor White
Write-Host "2. Open .env file and paste your API key" -ForegroundColor White
Write-Host "3. Run: python app.py" -ForegroundColor White
Write-Host "4. Click '🤖 Ask AI Assistant' button in dashboard" -ForegroundColor White
Write-Host ""
Write-Host "📖 For detailed setup guide, see: GEMINI_CHATBOT_SETUP.md" -ForegroundColor Magenta
Write-Host ""

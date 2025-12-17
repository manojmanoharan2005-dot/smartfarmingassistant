# Smart Farming Fertilizer System - Quick Start Script
# Starts both backend API and frontend servers

Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  Smart Farming Fertilizer Recommendation System" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ScriptDir "backend"

# Check if backend directory exists
if (-not (Test-Path $BackendDir)) {
    Write-Host "Error: backend directory not found!" -ForegroundColor Red
    Write-Host "Expected location: $BackendDir" -ForegroundColor Red
    exit 1
}

Write-Host "Starting Backend API Server..." -ForegroundColor Cyan
Write-Host "Location: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""

# Start backend in a new window
$BackendScript = @"
Set-Location '$ScriptDir'
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $BackendScript

Write-Host "Waiting for backend to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Starting Flask Frontend Server..." -ForegroundColor Cyan
Write-Host "Location: http://localhost:5000" -ForegroundColor Yellow
Write-Host ""

# Start frontend in a new window
$FrontendScript = @"
Set-Location '$ScriptDir'
python app.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $FrontendScript

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  System is running!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application at: http://localhost:5000" -ForegroundColor Yellow
Write-Host "API documentation at: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Close the PowerShell windows to stop the servers." -ForegroundColor Cyan
Write-Host ""

# AI Onboarding Chatbot - Simple Startup Script
# Environment variables are automatically loaded from .env by python-dotenv

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Onboarding Chatbot" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "The application will look for HF_TOKEN in environment variables." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Starting Streamlit application..." -ForegroundColor Green
Write-Host "Environment variables will be loaded automatically from .env" -ForegroundColor Gray
Write-Host ""
Write-Host "The application will open in your browser." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

# Run Streamlit app using python module to ensure correct environment
python -m streamlit run app.py

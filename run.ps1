# AI Onboarding Chatbot - Startup Script
# This script loads environment variables and starts the Streamlit application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Onboarding Chatbot - Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please create a .env file with your HF_TOKEN" -ForegroundColor Yellow
    Write-Host "You can copy .env.example to .env and update it" -ForegroundColor Yellow
    exit 1
}

# Load environment variables from .env file
Write-Host "Loading environment variables from .env..." -ForegroundColor Yellow
$envLoaded = $false
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($name, $value, 'Process')
        Write-Host "  Set $name" -ForegroundColor Green
        $envLoaded = $true
    }
}

if (-Not $envLoaded) {
    Write-Host "WARNING: No environment variables loaded from .env" -ForegroundColor Yellow
}

Write-Host ""

# Run system check
Write-Host "Running system checks..." -ForegroundColor Yellow
python check_system.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERROR: System checks failed!" -ForegroundColor Red
    Write-Host "Please fix the issues above before running the application." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Streamlit Application..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The application will open in your browser." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

# Run Streamlit app
streamlit run app.py

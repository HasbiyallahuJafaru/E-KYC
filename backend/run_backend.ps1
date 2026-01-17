# E-KYC Backend Startup Script
# This script activates the virtual environment and runs the backend server

Write-Host "=== E-KYC Backend Startup ===" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "$PSScriptRoot\venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0 -and -not $?) {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (-not (Test-Path "$PSScriptRoot\.env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating default .env file..." -ForegroundColor Yellow
    Copy-Item "$PSScriptRoot\.env.example" "$PSScriptRoot\.env" -ErrorAction SilentlyContinue
}

# Start the server
Write-Host "Starting FastAPI server..." -ForegroundColor Cyan
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

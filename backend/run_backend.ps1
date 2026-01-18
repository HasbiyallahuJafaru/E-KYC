# E-KYC Backend Startup Script
# This script runs the backend server from the correct directory

Write-Host "=== E-KYC Backend Startup ===" -ForegroundColor Green
Write-Host ""

# Ensure we're in the backend directory
Set-Location $PSScriptRoot

# Path to virtual environment (one level up)
$venvPath = Join-Path $PSScriptRoot ".." ".venv"
$pythonExe = Join-Path $venvPath "Scripts" "python.exe"

# Check if Python executable exists
if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR: Virtual environment not found at $venvPath" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "Using Python: $pythonExe" -ForegroundColor Cyan
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

# Run uvicorn from the backend directory
& $pythonExe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

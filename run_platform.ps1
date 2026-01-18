# Complete E-KYC Platform Startup Script
# Runs both backend and frontend

Write-Host "=== E-KYC Complete Platform Startup ===" -ForegroundColor Green
Write-Host ""

# Function to test if port is in use
function Test-Port {
    param($Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
    return $connection
}

# Check if backend is running
$backendRunning = Test-Port -Port 8000
$frontendRunning = Test-Port -Port 5173

if ($backendRunning) {
    Write-Host "✓ Backend already running on port 8000" -ForegroundColor Green
} else {
    Write-Host "Starting backend server..." -ForegroundColor Cyan
    $backendPath = Join-Path $PSScriptRoot "backend"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$backendPath`"; .\run_backend.ps1"
    Write-Host "✓ Backend starting on port 8000" -ForegroundColor Green
    Start-Sleep -Seconds 3
}

if ($frontendRunning) {
    Write-Host "✓ Frontend already running on port 5173" -ForegroundColor Green
} else {
    Write-Host "Starting frontend server..." -ForegroundColor Cyan
    $frontendPath = Join-Path $PSScriptRoot "frontend"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$frontendPath`"; .\run_frontend.ps1"
    Write-Host "✓ Frontend starting on port 5173" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== E-KYC Platform Ready ===" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API:      http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs:         http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Frontend App:     http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "To create an API key for testing:" -ForegroundColor Yellow
Write-Host "  cd backend" -ForegroundColor Gray
Write-Host "  python scripts\create_test_client.py" -ForegroundColor Gray
Write-Host ""
Write-Host "Then update frontend/.env with the API key" -ForegroundColor Yellow
Write-Host ""

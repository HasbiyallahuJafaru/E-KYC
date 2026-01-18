# Simple One-Command Startup for E-KYC Platform
# Usage: .\start.ps1

Write-Host "=== Starting E-KYC Platform ===" -ForegroundColor Green
Write-Host ""

# Kill any existing Python processes on port 8000
$backendProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -ErrorAction SilentlyContinue
if ($backendProcess) {
    Write-Host "Stopping existing backend process..." -ForegroundColor Yellow
    Stop-Process -Id $backendProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Kill any existing Node processes on port 5173
$frontendProcess = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -ErrorAction SilentlyContinue
if ($frontendProcess) {
    Write-Host "Stopping existing frontend process..." -ForegroundColor Yellow
    Stop-Process -Id $frontendProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Define paths
$rootDir = $PSScriptRoot
$backendDir = Join-Path $rootDir "backend"
$frontendDir = Join-Path $rootDir "frontend"
$venvDir = Join-Path $rootDir ".venv"
$pythonExe = Join-Path (Join-Path $venvDir "Scripts") "python.exe"

# Start Backend
Write-Host "Starting backend server..." -ForegroundColor Cyan
$backendCmd = "cd '$backendDir'; & '$pythonExe' -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $backendCmd
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting frontend server..." -ForegroundColor Cyan
$frontendCmd = "cd '$frontendDir'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $frontendCmd

Write-Host ""
Write-Host "=== Platform Started ===" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Docs:     http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Two PowerShell windows have opened - DO NOT CLOSE THEM" -ForegroundColor Yellow
Write-Host "To stop: Close both PowerShell windows or press Ctrl+C in each" -ForegroundColor Yellow
Write-Host ""

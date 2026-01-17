# E-KYC Frontend Installation and Run Script

Write-Host "=== E-KYC Frontend Setup ===" -ForegroundColor Green
Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "$PSScriptRoot\node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    npm install
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Dependencies installed successfully!" -ForegroundColor Green
    Write-Host ""
}

# Check if .env exists
if (-not (Test-Path "$PSScriptRoot\.env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating default .env file..." -ForegroundColor Yellow
    Copy-Item "$PSScriptRoot\.env.example" "$PSScriptRoot\.env" -ErrorAction SilentlyContinue
    Write-Host ""
    Write-Host "IMPORTANT: Update the API key in .env after creating a test client!" -ForegroundColor Yellow
    Write-Host ""
}

# Start the development server
Write-Host "Starting Vite development server..." -ForegroundColor Cyan
Write-Host "Frontend will be available at: http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

npm run dev

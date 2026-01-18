# Test CAC Entity Types Implementation
# Tests all entity types: Limited, PLC, Business Name, NGO

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Testing CAC Entity Type Support" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://127.0.0.1:8000"

# Wait for server to start
Start-Sleep -Seconds 2

# Test 1: Health Check
Write-Host "1. Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "   ✓ Server is healthy" -ForegroundColor Green
    Write-Host "   Environment: $($health.environment)" -ForegroundColor Gray
    Write-Host "   Version: $($health.version)" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ Health check failed: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Create a test API client first
Write-Host "2. Creating Test API Client..." -ForegroundColor Yellow
$createClientScript = @"
import asyncio
import sys
sys.path.insert(0, '.')
from app.core.database import get_db_context
from app.models.api_client import ApiClient

async def create_test_client():
    async with get_db_context() as db:
        # Check if client exists
        existing = db.query(ApiClient).filter(ApiClient.client_name == 'Test Client').first()
        if existing:
            print(existing.api_key)
            return
        
        # Create new client
        client = ApiClient(
            client_name='Test Client',
            is_active=True
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        print(client.api_key)

asyncio.run(create_test_client())
"@

$createClientScript | Out-File -FilePath "create_client_temp.py" -Encoding UTF8
$apiKey = & C:/Users/User/Documents/E-KYC/.venv/Scripts/python.exe create_client_temp.py
Remove-Item "create_client_temp.py" -ErrorAction SilentlyContinue

if (-not $apiKey) {
    Write-Host "   ✗ Failed to create API client" -ForegroundColor Red
    exit 1
}

Write-Host "   ✓ API Client created" -ForegroundColor Green
Write-Host "   API Key: $apiKey" -ForegroundColor Gray
Write-Host ""

$headers = @{
    "Authorization" = "Bearer $apiKey"
    "Content-Type" = "application/json"
}

# Test 2: Limited Company (RC123456)
Write-Host "3. Testing Limited Company (RC123456)..." -ForegroundColor Yellow
$limitedBody = @{
    rc_number = "RC123456"
    business_name = "ALPHA TRADING LIMITED"
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$baseUrl/api/v1/verify/corporate" -Method POST -Headers $headers -Body $limitedBody -ContentType "application/json"
    
    if ($result.cac_data.entity_type -eq "LIMITED") {
        Write-Host "   ✓ Entity Type: LIMITED" -ForegroundColor Green
        Write-Host "   ✓ Company: $($result.cac_data.company_name)" -ForegroundColor Green
        Write-Host "   ✓ Directors: $($result.cac_data.directors.Count)" -ForegroundColor Green
        Write-Host "   ✓ Shareholders: $($result.cac_data.shareholders.Count)" -ForegroundColor Green
        Write-Host "   ✓ Share Capital: ₦$($result.cac_data.share_capital)" -ForegroundColor Green
        Write-Host "   ✓ UBO Count: $($result.cac_data.ubo_count)" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Wrong entity type: $($result.cac_data.entity_type)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ✗ Test failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Business Name (BN12345)
Write-Host "4. Testing Business Name (BN12345)..." -ForegroundColor Yellow
$bnBody = @{
    rc_number = "BN12345"
    business_name = "PRECIOUS VENTURES"
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$baseUrl/api/v1/verify/corporate" -Method POST -Headers $headers -Body $bnBody -ContentType "application/json"
    
    if ($result.cac_data.entity_type -eq "BUSINESS_NAME") {
        Write-Host "   ✓ Entity Type: BUSINESS_NAME" -ForegroundColor Green
        Write-Host "   ✓ Company: $($result.cac_data.company_name)" -ForegroundColor Green
        Write-Host "   ✓ Proprietors: $($result.cac_data.proprietors.Count)" -ForegroundColor Green
        Write-Host "   ✓ Nature of Business: $($result.cac_data.nature_of_business)" -ForegroundColor Green
        Write-Host "   ✓ City: $($result.cac_data.city)" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Wrong entity type: $($result.cac_data.entity_type)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ✗ Test failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: NGO/Incorporated Trustees (IT54321)
Write-Host "5. Testing NGO/Incorporated Trustees (IT54321)..." -ForegroundColor Yellow
$ngoBody = @{
    rc_number = "IT54321"
    business_name = "HOPE FOR THE FUTURE FOUNDATION"
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$baseUrl/api/v1/verify/corporate" -Method POST -Headers $headers -Body $ngoBody -ContentType "application/json"
    
    if ($result.cac_data.entity_type -eq "INCORPORATED_TRUSTEES") {
        Write-Host "   ✓ Entity Type: INCORPORATED_TRUSTEES" -ForegroundColor Green
        Write-Host "   ✓ Company: $($result.cac_data.company_name)" -ForegroundColor Green
        Write-Host "   ✓ Trustees: $($result.cac_data.trustees.Count)" -ForegroundColor Green
        Write-Host "   ✓ Aims & Objectives: $($result.cac_data.aims_and_objectives.Substring(0, 50))..." -ForegroundColor Green
    } else {
        Write-Host "   ✗ Wrong entity type: $($result.cac_data.entity_type)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ✗ Test failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 5: PLC (RC789012)
Write-Host "6. Testing Public Limited Company (RC789012)..." -ForegroundColor Yellow
$plcBody = @{
    rc_number = "RC789012"
    business_name = "BETA INDUSTRIES PLC"
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$baseUrl/api/v1/verify/corporate" -Method POST -Headers $headers -Body $plcBody -ContentType "application/json"
    
    if ($result.cac_data.entity_type -eq "PLC") {
        Write-Host "   ✓ Entity Type: PLC" -ForegroundColor Green
        Write-Host "   ✓ Company: $($result.cac_data.company_name)" -ForegroundColor Green
        Write-Host "   ✓ Directors: $($result.cac_data.directors.Count)" -ForegroundColor Green
        Write-Host "   ✓ Shareholders: $($result.cac_data.shareholders.Count)" -ForegroundColor Green
        Write-Host "   ✓ Has Corporate Shareholder: $($result.cac_data.shareholders | Where-Object { $_.is_corporate } | Measure-Object | Select-Object -ExpandProperty Count)" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Wrong entity type: $($result.cac_data.entity_type)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ✗ Test failed: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "All Tests Completed!" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

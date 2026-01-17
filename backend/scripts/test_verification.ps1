# Test Corporate Verification Script
# Tests the API endpoint directly

$apiUrl = "http://localhost:8000/api/v1/verify/corporate"
$apiKey = "HgYpez7AORcjBWI5VwbXRf-J32MUHvoOIsl1LBN08tE"

$headers = @{
    "Authorization" = "Bearer $apiKey"
    "Content-Type" = "application/json"
}

$body = @{
    rc_number = "RC123456"
} | ConvertTo-Json

Write-Host "Testing Corporate Verification for RC123456..." -ForegroundColor Cyan
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $body -ErrorAction Stop
    
    Write-Host "✅ Verification Successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verification ID: $($response.verification_id)" -ForegroundColor Yellow
    Write-Host "Status: $($response.status)" -ForegroundColor Yellow
    Write-Host ""
    
    if ($response.cac_data) {
        Write-Host "Company Information:" -ForegroundColor Cyan
        Write-Host "  Company Name: $($response.cac_data.company_name)"
        Write-Host "  Verified: $($response.cac_data.verified)"
        Write-Host "  Incorporation Date: $($response.cac_data.incorporation_date)"
        Write-Host "  Status: $($response.cac_data.status)"
        Write-Host "  UBO Count: $($response.cac_data.ubo_count)"
        Write-Host ""
        
        if ($response.cac_data.ubos) {
            Write-Host "Ultimate Beneficial Owners:" -ForegroundColor Cyan
            foreach ($ubo in $response.cac_data.ubos) {
                Write-Host "  - $($ubo.name): $($ubo.ownership_percentage)% ($($ubo.ownership_type))"
            }
            Write-Host ""
        }
    }
    
    if ($response.risk_assessment) {
        Write-Host "Risk Assessment:" -ForegroundColor Cyan
        Write-Host "  Score: $($response.risk_assessment.score)/100"
        Write-Host "  Category: $($response.risk_assessment.category)"
        Write-Host ""
    }
    
    Write-Host "Processing Time: $($response.processing_time_ms)ms" -ForegroundColor Gray
    Write-Host "Report URL: $($response.report_url)" -ForegroundColor Gray
    
} catch {
    Write-Host "❌ Verification Failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        $errorData = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "Details: $($errorData.message)" -ForegroundColor Red
        Write-Host "Error Code: $($errorData.error_code)" -ForegroundColor Red
    }
}

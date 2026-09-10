$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $Root) { $Root = Get-Location }

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "           MailTrace AI - Starting All Services          " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

Write-Host "`n[1/3] Starting FastAPI Backend on Port 8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root\backend'; python -m uvicorn app.main:app --reload --port 8000"

Start-Sleep -Seconds 3

Write-Host "[2/3] Starting User Webmail Dashboard on Port 3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root'; npm run dev:user"

Start-Sleep -Seconds 2

Write-Host "[3/3] Starting Security Gateway Dashboard on Port 3001..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root'; npm run dev:security"

Start-Sleep -Seconds 3

Write-Host "`nOpening both dashboards in browser..." -ForegroundColor Yellow
Start-Process "http://localhost:3000"
Start-Process "http://localhost:3001"

Write-Host "`nAll services running and opened in browser!" -ForegroundColor Green
Write-Host "  * User Webmail:      http://localhost:3000" -ForegroundColor White
Write-Host "  * Security Gateway:  http://localhost:3001" -ForegroundColor White
Write-Host "  * Backend Docs:      http://localhost:8000/docs`n" -ForegroundColor White

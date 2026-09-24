# Quick dev runner for LRE (Backend + Visualizer)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Launching Logistics Requirements Engine (LRE)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check virtual environment
if (-not (Test-Path "$ProjectRoot\.venv\Scripts\python.exe")) {
    Write-Host "[1/3] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    .\.venv\Scripts\pip install -r lre_core\requirements.txt
} else {
    Write-Host "[1/3] Virtual environment detected (.venv)" -ForegroundColor Green
}

# 2. Start FastAPI Backend in new window
Write-Host "[2/3] Starting LRE-Core API at http://localhost:8000 ..." -ForegroundColor Cyan
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "Set-Location '$ProjectRoot'; .\.venv\Scripts\python -m uvicorn lre_core.app:app --host 0.0.0.0 --port 8000 --reload"

# 3. Start Visualizer static server in new window
Write-Host "[3/3] Starting LRE-Visualizer at http://localhost:8080 ..." -ForegroundColor Cyan
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "Set-Location '$ProjectRoot\lre_visualizer'; ..\.venv\Scripts\python -m http.server 8080"

Start-Sleep -Seconds 2
Start-Process "http://localhost:8080"

Write-Host "`nReady! Services are running:" -ForegroundColor Green
Write-Host "  - API Docs (Swagger): http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "  - Visualizer UI:      http://localhost:8080" -ForegroundColor Yellow

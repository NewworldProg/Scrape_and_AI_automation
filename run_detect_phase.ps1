# BERT AI Phase Detector - CLEAN VERSION
# Only detects conversation phase using BERT AI (no response generation)
# Usage: .\run_detect_phase.ps1

Write-Host "=== BERT AI Phase Detector ===" -ForegroundColor Cyan
Write-Host "Detecting conversation phase using BERT model..." -ForegroundColor Yellow
Write-Host ""

# Activate virtual environment
$venvActivate = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
    Write-Host "[OK] Virtual environment activated" -ForegroundColor Green
}
else {
    Write-Host "[WARN] No venv found - using system Python" -ForegroundColor Yellow
}

# Run BERT phase detection only
Write-Host ""
Write-Host "Running BERT AI phase detector..." -ForegroundColor Cyan
python ai\phase_detector.py

Write-Host ""
Write-Host "=== Phase Detection Complete ===" -ForegroundColor Green
Write-Host "BERT AI detected conversation phase" -ForegroundColor Cyan
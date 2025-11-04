# Train Phase Classifier Model
# This trains a BERT-based model to detect conversation phases

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PHASE CLASSIFIER MODEL TRAINING" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
$venvActivate = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
    Write-Host "[OK] Virtual environment activated" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "[INFO] Please create venv first: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Check if training data exists
if (-not (Test-Path "ai\phase_training_data.json")) {
    Write-Host "[ERROR] Training data not found!" -ForegroundColor Red
    Write-Host "[INFO] Expected: ai\phase_training_data.json" -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Training data found" -ForegroundColor Green
Write-Host ""

# Delete old model if exists
$oldModelDir = "ai\trained_models\phase_classifier_v1"
if (Test-Path $oldModelDir) {
    Write-Host "[INFO] Deleting old model..." -ForegroundColor Yellow
    Remove-Item -Path $oldModelDir -Recurse -Force
    Write-Host "[OK] Old model deleted" -ForegroundColor Green
    Write-Host ""
}

# Install required packages if needed
Write-Host "[INFO] Checking required packages..." -ForegroundColor Cyan
python -c "import transformers, torch, sklearn" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Installing required packages..." -ForegroundColor Yellow
    pip install transformers torch scikit-learn --quiet
    Write-Host "[OK] Packages installed" -ForegroundColor Green
    Write-Host ""
}

# Start training
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STARTING TRAINING..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] This may take 10-20 minutes depending on your hardware" -ForegroundColor Yellow
Write-Host "[INFO] Training 8 conversation phases:" -ForegroundColor Cyan
Write-Host "  1. Initial Response (after cover letter)" -ForegroundColor White
Write-Host "  2. Ask Job Details" -ForegroundColor White
Write-Host "  3. Knowledge Check (requires human)" -ForegroundColor Yellow
Write-Host "  4. Language Confirmation" -ForegroundColor White
Write-Host "  5. Rate Negotiation" -ForegroundColor White
Write-Host "  6. Deadline & Samples" -ForegroundColor White
Write-Host "  7. Structure Clarification" -ForegroundColor White
Write-Host "  8. Contract Acceptance" -ForegroundColor White
Write-Host ""

python ai\train_phase_classifier.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "TRAINING COMPLETE!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "[OK] Model saved to: ai\trained_models\phase_classifier_v1" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Test the model: python ai\phase_detector.py" -ForegroundColor White
    Write-Host "  2. Integrate with smart response: Update smart_chat_response.py" -ForegroundColor White
    Write-Host ""
}
else {
    Write-Host ""
    Write-Host "[ERROR] Training failed!" -ForegroundColor Red
    Write-Host "[INFO] Check error messages above" -ForegroundColor Yellow
    exit 1
}

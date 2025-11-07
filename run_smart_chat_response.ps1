# Smart Chat Response Generator - CLEAN VERSION
# Phase Detection: BERT AI only (no keywords, no fallbacks)
# Usage: .\run_smart_chat_response.ps1 [-Mode template|ai|both]
# Default: template (3 fast options)

param(
    [ValidateSet('template', 'ai', 'both')]
    [string]$Mode = 'template'
)

Write-Host "=== Smart Chat Response Generator - CLEAN ===" -ForegroundColor Cyan
Write-Host "BERT AI Phase Detection + Response Generation" -ForegroundColor Yellow

# Show mode info
switch ($Mode) {
    'template' { 
        Write-Host "Mode: TEMPLATE (Fast - 3 options)" -ForegroundColor Green 
        Write-Host "Description: Pre-written professional templates for detected phase" -ForegroundColor Gray
    }
    'ai' { 
        Write-Host "Mode: AI (GPT-2 Generated)" -ForegroundColor Yellow 
        Write-Host "Description: AI-generated response based on detected phase" -ForegroundColor Gray
    }
    'both' { 
        Write-Host "Mode: BOTH (Template + AI)" -ForegroundColor Magenta 
        Write-Host "Description: Both template and AI response for comparison" -ForegroundColor Gray
    }
}
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

# Run smart response generator
Write-Host ""
Write-Host "Running BERT AI phase detector + response generator..." -ForegroundColor Cyan
python ai\smart_chat_response.py --session-id latest --mode $Mode

Write-Host ""
Write-Host "=== Smart Response Complete ===" -ForegroundColor Green
Write-Host "BERT AI detected phase and generated responses" -ForegroundColor Cyan
Write-Host ""
Write-Host "Available modes:" -ForegroundColor Yellow
Write-Host "  template - Fast, 3 pre-written options (default)" -ForegroundColor White
Write-Host "  ai       - GPT-2 generated response" -ForegroundColor White
Write-Host "  both     - Template + AI (both responses)" -ForegroundColor Magenta

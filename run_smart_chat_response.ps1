# Smart Chat Response Generator - Phase Detection + Templates
# Usage: .\run_smart_chat_response.ps1 [-Mode template|hybrid|pure|summary]
# Default: template (5 fast options)

param(
    [ValidateSet('template', 'hybrid', 'pure', 'summary', 'all')]
    [string]$Mode = 'template'
)

Write-Host "=== Smart Chat Response Generator ===" -ForegroundColor Cyan
Write-Host "Detecting conversation phase and generating appropriate responses..." -ForegroundColor Yellow

# Show mode info
switch ($Mode) {
    'template' { 
        Write-Host "Mode: TEMPLATE (Fast - 5 options)" -ForegroundColor Green 
        Write-Host "Description: Pre-written professional templates" -ForegroundColor Gray
    }
    'hybrid' { 
        Write-Host "Mode: HYBRID (Template + AI)" -ForegroundColor Yellow 
        Write-Host "Description: Template base with AI personalization" -ForegroundColor Gray
    }
    'pure' { 
        Write-Host "Mode: PURE AI (Fully Generated)" -ForegroundColor Magenta 
        Write-Host "Description: 100% AI-generated from context" -ForegroundColor Gray
    }
    'summary' { 
        Write-Host "Mode: SUMMARY (Template + Context)" -ForegroundColor Cyan 
        Write-Host "Description: Template + AI context summary" -ForegroundColor Gray
    }
    'all' {
        Write-Host "Mode: ALL MODES (Sequential Generation)" -ForegroundColor Magenta
        Write-Host "Description: Generate ALL 4 modes one by one (~7-8s total)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Will generate 6 total options:" -ForegroundColor Yellow
        Write-Host "  - Template: 3 options (~0.1s)" -ForegroundColor Green
        Write-Host "  - Hybrid: 1 option (~2s)" -ForegroundColor Green
        Write-Host "  - Pure AI: 1 option (~3s)" -ForegroundColor Green
        Write-Host "  - Summary: 1 option (~2s)" -ForegroundColor Green
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
Write-Host "Running smart response generator..." -ForegroundColor Cyan
python ai\smart_chat_response.py --session-id latest --mode $Mode

Write-Host ""
Write-Host "=== Smart Response Complete ===" -ForegroundColor Green
Write-Host "Check temp_ai_suggestions.json for results" -ForegroundColor Cyan
Write-Host ""
Write-Host "Available modes:" -ForegroundColor Yellow
Write-Host "  template - Fast, 5 pre-written options (default)" -ForegroundColor White
Write-Host "  hybrid   - Template + AI personalization" -ForegroundColor White
Write-Host "  pure     - Fully AI-generated responses" -ForegroundColor White
Write-Host "  summary  - Template + AI context summary" -ForegroundColor White
Write-Host "  all      - ALL 4 modes (6 total options, ~7-8s)" -ForegroundColor Magenta

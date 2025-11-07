# Upwork Notification System Environment  
# Auto-generated on 2025-11-07 09:30:54

# Project paths (auto-detected)
$Global:UPWORK_PROJECT_ROOT = "E:\Repoi\UpworkNotif"
$Global:UPWORK_AI_DIR = "E:\Repoi\UpworkNotif\ai"
$Global:UPWORK_DATA_DIR = "E:\Repoi\UpworkNotif\data"
$Global:UPWORK_SCRIPTS_DIR = "E:\Repoi\UpworkNotif\scripts"

# Database and model paths
$Global:UPWORK_DATABASE_PATH = "E:\Repoi\UpworkNotif\data\chat_data.db"
$Global:UPWORK_BERT_MODEL_DIR = "E:\Repoi\UpworkNotif\ai\trained_models\phase_classifier_v1"

# Output paths
$Global:UPWORK_DASHBOARD_PATH = "E:\Repoi\UpworkNotif\chat_dashboard.html"
$Global:UPWORK_TEMP_AI_PATH = "E:\Repoi\UpworkNotif\temp_ai_suggestions.json"

Write-Host "✅ Environment loaded: $Global:UPWORK_PROJECT_ROOT" -ForegroundColor Green

function Test-UpworkEnvironment {
    Write-Host "🔍 Testing Upwork environment..." -ForegroundColor Yellow
    Write-Host "Project Root: $Global:UPWORK_PROJECT_ROOT" -ForegroundColor Cyan
    Write-Host "Python scripts: " -NoNewline
    if (Test-Path "$Global:UPWORK_AI_DIR\standalone_phase_detector.py") {
        Write-Host "✅" -ForegroundColor Green
    } else {
        Write-Host "❌" -ForegroundColor Red
    }
    Write-Host "Database: " -NoNewline
    if (Test-Path "$Global:UPWORK_DATABASE_PATH") {
        Write-Host "✅" -ForegroundColor Green
    } else {
        Write-Host "⚠️  (will be created)" -ForegroundColor Yellow
    }
}

function Invoke-UpworkPhaseDetector {
    param([string]$SessionId = "latest")
    $scriptPath = "$Global:UPWORK_AI_DIR\standalone_phase_detector.py"
    if (Test-Path $scriptPath) {
        python "$scriptPath" --session "$SessionId"
    } else {
        Write-Host "❌ Phase detector not found: $scriptPath" -ForegroundColor Red
    }
}

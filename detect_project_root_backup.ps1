# -*- coding: utf-8 -*-
# Project Root Detector for Upwork Notification System  
# Automatically detects project root and updates all 3 n8n workflows

param(
    [switch]$UpdateN8N = $true,
    [switch]$ShowPaths = $false,
    [switch]$Verbose = $false
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "PROJECT ROOT DETECTOR (ALL 3 WORKFLOWS)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# 1. DETECT PROJECT ROOT
$ProjectRoot = $null

# Method 1: Script location (most reliable)
if ($PSScriptRoot -and (Test-Path $PSScriptRoot)) {
    $ProjectRoot = $PSScriptRoot
    Write-Host "✅ Method 1: Script location detected" -ForegroundColor Green
    Write-Host "   Root: $ProjectRoot" -ForegroundColor White
}

# Method 2: Current directory fallback
if (-not $ProjectRoot) {
    $ProjectRoot = (Get-Location).Path
    Write-Host "⚠️  Method 2: Using current directory" -ForegroundColor Yellow
    Write-Host "   Root: $ProjectRoot" -ForegroundColor White
}

# 3. VALIDATE PROJECT STRUCTURE
Write-Host "`n🔍 Validating project structure..." -ForegroundColor Yellow

$RequiredMarkers = @(
    "ai\standalone_phase_detector.py",
    "ai\smart_chat_response.py",
    "n8n_chat_ai_workflow.json",
    "n8n_ai_cover_letter_workflow.json", 
    "n8n_workflow_conditional.json"
)

$IsValidProject = $true

foreach ($marker in $RequiredMarkers) {
    $markerPath = Join-Path $ProjectRoot $marker
    if (Test-Path $markerPath) {
        Write-Host "  ✅ $marker" -ForegroundColor Green
    }
    else {
        Write-Host "  ❌ $marker (missing)" -ForegroundColor Red
        $IsValidProject = $false
    }
}

if (-not $IsValidProject) {
    Write-Host "`n❌ Invalid project structure!" -ForegroundColor Red
    Write-Host "   Make sure you're running this from the Upwork Notification System root directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✅ Valid project structure confirmed!" -ForegroundColor Green

# 4. DISPLAY CURRENT PATHS IN ALL N8N WORKFLOWS
Write-Host "`n📋 Current n8n workflow paths:" -ForegroundColor Yellow

$WorkflowFiles = @(
    "n8n_chat_ai_workflow.json",
    "n8n_ai_cover_letter_workflow.json",
    "n8n_workflow_conditional.json"
)

foreach ($workflowFile in $WorkflowFiles) {
    $workflowPath = Join-Path $ProjectRoot $workflowFile
    if (Test-Path $workflowPath) {
        $content = Get-Content $workflowPath -Raw
        
        # Extract command paths more reliably
        if ($content -match '"command"[^"]+File[^"]+\"([^"]+)"') {
            $currentPath = $Matches[1] -replace '\\\\', '\'
            $currentRoot = (Split-Path $currentPath -Parent)
            
            Write-Host "  📄 $workflowFile" -ForegroundColor Cyan
            Write-Host "     Current: $currentRoot" -ForegroundColor Gray
            Write-Host "     Detected: $ProjectRoot" -ForegroundColor White
            
            if ($currentRoot -eq $ProjectRoot) {
                Write-Host "     Status: ✅ Correct" -ForegroundColor Green
            }
            else {
                Write-Host "     Status: ⚠️  Needs update" -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "  📄 $workflowFile" -ForegroundColor Cyan
            Write-Host "     Status: ℹ️  No paths found or different format" -ForegroundColor Blue
        }
    }
    else {
        Write-Host "  ❌ $workflowFile (not found)" -ForegroundColor Red
    }
}

# 5. UPDATE ALL N8N WORKFLOWS (if requested)
if ($UpdateN8N) {
    Write-Host "`n🔄 Updating all n8n workflows..." -ForegroundColor Yellow
    
    # Create backup directory
    $BackupDir = Join-Path $ProjectRoot "backup_n8n_original"
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
        Write-Host "📁 Created backup directory: backup_n8n_original" -ForegroundColor Cyan
    }
    
    $UpdatedCount = 0
    
    foreach ($workflowFile in $WorkflowFiles) {
        $workflowPath = Join-Path $ProjectRoot $workflowFile
        
        if (Test-Path $workflowPath) {
            Write-Host "Processing: $workflowFile" -ForegroundColor Cyan
            
            # Create backup
            $backupPath = Join-Path $BackupDir $workflowFile
            if (-not (Test-Path $backupPath)) {
                Copy-Item $workflowPath -Destination $backupPath -Force
                Write-Host "  📄 Backup created" -ForegroundColor Gray
            }
            
            # Read content
            $content = Get-Content $workflowPath -Raw -Encoding UTF8
            $originalContent = $content
            
            # Replace any hardcoded paths with current project root
            # Pattern 1: E:\Repoi\UpworkNotif (with double backslashes in JSON)
            $escapedProjectRoot = $ProjectRoot.Replace('\', '\\')
            $content = $content -replace 'E:\\\\Repoi\\\\UpworkNotif', $escapedProjectRoot
            
            # Pattern 2: E:/Repoi/UpworkNotif (forward slashes)
            $forwardProjectRoot = $ProjectRoot.Replace('\', '/')
            $content = $content -replace 'E:/Repoi/UpworkNotif', $forwardProjectRoot
            
            # Pattern 3: Other potential hardcoded paths (any drive)
            $content = $content -replace '[C-Z]:\\\\[^"]*\\\\UpworkNotif', $escapedProjectRoot
            
            # Pattern 4: workingDirectory paths
            $content = $content -replace '"workingDirectory":\s*"E:\\\\Repoi\\\\UpworkNotif"', "`"workingDirectory`": `"$escapedProjectRoot`""
            
            # Check if changes were made
            if ($content -ne $originalContent) {
                # Validate JSON
                try {
                    $null = $content | ConvertFrom-Json
                    
                    # Write updated content
                    $content | Out-File -FilePath $workflowPath -Encoding UTF8 -Force
                    
                    Write-Host "  ✅ Updated successfully" -ForegroundColor Green
                    $UpdatedCount++
                    
                }
                catch {
                    Write-Host "  ❌ JSON validation failed - skipping: $($_.Exception.Message)" -ForegroundColor Red
                }
            }
            else {
                Write-Host "  ℹ️  No changes needed" -ForegroundColor Blue
            }
        }
        else {
            Write-Host "  ❌ File not found: $workflowFile" -ForegroundColor Red
        }
    }
    
    Write-Host "`n✅ Updated $UpdatedCount workflow file(s)" -ForegroundColor Green
}

# 6. CREATE ENVIRONMENT FILE
Write-Host "`n🔧 Creating environment configuration..." -ForegroundColor Yellow

$EnvironmentContent = @"
# Upwork Notification System Environment
# Auto-generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

# Project paths (auto-detected)
`$Global:UPWORK_PROJECT_ROOT = "$ProjectRoot"
`$Global:UPWORK_AI_DIR = "$ProjectRoot\ai"
`$Global:UPWORK_DATA_DIR = "$ProjectRoot\data"
`$Global:UPWORK_SCRIPTS_DIR = "$ProjectRoot\scripts"

# Database and model paths
`$Global:UPWORK_DATABASE_PATH = "$ProjectRoot\data\chat_data.db"
`$Global:UPWORK_BERT_MODEL_DIR = "$ProjectRoot\ai\trained_models\phase_classifier_v1"

# Output paths
`$Global:UPWORK_DASHBOARD_PATH = "$ProjectRoot\chat_dashboard.html"
`$Global:UPWORK_TEMP_AI_PATH = "$ProjectRoot\temp_ai_suggestions.json"

Write-Host "✅ Environment loaded: `$Global:UPWORK_PROJECT_ROOT" -ForegroundColor Green

# Quick test functions
function Test-UpworkEnvironment {
    Write-Host "🔍 Testing Upwork environment..." -ForegroundColor Yellow
    Write-Host "Project Root: `$Global:UPWORK_PROJECT_ROOT" -ForegroundColor Cyan
    Write-Host "Python scripts: " -NoNewline
    if (Test-Path "`$Global:UPWORK_AI_DIR\standalone_phase_detector.py") {
        Write-Host "✅" -ForegroundColor Green
    } else {
        Write-Host "❌" -ForegroundColor Red
    }
    Write-Host "Database: " -NoNewline
    if (Test-Path "`$Global:UPWORK_DATABASE_PATH") {
        Write-Host "✅" -ForegroundColor Green
    } else {
        Write-Host "⚠️  (will be created)" -ForegroundColor Yellow
    }
}

function Invoke-UpworkPhaseDetector {
    param([string]`$SessionId = "latest")
    `$scriptPath = "`$Global:UPWORK_AI_DIR\standalone_phase_detector.py"
    if (Test-Path `$scriptPath) {
        python "`$scriptPath" --session "`$SessionId"
    } else {
        Write-Host "❌ Phase detector not found: `$scriptPath" -ForegroundColor Red
    }
}
"@

$EnvironmentFile = Join-Path $ProjectRoot "environment.ps1"
$EnvironmentContent | Out-File -FilePath $EnvironmentFile -Encoding UTF8 -Force

Write-Host "✅ Environment file created: environment.ps1" -ForegroundColor Green

# 7. FINAL SUMMARY
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "PROJECT DETECTION COMPLETE" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Detected Root: $ProjectRoot" -ForegroundColor White
Write-Host "🔧 Environment: environment.ps1" -ForegroundColor White
Write-Host "📁 Backups: backup_n8n_original/" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Yellow
Write-Host "1. Load environment: . .\environment.ps1" -ForegroundColor White
Write-Host "2. Test: Test-UpworkEnvironment" -ForegroundColor White  
Write-Host "3. Import updated workflows into n8n" -ForegroundColor White
Write-Host ""
Write-Host "🎉 All 3 n8n workflows are now configured for this machine!" -ForegroundColor Green
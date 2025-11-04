# 🗑️ Upwork Automation - Cleanup Script
# Briše sve nepotrebne fajlove i konsoliduje dokumentaciju

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   🗑️  UPWORK AUTOMATION CLEANUP SCRIPT" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Project root path
$projectRoot = "E:\Repoi\UpworkNotif"
cd $projectRoot

# ═══════════════════════════════════════════════════════
# ⚠️  BACKUP FIRST
# ═══════════════════════════════════════════════════════
Write-Host "📦 Creating backup..." -ForegroundColor Yellow
$backupFolder = "E:\Repoi\UpworkNotif_BACKUP_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
try {
    Copy-Item -Path $projectRoot -Destination $backupFolder -Recurse -ErrorAction Stop
    Write-Host "✅ Backup created at: $backupFolder" -ForegroundColor Green
}
catch {
    Write-Host "❌ Backup failed! Aborting cleanup." -ForegroundColor Red
    exit 1
}

Write-Host ""

# ═══════════════════════════════════════════════════════
# 🗂️  DELETION CATEGORIES
# ═══════════════════════════════════════════════════════

$deletedCount = 0
$errors = @()

# Function to safely delete file
function Remove-FileSafely {
    param([string]$path, [string]$description)
    
    if (Test-Path $path) {
        try {
            Remove-Item -Path $path -Force -ErrorAction Stop
            Write-Host "  ✅ Deleted: $description" -ForegroundColor Green
            return $true
        }
        catch {
            Write-Host "  ❌ Failed: $description - $($_.Exception.Message)" -ForegroundColor Red
            $script:errors += $description
            return $false
        }
    }
    else {
        Write-Host "  ⚠️  Not found: $description" -ForegroundColor Yellow
        return $false
    }
}

# ═══════════════════════════════════════════════════════
# 1️⃣  DELETE DUPLICATE README FILES
# ═══════════════════════════════════════════════════════
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "1️⃣  Deleting Duplicate README Files" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

$readmeFiles = @(
    "CHAT_AI_README.md",
    "AI_COVER_LETTER_README.md",
    "SMART_CHAT_RESPONSE_README.md",
    "MongoDB_Workflows_README.md",
    "AI_PROMPT_TEMPLATES.md",
    "CHAT_AI_SYSTEM_FILES.md",
    "ai\training\README.md"
)

foreach ($file in $readmeFiles) {
    if (Remove-FileSafely $file "README: $file") {
        $deletedCount++
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════
# 2️⃣  DELETE SUMMARY/GUIDE FILES
# ═══════════════════════════════════════════════════════
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "2️⃣  Deleting Summary/Guide Files" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

$summaryFiles = @(
    "AI_WORKFLOW_UPDATE_SUMMARY.md",
    "SMART_CHAT_IMPLEMENTATION_SUMMARY.md",
    "SEPARATED_WORKFLOW_SUMMARY.md",
    "DATABASE_WORKFLOW_SUMMARY.md",
    "UPDATED_WORKFLOW_SUMMARY.md",
    "RESPONSE_MODES_GUIDE.md",
    "ML_PHASE_DETECTION_GUIDE.md",
    "N8N_WORKFLOW_MODES.md"
)

foreach ($file in $summaryFiles) {
    if (Remove-FileSafely $file "Summary: $file") {
        $deletedCount++
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════
# 3️⃣  DELETE TEST FILES
# ═══════════════════════════════════════════════════════
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "3️⃣  Deleting Test Files" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

$testFiles = @(
    "test_all_sessions.py",
    "test_chat_context.py",
    "test_database_node.ps1",
    "test_db_direct.py",
    "test_db_raw.py",
    "test_db_sessions.py",
    "test_sessions.py",
    "test_simple_node.ps1",
    "check_n8n_workflow.py"
)

foreach ($file in $testFiles) {
    if (Remove-FileSafely $file "Test: $file") {
        $deletedCount++
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════
# 4️⃣  DELETE DATABASE NODE DUPLICATES
# ═══════════════════════════════════════════════════════
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "4️⃣  Deleting Database Node Duplicates" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

$dbNodeFiles = @(
    "database_node.ps1",
    "database_node_final.ps1",
    "database_node_fixed.ps1",
    "database_node_simple.ps1",
    "database_node_working.ps1",
    "db_node.ps1",
    "db_test.ps1"
)

foreach ($file in $dbNodeFiles) {
    if (Remove-FileSafely $file "DB Node: $file") {
        $deletedCount++
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════
# 5️⃣  DELETE UNUSED POWERSHELL SCRIPTS
# ═══════════════════════════════════════════════════════
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "5️⃣  Deleting Unused PowerShell Scripts" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

$unusedPSFiles = @(
    "run_chat_ai_generator.ps1",
    "run_chat_dashboard.ps1",
    "run_clean_chat_response.ps1",
    "run_continue_chat_workflow.ps1",
    "run_parse_from_db.ps1",
    "run_parser_latest.ps1",
    "run_simple_chrome_debug.ps1",
    "run_start_chrome_chat.ps1"
)

foreach ($file in $unusedPSFiles) {
    if (Remove-FileSafely $file "PowerShell: $file") {
        $deletedCount++
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════
# 6️⃣  DELETE OLD DATABASE FILE
# ═══════════════════════════════════════════════════════
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "6️⃣  Deleting Old Database File" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

if (Remove-FileSafely "chat_data.db" "Old Database: chat_data.db (root)") {
    $deletedCount++
}
Write-Host "  ℹ️  Correct database: data\chat_data.db (keeping)" -ForegroundColor Cyan

Write-Host ""

# ═══════════════════════════════════════════════════════
# 7️⃣  DELETE GITHUB PREP FILES
# ═══════════════════════════════════════════════════════
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "7️⃣  Deleting GitHub Prep Files" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

$githubFiles = @(
    "prepare_github_upload.py",
    "github_upload_list.json"
)

foreach ($file in $githubFiles) {
    if (Remove-FileSafely $file "GitHub: $file") {
        $deletedCount++
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════
# 8️⃣  REPLACE OLD README WITH NEW MASTER README
# ═══════════════════════════════════════════════════════
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "8️⃣  Replacing README with Master README" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

if (Test-Path "README_NEW.md") {
    try {
        if (Test-Path "README.md") {
            Remove-Item "README.md" -Force
            Write-Host "  ✅ Deleted old README.md" -ForegroundColor Green
        }
        
        Rename-Item -Path "README_NEW.md" -NewName "README.md" -Force
        Write-Host "  ✅ Renamed README_NEW.md → README.md" -ForegroundColor Green
    }
    catch {
        Write-Host "  ❌ Failed to replace README: $($_.Exception.Message)" -ForegroundColor Red
        $errors += "README replacement"
    }
}
else {
    Write-Host "  ⚠️  README_NEW.md not found - skipping" -ForegroundColor Yellow
}

Write-Host ""

# ═══════════════════════════════════════════════════════
# 9️⃣  DELETE FILES_TO_DELETE.md (cleanup guide itself)
# ═══════════════════════════════════════════════════════
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "9️⃣  Deleting Cleanup Guide" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

if (Remove-FileSafely "FILES_TO_DELETE.md" "Cleanup Guide: FILES_TO_DELETE.md") {
    $deletedCount++
}

Write-Host ""

# ═══════════════════════════════════════════════════════
# 📊 SUMMARY
# ═══════════════════════════════════════════════════════
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   📊 CLEANUP SUMMARY" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ✅ Files Deleted: $deletedCount" -ForegroundColor Green
Write-Host "  📦 Backup Location: $backupFolder" -ForegroundColor Cyan
Write-Host "  📄 New Master README: README.md" -ForegroundColor Cyan
Write-Host ""

if ($errors.Count -gt 0) {
    Write-Host "  ⚠️  Errors encountered:" -ForegroundColor Yellow
    foreach ($error in $errors) {
        Write-Host "     - $error" -ForegroundColor Yellow
    }
    Write-Host ""
}

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   ✅ CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 Project structure is now clean and organized." -ForegroundColor Green
Write-Host "📄 All documentation merged into single README.md" -ForegroundColor Green
Write-Host "🚀 Only 3 n8n workflows + essential scripts remain." -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review new README.md" -ForegroundColor White
Write-Host "  2. Test n8n workflows still work" -ForegroundColor White
Write-Host "  3. Delete backup folder if satisfied" -ForegroundColor White
Write-Host ""

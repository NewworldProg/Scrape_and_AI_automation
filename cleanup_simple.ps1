# Cleanup Script - Delete unnecessary files (Portable version)

$projectRoot = $PSScriptRoot
Set-Location $projectRoot

Write-Host "Project root: $projectRoot" -ForegroundColor Cyan
Write-Host "Creating backup..." -ForegroundColor Yellow

$backupFolder = Join-Path (Split-Path $projectRoot -Parent) "UpworkNotif_BACKUP_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item -Path $projectRoot -Destination $backupFolder -Recurse
Write-Host "Backup created at: $backupFolder" -ForegroundColor Green
Write-Host ""

$deletedCount = 0

# Delete README files
Write-Host "Deleting README files..." -ForegroundColor Cyan
$files = @(
    "CHAT_AI_README.md",
    "AI_COVER_LETTER_README.md",
    "SMART_CHAT_RESPONSE_README.md",
    "MongoDB_Workflows_README.md",
    "AI_PROMPT_TEMPLATES.md",
    "CHAT_AI_SYSTEM_FILES.md"
)
foreach ($f in $files) {
    if (Test-Path $f) { Remove-Item $f -Force; $deletedCount++; Write-Host "  Deleted: $f" }
}

# Delete summary files
Write-Host "Deleting summary files..." -ForegroundColor Cyan
$files = @(
    "AI_WORKFLOW_UPDATE_SUMMARY.md",
    "SMART_CHAT_IMPLEMENTATION_SUMMARY.md",
    "SEPARATED_WORKFLOW_SUMMARY.md",
    "DATABASE_WORKFLOW_SUMMARY.md",
    "UPDATED_WORKFLOW_SUMMARY.md",
    "RESPONSE_MODES_GUIDE.md",
    "ML_PHASE_DETECTION_GUIDE.md",
    "N8N_WORKFLOW_MODES.md"
)
foreach ($f in $files) {
    if (Test-Path $f) { Remove-Item $f -Force; $deletedCount++; Write-Host "  Deleted: $f" }
}

# Delete test files
Write-Host "Deleting test files..." -ForegroundColor Cyan
$files = @(
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
foreach ($f in $files) {
    if (Test-Path $f) { Remove-Item $f -Force; $deletedCount++; Write-Host "  Deleted: $f" }
}

# Delete database node files
Write-Host "Deleting database node files..." -ForegroundColor Cyan
$files = @(
    "database_node.ps1",
    "database_node_final.ps1",
    "database_node_fixed.ps1",
    "database_node_simple.ps1",
    "database_node_working.ps1",
    "db_node.ps1",
    "db_test.ps1"
)
foreach ($f in $files) {
    if (Test-Path $f) { Remove-Item $f -Force; $deletedCount++; Write-Host "  Deleted: $f" }
}

# Delete unused PowerShell files
Write-Host "Deleting unused PowerShell files..." -ForegroundColor Cyan
$files = @(
    "run_chat_ai_generator.ps1",
    "run_chat_dashboard.ps1",
    "run_clean_chat_response.ps1",
    "run_continue_chat_workflow.ps1",
    "run_parse_from_db.ps1",
    "run_parser_latest.ps1",
    "run_simple_chrome_debug.ps1",
    "run_start_chrome_chat.ps1"
)
foreach ($f in $files) {
    if (Test-Path $f) { Remove-Item $f -Force; $deletedCount++; Write-Host "  Deleted: $f" }
}

# Delete old database
Write-Host "Deleting old database..." -ForegroundColor Cyan
if (Test-Path "chat_data.db") { Remove-Item "chat_data.db" -Force; $deletedCount++; Write-Host "  Deleted: chat_data.db" }

# Delete GitHub prep files
Write-Host "Deleting GitHub prep files..." -ForegroundColor Cyan
$files = @("prepare_github_upload.py", "github_upload_list.json")
foreach ($f in $files) {
    if (Test-Path $f) { Remove-Item $f -Force; $deletedCount++; Write-Host "  Deleted: $f" }
}

# Replace README
Write-Host "Replacing README..." -ForegroundColor Cyan
if (Test-Path "README_NEW.md") {
    if (Test-Path "README.md") { Remove-Item "README.md" -Force }
    Rename-Item "README_NEW.md" "README.md"
    Write-Host "  README.md updated" -ForegroundColor Green
}

# Delete cleanup files
if (Test-Path "FILES_TO_DELETE.md") { Remove-Item "FILES_TO_DELETE.md" -Force; $deletedCount++ }

Write-Host ""
Write-Host "CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "Files deleted: $deletedCount" -ForegroundColor Green
Write-Host "Backup: $backupFolder" -ForegroundColor Cyan
Write-Host ""

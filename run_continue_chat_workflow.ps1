# Continue Chat Workflow - Simple Trigger
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Continuing Chat AI Workflow..."

try {
    # Simply trigger the chat scraper workflow again
    Set-Location "E:\Repoi\UpworkNotif"
    
    Write-Host "Step 1: Running chat scraper..."
    & ".\run_chat_scraper.ps1"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Chat scraper failed"
        exit 1
    }
    
    Write-Host "Step 2: Parsing chat messages..."
    & ".\run_chat_parser.ps1"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Chat parser failed"
        exit 1
    }
    
    Write-Host "Step 3: Generating AI responses..."
    & ".\run_chat_ai_generator.ps1" -SessionId "latest" -Type "professional"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "AI generator failed"
        exit 1
    }
    
    Write-Host "Step 4: Updating dashboard..."
    & ".\run_generate_and_open_chat_dashboard.ps1"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Dashboard update failed"
        exit 1
    }
    
    Write-Host "[OK] Chat workflow continued successfully!"
    exit 0
}
catch {
    Write-Host "Error continuing workflow: $($_.Exception.Message)"
    exit 1
}
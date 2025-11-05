# Universal Path Fixer - Converts all hardcoded paths to portable $PSScriptRoot
# Run this script to make all PowerShell scripts portable

$projectRoot = $PSScriptRoot
Write-Host "Fixing paths in: $projectRoot" -ForegroundColor Cyan

$hardcodedPath = "E:\Repoi\UpworkNotif"
$scriptsToFix = Get-ChildItem -Path $projectRoot -Filter "run_*.ps1"

$fixedCount = 0
$skippedCount = 0

foreach ($script in $scriptsToFix) {
    # Skip already fixed scripts
    if ($script.Name -in @("run_start_chrome_simple.ps1", "run_start_chrome_chat_simple.ps1")) {
        Write-Host "  [SKIP] $($script.Name) - Already portable" -ForegroundColor Yellow
        $skippedCount++
        continue
    }
    
    $content = Get-Content $script.FullName -Raw
    
    # Check if it contains hardcoded path
    if ($content -match [regex]::Escape($hardcodedPath)) {
        Write-Host "  [FIX] $($script.Name)" -ForegroundColor Green
        
        # Add $PSScriptRoot at the beginning if not present
        if ($content -notmatch '\$PSScriptRoot') {
            $content = "`$projectRoot = `$PSScriptRoot`n" + $content
        }
        
        # Replace all hardcoded paths with $projectRoot
        $content = $content -replace [regex]::Escape($hardcodedPath), '$projectRoot'
        
        # Also replace Set-Location with dynamic path
        $content = $content -replace 'Set-Location\s+"[^"]*"', 'Set-Location $projectRoot'
        
        # Save fixed content
        Set-Content -Path $script.FullName -Value $content -NoNewline
        $fixedCount++
    }
    else {
        Write-Host "  [OK] $($script.Name) - No hardcoded paths" -ForegroundColor Gray
        $skippedCount++
    }
}

Write-Host "`nSummary:" -ForegroundColor Cyan
Write-Host "  Fixed: $fixedCount scripts" -ForegroundColor Green
Write-Host "  Skipped: $skippedCount scripts" -ForegroundColor Yellow
Write-Host "`nAll scripts are now portable! ✅" -ForegroundColor Green

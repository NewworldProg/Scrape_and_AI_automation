# Simple Chrome Chat Starter - Identical to working version
# Starts Chrome with debug port 9223 for chat

try {
    Set-Location "E:\Repoi\UpworkNotif"
    
    # Set UTF-8 encoding
    $OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    
    # Chrome executable paths to try
    $chromePaths = @(
        "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "${env:LOCALAPPDATA}\Google\Chrome\Application\chrome.exe"
    )
    
    $chromePath = $null
    foreach ($path in $chromePaths) {
        if (Test-Path $path) {
            $chromePath = $path
            break
        }
    }
    
    if (-not $chromePath) {
        Write-Host "Chrome executable not found"
        exit 1
    }
    
    # Create chat profile directory
    $chatProfilePath = "E:\Repoi\UpworkNotif\chrome_profile_chat"
    if (-not (Test-Path $chatProfilePath)) {
        New-Item -ItemType Directory -Path $chatProfilePath -Force | Out-Null
    }
    
    # Start Chrome with chat debug port 9223
    $chromeArgs = @(
        "--remote-debugging-port=9223",
        "--user-data-dir=`"$chatProfilePath`"",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-default-apps",
        "--disable-popup-blocking",
        "--disable-translate",
        "--no-sandbox"
    )
    
    Write-Host "Starting Chrome for chat on port 9223..."
    
    Start-Process -FilePath $chromePath -ArgumentList $chromeArgs -WindowStyle Normal
    
    Write-Host "Chrome chat started successfully"
    exit 0
}
catch {
    Write-Host "Error starting Chrome chat: $($_.Exception.Message)"
    exit 1
}
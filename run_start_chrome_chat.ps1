# Chrome Browser Manager for Chat AI Assistant
# Starts Chrome with debug port for chat scraping

param(
    [int]$Port = 9223,
    [string]$ProfilePath = "chrome_profile_chat",
    [string]$StartUrl = "https://www.upwork.com/messages"
)

$ErrorActionPreference = "Stop"

try {
    # Set UTF-8 encoding
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $env:PYTHONIOENCODING = "utf-8"
    
    Write-Output "Starting Chrome for Chat AI Assistant (Port: $Port)"
    
    # Set working directory
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $scriptDir
    
    # Create profile directory if it doesn't exist
    $fullProfilePath = Join-Path $scriptDir $ProfilePath
    if (-not (Test-Path $fullProfilePath)) {
        New-Item -ItemType Directory -Path $fullProfilePath -Force | Out-Null
        Write-Output "Created profile directory: $fullProfilePath"
    }
    
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
        throw "Chrome executable not found. Please install Google Chrome."
    }
    
    Write-Output "Found Chrome: $chromePath"
    
    # Chrome startup arguments
    $chromeArgs = @(
        "--remote-debugging-port=$Port",
        "--user-data-dir=`"$fullProfilePath`"",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-default-apps",
        "--disable-popup-blocking",
        "--disable-translate",
        "--disable-background-timer-throttling",
        "--disable-renderer-backgrounding",
        "--disable-backgrounding-occluded-windows",
        "--disable-dev-shm-usage",
        "--no-sandbox"
    )
    
    # Add start URL
    if ($StartUrl) {
        $chromeArgs += "`"$StartUrl`""
    }
    
    # Check if Chrome is already running on this port
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:$Port/json/version" -UseBasicParsing -TimeoutSec 5
        Write-Output "Chrome already running on port $Port"
        
        $result = @{
            success      = $true
            port         = $Port
            profile_path = $fullProfilePath
            status       = "already_running"
            debug_url    = "http://localhost:$Port"
            timestamp    = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        }
        
        Write-Output ($result | ConvertTo-Json -Depth 3)
        exit 0
    }
    catch {
        Write-Output "Starting new Chrome instance..."
    }
    
    # Start Chrome
    $process = Start-Process -FilePath $chromePath -ArgumentList $chromeArgs -PassThru
    
    if ($process) {
        Write-Output "Chrome process started with PID: $($process.Id)"
        
        # Wait for Chrome to be ready
        $maxWait = 30
        $waited = 0
        $ready = $false
        
        while ($waited -lt $maxWait -and -not $ready) {
            Start-Sleep -Seconds 1
            $waited++
            
            try {
                $null = Invoke-WebRequest -Uri "http://localhost:$Port/json/version" -UseBasicParsing -TimeoutSec 2
                $ready = $true
                Write-Output "Chrome is ready on port $Port"
            }
            catch {
                Write-Output "Waiting for Chrome to be ready... ($waited/$maxWait)"
            }
        }
        
        if ($ready) {
            $result = @{
                success      = $true
                port         = $Port
                profile_path = $fullProfilePath
                process_id   = $process.Id
                status       = "started"
                debug_url    = "http://localhost:$Port"
                start_url    = $StartUrl
                timestamp    = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
            }
            
            Write-Output ($result | ConvertTo-Json -Depth 3)
            exit 0
        }
        else {
            throw "Chrome failed to start within $maxWait seconds"
        }
    }
    else {
        throw "Failed to start Chrome process"
    }
}
catch {
    $errorObj = @{
        success   = $false
        error     = $_.Exception.Message
        port      = $Port
        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
    }
    
    Write-Output ($errorObj | ConvertTo-Json -Depth 3)
    exit 1
}
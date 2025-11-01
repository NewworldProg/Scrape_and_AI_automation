# Chat AI Generator for n8n - Simple Version
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Set-Location "E:\Repoi\UpworkNotif"
Write-Host "Starting Chat AI Generator..."

try {
    # Activate venv if it exists
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & "venv\Scripts\Activate.ps1"
    }
    
    # Run AI generator
    $process = Start-Process -FilePath "python" -ArgumentList "ai\chat_gpt2_generator.py --session-id latest --type professional" -PassThru -NoNewWindow -Wait
    
    if ($process.ExitCode -eq 0) {
        Write-Host "Chat AI generator completed successfully"
        exit 0
    }
    else {
        Write-Host "Chat AI generator failed with exit code: $($process.ExitCode)"
        exit 1
    }
}
catch {
    Write-Host "Error running chat AI generator: $($_.Exception.Message)"
    exit 1
}
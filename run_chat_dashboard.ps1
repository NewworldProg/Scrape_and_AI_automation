# Chat Dashboard Generator for n8n - Simple Version
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Set-Location "E:\Repoi\UpworkNotif"
Write-Host "Starting Chat Dashboard Generator..."

try {
    # Activate venv if it exists
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & "venv\Scripts\Activate.ps1"
    }
    
    # Run dashboard generator
    $process = Start-Process -FilePath "python" -ArgumentList "scripts\chat_dashboard_generator.py" -PassThru -NoNewWindow -Wait
    
    if ($process.ExitCode -eq 0) {
        Write-Host "Chat dashboard generator completed successfully"
        exit 0
    }
    else {
        Write-Host "Chat dashboard generator failed with exit code: $($process.ExitCode)"
        exit 1
    }
}
catch {
    Write-Host "Error running chat dashboard generator: $($_.Exception.Message)"
    exit 1
}
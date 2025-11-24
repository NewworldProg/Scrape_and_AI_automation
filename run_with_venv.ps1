param(
    [Parameter(Mandatory=$true)][string]$ScriptPath,
    [Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments
)
Write-Host "Running: $ScriptPath" -ForegroundColor Cyan
& "E:\Repoi\UpworkNotif\venv\Scripts\Activate.ps1"
Set-Location "E:\Repoi\UpworkNotif"
if ($Arguments) { & $ScriptPath @Arguments } else { & $ScriptPath }

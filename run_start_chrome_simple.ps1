# Chrome Debug Starter
# log that script is starting
Write-Host "Starting Chrome..."
# inside variable define path to chrome
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
# if chrome path exists start chrome with remote debugging port and user data dir
# make new profile folder with all data
# log if chrome started or not found
if (Test-Path $chrome) {
    Start-Process $chrome "--remote-debugging-port=9222 --user-data-dir=E:\Repoi\UpworkNotif\chrome_profile"
    Write-Host "Chrome started"
}
else {
    Write-Host "Chrome not found"
}

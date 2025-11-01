# Install Chat AI Assistant Requirements
# Installs all necessary Python packages for the Chat AI workflow

$ErrorActionPreference = "Stop"

try {
    Write-Output "Installing Chat AI Assistant Requirements"
    
    # Set working directory
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $scriptDir
    
    # Required packages
    $packages = @(
        "selenium",
        "torch",
        "transformers",
        "beautifulsoup4",
        "requests",
        "pandas",
        "numpy"
    )
    
    Write-Output "Installing Python packages..."
    
    foreach ($package in $packages) {
        Write-Output "Installing $package..."
        & pip install $package --upgrade
        
        if ($LASTEXITCODE -ne 0) {
            Write-Output "Failed to install $package"
            exit 1
        }
    }
    
    Write-Output "All packages installed successfully!"
    
    # Verify installations
    Write-Output "Verifying installations..."
    
    $pythonScript = @"
import sys
try:
    import selenium
    print(f"Selenium: {selenium.__version__}")
    
    import torch
    print(f"PyTorch: {torch.__version__}")
    
    import transformers
    print(f"Transformers: {transformers.__version__}")
    
    import bs4
    print(f"BeautifulSoup4: {bs4.__version__}")
    
    import requests
    print(f"Requests: {requests.__version__}")
    
    import pandas
    print(f"Pandas: {pandas.__version__}")
    
    import numpy
    print(f"NumPy: {numpy.__version__}")
    
    print("\\n All packages verified successfully!")
    
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
"@
    
    $pythonScript | python
    
    if ($LASTEXITCODE -eq 0) {
        Write-Output ""
        Write-Output "Chat AI Assistant requirements installation complete!"
        Write-Output ""
        Write-Output "Next steps:"
        Write-Output "1. Import n8n_chat_ai_workflow.json into n8n"
        Write-Output "2. Run the workflow to start chat monitoring"
        Write-Output "3. Open chat_dashboard.html to view AI suggestions"
        Write-Output ""
    }
    else {
        Write-Output "Package verification failed"
        exit 1
    }
}
catch {
    Write-Output "Installation failed: $($_.Exception.Message)"
    exit 1
}
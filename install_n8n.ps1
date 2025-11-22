# takes parameters from the command line to determine
# dry run, force reinstall, workflows only, and install path with default path "."
param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$WorkflowsOnly,
    [string]$InstallPath = "."
)

# Enhanced N8N Upwork Notification System Installer
# Version 2.0 - Complete Installation with Node.js Dependencies
# log that installer is starting
# give it neon color (foreground cyan)
Write-Host @"

                N8N UPWORK NOTIFICATION SYSTEM                 
                    Enhanced Auto-Installer                       

"@ -ForegroundColor Cyan
# log if dry run is activated which means no changes will be made just checking if steps would succeed
if ($DryRun) {
    Write-Host " DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
    Write-Host ""
}

# Setup paths
# inside var put Get_location function for checking current directory
$originalPath = Get-Location
# inside newBasePath var put Resolve-Path function for getting full path of install location = "."
$newBasePath = Resolve-Path $InstallPath
# make venvPath var Join-Path function newPath + "venv"
$venvPath = Join-Path $newBasePath "venv"

# log installation path that will be used
Write-Host " Installation Path: $newBasePath" -ForegroundColor Green
Write-Host ""

# log STEP 1: NODE.JS DEPENDENCIES
Write-Host " STEP 1: Installing Node.js Dependencies..." -ForegroundColor Magenta

# inside var script to check for Node.js + write log if found or not found
try {
    $nodeVersion = node --version
    Write-Host "   Node.js found: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "   Node.js not found! Please install Node.js first." -ForegroundColor Red
    exit 1
}

# inside dar script to check for npm  + write log if found or not found
try {
    $npmVersion = npm --version
    Write-Host "   npm found: $npmVersion" -ForegroundColor Green
}
catch {
    Write-Host "   npm not found!" -ForegroundColor Red
    exit 1
}

# Install N8N globally if not present
try {
    $n8nVersion = n8n --version
    Write-Host "   N8N already installed: $n8nVersion" -ForegroundColor Green
}
catch {
    Write-Host "   Installing N8N globally..." -ForegroundColor Yellow
    if (-not $DryRun) {
        npm install -g n8n
        Write-Host "   N8N installed successfully" -ForegroundColor Green
    }
}

# Check if package.json exists by joining dir path and package.json if not makes one
# install local dependencies inside package.json if not in DryRun mode
$packageJsonPath = Join-Path $newBasePath "package.json"
if (Test-Path $packageJsonPath) {
    Write-Host "   Installing local Node.js dependencies..." -ForegroundColor Yellow
    if (-not $DryRun) {
        Set-Location $newBasePath
        npm install
        Write-Host "   Local dependencies installed" -ForegroundColor Green
    }
}
else {
    Write-Host "    No package.json found - creating with required dependencies..." -ForegroundColor Yellow
    if (-not $DryRun) {
        Set-Location $newBasePath
        
        # local dependencies that will be added to package.json
        $packageJson = @{
            name            = "upwork-notification-system"
            version         = "1.0.0"
            description     = "Automated job scraping and notification system for Upwork"
            main            = "index.js"
            scripts         = @{
                start  = "node index.js"
                scrape = "node js_scrapers/upwork_scraper.js"
                test   = "echo Error: no test specified"
            }
            repository      = @{
                type = "git"
                url  = "https://github.com/username/upwork-notification-system.git"
            }
            keywords        = @("upwork", "scraping", "automation", "notifications", "n8n")
            author          = "Your Name"
            license         = "MIT"
            dependencies    = @{
                "puppeteer-core"     = "^21.0.0"
                "puppeteer"          = "^21.0.0"
                "selenium-webdriver" = "^4.15.0"
                "cheerio"            = "^1.0.0-rc.12"
                "fs-extra"           = "^11.1.1"
                "axios"              = "^1.6.0"
                "dotenv"             = "^16.3.1"
            }
            devDependencies = @{
                "nodemon" = "^3.0.0"
            }
            engines         = @{
                node = ">=18.0.0"
                npm  = ">=9.0.0"
            }
        }
        
        $packageJson | ConvertTo-Json -Depth 4 | Out-File -FilePath "package.json" -Encoding UTF8
        
        # Install dependencies after creating package.json
        npm install
        Write-Host "   Created package.json and installed dependencies" -ForegroundColor Green
    }
}

# STEP 2: PYTHON VIRTUAL ENVIRONMENT (if not workflows-only)
# if not workflows-only flag is set skip python venv setup
if (-not $WorkflowsOnly) {
    Write-Host "`n STEP 2: Python Virtual Environment..." -ForegroundColor Magenta
    # Check if venv exists
    # if force flag is set delete and recreate
    # if not force flag if venv exists skip creation and tell user that venv exists
    # create venv it it does not exist or force is set inside venvPath
    # activate venv and install packages from requirements.txt or common packages
    # 1. make activateScript with venvPath + Scripts\Activate.ps1
    # 2. activate venv
    # 3. install packages
    if (Test-Path $venvPath) {
        if ($Force) {
            Write-Host "  [DELETE] Removing existing environment..." -ForegroundColor Yellow
            if (-not $DryRun) {
                Remove-Item $venvPath -Recurse -Force
            }
        }
        else {
            Write-Host "   Virtual environment exists (use -Force to recreate)" -ForegroundColor Green
        }
    }
    if (-not (Test-Path $venvPath) -or $Force) {
        Write-Host "   Creating Python virtual environment..." -ForegroundColor Yellow
        if (-not $DryRun) {
            python -m venv $venvPath
            Write-Host "   Virtual environment created" -ForegroundColor Green
            
            # Install Python packages
            Write-Host "   Installing Python packages..." -ForegroundColor Yellow
            $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
            & $activateScript
            
            # Install packages from requirements.txt if exists
            $requirementsPath = Join-Path $newBasePath "requirements.txt"
            if (Test-Path $requirementsPath) {
                pip install -r $requirementsPath
            }
            else {
                # Install common packages
                pip install selenium beautifulsoup4 requests pandas numpy python-dotenv
            }
            
            Write-Host "   Python packages installed" -ForegroundColor Green
        }
    }
    
    # Create helper scripts
    if (-not $DryRun) {
        Write-Host "   Creating helper scripts..." -ForegroundColor Yellow
        
        # Create activate script with venvPath + Scripts\Activate.ps1 + your custom message
        $activateContent = @"
Write-Host "Activating Upwork Notification System..." -ForegroundColor Cyan
& "$venvPath\Scripts\Activate.ps1"
Write-Host "Environment activated! Project: $newBasePath" -ForegroundColor Green
"@
        $activateContent | Out-File -FilePath "activate_env.ps1" -Encoding UTF8
        
        # Create run with venv script
        $runVenvContent = @"
param(
    [Parameter(Mandatory=`$true)][string]`$ScriptPath,
    [Parameter(ValueFromRemainingArguments=`$true)][string[]]`$Arguments
)
Write-Host "Running: `$ScriptPath" -ForegroundColor Cyan
& "$venvPath\Scripts\Activate.ps1"
Set-Location "$newBasePath"
if (`$Arguments) { & `$ScriptPath @Arguments } else { & `$ScriptPath }
"@
        $runVenvContent | Out-File -FilePath "run_with_venv.ps1" -Encoding UTF8
        
        # Create N8N launcher script
        $startN8nContent = @"
Write-Host "Starting N8N..." -ForegroundColor Cyan
Write-Host "N8N will be available at: http://localhost:5678" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop N8N" -ForegroundColor Gray
Write-Host ""

# Set N8N data directory to current project
`$env:N8N_USER_FOLDER = "$newBasePath\.n8n"

# Start N8N
n8n start
"@
        $startN8nContent | Out-File -FilePath "start_n8n.ps1" -Encoding UTF8
        
        Write-Host "   Helper scripts created" -ForegroundColor Green
    }
}

# STEP 3: N8N WORKFLOWS creation
# check for workflow json files in current directory
# count how many are found and log found/missing
Write-Host "`n STEP 3: N8N Workflow Setup..." -ForegroundColor Magenta

$workflowFiles = @(
    "n8n_job_scraper_workflow.json",
    "n8n_ai_cover_letter_workflow.json", 
    "n8n_chat_ai_workflow.json",
    "n8n_database_cleanup_workflow.json",
    "n8n_workflow_conditional.json"
)

$foundWorkflows = 0
$workflowsFound = @()
foreach ($workflow in $workflowFiles) {
    if (Test-Path $workflow) {
        Write-Host "   Found: $workflow" -ForegroundColor Green
        $foundWorkflows++
        $workflowsFound += $workflow
    }
    else {
        Write-Host "    Missing: $workflow" -ForegroundColor Yellow
    }
}
# if any workflows found process them
if ($foundWorkflows -gt 0) {
    Write-Host "   $foundWorkflows workflow(s) found - processing paths..." -ForegroundColor Green
    
    # Create n8n directory and process workflows
    $n8nDir = Join-Path $newBasePath "n8n"
    if (-not $DryRun) {
        if (-not (Test-Path $n8nDir)) {
            New-Item -ItemType Directory -Path $n8nDir -Force | Out-Null
            Write-Host "   Created n8n/ directory" -ForegroundColor Green
        }
        
        # Process each workflow file  
        foreach ($workflow in $workflowsFound) {
            $destinationPath = Join-Path $n8nDir $workflow
            $originalContent = Get-Content $workflow -Raw -Encoding UTF8
            
            # copy original content to content variable for safe manipulation
            # Replace hardcoded paths - safe string replacement
            $content = $originalContent
            $oldPathWindows = "E:\\Repoi\\UpworkNotif"
            $oldPathUnix = "E:/Repoi/UpworkNotif" 
            $newPathJson = $newBasePath -replace '\\', '\\'
            
            # JSON-safe path replacement
            $content = $content.Replace($oldPathWindows, $newPathJson)
            $content = $content.Replace($oldPathUnix, $newPathJson)
            $content = $content.Replace("E:\Repoi\UpworkNotif", $newPathJson)
            
            # Save updated workflow in n8n/ directory and log
            Set-Content -Path $destinationPath -Value $content -Encoding UTF8
            Write-Host "     Processed: $workflow -> n8n/" -ForegroundColor Green
        }
        
        Write-Host "   All workflows updated with correct paths!" -ForegroundColor Cyan
    }
    else {
        Write-Host "   [DRY RUN] Would create n8n/ directory and process $foundWorkflows workflows" -ForegroundColor Cyan
    }
}
else {
    Write-Host "    No workflow files found in current directory" -ForegroundColor Yellow
}

# STEP 4: ENVIRONMENT CONFIGURATION
# makes template for user to copy when they set up their .env file
Write-Host "`n  STEP 4: Environment Configuration..." -ForegroundColor Magenta

if (-not (Test-Path ".env")) {
    Write-Host "   Creating .env template..." -ForegroundColor Yellow
    if (-not $DryRun) {
        $envTemplate = @"
# Upwork Notification System Configuration
# Copy this to .env and fill in your values

# N8N Configuration
N8N_USER_FOLDER=.n8n
N8N_HOST=localhost
N8N_PORT=5678

# Database Configuration (if using)
DATABASE_URL=sqlite://./data/jobs.db

# OpenAI Configuration (for AI features)
OPENAI_API_KEY=your_openai_api_key_here

# Notification Settings
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
EMAIL_FROM=your_email@example.com
EMAIL_TO=target_email@example.com

# Scraping Configuration
SCRAPE_INTERVAL=300
MAX_CONCURRENT_JOBS=5

# Chrome/Browser Configuration
CHROME_EXECUTABLE_PATH=""
HEADLESS_MODE=true
"@
        $envTemplate | Out-File -FilePath ".env.template" -Encoding UTF8
        Write-Host "   Created .env.template" -ForegroundColor Green
    }
}
else {
    Write-Host "   .env file already exists" -ForegroundColor Green
}

# STEP 5: FINAL SETUP AND SUMMARY
# log installation complete and summary of steps done
Write-Host "`n Installation Complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host " Summary:" -ForegroundColor White
Write-Host " Node.js dependencies installed" -ForegroundColor Gray
Write-Host " N8N installed and configured" -ForegroundColor Gray
if (-not $WorkflowsOnly) {
    Write-Host " Python virtual environment ready" -ForegroundColor Gray
    Write-Host " Helper scripts created" -ForegroundColor Gray
}
Write-Host " Environment template created" -ForegroundColor Gray

Write-Host "`n Next Steps:" -ForegroundColor Yellow
Write-Host "1. Copy .env.template to .env and configure your settings" -ForegroundColor White
Write-Host "2. Start N8N: .\start_n8n.ps1" -ForegroundColor White
Write-Host "3. Import workflows from the .json files" -ForegroundColor White
if (-not $WorkflowsOnly) {
    Write-Host "4. Activate Python environment: .\activate_env.ps1" -ForegroundColor White
}

Write-Host "`n Enjoy your Upwork Notification System!" -ForegroundColor Magenta

# Return to original location
Set-Location $originalPath

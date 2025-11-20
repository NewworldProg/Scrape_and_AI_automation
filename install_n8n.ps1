param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$WorkflowsOnly,
    [string]$InstallPath = "."
)

# Enhanced N8N Upwork Notification System Installer
# Version 2.0 - Complete Installation with Node.js Dependencies

Write-Host @"

                N8N UPWORK NOTIFICATION SYSTEM                 
                    Enhanced Auto-Installer                       

"@ -ForegroundColor Cyan

if ($DryRun) {
    Write-Host " DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
    Write-Host ""
}

# Setup paths
$originalPath = Get-Location
$newBasePath = Resolve-Path $InstallPath
$venvPath = Join-Path $newBasePath "venv"

Write-Host " Installation Path: $newBasePath" -ForegroundColor Green
Write-Host ""

# STEP 1: NODE.JS DEPENDENCIES
Write-Host " STEP 1: Installing Node.js Dependencies..." -ForegroundColor Magenta

# Check for Node.js
try {
    $nodeVersion = node --version
    Write-Host "   Node.js found: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "   Node.js not found! Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Check for npm  
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

# Check if package.json exists and install local dependencies
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
        
        # Create comprehensive package.json
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
        
        # Install dependencies
        npm install
        Write-Host "   Created package.json and installed dependencies" -ForegroundColor Green
    }
}

# STEP 2: PYTHON VIRTUAL ENVIRONMENT (if not workflows-only)
if (-not $WorkflowsOnly) {
    Write-Host "`n STEP 2: Python Virtual Environment..." -ForegroundColor Magenta
    
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
        
        # Create activate script
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

# STEP 3: N8N WORKFLOWS
Write-Host "`n STEP 3: N8N Workflow Setup..." -ForegroundColor Magenta

$workflowFiles = @(
    "n8n_job_scraper_workflow.json",
    "n8n_ai_cover_letter_workflow.json", 
    "n8n_chat_ai_workflow.json",
    "n8n_database_cleanup_workflow.json",
    "n8n_workflow_conditional.json"
)

$foundWorkflows = 0
foreach ($workflow in $workflowFiles) {
    if (Test-Path $workflow) {
        Write-Host "   Found: $workflow" -ForegroundColor Green
        $foundWorkflows++
    }
    else {
        Write-Host "    Missing: $workflow" -ForegroundColor Yellow
    }
}

if ($foundWorkflows -gt 0) {
    Write-Host "   $foundWorkflows workflow(s) ready to import into N8N" -ForegroundColor Green
}
else {
    Write-Host "    No workflow files found in current directory" -ForegroundColor Yellow
}

# STEP 4: ENVIRONMENT CONFIGURATION
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

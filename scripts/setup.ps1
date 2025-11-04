# Setup script for Tax Assistant
# Run this script to set up the Python environment and initialize the database

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Tax Assistant Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python installed: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.8 or later." -ForegroundColor Red
    exit 1
}

# Navigate to project directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Split-Path -Parent $scriptPath
Set-Location $projectPath

Write-Host "Project directory: $projectPath" -ForegroundColor Cyan
Write-Host ""

# Create virtual environment if it doesn't exist
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (-Not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host "  Please edit .env file with your configuration" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Initialize database
Write-Host ""
Write-Host "Initializing database..." -ForegroundColor Yellow
python main.py init-db
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database initialized" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to initialize database" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your configuration" -ForegroundColor White
Write-Host "2. Add your entities: python main.py entity add --name 'Your Farm' --type farm" -ForegroundColor White
Write-Host "3. Start adding assets and transactions" -ForegroundColor White
Write-Host ""
Write-Host "For help: python main.py --help" -ForegroundColor Cyan

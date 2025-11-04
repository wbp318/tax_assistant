# Database backup script
# Creates a timestamped backup of the tax assistant database

param(
    [string]$BackupDir = "data\backups",
    [switch]$Compress
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Database Backup Utility" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to project directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Split-Path -Parent $scriptPath
Set-Location $projectPath

# Create backup directory if it doesn't exist
if (-Not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
    Write-Host "✓ Created backup directory: $BackupDir" -ForegroundColor Green
}

# Check if database exists
$dbPath = "data\tax_assistant.db"
if (-Not (Test-Path $dbPath)) {
    Write-Host "✗ Database not found at: $dbPath" -ForegroundColor Red
    exit 1
}

# Create timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupName = "tax_assistant_backup_$timestamp.db"
$backupPath = Join-Path $BackupDir $backupName

# Copy database
Write-Host "Backing up database..." -ForegroundColor Yellow
Write-Host "Source: $dbPath" -ForegroundColor Cyan
Write-Host "Destination: $backupPath" -ForegroundColor Cyan
Write-Host ""

try {
    Copy-Item $dbPath $backupPath -Force
    $backupSize = (Get-Item $backupPath).Length / 1MB
    Write-Host "✓ Backup created successfully" -ForegroundColor Green
    Write-Host "  Size: $([math]::Round($backupSize, 2)) MB" -ForegroundColor Cyan
    Write-Host "  Location: $backupPath" -ForegroundColor Cyan

    # Compress if requested
    if ($Compress) {
        Write-Host ""
        Write-Host "Compressing backup..." -ForegroundColor Yellow
        $zipPath = "$backupPath.zip"
        Compress-Archive -Path $backupPath -DestinationPath $zipPath -Force
        Remove-Item $backupPath
        $zipSize = (Get-Item $zipPath).Length / 1MB
        Write-Host "✓ Backup compressed" -ForegroundColor Green
        Write-Host "  Compressed size: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Cyan
        Write-Host "  Location: $zipPath" -ForegroundColor Cyan
    }

    # Clean up old backups (keep last 10)
    Write-Host ""
    Write-Host "Cleaning up old backups..." -ForegroundColor Yellow
    $backups = Get-ChildItem $BackupDir -Filter "tax_assistant_backup_*" | Sort-Object LastWriteTime -Descending
    if ($backups.Count -gt 10) {
        $toDelete = $backups | Select-Object -Skip 10
        foreach ($file in $toDelete) {
            Remove-Item $file.FullName
            Write-Host "  Deleted old backup: $($file.Name)" -ForegroundColor Gray
        }
        Write-Host "✓ Cleaned up $($toDelete.Count) old backup(s)" -ForegroundColor Green
    } else {
        Write-Host "✓ No old backups to clean up" -ForegroundColor Green
    }

} catch {
    Write-Host "✗ Backup failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Backup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan

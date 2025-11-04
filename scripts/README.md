# PowerShell Scripts

This directory contains PowerShell automation scripts for the Tax Assistant.

## Available Scripts

### setup.ps1
Initial setup script that:
- Creates Python virtual environment
- Installs dependencies
- Creates .env configuration file
- Initializes the database

**Usage:**
```powershell
.\scripts\setup.ps1
```

### backup_database.ps1
Creates timestamped backups of the tax database.

**Usage:**
```powershell
# Basic backup
.\scripts\backup_database.ps1

# Compressed backup
.\scripts\backup_database.ps1 -Compress

# Custom backup directory
.\scripts\backup_database.ps1 -BackupDir "C:\MyBackups"
```

**Features:**
- Timestamped backups
- Optional compression
- Automatic cleanup (keeps last 10 backups)

### generate_year_end_reports.ps1
Generates all tax reports for specified entities and tax year.

**Usage:**
```powershell
# Generate reports for specific entities
.\scripts\generate_year_end_reports.ps1 -Year 2024 -EntityIds 1,2,3

# Generate reports for all entities
.\scripts\generate_year_end_reports.ps1 -Year 2024 -AllEntities

# Generate for previous year (default)
.\scripts\generate_year_end_reports.ps1 -AllEntities
```

## Best Practices

1. **Run setup.ps1 first** when initializing a new installation
2. **Backup regularly** using backup_database.ps1
3. **Generate year-end reports** early to identify missing data
4. **Review .env file** after setup to configure entity names and settings

## Scheduling Automated Tasks

You can use Windows Task Scheduler to automate these scripts:

### Example: Daily Backup
```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\path\to\tax_assistant\scripts\backup_database.ps1 -Compress"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Tax Assistant Backup"
```

### Example: Monthly Reports
```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\path\to\tax_assistant\scripts\generate_year_end_reports.ps1 -AllEntities"
$trigger = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At 9am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Tax Assistant Monthly Reports"
```

## Execution Policy

If you encounter execution policy errors, you may need to adjust PowerShell's execution policy:

```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user (recommended)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run individual scripts with bypass
PowerShell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

## Additional Scripts

You can create additional PowerShell scripts for:
- Importing transactions from CSV/Excel files
- Exporting data to accounting software
- Generating custom reports
- Data validation and error checking
- Integration with external systems

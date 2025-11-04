# Year-end report generation script
# Generates all tax reports for specified entities and tax year

param(
    [Parameter(Mandatory=$false)]
    [int]$Year = (Get-Date).Year - 1,  # Default to previous year

    [Parameter(Mandatory=$false)]
    [int[]]$EntityIds,

    [switch]$AllEntities
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Year-End Report Generator" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tax Year: $Year" -ForegroundColor Yellow
Write-Host ""

# Navigate to project directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Split-Path -Parent $scriptPath
Set-Location $projectPath

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Get entity list if generating for all entities
if ($AllEntities) {
    Write-Host "Fetching all entities..." -ForegroundColor Yellow

    # Get entity list using Python
    $entitiesJson = python -c @"
from modules.entities.entity_manager import EntityManager
from database.database import init_database
import json

init_database()
em = EntityManager()
entities = em.get_all_entities()
entity_data = [{'id': e.id, 'name': e.name} for e in entities]
print(json.dumps(entity_data))
em.close()
"@

    $entities = $entitiesJson | ConvertFrom-Json
    $EntityIds = $entities | ForEach-Object { $_.id }

    Write-Host "Found $($entities.Count) entities" -ForegroundColor Green
    Write-Host ""
}

# Generate reports for each entity
foreach ($entityId in $EntityIds) {
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "Generating reports for Entity ID: $entityId" -ForegroundColor Yellow
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""

    # Schedule F Report
    Write-Host "Generating Schedule F..." -ForegroundColor Yellow
    python main.py report schedule-f --entity-id $entityId --year $Year
    Write-Host ""

    # You can add more report types here as they are implemented
    # python main.py report depreciation --entity-id $entityId --year $Year
    # python main.py report tax-projection --entity-id $entityId --year $Year
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Report Generation Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Reports saved to: reports\" -ForegroundColor Cyan

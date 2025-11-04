# Quick Start Guide - Tax Assistant

Welcome to your comprehensive tax management system for farming operations!

## Initial Setup (One-Time)

### 1. Run the Setup Script

Open PowerShell in the project directory and run:

```powershell
.\scripts\setup.ps1
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Create your .env configuration file
- Initialize the database

### 2. Configure Your Settings

Edit the `.env` file with your specific information:

```
# Update these with your actual entity names
FARM_ENTITY_NAME=Parker Farms
EQUIPMENT_ENTITY_NAME=Parker Equipment Holdings LLC
GRAIN_ENTITY_NAME=Parker Grain Storage LLC

# Tax year
DEFAULT_TAX_YEAR=2024

# Filing status
FILING_STATUS=married_filing_jointly
```

### 3. Create Your Entities

Activate the virtual environment:
```powershell
.\venv\Scripts\activate
```

Add your three business entities:

```bash
# Farm operation
python main.py entity add --name "Parker Farms" --type farm --accounting cash

# Equipment holding company
python main.py entity add --name "Parker Equipment Holdings LLC" --type equipment_holding --accounting accrual --ein XX-XXXXXXX

# Grain bin holding company
python main.py entity add --name "Parker Grain Storage LLC" --type grain_holding --accounting accrual --ein XX-XXXXXXX
```

Verify entities were created:
```bash
python main.py entity list
```

## Daily Usage

### Adding Assets (Equipment, Grain Bins, Buildings)

```bash
# Example: Add a tractor to equipment holding company (Entity ID 2)
python main.py asset add --entity-id 2 --description "John Deere 8R 410 Tractor" --cost 485000 --date 2024-03-15 --macrs-class "7-year" --type Equipment

# Example: Add grain bin to grain storage company (Entity ID 3)
python main.py asset add --entity-id 3 --description "50,000 Bu Grain Bin" --cost 125000 --date 2024-06-01 --macrs-class "10-year" --type "Agricultural Structure"

# List all assets
python main.py asset list

# List assets for specific entity
python main.py asset list --entity-id 2
```

### Recording Income Transactions

```bash
# Grain sales
python main.py transaction add --entity-id 1 --date 2024-10-15 --type income --category grain_sales --amount 285000 --description "Corn sales - 10,000 bushels"

# Government payments
python main.py transaction add --entity-id 1 --date 2024-09-30 --type income --category agricultural_program_payments --amount 45000 --description "ARC-CO payment"

# Crop insurance
python main.py transaction add --entity-id 1 --date 2024-08-20 --type income --category crop_insurance_proceeds --amount 15000 --description "Hail damage claim"
```

### Recording Expense Transactions

```bash
# Fertilizer
python main.py transaction add --entity-id 1 --date 2024-03-20 --type expense --category fertilizers_lime --amount 75000 --description "Spring fertilizer application"

# Seed
python main.py transaction add --entity-id 1 --date 2024-04-05 --type expense --category seeds_plants --amount 45000 --description "Corn and soybean seed"

# Fuel
python main.py transaction add --entity-id 1 --date 2024-06-15 --type expense --category gasoline_fuel_oil --amount 32000 --description "Diesel fuel - planting/harvest"

# Prepaid expense (for next year)
python main.py transaction add --entity-id 1 --date 2024-12-15 --type expense --category fertilizers_lime --amount 50000 --description "Prepaid fertilizer for 2025" --prepaid
```

Common expense categories:
- `fertilizers_lime`
- `seeds_plants`
- `gasoline_fuel_oil`
- `chemicals`
- `feed`
- `repairs_maintenance`
- `labor_hired`
- `rent_land_animals`
- `insurance`
- `taxes`
- `veterinary_breeding_medicine`

## Monthly/Quarterly Tasks

### Review Transaction Summary

```bash
# See income and expense summary for the year
python main.py transaction summary --entity-id 1 --year 2024
```

### Calculate Tax Liability

```bash
# Calculate current tax projection for farm entity
python main.py tax calculate --entity-id 1 --year 2024 --filing-status married_filing_jointly
```

This shows:
- Net farm profit
- Self-employment tax
- Federal income tax
- Louisiana state tax
- Total tax liability
- Effective tax rate

### Generate Reports

```bash
# Schedule F (farm profit/loss)
python main.py report schedule-f --entity-id 1 --year 2024
```

Reports are saved to the `reports/` directory.

## Year-End Tasks

### 1. Generate All Reports

Use the PowerShell script to generate all reports:

```powershell
.\scripts\generate_year_end_reports.ps1 -Year 2024 -AllEntities
```

### 2. Review Prepaid Expenses

Ensure prepaid expenses don't exceed the 50% rule.

### 3. Optimize Section 179 and Bonus Depreciation

Review asset depreciation to maximize tax benefits while staying within limits.

### 4. Backup Your Data

```powershell
.\scripts\backup_database.ps1 -Compress
```

## Tax Planning Scenarios

You can experiment with different scenarios:

1. **Timing grain sales** - Record sales in different years to see tax impact
2. **Prepaid expenses** - Model different prepaid expense amounts
3. **Section 179 elections** - Compare Section 179 vs bonus depreciation

## Common Workflows

### Harvest Season - Recording Grain Sales

```bash
# October grain sales
python main.py transaction add --entity-id 1 --date 2024-10-15 --type income --category grain_sales --amount 285000 --description "Corn - 10,000 bu @ $5.70"

python main.py transaction add --entity-id 1 --date 2024-11-05 --type income --category grain_sales --amount 195000 --description "Soybeans - 5,000 bu @ $11.25"
```

### Equipment Purchase

```bash
# Add equipment to equipment holding company
python main.py asset add --entity-id 2 --description "Case IH Combine 9250" --cost 625000 --date 2024-08-15 --macrs-class "7-year"

# The system automatically calculates:
# - Section 179 deduction (up to $1,220,000)
# - Bonus depreciation (60% in 2024)
# - MACRS depreciation on remaining basis
```

### Monthly Expense Recording

```bash
# Fuel expenses
python main.py transaction add --entity-id 1 --date 2024-07-15 --type expense --category gasoline_fuel_oil --amount 8500

# Labor
python main.py transaction add --entity-id 1 --date 2024-07-31 --type expense --category labor_hired --amount 12000

# Repairs
python main.py transaction add --entity-id 1 --date 2024-07-20 --type expense --category repairs_maintenance --amount 3500
```

## Getting Help

### Command Help

```bash
# General help
python main.py --help

# Entity commands
python main.py entity --help

# Asset commands
python main.py asset --help

# Transaction commands
python main.py transaction --help

# Tax commands
python main.py tax --help

# Report commands
python main.py report --help
```

### View System Log

Check `tax_assistant.log` for detailed operation logs.

## Tips for Success

1. **Enter transactions regularly** - Don't wait until year-end
2. **Categorize accurately** - Use the correct IRS categories
3. **Track all three entities separately** - Keep farm, equipment, and grain operations distinct
4. **Backup frequently** - Use the backup script weekly or monthly
5. **Review quarterly** - Check tax projections every quarter
6. **Mark prepaid expenses** - Use the --prepaid flag for accuracy
7. **Document descriptions** - Add clear descriptions for your CPA

## Tax Compliance Note

This system assists with tax preparation and planning. Always review with your qualified CPA before filing. The calculations follow current tax law for:

- Federal Schedule F
- Section 179 expensing (2024: $1,220,000 limit)
- Bonus depreciation (2024: 60%)
- MACRS depreciation
- Self-employment tax
- Louisiana state tax

---

**Need More Help?**

- Check the main README.md for detailed documentation
- Review the scripts/README.md for automation options
- Consult with your CPA for tax strategy

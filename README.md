# Tax Assistant for Farming Operations

A comprehensive tax management system designed for farming operations with multiple entities, built with expertise in federal and Louisiana state tax codes.

## Features

### Multi-Entity Management
- Farming operation (Schedule F)
- Equipment holding company
- Grain bin holding company
- Consolidated reporting across all entities

### Depreciation & Asset Management
- Section 179 expensing calculations
- Bonus depreciation (100% first-year depreciation)
- MACRS depreciation schedules
- Asset tracking across entities
- Farm equipment classification (3, 5, 7, 10, 15, 20-year property)
- Buildings and improvements

### Income & Expense Tracking
- Cash and accrual basis accounting support
- Farm-specific income categories (grain sales, government payments, crop insurance, etc.)
- Comprehensive expense categorization
- Multi-entity transaction allocation

### Tax Calculations
- Federal Schedule F (Form 1040)
- Form 4562 (Depreciation and Amortization)
- Louisiana state tax calculations
- Self-employment tax calculations
- Estimated quarterly tax projections

### Tax Planning Features
- Income timing scenarios (crop sales, prepaid expenses)
- Section 179 vs. bonus depreciation optimization
- Farm income averaging (3-year)
- Multi-year tax projections

### Reports
- Schedule F ready data export
- Form 4562 depreciation schedules
- Entity P&L and balance sheets
- Tax liability projections
- Quarterly estimated tax worksheets

## Project Structure

```
tax_assistant/
├── config/              # Configuration files
├── database/            # Database models and migrations
├── modules/             # Core functionality modules
│   ├── entities/        # Entity management
│   ├── assets/          # Asset and depreciation tracking
│   ├── transactions/    # Income/expense transactions
│   ├── tax_calc/        # Tax calculation engines
│   └── reports/         # Report generation
├── scripts/             # PowerShell automation scripts
├── data/                # Data storage
│   ├── raw/             # Import data (gitignored)
│   ├── processed/       # Processed data
│   └── backups/         # Database backups
├── reports/             # Generated reports (gitignored)
├── tests/               # Unit and integration tests
└── main.py              # Main application entry point
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   copy .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```bash
   python main.py init-db
   ```

## Usage

### Initialize Entities
```bash
python main.py add-entity "Farm Operation" --type farm
python main.py add-entity "Equipment Holdings LLC" --type equipment_holding
python main.py add-entity "Grain Storage LLC" --type grain_holding
```

### Add Assets
```bash
python main.py add-asset --entity "Equipment Holdings LLC" --description "John Deere 8R Tractor" --cost 450000 --date 2024-03-15 --class 7year
```

### Record Transactions
```bash
python main.py add-transaction --entity "Farm Operation" --type income --category grain_sales --amount 250000 --date 2024-10-15 --description "Corn sales"
```

### Generate Reports
```bash
python main.py generate-report schedule-f --year 2024
python main.py generate-report depreciation --year 2024
python main.py generate-report tax-projection --year 2024
```

## PowerShell Integration

PowerShell scripts are provided for:
- Bulk data import from spreadsheets
- Automated report generation
- Data export to accounting software
- Scheduled backup operations

See `scripts/README.md` for details.

## Tax Compliance Notes

This system is designed to assist with tax preparation and planning. Always consult with a qualified CPA or tax professional before filing tax returns. The calculations are based on:

- IRC (Internal Revenue Code) provisions
- Louisiana Revised Statutes Title 47 (Taxation)
- Current year tax rates and rules
- Agricultural-specific tax provisions

## License

Proprietary - For use by Tap Parker Farms operations only

## Support

For issues or questions, contact your tax advisor or system administrator.

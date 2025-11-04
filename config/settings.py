"""
Configuration settings for the tax assistant application.
Loads from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/data/tax_assistant.db')

# Tax Year
DEFAULT_TAX_YEAR = int(os.getenv('DEFAULT_TAX_YEAR', '2024'))

# Entity Configuration
FARM_ENTITY_NAME = os.getenv('FARM_ENTITY_NAME', 'Parker Farms')
EQUIPMENT_ENTITY_NAME = os.getenv('EQUIPMENT_ENTITY_NAME', 'Parker Equipment Holdings LLC')
GRAIN_ENTITY_NAME = os.getenv('GRAIN_ENTITY_NAME', 'Parker Grain Storage LLC')

# State
STATE = os.getenv('STATE', 'LA')

# Accounting Methods
FARM_ACCOUNTING_METHOD = os.getenv('FARM_ACCOUNTING_METHOD', 'cash')
EQUIPMENT_ACCOUNTING_METHOD = os.getenv('EQUIPMENT_ACCOUNTING_METHOD', 'accrual')
GRAIN_ACCOUNTING_METHOD = os.getenv('GRAIN_ACCOUNTING_METHOD', 'accrual')

# Filing Status
FILING_STATUS = os.getenv('FILING_STATUS', 'married_filing_jointly')
LA_FILING_STATUS = os.getenv('LA_FILING_STATUS', 'married_filing_jointly')

# Reporting
REPORT_OUTPUT_DIR = Path(os.getenv('REPORT_OUTPUT_DIR', str(BASE_DIR / 'reports')))
BACKUP_DIR = Path(os.getenv('BACKUP_DIR', str(BASE_DIR / 'data' / 'backups')))

# Feature Flags
ENABLE_FARM_INCOME_AVERAGING = os.getenv('ENABLE_FARM_INCOME_AVERAGING', 'true').lower() == 'true'
ENABLE_SECTION_179 = os.getenv('ENABLE_SECTION_179', 'true').lower() == 'true'
ENABLE_BONUS_DEPRECIATION = os.getenv('ENABLE_BONUS_DEPRECIATION', 'true').lower() == 'true'

# Ensure directories exist
REPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / 'data').mkdir(parents=True, exist_ok=True)

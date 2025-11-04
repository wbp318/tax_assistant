"""
Tax constants, rates, and thresholds for federal and Louisiana state taxes.
Updated for 2024 tax year.
"""

# ===== FEDERAL TAX RATES (2024) =====

# Income Tax Brackets (Married Filing Jointly)
FEDERAL_TAX_BRACKETS_MFJ_2024 = [
    {'min': 0, 'max': 23200, 'rate': 0.10},
    {'min': 23200, 'max': 94300, 'rate': 0.12},
    {'min': 94300, 'max': 201050, 'rate': 0.22},
    {'min': 201050, 'max': 383900, 'rate': 0.24},
    {'min': 383900, 'max': 487450, 'rate': 0.32},
    {'min': 487450, 'max': 731200, 'rate': 0.35},
    {'min': 731200, 'max': float('inf'), 'rate': 0.37}
]

# Income Tax Brackets (Single)
FEDERAL_TAX_BRACKETS_SINGLE_2024 = [
    {'min': 0, 'max': 11600, 'rate': 0.10},
    {'min': 11600, 'max': 47150, 'rate': 0.12},
    {'min': 47150, 'max': 100525, 'rate': 0.22},
    {'min': 100525, 'max': 191950, 'rate': 0.24},
    {'min': 191950, 'max': 243725, 'rate': 0.32},
    {'min': 243725, 'max': 609350, 'rate': 0.35},
    {'min': 609350, 'max': float('inf'), 'rate': 0.37}
]

# Standard Deductions (2024)
STANDARD_DEDUCTION_2024 = {
    'single': 14600,
    'married_filing_jointly': 29200,
    'married_filing_separately': 14600,
    'head_of_household': 21900
}

# Self-Employment Tax (2024)
SELF_EMPLOYMENT_TAX_RATE = 0.153  # 15.3% (12.4% Social Security + 2.9% Medicare)
SELF_EMPLOYMENT_DEDUCTION = 0.9235  # 92.35% of net earnings subject to SE tax
SOCIAL_SECURITY_WAGE_BASE_2024 = 168600  # Maximum earnings subject to Social Security tax
ADDITIONAL_MEDICARE_TAX_THRESHOLD_MFJ = 250000
ADDITIONAL_MEDICARE_TAX_THRESHOLD_SINGLE = 200000
ADDITIONAL_MEDICARE_TAX_RATE = 0.009  # Additional 0.9% Medicare tax on high earners

# ===== DEPRECIATION RULES =====

# Section 179 Limits (2024)
SECTION_179_LIMIT_2024 = 1220000  # Maximum Section 179 deduction
SECTION_179_PHASE_OUT_THRESHOLD_2024 = 3050000  # Phase-out begins at this equipment investment level

# Bonus Depreciation (2024)
BONUS_DEPRECIATION_RATE_2024 = 0.60  # 60% for 2024 (phasing down from 100%)
BONUS_DEPRECIATION_RATE_2023 = 0.80  # 80% for 2023
BONUS_DEPRECIATION_RATE_2022 = 1.00  # 100% for 2022 and earlier

# MACRS Property Classes (Recovery Periods in years)
MACRS_CLASSES = {
    '3-year': {
        'description': 'Tractors, breeding hogs, breeding sheep',
        'recovery_period': 3,
        'convention': 'half-year',
        'depreciation_method': 'DDB'  # Double Declining Balance
    },
    '5-year': {
        'description': 'Automobiles, trucks, computers, breeding/dairy cattle',
        'recovery_period': 5,
        'convention': 'half-year',
        'depreciation_method': 'DDB'
    },
    '7-year': {
        'description': 'Farm machinery and equipment (not in other classes)',
        'recovery_period': 7,
        'convention': 'half-year',
        'depreciation_method': 'DDB'
    },
    '10-year': {
        'description': 'Single purpose agricultural structures, fruit/nut trees',
        'recovery_period': 10,
        'convention': 'half-year',
        'depreciation_method': 'DDB'
    },
    '15-year': {
        'description': 'Drainage facilities, land improvements',
        'recovery_period': 15,
        'convention': 'half-year',
        'depreciation_method': 'SL'  # Straight Line
    },
    '20-year': {
        'description': 'Farm buildings (not single-purpose)',
        'recovery_period': 20,
        'convention': 'half-year',
        'depreciation_method': 'SL'
    },
    '27.5-year': {
        'description': 'Residential rental property',
        'recovery_period': 27.5,
        'convention': 'mid-month',
        'depreciation_method': 'SL'
    },
    '39-year': {
        'description': 'Nonresidential real property',
        'recovery_period': 39,
        'convention': 'mid-month',
        'depreciation_method': 'SL'
    }
}

# MACRS Depreciation Tables (Half-Year Convention)
# Percentages for each year of the recovery period
MACRS_DEPRECIATION_RATES_HY = {
    3: [0.3333, 0.4445, 0.1481, 0.0741],
    5: [0.2000, 0.3200, 0.1920, 0.1152, 0.1152, 0.0576],
    7: [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446],
    10: [0.1000, 0.1800, 0.1440, 0.1152, 0.0922, 0.0737, 0.0655, 0.0655, 0.0656, 0.0655, 0.0328],
    15: [0.0500, 0.0950, 0.0855, 0.0770, 0.0693, 0.0623, 0.0590, 0.0590, 0.0591, 0.0590,
         0.0591, 0.0590, 0.0591, 0.0590, 0.0591, 0.0295],
    20: [0.0375, 0.0722, 0.0668, 0.0618, 0.0571, 0.0528, 0.0489, 0.0452, 0.0447, 0.0447,
         0.0446, 0.0446, 0.0446, 0.0446, 0.0446, 0.0446, 0.0446, 0.0446, 0.0446, 0.0446, 0.0223]
}

# MACRS Depreciation Rates (Mid-Month Convention) - for real property
MACRS_DEPRECIATION_RATES_MM_27_5 = {
    # First year varies by month placed in service
    'month_1': 0.0303, 'month_2': 0.0273, 'month_3': 0.0242, 'month_4': 0.0212,
    'month_5': 0.0182, 'month_6': 0.0152, 'month_7': 0.0121, 'month_8': 0.0091,
    'month_9': 0.0061, 'month_10': 0.0030, 'month_11': 0.0000, 'month_12': 0.0000,
    'full_year': 0.0364  # Years 2-27
}

# ===== LOUISIANA STATE TAX =====

# Louisiana Income Tax Brackets (2024)
# Louisiana has a graduated income tax with three brackets
LA_TAX_BRACKETS_2024 = [
    {'min': 0, 'max': 12500, 'rate': 0.0185},       # 1.85%
    {'min': 12500, 'max': 50000, 'rate': 0.035},     # 3.5%
    {'min': 50000, 'max': float('inf'), 'rate': 0.0425}  # 4.25%
]

# Louisiana Standard Deduction (2024)
LA_STANDARD_DEDUCTION_2024 = {
    'single': 4500,
    'married_filing_jointly': 9000,
    'married_filing_separately': 4500,
    'head_of_household': 4500
}

# Louisiana Personal Exemption (2024)
LA_PERSONAL_EXEMPTION_2024 = 4500  # Per person
LA_DEPENDENT_EXEMPTION_2024 = 1000  # Per dependent

# Louisiana allows federal deduction for itemized deductions
LA_ALLOWS_FEDERAL_ITEMIZED_DEDUCTION = True

# ===== FARM-SPECIFIC PROVISIONS =====

# Farm Income Averaging
FARM_INCOME_AVERAGING_YEARS = 3  # Can average over 3 prior years

# Agricultural Property Thresholds
FARM_OPTIONAL_METHOD_THRESHOLD = 9060  # 2024 threshold for optional method of SE tax

# Prepaid Farm Expenses
PREPAID_FARM_EXPENSE_LIMIT = 0.50  # 50% rule - can't exceed 50% of other deductible farm expenses

# ===== QUARTERLY ESTIMATED TAX =====

QUARTERLY_TAX_DUE_DATES = {
    'Q1': '04-15',  # January 1 - March 31
    'Q2': '06-15',  # April 1 - May 31
    'Q3': '09-15',  # June 1 - August 31
    'Q4': '01-15'   # September 1 - December 31 (next year)
}

# Safe harbor rules for estimated tax
ESTIMATED_TAX_SAFE_HARBOR_CURRENT = 0.90  # 90% of current year tax
ESTIMATED_TAX_SAFE_HARBOR_PRIOR = 1.00    # 100% of prior year tax (110% if AGI > 150k)
ESTIMATED_TAX_HIGH_INCOME_THRESHOLD = 150000

# ===== TRANSACTION CATEGORIES =====

# Farm Income Categories (Schedule F)
FARM_INCOME_CATEGORIES = [
    'grain_sales',
    'livestock_sales_purchased',
    'livestock_sales_raised',
    'cooperative_distributions',
    'agricultural_program_payments',
    'ccc_loans_reported',
    'ccc_loans_forfeited',
    'crop_insurance_proceeds',
    'custom_hire_income',
    'other_farm_income'
]

# Farm Expense Categories (Schedule F)
FARM_EXPENSE_CATEGORIES = [
    'car_truck_expenses',
    'chemicals',
    'conservation_expenses',
    'custom_hire',
    'depreciation',
    'employee_benefit_programs',
    'feed',
    'fertilizers_lime',
    'freight_trucking',
    'gasoline_fuel_oil',
    'insurance',
    'interest_mortgage',
    'interest_other',
    'labor_hired',
    'pension_profit_sharing',
    'rent_machinery_equipment',
    'rent_land_animals',
    'repairs_maintenance',
    'seeds_plants',
    'storage_warehousing',
    'supplies',
    'taxes',
    'utilities',
    'veterinary_breeding_medicine',
    'other_expenses'
]

def get_tax_brackets(filing_status, year=2024, state=None):
    """
    Get tax brackets for a given filing status and year.

    Args:
        filing_status: 'single', 'married_filing_jointly', etc.
        year: Tax year (default 2024)
        state: State code (e.g., 'LA') for state brackets, None for federal

    Returns:
        List of tax bracket dictionaries
    """
    if state == 'LA':
        return LA_TAX_BRACKETS_2024

    if filing_status == 'married_filing_jointly':
        return FEDERAL_TAX_BRACKETS_MFJ_2024
    elif filing_status == 'single':
        return FEDERAL_TAX_BRACKETS_SINGLE_2024
    else:
        # Default to single for other filing statuses
        return FEDERAL_TAX_BRACKETS_SINGLE_2024

def get_standard_deduction(filing_status, year=2024, state=None):
    """Get standard deduction for filing status and year."""
    if state == 'LA':
        return LA_STANDARD_DEDUCTION_2024.get(filing_status, 0)
    return STANDARD_DEDUCTION_2024.get(filing_status, 0)

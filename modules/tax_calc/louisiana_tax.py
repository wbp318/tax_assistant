"""
Louisiana state tax calculations.
"""

from config.tax_constants import (
    LA_TAX_BRACKETS_2024,
    LA_STANDARD_DEDUCTION_2024,
    LA_PERSONAL_EXEMPTION_2024,
    LA_DEPENDENT_EXEMPTION_2024,
    LA_ALLOWS_FEDERAL_ITEMIZED_DEDUCTION
)
import logging

logger = logging.getLogger(__name__)


class LouisianaTaxCalculator:
    """Calculate Louisiana state income tax."""

    def __init__(self, filing_status='married_filing_jointly', tax_year=2024):
        """
        Initialize Louisiana tax calculator.

        Args:
            filing_status: Filing status
            tax_year: Tax year
        """
        self.filing_status = filing_status
        self.tax_year = tax_year
        self.tax_brackets = LA_TAX_BRACKETS_2024

    def calculate_louisiana_income_tax(self, louisiana_agi, num_exemptions=2,
                                       num_dependents=0, federal_itemized_deductions=0,
                                       use_standard_deduction=True):
        """
        Calculate Louisiana state income tax.

        Louisiana uses federal AGI as starting point, then applies state-specific
        deductions and exemptions.

        Args:
            louisiana_agi: Adjusted Gross Income for Louisiana (typically same as federal AGI)
            num_exemptions: Number of personal exemptions (taxpayer + spouse)
            num_dependents: Number of dependents
            federal_itemized_deductions: Federal itemized deductions (if using)
            use_standard_deduction: Use Louisiana standard deduction vs itemized

        Returns:
            Dictionary with Louisiana tax calculation
        """
        # Determine deduction amount
        if use_standard_deduction:
            if self.filing_status == 'married_filing_jointly':
                deduction = LA_STANDARD_DEDUCTION_2024['married_filing_jointly']
            elif self.filing_status == 'single':
                deduction = LA_STANDARD_DEDUCTION_2024['single']
            else:
                deduction = LA_STANDARD_DEDUCTION_2024.get(self.filing_status, 0)
            deduction_type = 'standard'
        else:
            # Louisiana allows federal itemized deductions (with some modifications)
            deduction = federal_itemized_deductions if LA_ALLOWS_FEDERAL_ITEMIZED_DEDUCTION else 0
            deduction_type = 'itemized'

        # Calculate personal exemptions
        personal_exemptions = num_exemptions * LA_PERSONAL_EXEMPTION_2024
        dependent_exemptions = num_dependents * LA_DEPENDENT_EXEMPTION_2024
        total_exemptions = personal_exemptions + dependent_exemptions

        # Calculate Louisiana taxable income
        la_taxable_income = max(0, louisiana_agi - deduction - total_exemptions)

        # Calculate Louisiana income tax using brackets
        total_tax = 0.0
        brackets_used = []

        for bracket in self.tax_brackets:
            bracket_min = bracket['min']
            bracket_max = bracket['max']
            rate = bracket['rate']

            if la_taxable_income > bracket_min:
                # Calculate taxable amount in this bracket
                if la_taxable_income <= bracket_max:
                    taxable_in_bracket = la_taxable_income - bracket_min
                else:
                    taxable_in_bracket = bracket_max - bracket_min

                tax_in_bracket = taxable_in_bracket * rate

                brackets_used.append({
                    'min': bracket_min,
                    'max': bracket_max,
                    'rate': rate,
                    'rate_percent': f"{rate * 100:.2f}%",
                    'taxable_amount': taxable_in_bracket,
                    'tax': tax_in_bracket
                })

                total_tax += tax_in_bracket

        effective_rate = (total_tax / louisiana_agi) if louisiana_agi > 0 else 0.0

        return {
            'louisiana_agi': louisiana_agi,
            'deduction_type': deduction_type,
            'deduction_amount': deduction,
            'personal_exemptions': personal_exemptions,
            'dependent_exemptions': dependent_exemptions,
            'total_exemptions': total_exemptions,
            'taxable_income': la_taxable_income,
            'total_tax': total_tax,
            'effective_rate': effective_rate,
            'effective_rate_percent': f"{effective_rate * 100:.2f}%",
            'brackets_used': brackets_used
        }

    def calculate_louisiana_farm_tax(self, net_farm_profit, other_income=0.0,
                                    federal_se_tax_deduction=0.0, num_exemptions=2,
                                    num_dependents=0, use_standard_deduction=True,
                                    federal_itemized_deductions=0):
        """
        Calculate Louisiana tax for farm operation.

        Args:
            net_farm_profit: Net profit from farm (Schedule F)
            other_income: Other income (non-farm)
            federal_se_tax_deduction: Deductible portion of federal SE tax
            num_exemptions: Number of personal exemptions
            num_dependents: Number of dependents
            use_standard_deduction: Use standard deduction
            federal_itemized_deductions: Federal itemized deductions

        Returns:
            Complete Louisiana tax calculation
        """
        # Calculate Louisiana AGI (similar to federal but may have state-specific adjustments)
        # For most farm operations, Louisiana AGI = Federal AGI
        la_agi = net_farm_profit + other_income - federal_se_tax_deduction

        # Calculate Louisiana income tax
        la_tax_calc = self.calculate_louisiana_income_tax(
            louisiana_agi=la_agi,
            num_exemptions=num_exemptions,
            num_dependents=num_dependents,
            federal_itemized_deductions=federal_itemized_deductions,
            use_standard_deduction=use_standard_deduction
        )

        return {
            'net_farm_profit': net_farm_profit,
            'other_income': other_income,
            'federal_se_tax_deduction': federal_se_tax_deduction,
            'louisiana_agi': la_agi,
            'tax_calculation': la_tax_calc,
            'total_louisiana_tax': la_tax_calc['total_tax']
        }


class CombinedTaxCalculator:
    """Calculate combined federal and Louisiana state taxes."""

    def __init__(self, filing_status='married_filing_jointly', tax_year=2024):
        """Initialize combined tax calculator."""
        from modules.tax_calc.federal_tax import FederalTaxCalculator

        self.filing_status = filing_status
        self.tax_year = tax_year
        self.federal_calc = FederalTaxCalculator(filing_status, tax_year)
        self.state_calc = LouisianaTaxCalculator(filing_status, tax_year)

    def calculate_combined_tax(self, total_income, total_expenses, depreciation,
                               other_income=0.0, num_exemptions=2, num_dependents=0,
                               use_standard_deduction=True, itemized_deductions=0):
        """
        Calculate combined federal and Louisiana state tax.

        Args:
            total_income: Total farm income
            total_expenses: Total farm expenses
            depreciation: Total depreciation
            other_income: Non-farm income
            num_exemptions: Personal exemptions
            num_dependents: Dependents
            use_standard_deduction: Use standard deduction
            itemized_deductions: Itemized deductions (if not using standard)

        Returns:
            Complete tax calculation for both federal and state
        """
        # Calculate federal tax
        federal_calc = self.federal_calc.calculate_farm_tax_liability(
            total_income=total_income,
            total_expenses=total_expenses,
            depreciation=depreciation,
            other_income=other_income,
            itemized_deductions=itemized_deductions,
            use_standard_deduction=use_standard_deduction
        )

        # Calculate Louisiana tax
        la_calc = self.state_calc.calculate_louisiana_farm_tax(
            net_farm_profit=federal_calc['net_farm_profit'],
            other_income=other_income,
            federal_se_tax_deduction=federal_calc['self_employment_tax']['deductible_se_tax'],
            num_exemptions=num_exemptions,
            num_dependents=num_dependents,
            use_standard_deduction=use_standard_deduction,
            federal_itemized_deductions=itemized_deductions
        )

        # Calculate combined totals
        total_tax_liability = federal_calc['total_federal_tax'] + la_calc['total_louisiana_tax']
        total_income_amount = total_income + other_income

        return {
            'tax_year': self.tax_year,
            'filing_status': self.filing_status,
            'farm_income': total_income,
            'farm_expenses': total_expenses,
            'depreciation': depreciation,
            'other_income': other_income,
            'net_farm_profit': federal_calc['net_farm_profit'],
            'agi': federal_calc['agi'],
            'federal_tax': federal_calc,
            'louisiana_tax': la_calc,
            'total_federal_tax': federal_calc['total_federal_tax'],
            'total_louisiana_tax': la_calc['total_louisiana_tax'],
            'total_tax_liability': total_tax_liability,
            'combined_effective_rate': (total_tax_liability / federal_calc['agi']) if federal_calc['agi'] > 0 else 0.0,
            'combined_effective_rate_percent': f"{((total_tax_liability / federal_calc['agi']) * 100) if federal_calc['agi'] > 0 else 0.0:.2f}%"
        }

"""
Federal tax calculations for farm income.
Includes Schedule F, self-employment tax, and income tax calculations.
"""

from config.tax_constants import (
    get_tax_brackets,
    get_standard_deduction,
    SELF_EMPLOYMENT_TAX_RATE,
    SELF_EMPLOYMENT_DEDUCTION,
    SOCIAL_SECURITY_WAGE_BASE_2024,
    ADDITIONAL_MEDICARE_TAX_THRESHOLD_MFJ,
    ADDITIONAL_MEDICARE_TAX_RATE,
    FARM_INCOME_AVERAGING_YEARS
)
import logging

logger = logging.getLogger(__name__)


class FederalTaxCalculator:
    """Calculate federal taxes for farm operations."""

    def __init__(self, filing_status='married_filing_jointly', tax_year=2024):
        """
        Initialize federal tax calculator.

        Args:
            filing_status: Filing status
            tax_year: Tax year
        """
        self.filing_status = filing_status
        self.tax_year = tax_year
        self.tax_brackets = get_tax_brackets(filing_status, tax_year)
        self.standard_deduction = get_standard_deduction(filing_status, tax_year)

    def calculate_self_employment_tax(self, net_farm_profit):
        """
        Calculate self-employment tax.

        Self-employment tax covers Social Security and Medicare taxes.
        Rate: 15.3% (12.4% Social Security + 2.9% Medicare)
        Only 92.35% of net earnings are subject to SE tax.

        Args:
            net_farm_profit: Net profit from farm operations

        Returns:
            Dictionary with SE tax calculation details
        """
        # Calculate net earnings from self-employment
        net_earnings = net_farm_profit * SELF_EMPLOYMENT_DEDUCTION  # 92.35%

        if net_earnings <= 0:
            return {
                'net_farm_profit': net_farm_profit,
                'net_earnings': 0.0,
                'social_security_tax': 0.0,
                'medicare_tax': 0.0,
                'additional_medicare_tax': 0.0,
                'total_se_tax': 0.0,
                'deductible_se_tax': 0.0
            }

        # Social Security tax (12.4% up to wage base)
        social_security_base = min(net_earnings, SOCIAL_SECURITY_WAGE_BASE_2024)
        social_security_tax = social_security_base * 0.124

        # Medicare tax (2.9% on all earnings)
        medicare_tax = net_earnings * 0.029

        # Additional Medicare tax (0.9% over threshold for high earners)
        additional_medicare_tax = 0.0
        if self.filing_status == 'married_filing_jointly':
            threshold = ADDITIONAL_MEDICARE_TAX_THRESHOLD_MFJ
        else:
            threshold = 200000  # Single/other

        if net_earnings > threshold:
            additional_medicare_tax = (net_earnings - threshold) * ADDITIONAL_MEDICARE_TAX_RATE

        # Total SE tax
        total_se_tax = social_security_tax + medicare_tax + additional_medicare_tax

        # Deductible portion (50% of SE tax)
        deductible_se_tax = total_se_tax * 0.50

        return {
            'net_farm_profit': net_farm_profit,
            'net_earnings': net_earnings,
            'social_security_tax': social_security_tax,
            'social_security_base': social_security_base,
            'medicare_tax': medicare_tax,
            'additional_medicare_tax': additional_medicare_tax,
            'total_se_tax': total_se_tax,
            'deductible_se_tax': deductible_se_tax
        }

    def calculate_income_tax(self, taxable_income):
        """
        Calculate federal income tax using tax brackets.

        Args:
            taxable_income: Taxable income after deductions

        Returns:
            Dictionary with income tax calculation
        """
        if taxable_income <= 0:
            return {
                'taxable_income': 0.0,
                'total_tax': 0.0,
                'effective_rate': 0.0,
                'brackets_used': []
            }

        total_tax = 0.0
        brackets_used = []
        remaining_income = taxable_income

        for bracket in self.tax_brackets:
            bracket_min = bracket['min']
            bracket_max = bracket['max']
            rate = bracket['rate']

            # Calculate income in this bracket
            if remaining_income <= 0:
                break

            if taxable_income > bracket_min:
                # Income falls in this bracket
                taxable_in_bracket = min(
                    remaining_income,
                    bracket_max - bracket_min
                )
                tax_in_bracket = taxable_in_bracket * rate

                brackets_used.append({
                    'min': bracket_min,
                    'max': bracket_max,
                    'rate': rate,
                    'taxable_amount': taxable_in_bracket,
                    'tax': tax_in_bracket
                })

                total_tax += tax_in_bracket
                remaining_income -= taxable_in_bracket

        effective_rate = (total_tax / taxable_income) if taxable_income > 0 else 0.0

        return {
            'taxable_income': taxable_income,
            'total_tax': total_tax,
            'effective_rate': effective_rate,
            'brackets_used': brackets_used
        }

    def calculate_farm_tax_liability(self, total_income, total_expenses, depreciation,
                                    other_income=0.0, itemized_deductions=0.0,
                                    exemptions=0, use_standard_deduction=True):
        """
        Calculate complete federal tax liability for farm operation.

        Args:
            total_income: Total farm income
            total_expenses: Total farm expenses (excluding depreciation)
            depreciation: Total depreciation (including Section 179, bonus, MACRS)
            other_income: Non-farm income
            itemized_deductions: Itemized deductions (if not using standard deduction)
            exemptions: Number of exemptions/dependents
            use_standard_deduction: Use standard deduction vs itemized

        Returns:
            Complete tax calculation dictionary
        """
        # Calculate net farm profit (Schedule F)
        total_deductions = total_expenses + depreciation
        net_farm_profit = total_income - total_deductions

        # Calculate self-employment tax
        se_tax_calc = self.calculate_self_employment_tax(net_farm_profit)

        # Calculate Adjusted Gross Income (AGI)
        agi = net_farm_profit + other_income - se_tax_calc['deductible_se_tax']

        # Calculate deductions
        if use_standard_deduction:
            deduction = self.standard_deduction
            deduction_type = 'standard'
        else:
            deduction = itemized_deductions
            deduction_type = 'itemized'

        # Calculate taxable income
        taxable_income = max(0, agi - deduction)

        # Calculate income tax
        income_tax_calc = self.calculate_income_tax(taxable_income)

        # Total federal tax liability
        total_federal_tax = income_tax_calc['total_tax'] + se_tax_calc['total_se_tax']

        return {
            'farm_income': total_income,
            'farm_expenses': total_expenses,
            'depreciation': depreciation,
            'total_farm_deductions': total_deductions,
            'net_farm_profit': net_farm_profit,
            'other_income': other_income,
            'self_employment_tax': se_tax_calc,
            'agi': agi,
            'deduction_type': deduction_type,
            'deduction_amount': deduction,
            'taxable_income': taxable_income,
            'income_tax': income_tax_calc,
            'total_federal_tax': total_federal_tax,
            'effective_total_rate': (total_federal_tax / agi) if agi > 0 else 0.0
        }

    def calculate_farm_income_averaging(self, current_year_income, prior_year_incomes):
        """
        Calculate tax using farm income averaging.

        Farm income averaging allows farmers to average income over the prior
        3 years to reduce tax impact of fluctuating income.

        Args:
            current_year_income: Net farm income for current year
            prior_year_incomes: List of net farm income for prior 3 years [year-3, year-2, year-1]

        Returns:
            Dictionary with income averaging calculation
        """
        if len(prior_year_incomes) != 3:
            raise ValueError("Must provide exactly 3 prior years of income")

        # Calculate average of prior 3 years
        avg_prior_income = sum(prior_year_incomes) / 3

        # Calculate elected farm income (amount to average)
        # This is typically the excess of current year over the 3-year average
        elected_farm_income = max(0, current_year_income - avg_prior_income)

        # Allocate elected farm income to prior 3 years
        allocated_to_each_year = elected_farm_income / 3

        return {
            'current_year_income': current_year_income,
            'prior_year_incomes': prior_year_incomes,
            'average_prior_income': avg_prior_income,
            'elected_farm_income': elected_farm_income,
            'allocated_per_year': allocated_to_each_year,
            'note': 'This calculation provides the basics. Complete Schedule J calculation requires prior year tax returns.'
        }

    def estimate_quarterly_taxes(self, estimated_annual_tax, payments_made=None):
        """
        Estimate quarterly tax payments.

        Args:
            estimated_annual_tax: Estimated annual tax liability
            payments_made: List of quarterly payments already made

        Returns:
            Dictionary with quarterly payment schedule
        """
        if payments_made is None:
            payments_made = [0, 0, 0, 0]

        quarterly_amount = estimated_annual_tax / 4
        total_paid = sum(payments_made)
        remaining = max(0, estimated_annual_tax - total_paid)

        quarters_remaining = 4 - len([p for p in payments_made if p > 0])
        if quarters_remaining > 0:
            recommended_next_payment = remaining / quarters_remaining
        else:
            recommended_next_payment = 0

        return {
            'estimated_annual_tax': estimated_annual_tax,
            'quarterly_amount': quarterly_amount,
            'payments_made': payments_made,
            'total_paid': total_paid,
            'remaining_due': remaining,
            'recommended_next_payment': recommended_next_payment,
            'payment_schedule': {
                'Q1': quarterly_amount,
                'Q2': quarterly_amount,
                'Q3': quarterly_amount,
                'Q4': quarterly_amount
            }
        }

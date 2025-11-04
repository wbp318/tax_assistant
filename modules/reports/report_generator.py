"""
Report generation for tax documents and summaries.
"""

from datetime import datetime
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate tax reports and summaries."""

    def __init__(self, output_dir='reports'):
        """
        Initialize report generator.

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_schedule_f_summary(self, entity_name, tax_year, income_summary,
                                    expense_summary, depreciation, net_profit):
        """
        Generate Schedule F summary report.

        Args:
            entity_name: Name of farm entity
            tax_year: Tax year
            income_summary: Income summary dict
            expense_summary: Expense summary dict
            depreciation: Total depreciation
            net_profit: Net farm profit

        Returns:
            Report text
        """
        report = []
        report.append("=" * 80)
        report.append(f"SCHEDULE F - PROFIT OR LOSS FROM FARMING")
        report.append(f"Entity: {entity_name}")
        report.append(f"Tax Year: {tax_year}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")

        # PART I - FARM INCOME
        report.append("PART I - FARM INCOME")
        report.append("-" * 80)

        total_income = 0.0
        for category, amount in income_summary.get('by_category', {}).items():
            category_display = category.replace('_', ' ').title()
            report.append(f"  {category_display:<50} ${amount:>15,.2f}")
            total_income += amount

        report.append("-" * 80)
        report.append(f"  {'TOTAL INCOME':<50} ${total_income:>15,.2f}")
        report.append("")

        # PART II - FARM EXPENSES
        report.append("PART II - FARM EXPENSES")
        report.append("-" * 80)

        total_expenses = 0.0
        for category, amount in expense_summary.get('by_category', {}).items():
            category_display = category.replace('_', ' ').title()
            report.append(f"  {category_display:<50} ${amount:>15,.2f}")
            total_expenses += amount

        # Add depreciation
        report.append(f"  {'Depreciation':<50} ${depreciation:>15,.2f}")
        total_expenses += depreciation

        report.append("-" * 80)
        report.append(f"  {'TOTAL EXPENSES':<50} ${total_expenses:>15,.2f}")
        report.append("")

        # PART III - NET PROFIT OR LOSS
        report.append("PART III - NET FARM PROFIT OR (LOSS)")
        report.append("-" * 80)
        report.append(f"  {'Net Farm Profit (Loss)':<50} ${net_profit:>15,.2f}")
        report.append("=" * 80)

        return "\n".join(report)

    def generate_depreciation_report(self, entity_name, tax_year, assets_depreciation):
        """
        Generate Form 4562 depreciation summary.

        Args:
            entity_name: Entity name
            tax_year: Tax year
            assets_depreciation: List of asset depreciation details

        Returns:
            Report text
        """
        report = []
        report.append("=" * 100)
        report.append(f"FORM 4562 - DEPRECIATION AND AMORTIZATION")
        report.append(f"Entity: {entity_name}")
        report.append(f"Tax Year: {tax_year}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 100)
        report.append("")

        # Summary totals
        total_section_179 = 0.0
        total_bonus = 0.0
        total_macrs = 0.0

        # Asset details
        report.append("ASSET DEPRECIATION DETAILS")
        report.append("-" * 100)
        report.append(f"{'Description':<30} {'Class':<10} {'Section 179':>15} {'Bonus':>15} {'MACRS':>15} {'Total':>15}")
        report.append("-" * 100)

        for asset in assets_depreciation:
            desc = asset.get('description', '')[:28]
            macrs_class = asset.get('macrs_class', '')
            s179 = asset.get('section_179', 0.0)
            bonus = asset.get('bonus_depreciation', 0.0)
            macrs = asset.get('macrs_depreciation', 0.0)
            total = s179 + bonus + macrs

            report.append(f"{desc:<30} {macrs_class:<10} ${s179:>14,.2f} ${bonus:>14,.2f} ${macrs:>14,.2f} ${total:>14,.2f}")

            total_section_179 += s179
            total_bonus += bonus
            total_macrs += macrs

        report.append("-" * 100)
        report.append(f"{'TOTALS':<30} {'':<10} ${total_section_179:>14,.2f} ${total_bonus:>14,.2f} ${total_macrs:>14,.2f} ${total_section_179 + total_bonus + total_macrs:>14,.2f}")
        report.append("=" * 100)

        return "\n".join(report)

    def generate_tax_projection_report(self, tax_year, combined_tax_calc):
        """
        Generate tax projection/liability report.

        Args:
            tax_year: Tax year
            combined_tax_calc: Combined tax calculation dict

        Returns:
            Report text
        """
        report = []
        report.append("=" * 80)
        report.append(f"TAX PROJECTION AND LIABILITY SUMMARY")
        report.append(f"Tax Year: {tax_year}")
        report.append(f"Filing Status: {combined_tax_calc.get('filing_status', '').replace('_', ' ').title()}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")

        # Farm income summary
        report.append("FARM INCOME SUMMARY")
        report.append("-" * 80)
        report.append(f"  {'Gross Farm Income':<50} ${combined_tax_calc.get('farm_income', 0):>15,.2f}")
        report.append(f"  {'Farm Expenses':<50} ${combined_tax_calc.get('farm_expenses', 0):>15,.2f}")
        report.append(f"  {'Depreciation':<50} ${combined_tax_calc.get('depreciation', 0):>15,.2f}")
        report.append(f"  {'Net Farm Profit':<50} ${combined_tax_calc.get('net_farm_profit', 0):>15,.2f}")
        report.append(f"  {'Other Income':<50} ${combined_tax_calc.get('other_income', 0):>15,.2f}")
        report.append(f"  {'Adjusted Gross Income (AGI)':<50} ${combined_tax_calc.get('agi', 0):>15,.2f}")
        report.append("")

        # Federal tax
        federal = combined_tax_calc.get('federal_tax', {})
        se_tax = federal.get('self_employment_tax', {})

        report.append("FEDERAL TAX")
        report.append("-" * 80)
        report.append(f"  {'Self-Employment Tax:':<50}")
        report.append(f"    {'Social Security':<48} ${se_tax.get('social_security_tax', 0):>15,.2f}")
        report.append(f"    {'Medicare':<48} ${se_tax.get('medicare_tax', 0):>15,.2f}")
        report.append(f"    {'Total SE Tax':<48} ${se_tax.get('total_se_tax', 0):>15,.2f}")
        report.append("")
        report.append(f"  {'Taxable Income':<50} ${federal.get('taxable_income', 0):>15,.2f}")
        income_tax = federal.get('income_tax', {})
        report.append(f"  {'Income Tax':<50} ${income_tax.get('total_tax', 0):>15,.2f}")
        report.append(f"  {'Total Federal Tax':<50} ${combined_tax_calc.get('total_federal_tax', 0):>15,.2f}")
        report.append("")

        # Louisiana tax
        la_tax = combined_tax_calc.get('louisiana_tax', {})
        la_calc = la_tax.get('tax_calculation', {})

        report.append("LOUISIANA STATE TAX")
        report.append("-" * 80)
        report.append(f"  {'Louisiana AGI':<50} ${la_calc.get('louisiana_agi', 0):>15,.2f}")
        report.append(f"  {'Deductions':<50} ${la_calc.get('deduction_amount', 0):>15,.2f}")
        report.append(f"  {'Exemptions':<50} ${la_calc.get('total_exemptions', 0):>15,.2f}")
        report.append(f"  {'Taxable Income':<50} ${la_calc.get('taxable_income', 0):>15,.2f}")
        report.append(f"  {'Louisiana Income Tax':<50} ${combined_tax_calc.get('total_louisiana_tax', 0):>15,.2f}")
        report.append("")

        # Total
        report.append("TOTAL TAX LIABILITY")
        report.append("=" * 80)
        report.append(f"  {'Total Federal Tax':<50} ${combined_tax_calc.get('total_federal_tax', 0):>15,.2f}")
        report.append(f"  {'Total Louisiana Tax':<50} ${combined_tax_calc.get('total_louisiana_tax', 0):>15,.2f}")
        report.append("-" * 80)
        report.append(f"  {'TOTAL TAX LIABILITY':<50} ${combined_tax_calc.get('total_tax_liability', 0):>15,.2f}")
        report.append(f"  {'Combined Effective Rate':<50} {combined_tax_calc.get('combined_effective_rate_percent', '0.00%'):>16}")
        report.append("=" * 80)

        return "\n".join(report)

    def save_report(self, filename, content):
        """
        Save report to file.

        Args:
            filename: Filename (without path)
            content: Report content

        Returns:
            Path to saved file
        """
        filepath = self.output_dir / filename

        try:
            with open(filepath, 'w') as f:
                f.write(content)
            logger.info(f"Report saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            raise

    def save_json_report(self, filename, data):
        """
        Save report data as JSON.

        Args:
            filename: Filename (without path)
            data: Data to save

        Returns:
            Path to saved file
        """
        filepath = self.output_dir / filename

        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"JSON report saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save JSON report: {e}")
            raise

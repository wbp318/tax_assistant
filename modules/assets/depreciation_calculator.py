"""
Depreciation calculation engine.
Handles Section 179, Bonus Depreciation, and MACRS calculations.
"""

from config.tax_constants import (
    SECTION_179_LIMIT_2024,
    SECTION_179_PHASE_OUT_THRESHOLD_2024,
    BONUS_DEPRECIATION_RATE_2024,
    BONUS_DEPRECIATION_RATE_2023,
    BONUS_DEPRECIATION_RATE_2022,
    MACRS_CLASSES,
    MACRS_DEPRECIATION_RATES_HY
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DepreciationCalculator:
    """Calculate depreciation for assets using various methods."""

    def __init__(self, tax_year=2024):
        """
        Initialize depreciation calculator.

        Args:
            tax_year: Tax year for calculations
        """
        self.tax_year = tax_year

    def get_bonus_depreciation_rate(self, tax_year=None):
        """
        Get bonus depreciation rate for a given tax year.

        Args:
            tax_year: Tax year (default to instance tax_year)

        Returns:
            Bonus depreciation rate (0.0 to 1.0)
        """
        year = tax_year or self.tax_year

        if year >= 2024:
            return BONUS_DEPRECIATION_RATE_2024  # 60%
        elif year == 2023:
            return BONUS_DEPRECIATION_RATE_2023  # 80%
        else:
            return BONUS_DEPRECIATION_RATE_2022  # 100%

    def calculate_section_179(self, asset_cost, total_equipment_placed=None, elected_amount=None):
        """
        Calculate Section 179 deduction.

        Section 179 allows immediate expensing of qualified property up to a limit.
        The deduction phases out dollar-for-dollar once total equipment placed in service
        exceeds the threshold.

        Args:
            asset_cost: Cost of the individual asset
            total_equipment_placed: Total equipment placed in service this year (for phase-out)
            elected_amount: Specific amount to elect (if None, maximize)

        Returns:
            Dictionary with Section 179 calculation details
        """
        # Maximum Section 179 deduction for the year
        max_deduction = SECTION_179_LIMIT_2024

        # Check for phase-out
        if total_equipment_placed and total_equipment_placed > SECTION_179_PHASE_OUT_THRESHOLD_2024:
            excess = total_equipment_placed - SECTION_179_PHASE_OUT_THRESHOLD_2024
            max_deduction = max(0, max_deduction - excess)

        # Determine Section 179 amount
        if elected_amount is not None:
            section_179_amount = min(elected_amount, asset_cost, max_deduction)
        else:
            # Maximize Section 179 (up to asset cost and limit)
            section_179_amount = min(asset_cost, max_deduction)

        remaining_basis = asset_cost - section_179_amount

        return {
            'section_179_amount': section_179_amount,
            'remaining_basis': remaining_basis,
            'max_available': max_deduction,
            'fully_expensed': section_179_amount == asset_cost
        }

    def calculate_bonus_depreciation(self, remaining_basis, placed_in_service_date=None):
        """
        Calculate bonus depreciation.

        Bonus depreciation is taken after Section 179 and before MACRS.
        The rate varies by year and is being phased down.

        Args:
            remaining_basis: Asset basis after Section 179
            placed_in_service_date: Date asset was placed in service

        Returns:
            Dictionary with bonus depreciation details
        """
        # Determine bonus rate based on placed in service year
        if placed_in_service_date:
            year = placed_in_service_date.year
        else:
            year = self.tax_year

        bonus_rate = self.get_bonus_depreciation_rate(year)
        bonus_amount = remaining_basis * bonus_rate
        remaining_basis_after_bonus = remaining_basis - bonus_amount

        return {
            'bonus_amount': bonus_amount,
            'bonus_rate': bonus_rate,
            'remaining_basis': remaining_basis_after_bonus,
            'fully_depreciated': bonus_amount == remaining_basis
        }

    def calculate_macrs_depreciation(self, asset_basis, macrs_class, year_in_service,
                                    current_year=None, placed_in_service_date=None):
        """
        Calculate MACRS depreciation for a given year.

        Args:
            asset_basis: Asset basis for MACRS (after Section 179 and bonus)
            macrs_class: MACRS class (e.g., '3-year', '5-year', '7-year')
            year_in_service: Which year of the asset's recovery period (1, 2, 3, ...)
            current_year: Current tax year for calculation
            placed_in_service_date: Date asset was placed in service

        Returns:
            Dictionary with MACRS depreciation details
        """
        if asset_basis <= 0:
            return {
                'macrs_amount': 0.0,
                'depreciation_rate': 0.0,
                'year_in_service': year_in_service,
                'fully_depreciated': True
            }

        # Get MACRS class information
        if macrs_class not in MACRS_CLASSES:
            raise ValueError(f"Invalid MACRS class: {macrs_class}")

        class_info = MACRS_CLASSES[macrs_class]
        recovery_period = int(class_info['recovery_period'])

        # Get depreciation rate for this year
        # Note: MACRS tables are 0-indexed, so year_in_service=1 uses index 0
        if recovery_period in MACRS_DEPRECIATION_RATES_HY:
            rates = MACRS_DEPRECIATION_RATES_HY[recovery_period]
            rate_index = year_in_service - 1

            if rate_index < len(rates):
                depreciation_rate = rates[rate_index]
            else:
                depreciation_rate = 0.0  # Fully depreciated
        else:
            # For classes not in the table, use straight-line
            depreciation_rate = 1.0 / recovery_period

        macrs_amount = asset_basis * depreciation_rate

        return {
            'macrs_amount': macrs_amount,
            'depreciation_rate': depreciation_rate,
            'year_in_service': year_in_service,
            'recovery_period': recovery_period,
            'fully_depreciated': year_in_service > len(MACRS_DEPRECIATION_RATES_HY.get(recovery_period, []))
        }

    def calculate_total_depreciation(self, asset_cost, macrs_class, placed_in_service_date,
                                    tax_year=None, use_section_179=True, section_179_amount=None,
                                    use_bonus=True, total_equipment_placed=None):
        """
        Calculate total first-year depreciation for an asset.

        This combines Section 179, Bonus Depreciation, and MACRS.

        Args:
            asset_cost: Original cost of asset
            macrs_class: MACRS classification
            placed_in_service_date: Date placed in service
            tax_year: Tax year for calculation
            use_section_179: Whether to use Section 179
            section_179_amount: Specific Section 179 amount (None = maximize)
            use_bonus: Whether to use bonus depreciation
            total_equipment_placed: Total equipment for Section 179 phase-out

        Returns:
            Dictionary with complete depreciation breakdown
        """
        year = tax_year or self.tax_year
        result = {
            'asset_cost': asset_cost,
            'tax_year': year,
            'section_179': 0.0,
            'bonus_depreciation': 0.0,
            'macrs_depreciation': 0.0,
            'total_depreciation': 0.0,
            'remaining_basis': asset_cost
        }

        current_basis = asset_cost

        # Step 1: Section 179 (if elected)
        if use_section_179 and current_basis > 0:
            s179_calc = self.calculate_section_179(
                current_basis,
                total_equipment_placed,
                section_179_amount
            )
            result['section_179'] = s179_calc['section_179_amount']
            current_basis = s179_calc['remaining_basis']

        # Step 2: Bonus Depreciation (if elected and applicable)
        if use_bonus and current_basis > 0:
            bonus_calc = self.calculate_bonus_depreciation(
                current_basis,
                placed_in_service_date
            )
            result['bonus_depreciation'] = bonus_calc['bonus_amount']
            result['bonus_rate'] = bonus_calc['bonus_rate']
            current_basis = bonus_calc['remaining_basis']

        # Step 3: MACRS Depreciation on remaining basis
        if current_basis > 0:
            macrs_calc = self.calculate_macrs_depreciation(
                current_basis,
                macrs_class,
                year_in_service=1,
                current_year=year,
                placed_in_service_date=placed_in_service_date
            )
            result['macrs_depreciation'] = macrs_calc['macrs_amount']
            result['macrs_rate'] = macrs_calc['depreciation_rate']
            current_basis -= macrs_calc['macrs_amount']

        # Calculate totals
        result['total_depreciation'] = (
            result['section_179'] +
            result['bonus_depreciation'] +
            result['macrs_depreciation']
        )
        result['remaining_basis'] = current_basis
        result['basis_for_future_macrs'] = asset_cost - result['section_179'] - result['bonus_depreciation']

        return result

    def calculate_annual_depreciation_schedule(self, asset_cost, macrs_class,
                                               placed_in_service_date, first_year_section_179=0.0,
                                               first_year_bonus=0.0, years_to_project=None):
        """
        Calculate multi-year depreciation schedule for an asset.

        Args:
            asset_cost: Original asset cost
            macrs_class: MACRS class
            placed_in_service_date: Date placed in service
            first_year_section_179: Section 179 taken in first year
            first_year_bonus: Bonus depreciation taken in first year
            years_to_project: Number of years to project (None = full recovery)

        Returns:
            List of dictionaries with yearly depreciation
        """
        if macrs_class not in MACRS_CLASSES:
            raise ValueError(f"Invalid MACRS class: {macrs_class}")

        recovery_period = int(MACRS_CLASSES[macrs_class]['recovery_period'])

        # MACRS tables typically have recovery_period + 1 entries due to half-year convention
        if years_to_project is None:
            years_to_project = recovery_period + 1

        # Calculate basis for MACRS (after Section 179 and Bonus)
        macrs_basis = asset_cost - first_year_section_179 - first_year_bonus

        schedule = []
        remaining_book_value = asset_cost
        placed_year = placed_in_service_date.year

        for year_number in range(1, years_to_project + 1):
            year_data = {
                'year': placed_year + year_number - 1,
                'year_in_service': year_number,
                'beginning_book_value': remaining_book_value
            }

            # First year includes Section 179 and Bonus
            if year_number == 1:
                year_data['section_179'] = first_year_section_179
                year_data['bonus_depreciation'] = first_year_bonus

                # First year MACRS
                if macrs_basis > 0:
                    macrs_calc = self.calculate_macrs_depreciation(
                        macrs_basis, macrs_class, year_number
                    )
                    year_data['macrs_depreciation'] = macrs_calc['macrs_amount']
                else:
                    year_data['macrs_depreciation'] = 0.0
            else:
                # Subsequent years - only MACRS
                year_data['section_179'] = 0.0
                year_data['bonus_depreciation'] = 0.0

                if macrs_basis > 0:
                    macrs_calc = self.calculate_macrs_depreciation(
                        macrs_basis, macrs_class, year_number
                    )
                    year_data['macrs_depreciation'] = macrs_calc['macrs_amount']
                else:
                    year_data['macrs_depreciation'] = 0.0

            # Calculate totals
            year_data['total_depreciation'] = (
                year_data.get('section_179', 0.0) +
                year_data.get('bonus_depreciation', 0.0) +
                year_data['macrs_depreciation']
            )

            remaining_book_value -= year_data['total_depreciation']
            year_data['ending_book_value'] = max(0, remaining_book_value)

            schedule.append(year_data)

            # Stop if fully depreciated
            if remaining_book_value <= 0:
                break

        return schedule

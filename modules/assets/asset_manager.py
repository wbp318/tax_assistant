"""
Asset management for tracking equipment, buildings, and other depreciable property.
"""

from database.models import Asset, DepreciationSchedule
from database.database import get_session
from modules.assets.depreciation_calculator import DepreciationCalculator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AssetManager:
    """Manage assets and depreciation schedules."""

    def __init__(self):
        self.session = get_session()
        self.depreciation_calc = DepreciationCalculator()

    def add_asset(self, entity_id, description, purchase_price, purchase_date,
                  macrs_class, asset_type=None, in_service_date=None,
                  salvage_value=0.0, notes=None, auto_calculate_depreciation=True,
                  use_section_179=True, section_179_amount=None, use_bonus=True):
        """
        Add a new asset.

        Args:
            entity_id: ID of owning entity
            description: Asset description
            purchase_price: Purchase price
            purchase_date: Purchase date
            macrs_class: MACRS class (3-year, 5-year, 7-year, etc.)
            asset_type: Type of asset (Equipment, Building, etc.)
            in_service_date: Date placed in service (defaults to purchase_date)
            salvage_value: Expected salvage value
            notes: Additional notes
            auto_calculate_depreciation: Auto-calculate first year depreciation
            use_section_179: Use Section 179 expensing
            section_179_amount: Specific Section 179 amount
            use_bonus: Use bonus depreciation

        Returns:
            Asset object
        """
        try:
            if in_service_date is None:
                in_service_date = purchase_date

            asset = Asset(
                entity_id=entity_id,
                description=description,
                asset_type=asset_type or 'Equipment',
                purchase_date=purchase_date,
                purchase_price=purchase_price,
                salvage_value=salvage_value,
                macrs_class=macrs_class,
                in_service_date=in_service_date,
                current_book_value=purchase_price,
                notes=notes
            )

            # Auto-calculate first year depreciation if requested
            if auto_calculate_depreciation:
                first_year = in_service_date.year
                depreciation = self.depreciation_calc.calculate_total_depreciation(
                    asset_cost=purchase_price,
                    macrs_class=macrs_class,
                    placed_in_service_date=in_service_date,
                    tax_year=first_year,
                    use_section_179=use_section_179,
                    section_179_amount=section_179_amount,
                    use_bonus=use_bonus
                )

                asset.section_179_amount = depreciation['section_179']
                asset.bonus_depreciation_amount = depreciation['bonus_depreciation']

                # Create first year depreciation schedule
                schedule = DepreciationSchedule(
                    asset=asset,
                    tax_year=first_year,
                    section_179_deduction=depreciation['section_179'],
                    bonus_depreciation=depreciation['bonus_depreciation'],
                    macrs_depreciation=depreciation['macrs_depreciation'],
                    total_depreciation=depreciation['total_depreciation'],
                    beginning_book_value=purchase_price,
                    ending_book_value=depreciation['remaining_basis']
                )

                asset.depreciation_schedules.append(schedule)
                asset.accumulated_depreciation = depreciation['total_depreciation']
                asset.current_book_value = depreciation['remaining_basis']

            self.session.add(asset)
            self.session.commit()
            logger.info(f"Added asset: {description} for entity {entity_id}")
            return asset

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to add asset: {e}")
            raise

    def get_asset(self, asset_id):
        """Get asset by ID."""
        return self.session.query(Asset).filter_by(id=asset_id).first()

    def get_assets_by_entity(self, entity_id, active_only=True):
        """Get all assets for an entity."""
        query = self.session.query(Asset).filter_by(entity_id=entity_id)
        if active_only:
            query = query.filter_by(active=True)
        return query.all()

    def get_all_assets(self, active_only=True):
        """Get all assets across all entities."""
        query = self.session.query(Asset)
        if active_only:
            query = query.filter_by(active=True)
        return query.all()

    def calculate_depreciation_for_year(self, asset_id, tax_year):
        """
        Calculate depreciation for a specific year.

        Args:
            asset_id: Asset ID
            tax_year: Tax year to calculate

        Returns:
            DepreciationSchedule object
        """
        asset = self.get_asset(asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        # Check if already calculated
        existing = self.session.query(DepreciationSchedule).filter_by(
            asset_id=asset_id,
            tax_year=tax_year
        ).first()

        if existing:
            logger.info(f"Depreciation for asset {asset_id} year {tax_year} already exists")
            return existing

        # Determine year in service
        placed_year = asset.in_service_date.year
        year_in_service = tax_year - placed_year + 1

        if year_in_service < 1:
            raise ValueError(f"Tax year {tax_year} is before asset placed in service")

        # Get beginning book value (ending book value from prior year)
        if year_in_service == 1:
            beginning_book_value = asset.purchase_price
        else:
            prior_year_schedule = self.session.query(DepreciationSchedule).filter_by(
                asset_id=asset_id,
                tax_year=tax_year - 1
            ).first()

            if not prior_year_schedule:
                raise ValueError(f"Prior year depreciation not found for year {tax_year - 1}")

            beginning_book_value = prior_year_schedule.ending_book_value

        # Calculate depreciation
        if year_in_service == 1:
            # First year - may include Section 179 and Bonus
            depreciation = self.depreciation_calc.calculate_total_depreciation(
                asset_cost=asset.purchase_price,
                macrs_class=asset.macrs_class,
                placed_in_service_date=asset.in_service_date,
                tax_year=tax_year,
                use_section_179=True,
                use_bonus=True
            )

            schedule = DepreciationSchedule(
                asset_id=asset_id,
                tax_year=tax_year,
                section_179_deduction=depreciation['section_179'],
                bonus_depreciation=depreciation['bonus_depreciation'],
                macrs_depreciation=depreciation['macrs_depreciation'],
                total_depreciation=depreciation['total_depreciation'],
                beginning_book_value=beginning_book_value,
                ending_book_value=depreciation['remaining_basis']
            )
        else:
            # Subsequent years - only MACRS on remaining basis
            macrs_basis = asset.purchase_price - asset.section_179_amount - asset.bonus_depreciation_amount

            macrs_calc = self.depreciation_calc.calculate_macrs_depreciation(
                asset_basis=macrs_basis,
                macrs_class=asset.macrs_class,
                year_in_service=year_in_service,
                current_year=tax_year,
                placed_in_service_date=asset.in_service_date
            )

            total_depr = macrs_calc['macrs_amount']

            schedule = DepreciationSchedule(
                asset_id=asset_id,
                tax_year=tax_year,
                section_179_deduction=0.0,
                bonus_depreciation=0.0,
                macrs_depreciation=macrs_calc['macrs_amount'],
                total_depreciation=total_depr,
                beginning_book_value=beginning_book_value,
                ending_book_value=beginning_book_value - total_depr,
                is_final_year=macrs_calc['fully_depreciated']
            )

        try:
            self.session.add(schedule)

            # Update asset accumulated depreciation
            asset.accumulated_depreciation += schedule.total_depreciation
            asset.current_book_value = schedule.ending_book_value

            self.session.commit()
            logger.info(f"Calculated depreciation for asset {asset_id} year {tax_year}")
            return schedule

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to calculate depreciation: {e}")
            raise

    def get_total_depreciation_for_entity(self, entity_id, tax_year):
        """
        Get total depreciation for an entity in a given tax year.

        Args:
            entity_id: Entity ID
            tax_year: Tax year

        Returns:
            Dictionary with depreciation breakdown
        """
        assets = self.get_assets_by_entity(entity_id, active_only=True)

        total_section_179 = 0.0
        total_bonus = 0.0
        total_macrs = 0.0

        for asset in assets:
            schedule = self.session.query(DepreciationSchedule).filter_by(
                asset_id=asset.id,
                tax_year=tax_year
            ).first()

            if schedule:
                total_section_179 += schedule.section_179_deduction
                total_bonus += schedule.bonus_depreciation
                total_macrs += schedule.macrs_depreciation

        return {
            'entity_id': entity_id,
            'tax_year': tax_year,
            'section_179': total_section_179,
            'bonus_depreciation': total_bonus,
            'macrs_depreciation': total_macrs,
            'total_depreciation': total_section_179 + total_bonus + total_macrs,
            'asset_count': len(assets)
        }

    def dispose_asset(self, asset_id, disposal_date, disposal_proceeds):
        """
        Record disposal of an asset.

        Args:
            asset_id: Asset ID
            disposal_date: Date of disposal
            disposal_proceeds: Proceeds from sale

        Returns:
            Dictionary with gain/loss calculation
        """
        asset = self.get_asset(asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        try:
            asset.disposal_date = disposal_date
            asset.disposal_proceeds = disposal_proceeds
            asset.active = False

            # Calculate gain or loss
            book_value = asset.current_book_value
            gain_loss = disposal_proceeds - book_value

            self.session.commit()
            logger.info(f"Asset {asset_id} disposed on {disposal_date}")

            return {
                'asset_id': asset_id,
                'book_value': book_value,
                'proceeds': disposal_proceeds,
                'gain_loss': gain_loss,
                'is_gain': gain_loss > 0
            }

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to dispose asset: {e}")
            raise

    def close(self):
        """Close database session."""
        self.session.close()

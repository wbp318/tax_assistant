"""
Database models for the tax assistant application.
Handles entities, assets, transactions, and depreciation tracking.
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class EntityType(enum.Enum):
    """Types of business entities."""
    FARM = "farm"
    EQUIPMENT_HOLDING = "equipment_holding"
    GRAIN_HOLDING = "grain_holding"
    OTHER = "other"


class AccountingMethod(enum.Enum):
    """Accounting methods."""
    CASH = "cash"
    ACCRUAL = "accrual"
    HYBRID = "hybrid"


class TransactionType(enum.Enum):
    """Transaction types."""
    INCOME = "income"
    EXPENSE = "expense"


class Entity(Base):
    """Business entities (farm, holding companies, etc.)."""
    __tablename__ = 'entities'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    entity_type = Column(Enum(EntityType), nullable=False)
    accounting_method = Column(Enum(AccountingMethod), nullable=False, default=AccountingMethod.CASH)
    ein = Column(String(20))  # Employer Identification Number
    formation_date = Column(Date)
    state = Column(String(2), default='LA')
    notes = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assets = relationship("Asset", back_populates="entity", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="entity", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Entity(name='{self.name}', type='{self.entity_type.value}')>"


class Asset(Base):
    """Assets owned by entities (equipment, buildings, etc.)."""
    __tablename__ = 'assets'

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False)
    description = Column(String(500), nullable=False)
    asset_type = Column(String(100))  # Equipment, Building, Land Improvement, etc.

    # Purchase information
    purchase_date = Column(Date, nullable=False)
    purchase_price = Column(Float, nullable=False)
    salvage_value = Column(Float, default=0.0)

    # Depreciation classification
    macrs_class = Column(String(20))  # 3-year, 5-year, 7-year, etc.
    recovery_period = Column(Integer)  # In years
    depreciation_method = Column(String(20))  # MACRS, SL, DDB, Section 179, Bonus

    # Section 179 and Bonus Depreciation
    section_179_amount = Column(Float, default=0.0)
    bonus_depreciation_amount = Column(Float, default=0.0)

    # Current status
    in_service_date = Column(Date)
    disposal_date = Column(Date)
    disposal_proceeds = Column(Float)

    # Tracking
    accumulated_depreciation = Column(Float, default=0.0)
    current_book_value = Column(Float)

    notes = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    entity = relationship("Entity", back_populates="assets")
    depreciation_schedules = relationship("DepreciationSchedule", back_populates="asset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Asset(description='{self.description}', entity='{self.entity.name if self.entity else None}')>"


class DepreciationSchedule(Base):
    """Annual depreciation schedule for each asset."""
    __tablename__ = 'depreciation_schedules'

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False)
    tax_year = Column(Integer, nullable=False)

    # Depreciation amounts
    section_179_deduction = Column(Float, default=0.0)
    bonus_depreciation = Column(Float, default=0.0)
    macrs_depreciation = Column(Float, default=0.0)
    total_depreciation = Column(Float, default=0.0)

    # Book values
    beginning_book_value = Column(Float)
    ending_book_value = Column(Float)

    # Status
    is_final_year = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    asset = relationship("Asset", back_populates="depreciation_schedules")

    def __repr__(self):
        return f"<DepreciationSchedule(asset_id={self.asset_id}, year={self.tax_year}, total=${self.total_depreciation:,.2f})>"


class Transaction(Base):
    """Income and expense transactions."""
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False)

    # Transaction details
    transaction_date = Column(Date, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    category = Column(String(100), nullable=False)  # grain_sales, fertilizer, etc.

    # Amounts
    amount = Column(Float, nullable=False)

    # Description
    description = Column(Text)
    reference_number = Column(String(100))  # Check number, invoice number, etc.

    # Tax treatment
    is_prepaid_expense = Column(Boolean, default=False)
    is_capital_expense = Column(Boolean, default=False)
    tax_year = Column(Integer)  # Year this transaction applies to for tax purposes

    # Cash vs Accrual
    cash_date = Column(Date)  # When cash was received/paid
    accrual_date = Column(Date)  # When income was earned/expense was incurred

    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    entity = relationship("Entity", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(date={self.transaction_date}, type={self.transaction_type.value}, amount=${self.amount:,.2f})>"


class TaxCalculation(Base):
    """Stored tax calculations and scenarios."""
    __tablename__ = 'tax_calculations'

    id = Column(Integer, primary_key=True)
    tax_year = Column(Integer, nullable=False)
    scenario_name = Column(String(200), default="Default")

    # Entity (None = consolidated)
    entity_id = Column(Integer, ForeignKey('entities.id'))

    # Income
    total_income = Column(Float, default=0.0)
    farm_income = Column(Float, default=0.0)

    # Expenses
    total_expenses = Column(Float, default=0.0)
    depreciation = Column(Float, default=0.0)
    section_179 = Column(Float, default=0.0)

    # Net
    net_farm_profit = Column(Float, default=0.0)

    # Self-Employment Tax
    se_tax = Column(Float, default=0.0)

    # Federal Income Tax
    federal_taxable_income = Column(Float, default=0.0)
    federal_tax = Column(Float, default=0.0)

    # Louisiana State Tax
    la_taxable_income = Column(Float, default=0.0)
    la_state_tax = Column(Float, default=0.0)

    # Total Tax Liability
    total_tax_liability = Column(Float, default=0.0)

    # Effective Rates
    effective_federal_rate = Column(Float, default=0.0)
    effective_total_rate = Column(Float, default=0.0)

    # Metadata
    calculation_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TaxCalculation(year={self.tax_year}, scenario='{self.scenario_name}', total_tax=${self.total_tax_liability:,.2f})>"


class TaxScenario(Base):
    """Tax planning scenarios with different assumptions."""
    __tablename__ = 'tax_scenarios'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    tax_year = Column(Integer, nullable=False)
    description = Column(Text)

    # Scenario parameters (stored as JSON-like text)
    # Could include: income timing, section 179 elections, prepaid expenses, etc.
    parameters = Column(Text)

    # Results reference
    calculation_id = Column(Integer, ForeignKey('tax_calculations.id'))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TaxScenario(name='{self.name}', year={self.tax_year})>"

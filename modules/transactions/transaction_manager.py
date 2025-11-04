"""
Transaction management for income and expenses.
"""

from database.models import Transaction, TransactionType, Entity, AccountingMethod
from database.database import get_session
from config.tax_constants import FARM_INCOME_CATEGORIES, FARM_EXPENSE_CATEGORIES
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TransactionManager:
    """Manage income and expense transactions."""

    def __init__(self):
        self.session = get_session()

    def add_transaction(self, entity_id, transaction_date, transaction_type,
                       category, amount, description=None, reference_number=None,
                       is_prepaid=False, is_capital=False, cash_date=None,
                       accrual_date=None, tax_year=None, notes=None):
        """
        Add a new transaction.

        Args:
            entity_id: Entity ID
            transaction_date: Transaction date
            transaction_type: 'income' or 'expense'
            category: Category (e.g., 'grain_sales', 'fertilizer')
            amount: Transaction amount
            description: Description
            reference_number: Check/invoice number
            is_prepaid: Is this a prepaid expense?
            is_capital: Is this a capital expense?
            cash_date: Date cash was received/paid (for cash basis)
            accrual_date: Date income earned/expense incurred (for accrual)
            tax_year: Tax year this applies to
            notes: Additional notes

        Returns:
            Transaction object
        """
        try:
            # Convert string to enum
            if isinstance(transaction_type, str):
                transaction_type = TransactionType[transaction_type.upper()]

            # Determine tax year if not provided
            if tax_year is None:
                tax_year = transaction_date.year

            # Set cash/accrual dates if not provided
            if cash_date is None:
                cash_date = transaction_date
            if accrual_date is None:
                accrual_date = transaction_date

            transaction = Transaction(
                entity_id=entity_id,
                transaction_date=transaction_date,
                transaction_type=transaction_type,
                category=category,
                amount=amount,
                description=description,
                reference_number=reference_number,
                is_prepaid_expense=is_prepaid,
                is_capital_expense=is_capital,
                cash_date=cash_date,
                accrual_date=accrual_date,
                tax_year=tax_year,
                notes=notes
            )

            self.session.add(transaction)
            self.session.commit()
            logger.info(f"Added {transaction_type.value} transaction: {category} ${amount:,.2f}")
            return transaction

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to add transaction: {e}")
            raise

    def get_transaction(self, transaction_id):
        """Get transaction by ID."""
        return self.session.query(Transaction).filter_by(id=transaction_id).first()

    def get_transactions_by_entity(self, entity_id, start_date=None, end_date=None,
                                   transaction_type=None, category=None):
        """
        Get transactions for an entity with optional filters.

        Args:
            entity_id: Entity ID
            start_date: Start date filter
            end_date: End date filter
            transaction_type: Filter by type (income/expense)
            category: Filter by category

        Returns:
            List of Transaction objects
        """
        query = self.session.query(Transaction).filter_by(entity_id=entity_id)

        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        if transaction_type:
            if isinstance(transaction_type, str):
                transaction_type = TransactionType[transaction_type.upper()]
            query = query.filter_by(transaction_type=transaction_type)
        if category:
            query = query.filter_by(category=category)

        return query.order_by(Transaction.transaction_date).all()

    def get_transactions_for_tax_year(self, entity_id, tax_year, accounting_method='cash'):
        """
        Get transactions for a tax year using specified accounting method.

        Args:
            entity_id: Entity ID
            tax_year: Tax year
            accounting_method: 'cash' or 'accrual'

        Returns:
            Dictionary with income and expense transactions
        """
        # Get entity to check accounting method
        entity = self.session.query(Entity).filter_by(id=entity_id).first()
        if not entity:
            raise ValueError(f"Entity {entity_id} not found")

        # Use entity's accounting method if not specified
        if accounting_method is None:
            accounting_method = entity.accounting_method.value

        # Determine which date to use
        if accounting_method == 'cash':
            date_field = Transaction.cash_date
        elif accounting_method == 'accrual':
            date_field = Transaction.accrual_date
        else:
            date_field = Transaction.transaction_date

        # Query for tax year
        start_date = datetime(tax_year, 1, 1).date()
        end_date = datetime(tax_year, 12, 31).date()

        income_transactions = self.session.query(Transaction).filter(
            Transaction.entity_id == entity_id,
            Transaction.transaction_type == TransactionType.INCOME,
            date_field >= start_date,
            date_field <= end_date,
            Transaction.is_capital_expense == False
        ).all()

        expense_transactions = self.session.query(Transaction).filter(
            Transaction.entity_id == entity_id,
            Transaction.transaction_type == TransactionType.EXPENSE,
            date_field >= start_date,
            date_field <= end_date,
            Transaction.is_capital_expense == False
        ).all()

        return {
            'income': income_transactions,
            'expenses': expense_transactions,
            'accounting_method': accounting_method
        }

    def get_income_summary(self, entity_id, tax_year, accounting_method='cash'):
        """
        Get income summary by category for a tax year.

        Args:
            entity_id: Entity ID
            tax_year: Tax year
            accounting_method: Accounting method

        Returns:
            Dictionary with income by category
        """
        transactions = self.get_transactions_for_tax_year(
            entity_id, tax_year, accounting_method
        )

        income_by_category = {}
        total_income = 0.0

        for trans in transactions['income']:
            if trans.category not in income_by_category:
                income_by_category[trans.category] = 0.0
            income_by_category[trans.category] += trans.amount
            total_income += trans.amount

        return {
            'tax_year': tax_year,
            'entity_id': entity_id,
            'by_category': income_by_category,
            'total_income': total_income
        }

    def get_expense_summary(self, entity_id, tax_year, accounting_method='cash'):
        """
        Get expense summary by category for a tax year.

        Args:
            entity_id: Entity ID
            tax_year: Tax year
            accounting_method: Accounting method

        Returns:
            Dictionary with expenses by category
        """
        transactions = self.get_transactions_for_tax_year(
            entity_id, tax_year, accounting_method
        )

        expense_by_category = {}
        total_expenses = 0.0

        for trans in transactions['expenses']:
            if trans.category not in expense_by_category:
                expense_by_category[trans.category] = 0.0
            expense_by_category[trans.category] += trans.amount
            total_expenses += trans.amount

        return {
            'tax_year': tax_year,
            'entity_id': entity_id,
            'by_category': expense_by_category,
            'total_expenses': total_expenses
        }

    def validate_prepaid_expenses(self, entity_id, tax_year):
        """
        Validate that prepaid expenses don't exceed 50% rule.

        The IRS requires that prepaid farm expenses don't exceed 50% of
        other deductible farm expenses.

        Args:
            entity_id: Entity ID
            tax_year: Tax year

        Returns:
            Dictionary with validation results
        """
        expense_summary = self.get_expense_summary(entity_id, tax_year)

        prepaid_expenses = sum(
            trans.amount
            for trans in self.get_transactions_for_tax_year(entity_id, tax_year)['expenses']
            if trans.is_prepaid_expense
        )

        other_expenses = expense_summary['total_expenses'] - prepaid_expenses

        max_allowed_prepaid = other_expenses * 0.50
        exceeds_limit = prepaid_expenses > max_allowed_prepaid

        return {
            'tax_year': tax_year,
            'prepaid_expenses': prepaid_expenses,
            'other_expenses': other_expenses,
            'max_allowed_prepaid': max_allowed_prepaid,
            'exceeds_limit': exceeds_limit,
            'excess_amount': max(0, prepaid_expenses - max_allowed_prepaid)
        }

    def delete_transaction(self, transaction_id):
        """Delete a transaction."""
        try:
            transaction = self.get_transaction(transaction_id)
            if not transaction:
                raise ValueError(f"Transaction {transaction_id} not found")

            self.session.delete(transaction)
            self.session.commit()
            logger.info(f"Deleted transaction {transaction_id}")
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to delete transaction: {e}")
            raise

    def update_transaction(self, transaction_id, **kwargs):
        """Update transaction attributes."""
        try:
            transaction = self.get_transaction(transaction_id)
            if not transaction:
                raise ValueError(f"Transaction {transaction_id} not found")

            for key, value in kwargs.items():
                if hasattr(transaction, key):
                    setattr(transaction, key, value)

            transaction.updated_at = datetime.utcnow()
            self.session.commit()
            logger.info(f"Updated transaction {transaction_id}")
            return transaction

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to update transaction: {e}")
            raise

    def close(self):
        """Close database session."""
        self.session.close()

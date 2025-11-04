"""
Main application entry point for the Tax Assistant.
Provides CLI interface for managing farm tax operations.
"""

import click
from rich.console import Console
from rich.table import Table
from datetime import datetime, date
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tax_assistant.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
console = Console()


# Import modules
from database.database import init_database, db
from modules.entities.entity_manager import EntityManager
from modules.assets.asset_manager import AssetManager
from modules.transactions.transaction_manager import TransactionManager
from modules.tax_calc.louisiana_tax import CombinedTaxCalculator
from modules.reports.report_generator import ReportGenerator
from config.settings import DEFAULT_TAX_YEAR


@click.group()
def cli():
    """Tax Assistant for Farming Operations - Manage entities, assets, transactions, and tax calculations."""
    pass


@cli.command()
def init_db():
    """Initialize the database."""
    try:
        init_database()
        console.print("[green]✓ Database initialized successfully![/green]")
    except Exception as e:
        console.print(f"[red]✗ Failed to initialize database: {e}[/red]")
        logger.error(f"Database initialization failed: {e}")


@cli.group()
def entity():
    """Manage business entities (farm, holding companies)."""
    pass


@entity.command('add')
@click.option('--name', required=True, help='Entity name')
@click.option('--type', 'entity_type', required=True,
              type=click.Choice(['farm', 'equipment_holding', 'grain_holding', 'other']),
              help='Entity type')
@click.option('--accounting', default='cash',
              type=click.Choice(['cash', 'accrual', 'hybrid']),
              help='Accounting method')
@click.option('--ein', help='Employer Identification Number')
@click.option('--state', default='LA', help='State code')
def entity_add(name, entity_type, accounting, ein, state):
    """Add a new entity."""
    try:
        em = EntityManager()
        entity = em.create_entity(
            name=name,
            entity_type=entity_type,
            accounting_method=accounting,
            ein=ein,
            state=state
        )
        console.print(f"[green]✓ Created entity: {entity.name} (ID: {entity.id})[/green]")
        em.close()
    except Exception as e:
        console.print(f"[red]✗ Failed to create entity: {e}[/red]")


@entity.command('list')
def entity_list():
    """List all entities."""
    try:
        em = EntityManager()
        entities = em.get_all_entities()

        table = Table(title="Business Entities")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Accounting", style="blue")
        table.add_column("Assets", style="magenta")
        table.add_column("Transactions", style="magenta")

        for entity in entities:
            summary = em.get_entity_summary(entity.id)
            table.add_row(
                str(entity.id),
                entity.name,
                entity.entity_type.value,
                entity.accounting_method.value,
                str(summary['asset_count']),
                str(summary['transaction_count'])
            )

        console.print(table)
        em.close()
    except Exception as e:
        console.print(f"[red]✗ Failed to list entities: {e}[/red]")


@cli.group()
def asset():
    """Manage assets and depreciation."""
    pass


@asset.command('add')
@click.option('--entity-id', required=True, type=int, help='Entity ID')
@click.option('--description', required=True, help='Asset description')
@click.option('--cost', required=True, type=float, help='Purchase price')
@click.option('--date', 'purchase_date', required=True, help='Purchase date (YYYY-MM-DD)')
@click.option('--macrs-class', required=True, help='MACRS class (e.g., 3-year, 5-year, 7-year)')
@click.option('--type', 'asset_type', default='Equipment', help='Asset type')
@click.option('--section-179/--no-section-179', default=True, help='Use Section 179')
@click.option('--bonus/--no-bonus', default=True, help='Use bonus depreciation')
def asset_add(entity_id, description, cost, purchase_date, macrs_class, asset_type, section_179, bonus):
    """Add a new asset."""
    try:
        am = AssetManager()
        purchase_date_obj = datetime.strptime(purchase_date, '%Y-%m-%d').date()

        asset = am.add_asset(
            entity_id=entity_id,
            description=description,
            purchase_price=cost,
            purchase_date=purchase_date_obj,
            macrs_class=macrs_class,
            asset_type=asset_type,
            use_section_179=section_179,
            use_bonus=bonus
        )

        console.print(f"[green]✓ Added asset: {asset.description} (ID: {asset.id})[/green]")
        console.print(f"  First year depreciation: ${asset.accumulated_depreciation:,.2f}")
        am.close()
    except Exception as e:
        console.print(f"[red]✗ Failed to add asset: {e}[/red]")


@asset.command('list')
@click.option('--entity-id', type=int, help='Filter by entity ID')
def asset_list(entity_id):
    """List assets."""
    try:
        am = AssetManager()

        if entity_id:
            assets = am.get_assets_by_entity(entity_id)
        else:
            assets = am.get_all_assets()

        table = Table(title=f"Assets{f' for Entity {entity_id}' if entity_id else ''}")
        table.add_column("ID", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("MACRS Class", style="yellow")
        table.add_column("Cost", style="blue")
        table.add_column("Book Value", style="magenta")
        table.add_column("Placed in Service", style="cyan")

        for asset in assets:
            table.add_row(
                str(asset.id),
                asset.description,
                asset.macrs_class or '',
                f"${asset.purchase_price:,.2f}",
                f"${asset.current_book_value:,.2f}",
                asset.in_service_date.strftime('%Y-%m-%d') if asset.in_service_date else ''
            )

        console.print(table)
        am.close()
    except Exception as e:
        console.print(f"[red]✗ Failed to list assets: {e}[/red]")


@cli.group()
def transaction():
    """Manage income and expense transactions."""
    pass


@transaction.command('add')
@click.option('--entity-id', required=True, type=int, help='Entity ID')
@click.option('--date', 'trans_date', required=True, help='Transaction date (YYYY-MM-DD)')
@click.option('--type', 'trans_type', required=True, type=click.Choice(['income', 'expense']), help='Transaction type')
@click.option('--category', required=True, help='Category (e.g., grain_sales, fertilizer)')
@click.option('--amount', required=True, type=float, help='Amount')
@click.option('--description', help='Description')
@click.option('--prepaid', is_flag=True, help='Mark as prepaid expense')
def transaction_add(entity_id, trans_date, trans_type, category, amount, description, prepaid):
    """Add a transaction."""
    try:
        tm = TransactionManager()
        trans_date_obj = datetime.strptime(trans_date, '%Y-%m-%d').date()

        trans = tm.add_transaction(
            entity_id=entity_id,
            transaction_date=trans_date_obj,
            transaction_type=trans_type,
            category=category,
            amount=amount,
            description=description,
            is_prepaid=prepaid
        )

        console.print(f"[green]✓ Added {trans_type}: ${amount:,.2f} - {category}[/green]")
        tm.close()
    except Exception as e:
        console.print(f"[red]✗ Failed to add transaction: {e}[/red]")


@transaction.command('summary')
@click.option('--entity-id', required=True, type=int, help='Entity ID')
@click.option('--year', type=int, default=DEFAULT_TAX_YEAR, help='Tax year')
def transaction_summary(entity_id, year):
    """Show transaction summary for a tax year."""
    try:
        tm = TransactionManager()

        income = tm.get_income_summary(entity_id, year)
        expenses = tm.get_expense_summary(entity_id, year)

        console.print(f"\n[bold]Transaction Summary for Entity {entity_id} - Tax Year {year}[/bold]\n")

        # Income
        console.print("[green]INCOME:[/green]")
        for category, amount in income['by_category'].items():
            console.print(f"  {category.replace('_', ' ').title():<40} ${amount:>15,.2f}")
        console.print(f"  {'TOTAL INCOME':<40} ${income['total_income']:>15,.2f}\n")

        # Expenses
        console.print("[red]EXPENSES:[/red]")
        for category, amount in expenses['by_category'].items():
            console.print(f"  {category.replace('_', ' ').title():<40} ${amount:>15,.2f}")
        console.print(f"  {'TOTAL EXPENSES':<40} ${expenses['total_expenses']:>15,.2f}\n")

        # Net
        net = income['total_income'] - expenses['total_expenses']
        console.print(f"  [bold]{'NET (before depreciation)':<40} ${net:>15,.2f}[/bold]")

        tm.close()
    except Exception as e:
        console.print(f"[red]✗ Failed to get summary: {e}[/red]")


@cli.group()
def tax():
    """Calculate taxes and generate projections."""
    pass


@tax.command('calculate')
@click.option('--entity-id', required=True, type=int, help='Entity ID')
@click.option('--year', type=int, default=DEFAULT_TAX_YEAR, help='Tax year')
@click.option('--filing-status', default='married_filing_jointly', help='Filing status')
def tax_calculate(entity_id, year, filing_status):
    """Calculate taxes for an entity."""
    try:
        # Get transaction summary
        tm = TransactionManager()
        income = tm.get_income_summary(entity_id, year)
        expenses = tm.get_expense_summary(entity_id, year)

        # Get depreciation
        am = AssetManager()
        depreciation_data = am.get_total_depreciation_for_entity(entity_id, year)

        # Calculate tax
        calc = CombinedTaxCalculator(filing_status=filing_status, tax_year=year)
        tax_result = calc.calculate_combined_tax(
            total_income=income['total_income'],
            total_expenses=expenses['total_expenses'],
            depreciation=depreciation_data['total_depreciation']
        )

        # Display results
        console.print(f"\n[bold]Tax Calculation for Entity {entity_id} - {year}[/bold]\n")
        console.print(f"Farm Income:          ${tax_result['farm_income']:>15,.2f}")
        console.print(f"Farm Expenses:        ${tax_result['farm_expenses']:>15,.2f}")
        console.print(f"Depreciation:         ${tax_result['depreciation']:>15,.2f}")
        console.print(f"Net Farm Profit:      ${tax_result['net_farm_profit']:>15,.2f}")
        console.print(f"\nFederal Tax:          ${tax_result['total_federal_tax']:>15,.2f}")
        console.print(f"Louisiana Tax:        ${tax_result['total_louisiana_tax']:>15,.2f}")
        console.print(f"[bold]TOTAL TAX:            ${tax_result['total_tax_liability']:>15,.2f}[/bold]")
        console.print(f"Effective Rate:       {tax_result['combined_effective_rate_percent']:>16}")

        tm.close()
        am.close()
    except Exception as e:
        console.print(f"[red]✗ Failed to calculate tax: {e}[/red]")
        logger.error(f"Tax calculation failed: {e}")


@cli.group()
def report():
    """Generate tax reports."""
    pass


@report.command('schedule-f')
@click.option('--entity-id', required=True, type=int, help='Entity ID')
@click.option('--year', type=int, default=DEFAULT_TAX_YEAR, help='Tax year')
def report_schedule_f(entity_id, year):
    """Generate Schedule F report."""
    try:
        tm = TransactionManager()
        am = AssetManager()
        em = EntityManager()

        entity = em.get_entity(entity_id)
        income = tm.get_income_summary(entity_id, year)
        expenses = tm.get_expense_summary(entity_id, year)
        depreciation_data = am.get_total_depreciation_for_entity(entity_id, year)
        net_profit = income['total_income'] - expenses['total_expenses'] - depreciation_data['total_depreciation']

        rg = ReportGenerator()
        report_text = rg.generate_schedule_f_summary(
            entity_name=entity.name,
            tax_year=year,
            income_summary=income,
            expense_summary=expenses,
            depreciation=depreciation_data['total_depreciation'],
            net_profit=net_profit
        )

        console.print(report_text)

        filename = f"schedule_f_{entity.name.replace(' ', '_')}_{year}.txt"
        filepath = rg.save_report(filename, report_text)
        console.print(f"\n[green]✓ Report saved to: {filepath}[/green]")

        tm.close()
        am.close()
        em.close()
    except Exception as e:
        console.print(f"[red]✗ Failed to generate report: {e}[/red]")


if __name__ == '__main__':
    cli()

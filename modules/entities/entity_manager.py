"""
Entity management for farm and holding companies.
"""

from database.models import Entity, EntityType, AccountingMethod
from database.database import get_session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EntityManager:
    """Manage business entities."""

    def __init__(self):
        self.session = get_session()

    def create_entity(self, name, entity_type, accounting_method='cash', ein=None,
                     formation_date=None, state='LA', notes=None):
        """
        Create a new business entity.

        Args:
            name: Entity name
            entity_type: Type of entity (farm, equipment_holding, grain_holding)
            accounting_method: Accounting method (cash, accrual, hybrid)
            ein: Employer Identification Number
            formation_date: Date entity was formed
            state: State code (default LA)
            notes: Additional notes

        Returns:
            Entity object
        """
        try:
            # Convert string to enum
            if isinstance(entity_type, str):
                entity_type = EntityType[entity_type.upper()]
            if isinstance(accounting_method, str):
                accounting_method = AccountingMethod[accounting_method.upper()]

            entity = Entity(
                name=name,
                entity_type=entity_type,
                accounting_method=accounting_method,
                ein=ein,
                formation_date=formation_date,
                state=state,
                notes=notes
            )

            self.session.add(entity)
            self.session.commit()
            logger.info(f"Created entity: {name} ({entity_type.value})")
            return entity

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to create entity: {e}")
            raise

    def get_entity(self, entity_id):
        """Get entity by ID."""
        return self.session.query(Entity).filter_by(id=entity_id).first()

    def get_entity_by_name(self, name):
        """Get entity by name."""
        return self.session.query(Entity).filter_by(name=name).first()

    def get_all_entities(self, active_only=True):
        """
        Get all entities.

        Args:
            active_only: Only return active entities (default True)

        Returns:
            List of Entity objects
        """
        query = self.session.query(Entity)
        if active_only:
            query = query.filter_by(active=True)
        return query.all()

    def get_entities_by_type(self, entity_type, active_only=True):
        """
        Get entities by type.

        Args:
            entity_type: Entity type to filter by
            active_only: Only return active entities

        Returns:
            List of Entity objects
        """
        if isinstance(entity_type, str):
            entity_type = EntityType[entity_type.upper()]

        query = self.session.query(Entity).filter_by(entity_type=entity_type)
        if active_only:
            query = query.filter_by(active=True)
        return query.all()

    def update_entity(self, entity_id, **kwargs):
        """
        Update entity attributes.

        Args:
            entity_id: Entity ID
            **kwargs: Attributes to update

        Returns:
            Updated Entity object
        """
        try:
            entity = self.get_entity(entity_id)
            if not entity:
                raise ValueError(f"Entity {entity_id} not found")

            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            entity.updated_at = datetime.utcnow()
            self.session.commit()
            logger.info(f"Updated entity: {entity.name}")
            return entity

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to update entity: {e}")
            raise

    def deactivate_entity(self, entity_id):
        """Deactivate an entity (soft delete)."""
        return self.update_entity(entity_id, active=False)

    def activate_entity(self, entity_id):
        """Activate an entity."""
        return self.update_entity(entity_id, active=True)

    def delete_entity(self, entity_id):
        """
        Permanently delete an entity and all related data.
        WARNING: This will cascade delete all assets and transactions!
        """
        try:
            entity = self.get_entity(entity_id)
            if not entity:
                raise ValueError(f"Entity {entity_id} not found")

            name = entity.name
            self.session.delete(entity)
            self.session.commit()
            logger.warning(f"Deleted entity: {name}")
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to delete entity: {e}")
            raise

    def get_entity_summary(self, entity_id):
        """
        Get summary information for an entity.

        Returns:
            Dictionary with entity details and counts
        """
        entity = self.get_entity(entity_id)
        if not entity:
            return None

        return {
            'id': entity.id,
            'name': entity.name,
            'type': entity.entity_type.value,
            'accounting_method': entity.accounting_method.value,
            'ein': entity.ein,
            'state': entity.state,
            'active': entity.active,
            'asset_count': len(entity.assets),
            'transaction_count': len(entity.transactions),
            'created_at': entity.created_at,
            'notes': entity.notes
        }

    def close(self):
        """Close database session."""
        self.session.close()

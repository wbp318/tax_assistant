"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config.settings import DATABASE_URL
from database.models import Base
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager."""

    def __init__(self, database_url=None):
        """Initialize database connection."""
        self.database_url = database_url or DATABASE_URL
        self.engine = None
        self.session_factory = None
        self.Session = None

    def connect(self):
        """Create database engine and session factory."""
        try:
            self.engine = create_engine(self.database_url, echo=False)
            self.session_factory = sessionmaker(bind=self.engine)
            self.Session = scoped_session(self.session_factory)
            logger.info(f"Database connected: {self.database_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

    def create_tables(self):
        """Create all tables in the database."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            return False

    def drop_tables(self):
        """Drop all tables in the database."""
        try:
            Base.metadata.drop_all(self.engine)
            logger.info("Database tables dropped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            return False

    def get_session(self):
        """Get a new database session."""
        if not self.Session:
            self.connect()
        return self.Session()

    def close(self):
        """Close database connection."""
        if self.Session:
            self.Session.remove()
        if self.engine:
            self.engine.dispose()
        logger.info("Database connection closed")


# Global database instance
db = Database()


def init_database():
    """Initialize database with tables."""
    db.connect()
    db.create_tables()
    return db


def get_session():
    """Get a database session."""
    return db.get_session()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

import os
from typing import Generator, Optional

import logging
logger = logging.getLogger("distributed_pg_lock")

Base = declarative_base()

class Database:
    """A database connection manager with connection pooling and scoped sessions.
    
    Features:
    - Connection pooling with configurable size
    - Automatic connection health checks
    - Thread-safe scoped sessions
    - Context manager for automatic session cleanup
    - Table creation utility
    """
    
    def __init__(self, db_url: Optional[str] = None, **engine_kwargs):
        """Initialize the database connection.
        
        Args:
            db_url: Database connection URL. If None, uses DB_URL environment variable.
            **engine_kwargs: Additional kwargs to pass to create_engine()
        """
        logger.info("Initializing lock manager")
        self.db_url = db_url or os.getenv("DB_URL")
        if not self.db_url:
            raise ValueError(
                "Database URL not provided.\n"
                "Please pass `db_url` explicitly or set the DB_URL environment variable.\n\n"
                "Expected format examples:\n"
                "  - PostgreSQL: postgresql://user:password@localhost:5432/dbname\n"
                "\n"
                "Example usage:\n"
                "  export DB_URL='postgresql://user:pass@localhost:5432/mydb'\n"
                "  or\n"
                "  db = DatabaseConnector(db_url='postgresql://user:pass@localhost:5432/mydb')"
                )
            
        # Default engine configuration
        default_config = {
            'pool_size': 10,
            'max_overflow': 20,
            'pool_pre_ping': True,
            'pool_recycle': 3600,  # Recycle connections every hour
            'pool_timeout': 30,    # Wait 30 seconds for connection
            'echo': False,         # Don't log all SQL by default
            'future': True,        # Enable SQLAlchemy 2.0 behavior
            'execution_options': {
                'isolation_level': 'READ COMMITTED'
            }
        }
        default_config.update(engine_kwargs)
        
        self.engine = create_engine(self.db_url, **default_config)
        self.session_factory = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            future= True,        # Enable SQLAlchemy 2.0 behavior
        )
        self.ScopedSession = scoped_session(self.session_factory)

    @contextmanager
    def session(self) -> Generator[scoped_session, None, None]:
        """Provide a transactional scope around a series of operations.
        
        Usage:
            with db.session() as session:
                # Do database operations
                session.query(...)
        """
        session = self.ScopedSession()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            self.ScopedSession.remove()

    def create_tables(self, checkfirst: bool = True) -> None:
        """Create all tables defined in your models.
        
        Args:
            checkfirst: If True, will skip tables that already exist
        """
        Base.metadata.create_all(bind=self.engine, checkfirst=checkfirst)

    def drop_tables(self, checkfirst: bool = True) -> None:
        """Drop all tables (useful for testing).
        
        Args:
            checkfirst: If True, will skip tables that don't exist
        """
        Base.metadata.drop_all(bind=self.engine, checkfirst=checkfirst)

    def get_session(self) -> scoped_session:
        """Get a raw session (use with caution - you must close it manually).
        
        Prefer using the session() context manager for most cases.
        """
        return self.ScopedSession()

# Singleton instance with lazy initialization
class _DatabaseProxy:
    def __init__(self):
        self._instance = None
        self._initialized = False
    
    def initialize(self, db_url: Optional[str] = None, **engine_kwargs) -> None:
        """Initialize the database connection.
        
        Args:
            db_url: Database connection URL
            **engine_kwargs: Additional SQLAlchemy engine parameters
            
        Note:
            Can be safely called multiple times. Subsequent calls will be ignored.
        """
        if not self._initialized:
            self._instance = Database(db_url, **engine_kwargs)
            self._initialized = True
        else:
            # Log a warning instead of raising error
            logger.warning("Database already initialized. Subsequent initialize() calls are ignored.")
    
    def reset(self):
        """Reset the database instance for testing"""
        self._instance = None
        self._initialized = False

    def __getattr__(self, name):
        if self._instance is None:
            # Attempt auto-initialization from environment
            db_url = os.getenv("DB_URL")
            if db_url:
                self.initialize(db_url)
            else:
                raise RuntimeError(
                    "Database not initialized. You must either:\n"
                    "1. Call db.initialize(db_url='...') before using database operations\n"
                    "2. Set the DB_URL environment variable\n"
                    "3. Or configure through your application's settings"
                )
        return getattr(self._instance, name)

# Global proxy instance
db = _DatabaseProxy()
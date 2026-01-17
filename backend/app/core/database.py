"""
Database connection and session management using SQLAlchemy 2.0.
Implements connection pooling and production-grade session handling.
"""

from typing import Generator
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create SQLAlchemy engine with connection pooling
is_sqlite = str(settings.database_url).startswith('sqlite')

engine_kwargs = {
    "echo": settings.debug,
}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({
        "poolclass": QueuePool,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    })

engine = create_engine(str(settings.database_url), **engine_kwargs)


@event.listens_for(Engine, "connect")
def set_search_path(dbapi_conn, connection_record):
    """Set PostgreSQL search path and enable Row-Level Security on connection."""
    # Only for PostgreSQL
    if hasattr(dbapi_conn, 'cursor'):
        try:
            existing_autocommit = dbapi_conn.autocommit
            dbapi_conn.autocommit = True
            cursor = dbapi_conn.cursor()
            cursor.execute("SET search_path TO public")
            cursor.close()
            dbapi_conn.autocommit = existing_autocommit
        except Exception:
            # Ignore for non-PostgreSQL databases
            pass


# Session factory for database operations
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Base class for all database models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that provides database session to route handlers.
    Ensures proper session cleanup after request completion.
    
    Yields:
        Database session instance
        
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.
    Only used for initial setup; use Alembic migrations in production.
    """
    logger.info("Initializing database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization complete")


def close_db() -> None:
    """Close all database connections. Called on application shutdown."""
    logger.info("Closing database connections")
    engine.dispose()

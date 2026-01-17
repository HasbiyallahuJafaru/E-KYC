"""
Base model with common fields for all database tables.
Provides automatic timestamps and soft delete functionality.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase
from app.core.database import Base


class TimeStampedModel(Base):
    """
    Abstract base model with timestamp fields.
    All models inherit created_at and updated_at tracking.
    """
    
    __abstract__ = True
    
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="Timestamp when record was created"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Timestamp when record was last updated"
    )
    is_deleted = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Soft delete flag"
    )

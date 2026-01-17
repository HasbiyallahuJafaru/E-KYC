"""
API Client model for managing external clients consuming the E-KYC API.
Stores API keys, quotas, and billing information.
"""

from sqlalchemy import Column, String, Integer, Boolean, Index
from sqlalchemy.orm import relationship
import uuid
from app.core.types import UUID
from app.models.base import TimeStampedModel


class ApiClient(TimeStampedModel):
    """
    Represents an external client (bank/fintech) consuming the verification API.
    Each client has unique API keys for authentication and rate limiting.
    """
    
    __tablename__ = "api_clients"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique client identifier"
    )
    name = Column(
        String(255),
        nullable=False,
        comment="Client organization name"
    )
    api_key_hash = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Hashed API key for authentication"
    )
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether client can make API requests"
    )
    rate_limit_per_minute = Column(
        Integer,
        nullable=False,
        default=100,
        comment="Maximum requests per minute"
    )
    monthly_quota = Column(
        Integer,
        nullable=True,
        comment="Monthly verification quota (null = unlimited)"
    )
    current_month_usage = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Verifications used in current month"
    )
    billing_tier = Column(
        String(50),
        nullable=False,
        default="standard",
        comment="Billing tier: standard, premium, enterprise"
    )
    webhook_url = Column(
        String(500),
        nullable=True,
        comment="URL for webhook notifications (optional)"
    )
    webhook_secret = Column(
        String(255),
        nullable=True,
        comment="Secret for webhook signature verification"
    )
    contact_email = Column(
        String(255),
        nullable=False,
        comment="Primary contact email"
    )
    contact_phone = Column(
        String(50),
        nullable=True,
        comment="Contact phone number"
    )
    
    # Relationships
    verification_logs = relationship(
        "VerificationLog",
        back_populates="client",
        lazy="dynamic"
    )
    
    __table_args__ = (
        Index("idx_api_client_active", "is_active", "is_deleted"),
        {"comment": "External API clients with authentication and billing details"}
    )
    
    def __repr__(self) -> str:
        return f"<ApiClient(id={self.id}, name='{self.name}', active={self.is_active})>"

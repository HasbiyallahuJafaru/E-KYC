"""
Verification Log model for API usage tracking and billing.
Records every verification request for cost allocation and invoice generation.
"""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Index, Numeric
from sqlalchemy.orm import relationship
import uuid
from app.core.types import UUID
from app.models.base import TimeStampedModel


class VerificationLog(TimeStampedModel):
    """
    API usage log for billing and analytics.
    Tracks every verification request with response time and cost.
    """
    
    __tablename__ = "verification_logs"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique log entry identifier"
    )
    client_id = Column(
        UUID(as_uuid=True),
        ForeignKey("api_clients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="API client who made the request"
    )
    verification_id = Column(
        UUID(as_uuid=True),
        ForeignKey("verification_results.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Reference to verification result (null if failed before creation)"
    )
    
    # Request Details
    request_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Type: INDIVIDUAL, CORPORATE, COMPLETE"
    )
    endpoint = Column(
        String(200),
        nullable=False,
        comment="API endpoint called"
    )
    request_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique request ID for tracing"
    )
    
    # Performance Metrics
    response_time_ms = Column(
        Integer,
        nullable=True,
        comment="Total response time in milliseconds"
    )
    provider_time_ms = Column(
        Integer,
        nullable=True,
        comment="Time spent calling VerifyMe.ng in milliseconds"
    )
    
    # Result
    success = Column(
        Boolean,
        nullable=False,
        index=True,
        comment="Whether request succeeded"
    )
    status_code = Column(
        Integer,
        nullable=False,
        comment="HTTP status code returned"
    )
    error_code = Column(
        String(100),
        nullable=True,
        comment="Error code if request failed"
    )
    
    # Billing
    cost_ngn = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Cost in NGN charged for this verification"
    )
    billed = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether this request has been billed"
    )
    billing_month = Column(
        String(7),
        nullable=False,
        index=True,
        comment="Billing month in YYYY-MM format"
    )
    
    # Relationships
    client = relationship("ApiClient", back_populates="verification_logs")
    
    __table_args__ = (
        Index("idx_verification_log_client_month", "client_id", "billing_month"),
        Index("idx_verification_log_created", "created_at"),
        Index("idx_verification_log_billing", "billed", "billing_month"),
        {"comment": "API usage log for billing and analytics"}
    )
    
    def __repr__(self) -> str:
        return f"<VerificationLog(id={self.id}, client={self.client_id}, type={self.request_type}, success={self.success})>"

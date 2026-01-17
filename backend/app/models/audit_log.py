"""
Audit Log model for immutable compliance trail.
Write-Once-Read-Many (WORM) storage with 5-year retention per CBN/FATF requirements.
"""

from sqlalchemy import Column, String, Text, Boolean, Enum as SQLEnum, ForeignKey, Index
import uuid
from app.core.types import UUID, JSONB
from app.models.base import TimeStampedModel


class AuditLog(TimeStampedModel):
    """
    Immutable audit trail for all system actions.
    Protected by database triggers preventing UPDATE/DELETE operations.
    """
    
    __tablename__ = "audit_logs"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique audit log entry identifier"
    )
    
    # Actor Information
    user_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Internal user who performed the action (null for system/API)"
    )
    client_id = Column(
        UUID(as_uuid=True),
        ForeignKey("api_clients.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="External API client who performed the action"
    )
    actor_type = Column(
        String(50),
        nullable=False,
        comment="Type of actor: USER, API_CLIENT, SYSTEM"
    )
    actor_name = Column(
        String(255),
        nullable=True,
        comment="Name of actor for human readability"
    )
    
    # Action Details
    action = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Action performed (e.g., VERIFY_BVN, APPROVE_CUSTOMER, UPDATE_RISK_RATING)"
    )
    resource_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of resource affected (CUSTOMER, VERIFICATION, DOCUMENT, etc.)"
    )
    resource_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID of affected resource"
    )
    
    # Request Context
    request_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Request ID for tracing related audit entries"
    )
    ip_address = Column(
        String(45),
        nullable=True,
        comment="IP address of requester (supports IPv6)"
    )
    user_agent = Column(
        String(500),
        nullable=True,
        comment="User agent string"
    )
    
    # Detailed Information
    description = Column(
        Text,
        nullable=True,
        comment="Human-readable description of the action"
    )
    before_state = Column(
        JSONB,
        nullable=True,
        comment="State of resource before action (for updates)"
    )
    after_state = Column(
        JSONB,
        nullable=True,
        comment="State of resource after action (for updates)"
    )
    extra_data = Column(
        JSONB,
        nullable=True,
        comment="Additional context data"
    )
    
    # Result
    success = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether action succeeded"
    )
    error_code = Column(
        String(100),
        nullable=True,
        comment="Error code if action failed"
    )
    error_message = Column(
        Text,
        nullable=True,
        comment="Error message if action failed"
    )
    
    # Compliance
    retention_category = Column(
        String(50),
        nullable=False,
        default="STANDARD",
        comment="Retention category: STANDARD (5yr), ENHANCED (7yr), PERMANENT"
    )
    scrub_after_date = Column(
        JSONB,
        nullable=True,
        comment="Date after which record can be scrubbed (NULL = never)"
    )
    
    __table_args__ = (
        Index("idx_audit_action", "action", "created_at"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
        Index("idx_audit_actor", "actor_type", "user_id", "client_id"),
        Index("idx_audit_request", "request_id"),
        {"comment": "Immutable audit trail (WORM) - do not modify after creation"}
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, resource={self.resource_type}, success={self.success})>"

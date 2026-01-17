"""
Workflow model for Maker-Checker-Approver approval process.
Implements multi-level authorization per PRD Section 3.
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
import uuid
from app.core.types import UUID, JSONB
import enum
from app.models.base import TimeStampedModel


class WorkflowState(str, enum.Enum):
    """States in the approval workflow."""
    DRAFT = "DRAFT"                      # Maker is still working
    PENDING_CHECKER = "PENDING_CHECKER"  # Waiting for Branch Head review
    PENDING_APPROVER = "PENDING_APPROVER"  # Waiting for Zonal Head final approval
    APPROVED = "APPROVED"                # Fully approved
    REJECTED = "REJECTED"                # Rejected at any stage
    CANCELLED = "CANCELLED"              # Cancelled by Maker


class WorkflowActionType(str, enum.Enum):
    """Types of workflow actions."""
    SUBMIT = "SUBMIT"          # Maker submits for review
    APPROVE = "APPROVE"        # Checker or Approver approves
    REJECT = "REJECT"          # Checker or Approver rejects
    OVERRIDE_REQUEST = "OVERRIDE_REQUEST"  # Request to override risk rating
    CANCEL = "CANCEL"          # Maker cancels submission


class Workflow(TimeStampedModel):
    """
    Approval workflow for customer verifications.
    Enforces Maker-Checker-Approver hierarchy with branch/zone isolation.
    """
    
    __tablename__ = "workflows"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique workflow identifier"
    )
    verification_id = Column(
        UUID(as_uuid=True),
        ForeignKey("verification_results.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
        comment="Verification result being reviewed"
    )
    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Customer under review"
    )
    
    # Current State
    current_state = Column(
        SQLEnum(WorkflowState),
        nullable=False,
        default=WorkflowState.DRAFT,
        index=True,
        comment="Current workflow state"
    )
    
    # Maker (Level 1)
    maker_user_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="User who initiated the verification (Marketer/CS)"
    )
    maker_submitted_at = Column(
        JSONB,
        nullable=True,
        comment="Timestamp when Maker submitted for review"
    )
    
    # Checker (Level 2 - Branch Head)
    checker_required = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether Checker approval is required"
    )
    checker_user_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Branch Head who reviewed"
    )
    checker_action = Column(
        SQLEnum(WorkflowActionType),
        nullable=True,
        comment="Action taken by Checker (APPROVE/REJECT)"
    )
    checker_comment = Column(
        Text,
        nullable=True,
        comment="Checker's comments or justification"
    )
    checker_actioned_at = Column(
        JSONB,
        nullable=True,
        comment="Timestamp when Checker took action"
    )
    
    # Approver (Level 3 - Zonal Head)
    approver_required = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether Approver sign-off is required (High-Risk/PEP/Override)"
    )
    approver_user_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Zonal Head who gave final approval"
    )
    approver_action = Column(
        SQLEnum(WorkflowActionType),
        nullable=True,
        comment="Action taken by Approver (APPROVE/REJECT)"
    )
    approver_comment = Column(
        Text,
        nullable=True,
        comment="Approver's comments or justification"
    )
    approver_actioned_at = Column(
        JSONB,
        nullable=True,
        comment="Timestamp when Approver took action"
    )
    
    # Override Handling
    is_override_request = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether this is a risk rating override request"
    )
    override_justification = Column(
        Text,
        nullable=True,
        comment="Mandatory justification for override requests"
    )
    original_risk_score = Column(
        Integer,
        nullable=True,
        comment="Original system-calculated risk score"
    )
    override_risk_score = Column(
        Integer,
        nullable=True,
        comment="Requested override risk score"
    )
    risk_impact_analysis = Column(
        JSONB,
        nullable=True,
        comment="Visual diff showing which rules are being bypassed"
    )
    
    # Branch/Zone for RLS
    branch_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Branch where verification was initiated"
    )
    zone_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Zone for Approver visibility"
    )
    
    # Metadata
    priority = Column(
        String(20),
        nullable=False,
        default="NORMAL",
        comment="Priority: LOW, NORMAL, HIGH, URGENT"
    )
    sla_due_date = Column(
        JSONB,
        nullable=True,
        comment="SLA deadline for completion"
    )
    notes = Column(
        Text,
        nullable=True,
        comment="Additional notes"
    )
    
    __table_args__ = (
        Index("idx_workflow_state_branch", "current_state", "branch_id", "is_deleted"),
        Index("idx_workflow_pending_checker", "current_state", "checker_user_id"),
        Index("idx_workflow_pending_approver", "current_state", "approver_user_id"),
        Index("idx_workflow_override", "is_override_request", "current_state"),
        {"comment": "Multi-level approval workflow (Maker-Checker-Approver)"}
    )
    
    def __repr__(self) -> str:
        return f"<Workflow(id={self.id}, state={self.current_state}, override={self.is_override_request})>"

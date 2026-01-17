"""
Verification Result model storing complete verification data from VerifyMe.ng.
Includes BVN, NIN, CAC responses and cross-validation analysis.
"""

from sqlalchemy import Column, String, Integer, Boolean, Enum as SQLEnum, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
import uuid
from app.core.types import UUID, JSONB
import enum
from app.models.base import TimeStampedModel


class VerificationStatus(str, enum.Enum):
    """Status of verification request."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class VerificationType(str, enum.Enum):
    """Type of verification performed."""
    INDIVIDUAL = "INDIVIDUAL"  # BVN + NIN only
    CORPORATE = "CORPORATE"   # CAC only
    COMPLETE = "COMPLETE"      # Individual + Corporate + Risk


class VerificationResult(TimeStampedModel):
    """
    Complete verification result with external provider responses.
    Stores raw data from VerifyMe.ng and computed cross-validation results.
    """
    
    __tablename__ = "verification_results"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique verification identifier"
    )
    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Reference to customer record"
    )
    client_id = Column(
        UUID(as_uuid=True),
        ForeignKey("api_clients.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="API client who requested verification (null for internal)"
    )
    verification_type = Column(
        SQLEnum(VerificationType),
        nullable=False,
        comment="Type of verification performed"
    )
    status = Column(
        SQLEnum(VerificationStatus),
        nullable=False,
        default=VerificationStatus.PENDING,
        index=True,
        comment="Current status of verification"
    )
    
    # BVN Verification Data
    bvn_verified = Column(
        Boolean,
        nullable=True,
        comment="BVN validation successful"
    )
    bvn_data = Column(
        JSONB,
        nullable=True,
        comment="Raw BVN response from VerifyMe.ng"
    )
    bvn_name = Column(
        String(255),
        nullable=True,
        comment="Name from BVN record"
    )
    bvn_dob = Column(
        String(20),
        nullable=True,
        comment="Date of birth from BVN"
    )
    bvn_phone = Column(
        String(20),
        nullable=True,
        comment="Phone number from BVN"
    )
    
    # NIN Verification Data
    nin_verified = Column(
        Boolean,
        nullable=True,
        comment="NIN validation successful"
    )
    nin_data = Column(
        JSONB,
        nullable=True,
        comment="Raw NIN response from VerifyMe.ng"
    )
    nin_name = Column(
        String(255),
        nullable=True,
        comment="Name from NIN record"
    )
    nin_dob = Column(
        String(20),
        nullable=True,
        comment="Date of birth from NIN"
    )
    nin_address = Column(
        String(500),
        nullable=True,
        comment="Address from NIN record"
    )
    
    # CAC Verification Data
    cac_verified = Column(
        Boolean,
        nullable=True,
        comment="CAC lookup successful"
    )
    cac_data = Column(
        JSONB,
        nullable=True,
        comment="Raw CAC response from VerifyMe.ng (company details, directors, shareholders)"
    )
    cac_company_name = Column(
        String(255),
        nullable=True,
        comment="Registered company name from CAC"
    )
    cac_incorporation_date = Column(
        String(20),
        nullable=True,
        comment="Date of incorporation from CAC"
    )
    cac_status = Column(
        String(50),
        nullable=True,
        comment="Company registration status"
    )
    
    # Cross-Validation Results
    cross_validation_passed = Column(
        Boolean,
        nullable=True,
        comment="BVN/NIN cross-validation passed"
    )
    cross_validation_confidence = Column(
        Integer,
        nullable=True,
        comment="Confidence score 0-100 for name/DOB matching"
    )
    cross_validation_issues = Column(
        JSONB,
        nullable=True,
        comment="List of discrepancies found (name_mismatch, dob_mismatch, etc.)"
    )
    cross_validation_details = Column(
        Text,
        nullable=True,
        comment="Human-readable explanation of validation results"
    )
    
    # UBO Analysis Results (for corporate)
    ubo_identified = Column(
        Boolean,
        nullable=True,
        comment="Ultimate Beneficial Owners successfully identified"
    )
    ubo_data = Column(
        JSONB,
        nullable=True,
        comment="UBO analysis results with shareholders ≥25%"
    )
    ubo_count = Column(
        Integer,
        nullable=True,
        comment="Number of UBOs identified"
    )
    
    # Risk Assessment
    risk_score = Column(
        Integer,
        nullable=True,
        comment="Calculated risk score 0-100"
    )
    risk_category = Column(
        String(20),
        nullable=True,
        comment="Risk category: LOW, MEDIUM, HIGH, PROHIBITED"
    )
    risk_breakdown = Column(
        JSONB,
        nullable=True,
        comment="Detailed risk score breakdown by factor"
    )
    
    # Provider Metadata
    provider_name = Column(
        String(50),
        nullable=False,
        default="verifyme",
        comment="Verification provider used (verifyme, mock)"
    )
    provider_request_id = Column(
        String(100),
        nullable=True,
        comment="Provider's internal request ID for tracing"
    )
    processing_time_ms = Column(
        Integer,
        nullable=True,
        comment="Total processing time in milliseconds"
    )
    
    # Report
    report_url = Column(
        String(500),
        nullable=True,
        comment="URL to download verification report"
    )
    report_generated_at = Column(
        JSONB,
        nullable=True,
        comment="Timestamp when report was generated"
    )
    
    # Error Tracking
    error_code = Column(
        String(100),
        nullable=True,
        comment="Error code if verification failed"
    )
    error_message = Column(
        Text,
        nullable=True,
        comment="Error message for failed verifications"
    )
    
    # Relationships
    customer = relationship("Customer", back_populates="verification_results")
    client = relationship("ApiClient", foreign_keys=[client_id])
    
    __table_args__ = (
        Index("idx_verification_status", "status", "is_deleted"),
        Index("idx_verification_customer", "customer_id", "created_at"),
        Index("idx_verification_client", "client_id", "created_at"),
        {"comment": "Complete verification results with provider responses and analysis"}
    )
    
    def __repr__(self) -> str:
        return f"<VerificationResult(id={self.id}, type={self.verification_type}, status={self.status})>"

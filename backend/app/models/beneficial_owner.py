"""
Beneficial Ownership model for tracking UBOs per FATF/CBN requirements.
Identifies individuals with ≥25% ownership or control of corporate entities.
"""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Date, Index, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
import uuid
from app.core.types import UUID, JSONB
from app.models.base import TimeStampedModel


class BeneficialOwner(TimeStampedModel):
    """
    Ultimate Beneficial Owner (UBO) with ≥25% ownership or effective control.
    Traces corporate ownership to natural persons per FATF Recommendation 24.
    """
    
    __tablename__ = "beneficial_owners"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique beneficial owner record identifier"
    )
    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Corporate customer this UBO relates to"
    )
    
    # UBO Identity
    full_name = Column(
        String(255),
        nullable=False,
        comment="Full legal name of beneficial owner"
    )
    bvn = Column(
        String(11),
        nullable=True,
        index=True,
        comment="BVN of beneficial owner (if Nigerian)"
    )
    nin = Column(
        String(11),
        nullable=True,
        comment="NIN of beneficial owner"
    )
    date_of_birth = Column(
        Date,
        nullable=True,
        comment="Date of birth"
    )
    nationality = Column(
        String(100),
        nullable=True,
        comment="Nationality"
    )
    residential_address = Column(
        String(500),
        nullable=True,
        comment="Residential address"
    )
    
    # Ownership Details
    ownership_percentage = Column(
        Numeric(5, 2),
        nullable=False,
        comment="Percentage of ownership (0.00 to 100.00)"
    )
    ownership_type = Column(
        String(100),
        nullable=False,
        default="DIRECT",
        comment="DIRECT or INDIRECT ownership"
    )
    control_mechanism = Column(
        String(200),
        nullable=True,
        comment="How control is exercised (e.g., voting rights, board control)"
    )
    trace_depth = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Number of corporate layers traced to identify UBO"
    )
    
    # Verification Status
    bvn_verified = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether BVN has been verified"
    )
    is_pep = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether UBO is a Politically Exposed Person"
    )
    sanctions_screened = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether sanctions screening has been performed"
    )
    sanctions_match = Column(
        Boolean,
        nullable=True,
        comment="Whether UBO matched sanctions lists"
    )
    
    # Metadata
    source_document = Column(
        String(100),
        nullable=True,
        comment="Source document (e.g., CAC Form 2, Shareholder Register)"
    )
    effective_date = Column(
        Date,
        nullable=True,
        comment="Date ownership became effective"
    )
    notes = Column(
        String(1000),
        nullable=True,
        comment="Additional notes on ownership structure"
    )
    verification_data = Column(
        JSONB,
        nullable=True,
        comment="Raw verification data from VerifyMe.ng for this UBO"
    )
    
    # Relationships
    customer = relationship("Customer", back_populates="beneficial_owners")
    
    __table_args__ = (
        Index("idx_ubo_customer", "customer_id", "is_deleted"),
        Index("idx_ubo_ownership", "ownership_percentage", "is_deleted"),
        Index("idx_ubo_pep", "is_pep", "sanctions_match"),
        {"comment": "Ultimate Beneficial Owners with ≥25% ownership or control"}
    )
    
    def __repr__(self) -> str:
        return f"<BeneficialOwner(id={self.id}, name='{self.full_name}', ownership={self.ownership_percentage}%)>"

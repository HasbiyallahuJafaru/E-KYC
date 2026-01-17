"""
Document model for storing customer KYC documents with expiry tracking.
Supports ID cards, passports, utility bills, and corporate certificates.
"""

from sqlalchemy import Column, String, Integer, Date, Enum as SQLEnum, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
import uuid
from app.core.types import UUID, JSONB
import enum
from app.models.base import TimeStampedModel


class DocumentType(str, enum.Enum):
    """Document types per CBN KYC requirements."""
    # Individual ID Documents
    NATIONAL_ID = "NATIONAL_ID"
    INTERNATIONAL_PASSPORT = "INTERNATIONAL_PASSPORT"
    DRIVERS_LICENSE = "DRIVERS_LICENSE"
    VOTERS_CARD = "VOTERS_CARD"
    
    # Address Verification
    UTILITY_BILL = "UTILITY_BILL"
    BANK_STATEMENT = "BANK_STATEMENT"
    TENANCY_AGREEMENT = "TENANCY_AGREEMENT"
    
    # Corporate Documents
    CAC_CERTIFICATE = "CAC_CERTIFICATE"
    CAC_FORM_2 = "CAC_FORM_2"  # Share allotment
    CAC_FORM_7 = "CAC_FORM_7"  # Directors particulars
    MEMORANDUM_OF_ASSOCIATION = "MEMORANDUM_OF_ASSOCIATION"
    
    # Supporting Documents
    PASSPORT_PHOTOGRAPH = "PASSPORT_PHOTOGRAPH"
    EMPLOYMENT_LETTER = "EMPLOYMENT_LETTER"
    REFERENCE_LETTER = "REFERENCE_LETTER"
    TAX_CLEARANCE = "TAX_CLEARANCE"


class DocumentStatus(str, enum.Enum):
    """Document verification status."""
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class Document(TimeStampedModel):
    """
    Customer document with metadata and verification status.
    Tracks expiry dates and proactive notifications per compliance requirements.
    """
    
    __tablename__ = "documents"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique document identifier"
    )
    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Customer who owns this document"
    )
    document_type = Column(
        SQLEnum(DocumentType),
        nullable=False,
        index=True,
        comment="Type of document"
    )
    document_number = Column(
        String(100),
        nullable=True,
        comment="Document number (passport number, ID number, etc.)"
    )
    issue_date = Column(
        Date,
        nullable=True,
        comment="Date document was issued"
    )
    expiry_date = Column(
        Date,
        nullable=True,
        index=True,
        comment="Document expiration date"
    )
    issuing_authority = Column(
        String(200),
        nullable=True,
        comment="Authority that issued the document"
    )
    issuing_country = Column(
        String(100),
        nullable=True,
        default="Nigeria",
        comment="Country that issued the document"
    )
    
    # Storage
    file_path = Column(
        String(500),
        nullable=True,
        comment="Encrypted storage path for document file"
    )
    file_size_bytes = Column(
        Integer,
        nullable=True,
        comment="File size in bytes"
    )
    file_mime_type = Column(
        String(100),
        nullable=True,
        comment="MIME type of uploaded file"
    )
    file_hash = Column(
        String(64),
        nullable=True,
        comment="SHA-256 hash for integrity verification"
    )
    
    # Verification Status
    status = Column(
        SQLEnum(DocumentStatus),
        nullable=False,
        default=DocumentStatus.PENDING_REVIEW,
        index=True,
        comment="Current verification status"
    )
    verified_by_user_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="User who verified this document"
    )
    verified_at = Column(
        JSONB,
        nullable=True,
        comment="Timestamp when document was verified"
    )
    rejection_reason = Column(
        String(500),
        nullable=True,
        comment="Reason for rejection if status is REJECTED"
    )
    
    # Metadata
    notes = Column(
        String(1000),
        nullable=True,
        comment="Additional notes or observations"
    )
    is_primary = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this is the primary document of its type"
    )
    
    # Relationships
    customer = relationship("Customer", back_populates="documents")
    
    __table_args__ = (
        Index("idx_document_expiry", "expiry_date", "status"),
        Index("idx_document_customer_type", "customer_id", "document_type"),
        {"comment": "Customer KYC documents with expiry tracking"}
    )
    
    def __repr__(self) -> str:
        return f"<Document(id={self.id}, type={self.document_type}, status={self.status})>"

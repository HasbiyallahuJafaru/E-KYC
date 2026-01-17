"""
Customer model representing individuals or corporate entities undergoing verification.
Stores customer details, risk ratings, and tier classifications per CBN requirements.
"""

from sqlalchemy import Column, String, Date, Boolean, Enum as SQLEnum, Integer, Index
from sqlalchemy.orm import relationship
import uuid
from app.core.types import UUID, JSONB
import enum
from app.models.base import TimeStampedModel


class CustomerType(str, enum.Enum):
    """Customer classification types per CBN/FATF guidelines."""
    INDIVIDUAL = "INDIVIDUAL"
    CORPORATE = "CORPORATE"
    NGO = "NGO"
    GOVERNMENT = "GOVERNMENT"


class RiskRating(str, enum.Enum):
    """Risk assessment categories."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    PROHIBITED = "PROHIBITED"


class KYCTier(str, enum.Enum):
    """CBN KYC tier classifications with transaction limits."""
    TIER_1 = "TIER_1"  # Entry level: NGN 300k balance, NGN 50k daily
    TIER_2 = "TIER_2"  # Medium: NGN 500k balance, NGN 200k daily
    TIER_3 = "TIER_3"  # Full KYC: Unlimited


class Customer(TimeStampedModel):
    """
    Customer entity with complete KYC/CDD information.
    Supports both individual and corporate customers per Nigerian banking standards.
    """
    
    __tablename__ = "customers"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique customer identifier"
    )
    customer_type = Column(
        SQLEnum(CustomerType),
        nullable=False,
        index=True,
        comment="Customer type: individual, corporate, NGO, government"
    )
    
    # Individual Customer Fields
    bvn = Column(
        String(11),
        nullable=True,
        unique=True,
        index=True,
        comment="Bank Verification Number (11 digits, mandatory for individuals)"
    )
    nin = Column(
        String(11),
        nullable=True,
        index=True,
        comment="National Identification Number (11 digits)"
    )
    first_name = Column(
        String(100),
        nullable=True,
        comment="Customer first name"
    )
    middle_name = Column(
        String(100),
        nullable=True,
        comment="Customer middle name"
    )
    last_name = Column(
        String(100),
        nullable=True,
        comment="Customer last name"
    )
    date_of_birth = Column(
        Date,
        nullable=True,
        comment="Date of birth for individuals"
    )
    
    # Corporate Customer Fields
    rc_number = Column(
        String(50),
        nullable=True,
        unique=True,
        index=True,
        comment="CAC Registration Number for corporate entities"
    )
    business_name = Column(
        String(255),
        nullable=True,
        comment="Registered business name"
    )
    incorporation_date = Column(
        Date,
        nullable=True,
        comment="Date of incorporation"
    )
    
    # Common Fields
    phone_number = Column(
        String(20),
        nullable=False,
        comment="Primary phone number"
    )
    email = Column(
        String(255),
        nullable=True,
        comment="Email address"
    )
    residential_address = Column(
        String(500),
        nullable=True,
        comment="Residential or business address"
    )
    city = Column(
        String(100),
        nullable=True,
        comment="City"
    )
    state = Column(
        String(100),
        nullable=True,
        comment="State"
    )
    country = Column(
        String(100),
        nullable=False,
        default="Nigeria",
        comment="Country (ISO code or name)"
    )
    nationality = Column(
        String(100),
        nullable=True,
        comment="Nationality for individuals"
    )
    
    # KYC Classification
    kyc_tier = Column(
        SQLEnum(KYCTier),
        nullable=False,
        default=KYCTier.TIER_1,
        comment="CBN KYC tier classification"
    )
    risk_rating = Column(
        SQLEnum(RiskRating),
        nullable=False,
        default=RiskRating.LOW,
        index=True,
        comment="Current risk assessment rating"
    )
    risk_score = Column(
        Integer,
        nullable=True,
        comment="Calculated risk score (0-100)"
    )
    is_pep = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Politically Exposed Person flag"
    )
    pep_details = Column(
        JSONB,
        nullable=True,
        comment="PEP position and relationship details"
    )
    
    # Occupation and Business
    occupation = Column(
        String(200),
        nullable=True,
        comment="Occupation for individuals"
    )
    industry_sector = Column(
        String(200),
        nullable=True,
        comment="Industry sector or line of business"
    )
    source_of_funds = Column(
        String(200),
        nullable=True,
        comment="Source of funds/income"
    )
    expected_monthly_turnover = Column(
        Integer,
        nullable=True,
        comment="Expected monthly transaction volume in NGN"
    )
    
    # Branch Assignment for Row-Level Security
    branch_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Branch handling this customer (for RLS)"
    )
    zone_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Zone for hierarchical approval (for RLS)"
    )
    
    # Metadata
    external_reference = Column(
        String(100),
        nullable=True,
        comment="Client's internal customer reference"
    )
    extra_data = Column(
        JSONB,
        nullable=True,
        comment="Additional custom fields"
    )
    
    # Relationships
    verification_results = relationship(
        "VerificationResult",
        back_populates="customer",
        lazy="dynamic"
    )
    documents = relationship(
        "Document",
        back_populates="customer",
        lazy="dynamic"
    )
    beneficial_owners = relationship(
        "BeneficialOwner",
        back_populates="customer",
        lazy="dynamic"
    )
    
    __table_args__ = (
        Index("idx_customer_risk", "risk_rating", "is_deleted"),
        Index("idx_customer_branch", "branch_id", "is_deleted"),
        Index("idx_customer_pep", "is_pep", "risk_rating"),
        {"comment": "Customer master data with KYC/CDD information"}
    )
    
    def __repr__(self) -> str:
        if self.customer_type == CustomerType.INDIVIDUAL:
            return f"<Customer(id={self.id}, name='{self.first_name} {self.last_name}', bvn='{self.bvn}')>"
        else:
            return f"<Customer(id={self.id}, business='{self.business_name}', rc='{self.rc_number}')>"

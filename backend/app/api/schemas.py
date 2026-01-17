"""
Pydantic schemas for API request/response validation.
Ensures type safety and automatic API documentation.
"""

from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


# Request Schemas
class IndividualVerificationRequest(BaseModel):
    """Request schema for individual verification."""
    bvn: str = Field(..., min_length=11, max_length=11, description="11-digit Bank Verification Number")
    nin: str = Field(..., min_length=11, max_length=11, description="11-digit National Identification Number")
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    
    @field_validator('bvn', 'nin')
    @classmethod
    def validate_numeric(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('Must contain only digits')
        return v


class CorporateVerificationRequest(BaseModel):
    """Request schema for corporate verification."""
    rc_number: str = Field(..., min_length=5, max_length=50, description="CAC Registration Number")
    business_name: Optional[str] = Field(None, max_length=255)
    expected_ubo_count: Optional[int] = Field(None, ge=1, le=10)


class CompleteVerificationRequest(BaseModel):
    """Request schema for complete verification (individual + corporate)."""
    # Individual fields
    bvn: str = Field(..., min_length=11, max_length=11)
    nin: str = Field(..., min_length=11, max_length=11)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    date_of_birth: Optional[date] = None
    
    # Corporate fields (optional)
    rc_number: Optional[str] = Field(None, max_length=50)
    business_name: Optional[str] = Field(None, max_length=255)
    
    # Additional context
    occupation: Optional[str] = Field(None, max_length=200)
    industry_sector: Optional[str] = None
    is_pep: bool = False
    nationality: str = Field(default="Nigeria", max_length=100)


# Response Schemas
class BVNData(BaseModel):
    """BVN verification data."""
    verified: bool
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    phone_number: Optional[str] = None
    

class NINData(BaseModel):
    """NIN verification data."""
    verified: bool
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None


class CrossValidationData(BaseModel):
    """Cross-validation result data."""
    passed: bool
    confidence: int = Field(..., ge=0, le=100)
    issues: List[str]
    explanation: str


class UBOInfo(BaseModel):
    """Ultimate Beneficial Owner information."""
    name: str
    ownership_percentage: float
    ownership_type: str
    is_verified: bool = False


class CACData(BaseModel):
    """CAC registry data."""
    verified: bool
    company_name: Optional[str] = None
    incorporation_date: Optional[str] = None
    status: Optional[str] = None
    ubo_count: Optional[int] = None
    ubos: Optional[List[UBOInfo]] = None


class RiskAssessment(BaseModel):
    """Risk assessment result."""
    score: int = Field(..., ge=0, le=100)
    category: str  # LOW, MEDIUM, HIGH, PROHIBITED
    breakdown: dict
    risk_drivers: List[str]
    required_actions: List[str]


class VerificationResponse(BaseModel):
    """Complete verification response."""
    verification_id: UUID
    status: str  # PENDING, PROCESSING, COMPLETED, FAILED
    verification_type: str  # INDIVIDUAL, CORPORATE, COMPLETE
    
    # BVN/NIN data
    bvn_data: Optional[BVNData] = None
    nin_data: Optional[NINData] = None
    cross_validation: Optional[CrossValidationData] = None
    
    # CAC/UBO data
    cac_data: Optional[CACData] = None
    
    # Risk assessment
    risk_assessment: Optional[RiskAssessment] = None
    
    # Report
    report_url: Optional[str] = None
    
    # Metadata
    processing_time_ms: Optional[int] = None
    created_at: str
    
    # Error info (if failed)
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Standard error response."""
    error_code: str
    message: str
    details: Optional[dict] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    environment: str
    version: str

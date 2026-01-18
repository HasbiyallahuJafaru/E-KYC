"""
Base interface for verification providers.
Defines contract that all providers (VerifyMe.ng, mock, future alternatives) must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class BVNResult:
    """Structured BVN verification result."""
    success: bool
    bvn: str
    full_name: str
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None  # Format: YYYY-MM-DD
    phone_number: Optional[str] = None
    gender: Optional[str] = None
    raw_data: Optional[dict] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class NINResult:
    """Structured NIN verification result."""
    success: bool
    nin: str
    full_name: str
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None  # Format: YYYY-MM-DD
    gender: Optional[str] = None
    address: Optional[str] = None
    state_of_origin: Optional[str] = None
    lga: Optional[str] = None
    raw_data: Optional[dict] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class ShareholderInfo:
    """Individual shareholder information."""
    name: str
    percentage: float
    is_corporate: bool
    corporate_rc: Optional[str] = None


@dataclass
class DirectorInfo:
    """Company director information."""
    name: str
    position: str
    appointment_date: Optional[str] = None
    status: Optional[str] = None  # ACTIVE, REMOVED, RESIGNED
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


@dataclass
class ProprietorInfo:
    """Business name proprietor/partner information."""
    name: str
    percentage: Optional[float] = None  # For partnerships
    address: Optional[str] = None
    nationality: Optional[str] = None


@dataclass
class TrusteeInfo:
    """NGO/Incorporated Trustee information."""
    name: str
    appointment_date: Optional[str] = None
    address: Optional[str] = None


@dataclass
class CACResult:
    """Structured CAC registry lookup result."""
    success: bool
    rc_number: str
    company_name: str
    entity_type: Optional[str] = None  # LIMITED, PLC, BUSINESS_NAME, NGO, INCORPORATED_TRUSTEES
    company_type: Optional[str] = None  # Ltd, PLC, Business Name, NGO (for backward compatibility)
    status: Optional[str] = None  # ACTIVE, INACTIVE, DISSOLVED
    incorporation_date: Optional[str] = None  # Format: YYYY-MM-DD
    registered_address: Optional[str] = None
    
    # Fields for Limited Companies (Ltd/PLC)
    directors: list[DirectorInfo] = None
    shareholders: list[ShareholderInfo] = None
    share_capital: Optional[float] = None
    company_email: Optional[str] = None
    company_phone: Optional[str] = None
    
    # Fields for Business Names
    proprietors: list[ProprietorInfo] = None
    business_commencement_date: Optional[str] = None
    nature_of_business: Optional[str] = None
    
    # Fields for NGOs/Incorporated Trustees
    trustees: list[TrusteeInfo] = None
    aims_and_objectives: Optional[str] = None
    
    # Common optional fields
    city: Optional[str] = None
    state: Optional[str] = None
    lga: Optional[str] = None
    postal_code: Optional[str] = None
    branch_address: Optional[str] = None
    
    raw_data: Optional[dict] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.directors is None:
            self.directors = []
        if self.shareholders is None:
            self.shareholders = []
        if self.proprietors is None:
            self.proprietors = []
        if self.trustees is None:
            self.trustees = []


class VerificationProvider(ABC):
    """
    Abstract base class for verification providers.
    All provider implementations must adhere to this interface.
    """
    
    @abstractmethod
    async def verify_bvn(self, bvn: str) -> BVNResult:
        """
        Verify a Bank Verification Number.
        
        Args:
            bvn: 11-digit BVN string
            
        Returns:
            BVNResult with verification data or error
            
        Raises:
            ProviderUnavailableError: Service temporarily unavailable
            ProviderTimeoutError: Request timed out
            BVNValidationError: Invalid BVN format or not found
        """
        pass
    
    @abstractmethod
    async def verify_nin(self, nin: str) -> NINResult:
        """
        Verify a National Identification Number.
        
        Args:
            nin: 11-digit NIN string
            
        Returns:
            NINResult with verification data or error
            
        Raises:
            ProviderUnavailableError: Service temporarily unavailable
            ProviderTimeoutError: Request timed out
            NINValidationError: Invalid NIN format or not found
        """
        pass
    
    @abstractmethod
    async def verify_cac(self, rc_number: str) -> CACResult:
        """
        Lookup company in CAC registry.
        
        Args:
            rc_number: CAC Registration/RC number
            
        Returns:
            CACResult with company details, directors, and shareholders
            
        Raises:
            ProviderUnavailableError: Service temporarily unavailable
            ProviderTimeoutError: Request timed out
            CACLookupError: Invalid RC number or company not found
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider."""
        pass

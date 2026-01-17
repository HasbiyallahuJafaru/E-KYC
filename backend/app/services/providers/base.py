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


@dataclass
class CACResult:
    """Structured CAC registry lookup result."""
    success: bool
    rc_number: str
    company_name: str
    company_type: Optional[str] = None  # Ltd, PLC, Business Name, NGO
    status: Optional[str] = None  # ACTIVE, INACTIVE, DISSOLVED
    incorporation_date: Optional[str] = None  # Format: YYYY-MM-DD
    registered_address: Optional[str] = None
    directors: list[DirectorInfo] = None
    shareholders: list[ShareholderInfo] = None
    share_capital: Optional[float] = None
    raw_data: Optional[dict] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.directors is None:
            self.directors = []
        if self.shareholders is None:
            self.shareholders = []


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

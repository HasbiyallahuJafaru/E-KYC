"""
VerifyMe.ng API client for production verification.
Implements Authorization: Bearer <secret> pattern per VerifyMe.ng docs.
"""

import httpx
from typing import Optional
from app.services.providers.base import (
    VerificationProvider,
    BVNResult,
    NINResult,
    CACResult,
    ShareholderInfo,
    DirectorInfo
)
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import (
    BVNValidationError,
    NINValidationError,
    CACLookupError,
    ProviderUnavailableError,
    ProviderTimeoutError
)

logger = get_logger(__name__)


class VerifyMeProvider(VerificationProvider):
    """
    VerifyMe.ng API client with proper error handling and retry logic.
    Uses synchronous HTTP calls for speed (fail-fast approach).
    """
    
    def __init__(self):
        self.base_url = settings.verifyme_base_url
        self.secret = settings.verifyme_secret
        self.timeout = settings.provider_timeout_seconds
        
        # HTTP client with timeout configuration
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
            headers={
                "Authorization": f"Bearer {self.secret}",
                "Content-Type": "application/json"
            }
        )
    
    async def _make_request(
        self,
        endpoint: str,
        payload: dict,
        error_class: type
    ) -> dict:
        """
        Make HTTP request to VerifyMe.ng with error handling.
        
        Args:
            endpoint: API endpoint path
            payload: Request JSON payload
            error_class: Exception class to raise on errors
            
        Returns:
            Response JSON data
            
        Raises:
            ProviderTimeoutError: Request timed out
            ProviderUnavailableError: Service unavailable (5xx)
            error_class: Validation failed (4xx)
        """
        try:
            logger.info(f"Calling VerifyMe.ng: {endpoint}")
            
            response = await self.client.post(endpoint, json=payload)
            
            # Handle successful responses
            if response.status_code == 200:
                data = response.json()
                logger.info(f"VerifyMe.ng success: {endpoint}")
                return data
            
            # Handle client errors (4xx)
            if 400 <= response.status_code < 500:
                error_data = response.json() if response.text else {}
                error_message = error_data.get("message", "Validation failed")
                logger.warning(f"VerifyMe.ng validation error: {error_message}")
                raise error_class(
                    message=error_message,
                    details={"status_code": response.status_code, "response": error_data}
                )
            
            # Handle server errors (5xx)
            if response.status_code >= 500:
                logger.error(f"VerifyMe.ng server error: {response.status_code}")
                raise ProviderUnavailableError(
                    message="VerifyMe.ng service temporarily unavailable",
                    details={"status_code": response.status_code}
                )
            
            # Unexpected status code
            raise ProviderUnavailableError(
                message=f"Unexpected response from VerifyMe.ng: {response.status_code}"
            )
        
        except httpx.TimeoutException:
            logger.error(f"VerifyMe.ng timeout on {endpoint}")
            raise ProviderTimeoutError(
                message="VerifyMe.ng request timed out",
                details={"endpoint": endpoint, "timeout_seconds": self.timeout}
            )
        
        except httpx.ConnectError:
            logger.error(f"VerifyMe.ng connection error on {endpoint}")
            raise ProviderUnavailableError(
                message="Could not connect to VerifyMe.ng",
                details={"endpoint": endpoint}
            )
        
        except (BVNValidationError, NINValidationError, CACLookupError, 
                ProviderUnavailableError, ProviderTimeoutError):
            # Re-raise our custom exceptions
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error calling VerifyMe.ng: {str(e)}", exc_info=True)
            raise ProviderUnavailableError(
                message="Unexpected error communicating with VerifyMe.ng",
                details={"error": str(e)}
            )
    
    async def verify_bvn(self, bvn: str) -> BVNResult:
        """
        Verify BVN via VerifyMe.ng API.
        
        Endpoint: POST /v1/verifications/identity/bvn
        Request: {"bvn": "22123456789"}
        """
        # Basic validation
        if not bvn or len(bvn) != 11 or not bvn.isdigit():
            return BVNResult(
                success=False,
                bvn=bvn,
                full_name="",
                error_code="INVALID_BVN_FORMAT",
                error_message="BVN must be exactly 11 digits"
            )
        
        try:
            # Call VerifyMe.ng
            data = await self._make_request(
                endpoint="/verifications/identity/bvn",
                payload={"bvn": bvn},
                error_class=BVNValidationError
            )
            
            # Parse response (adjust based on actual VerifyMe.ng response format)
            # This is a template - update when you have actual API documentation
            verification_data = data.get("data", {})
            
            return BVNResult(
                success=True,
                bvn=bvn,
                full_name=verification_data.get("fullName", ""),
                first_name=verification_data.get("firstName"),
                middle_name=verification_data.get("middleName"),
                last_name=verification_data.get("lastName"),
                date_of_birth=verification_data.get("dateOfBirth"),
                phone_number=verification_data.get("phoneNumber"),
                gender=verification_data.get("gender"),
                raw_data=verification_data
            )
        
        except (BVNValidationError, ProviderUnavailableError, ProviderTimeoutError) as e:
            # Return error result instead of raising
            return BVNResult(
                success=False,
                bvn=bvn,
                full_name="",
                error_code=e.error_code,
                error_message=e.message
            )
    
    async def verify_nin(self, nin: str) -> NINResult:
        """
        Verify NIN via VerifyMe.ng API.
        
        Endpoint: POST /v1/verifications/identity/nin
        Request: {"nin": "12345678901"}
        """
        # Basic validation
        if not nin or len(nin) != 11 or not nin.isdigit():
            return NINResult(
                success=False,
                nin=nin,
                full_name="",
                error_code="INVALID_NIN_FORMAT",
                error_message="NIN must be exactly 11 digits"
            )
        
        try:
            # Call VerifyMe.ng
            data = await self._make_request(
                endpoint="/verifications/identity/nin",
                payload={"nin": nin},
                error_class=NINValidationError
            )
            
            # Parse response
            verification_data = data.get("data", {})
            
            return NINResult(
                success=True,
                nin=nin,
                full_name=verification_data.get("fullName", ""),
                first_name=verification_data.get("firstName"),
                middle_name=verification_data.get("middleName"),
                last_name=verification_data.get("lastName"),
                date_of_birth=verification_data.get("dateOfBirth"),
                gender=verification_data.get("gender"),
                address=verification_data.get("address"),
                state_of_origin=verification_data.get("stateOfOrigin"),
                lga=verification_data.get("lga"),
                raw_data=verification_data
            )
        
        except (NINValidationError, ProviderUnavailableError, ProviderTimeoutError) as e:
            return NINResult(
                success=False,
                nin=nin,
                full_name="",
                error_code=e.error_code,
                error_message=e.message
            )
    
    async def verify_cac(self, rc_number: str) -> CACResult:
        """
        Lookup company in CAC registry via VerifyMe.ng API.
        
        Endpoint: POST /v1/verifications/business/cac
        Request: {"rc_number": "RC123456"}
        """
        # Basic validation
        if not rc_number or len(rc_number) < 5:
            return CACResult(
                success=False,
                rc_number=rc_number,
                company_name="",
                error_code="INVALID_RC_NUMBER",
                error_message="Invalid RC number format"
            )
        
        try:
            # Call VerifyMe.ng
            data = await self._make_request(
                endpoint="/verifications/business/cac",
                payload={"rc_number": rc_number},
                error_class=CACLookupError
            )
            
            # Parse response
            company_data = data.get("data", {})
            
            # Parse directors
            directors = []
            for director_data in company_data.get("directors", []):
                directors.append(DirectorInfo(
                    name=director_data.get("name", ""),
                    position=director_data.get("position", "Director"),
                    appointment_date=director_data.get("appointmentDate")
                ))
            
            # Parse shareholders
            shareholders = []
            for shareholder_data in company_data.get("shareholders", []):
                shareholders.append(ShareholderInfo(
                    name=shareholder_data.get("name", ""),
                    percentage=float(shareholder_data.get("percentage", 0)),
                    is_corporate=shareholder_data.get("type") == "CORPORATE",
                    corporate_rc=shareholder_data.get("rc_number")
                ))
            
            return CACResult(
                success=True,
                rc_number=rc_number,
                company_name=company_data.get("companyName", ""),
                company_type=company_data.get("companyType"),
                status=company_data.get("status"),
                incorporation_date=company_data.get("incorporationDate"),
                registered_address=company_data.get("registeredAddress"),
                directors=directors,
                shareholders=shareholders,
                share_capital=company_data.get("shareCapital"),
                raw_data=company_data
            )
        
        except (CACLookupError, ProviderUnavailableError, ProviderTimeoutError) as e:
            return CACResult(
                success=False,
                rc_number=rc_number,
                company_name="",
                error_code=e.error_code,
                error_message=e.message
            )
    
    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "verifyme"
    
    async def close(self):
        """Close HTTP client connection."""
        await self.client.aclose()

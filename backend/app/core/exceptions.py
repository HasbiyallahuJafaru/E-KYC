"""
Custom exception hierarchy for the E-KYC Check application.
Provides clear, actionable error messages for API clients and internal debugging.
"""

from typing import Optional, Any


class EKYCBaseException(Exception):
    """Base exception for all E-KYC Check errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# Verification Provider Errors
class VerificationProviderError(EKYCBaseException):
    """Base exception for external verification provider errors."""
    pass


class BVNValidationError(VerificationProviderError):
    """BVN validation failed or service unavailable."""
    
    def __init__(self, message: str = "BVN validation failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="BVN_VALIDATION_FAILED",
            status_code=400,
            details=details
        )


class NINValidationError(VerificationProviderError):
    """NIN validation failed or service unavailable."""
    
    def __init__(self, message: str = "NIN validation failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="NIN_VALIDATION_FAILED",
            status_code=400,
            details=details
        )


class CACLookupError(VerificationProviderError):
    """CAC registry lookup failed or company not found."""
    
    def __init__(self, message: str = "CAC lookup failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="CAC_LOOKUP_FAILED",
            status_code=400,
            details=details
        )


class ProviderUnavailableError(VerificationProviderError):
    """Verification provider is temporarily unavailable."""
    
    def __init__(self, message: str = "Verification service temporarily unavailable", details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="PROVIDER_UNAVAILABLE",
            status_code=503,
            details=details
        )


class ProviderTimeoutError(VerificationProviderError):
    """Verification provider request timed out."""
    
    def __init__(self, message: str = "Verification request timed out", details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="PROVIDER_TIMEOUT",
            status_code=504,
            details=details
        )


# Authentication and Authorization Errors
class AuthenticationError(EKYCBaseException):
    """Authentication failed."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_FAILED",
            status_code=401,
            details=details
        )


class AuthorizationError(EKYCBaseException):
    """User does not have permission for this operation."""
    
    def __init__(self, message: str = "Access denied", details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="ACCESS_DENIED",
            status_code=403,
            details=details
        )


class RateLimitExceededError(EKYCBaseException):
    """API rate limit exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"retry_after": retry_after}
        )


# Validation Errors
class CrossValidationError(EKYCBaseException):
    """Cross-validation between BVN and NIN failed."""
    
    def __init__(self, message: str = "Cross-validation failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code="CROSS_VALIDATION_FAILED",
            status_code=422,
            details=details
        )


class InvalidInputError(EKYCBaseException):
    """Invalid input data provided."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            error_code="INVALID_INPUT",
            status_code=400,
            details=details
        )


# Workflow Errors
class WorkflowStateError(EKYCBaseException):
    """Invalid workflow state transition."""
    
    def __init__(self, message: str, current_state: str, requested_state: str):
        super().__init__(
            message=message,
            error_code="INVALID_WORKFLOW_STATE",
            status_code=409,
            details={"current_state": current_state, "requested_state": requested_state}
        )


# Resource Errors
class ResourceNotFoundError(EKYCBaseException):
    """Requested resource not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found",
            error_code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class ResourceAlreadyExistsError(EKYCBaseException):
    """Resource already exists."""
    
    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            message=f"{resource_type} already exists",
            error_code="RESOURCE_ALREADY_EXISTS",
            status_code=409,
            details={"resource_type": resource_type, "identifier": identifier}
        )

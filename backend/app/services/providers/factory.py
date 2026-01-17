"""
Provider factory for instantiating the correct verification provider.
Selects mock or VerifyMe.ng based on configuration.
"""

from app.services.providers.base import VerificationProvider
from app.services.providers.mock import MockProvider
from app.services.providers.verifyme import VerifyMeProvider
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_verification_provider() -> VerificationProvider:
    """
    Factory function to get the configured verification provider.
    
    Returns:
        VerificationProvider instance (MockProvider or VerifyMeProvider)
        
    Usage:
        provider = get_verification_provider()
        result = await provider.verify_bvn("22123456789")
    """
    provider_name = settings.verification_provider
    
    if provider_name == "mock":
        logger.info("Using MockProvider for verifications")
        return MockProvider()
    
    elif provider_name == "verifyme":
        logger.info("Using VerifyMeProvider for verifications")
        return VerifyMeProvider()
    
    else:
        logger.warning(f"Unknown provider '{provider_name}', falling back to MockProvider")
        return MockProvider()

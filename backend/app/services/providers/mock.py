"""
Mock verification provider for testing and development.
Returns realistic Nigerian data without calling external APIs.
"""

from typing import Optional
from app.services.providers.base import (
    VerificationProvider,
    BVNResult,
    NINResult,
    CACResult,
    ShareholderInfo,
    DirectorInfo
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class MockProvider(VerificationProvider):
    """
    Mock provider returning predefined test data.
    Useful for development, testing, and demos without API costs.
    """
    
    # Test data: Valid BVN that matches NIN
    VALID_BVN = "22123456789"
    VALID_NIN = "12345678901"
    
    # Test data: Mismatched names for cross-validation testing
    MISMATCH_BVN = "22987654321"
    MISMATCH_NIN = "19876543210"
    
    # Test data: Corporate
    VALID_RC = "RC123456"
    
    async def verify_bvn(self, bvn: str) -> BVNResult:
        """
        Mock BVN verification with predefined responses.
        Returns different data based on BVN value for testing scenarios.
        """
        logger.info(f"Mock BVN verification for: {bvn}")
        
        # Invalid format
        if len(bvn) != 11 or not bvn.isdigit():
            return BVNResult(
                success=False,
                bvn=bvn,
                full_name="",
                error_code="INVALID_BVN_FORMAT",
                error_message="BVN must be exactly 11 digits"
            )
        
        # Valid matching BVN
        if bvn == self.VALID_BVN:
            return BVNResult(
                success=True,
                bvn=bvn,
                full_name="OBI, JOHN PAUL",
                first_name="JOHN",
                middle_name="PAUL",
                last_name="OBI",
                date_of_birth="1985-03-15",
                phone_number="+2348031234567",
                gender="Male",
                raw_data={
                    "bvn": bvn,
                    "firstName": "JOHN",
                    "middleName": "PAUL",
                    "lastName": "OBI",
                    "dateOfBirth": "15-Mar-1985",
                    "phoneNumber": "08031234567",
                    "enrollmentBank": "058",
                    "enrollmentBranch": "Lagos",
                    "registrationDate": "2014-06-20"
                }
            )
        
        # Mismatch scenario - different name order
        if bvn == self.MISMATCH_BVN:
            return BVNResult(
                success=True,
                bvn=bvn,
                full_name="ADEBAYO, OLUWASEUN TEMITOPE",
                first_name="OLUWASEUN",
                middle_name="TEMITOPE",
                last_name="ADEBAYO",
                date_of_birth="1990-07-22",
                phone_number="+2347012345678",
                gender="Male",
                raw_data={
                    "bvn": bvn,
                    "firstName": "OLUWASEUN",
                    "middleName": "TEMITOPE",
                    "lastName": "ADEBAYO",
                    "dateOfBirth": "22-Jul-1990",
                    "phoneNumber": "07012345678"
                }
            )
        
        # BVN not found
        return BVNResult(
            success=False,
            bvn=bvn,
            full_name="",
            error_code="BVN_NOT_FOUND",
            error_message="BVN record not found in database"
        )
    
    async def verify_nin(self, nin: str) -> NINResult:
        """
        Mock NIN verification with predefined responses.
        Returns different data based on NIN value for testing scenarios.
        """
        logger.info(f"Mock NIN verification for: {nin}")
        
        # Invalid format
        if len(nin) != 11 or not nin.isdigit():
            return NINResult(
                success=False,
                nin=nin,
                full_name="",
                error_code="INVALID_NIN_FORMAT",
                error_message="NIN must be exactly 11 digits"
            )
        
        # Valid matching NIN (matches VALID_BVN)
        if nin == self.VALID_NIN:
            return NINResult(
                success=True,
                nin=nin,
                full_name="JOHN PAUL OBI",  # Different order from BVN
                first_name="JOHN",
                middle_name="PAUL",
                last_name="OBI",
                date_of_birth="1985-03-15",
                gender="M",
                address="12 Allen Avenue, Ikeja, Lagos State",
                state_of_origin="Anambra",
                lga="Onitsha North",
                raw_data={
                    "nin": nin,
                    "firstname": "JOHN",
                    "middlename": "PAUL",
                    "surname": "OBI",
                    "birthdate": "1985-03-15",
                    "gender": "M",
                    "residence_address": "12 Allen Avenue, Ikeja, Lagos State",
                    "residence_state": "Lagos",
                    "origin_state": "Anambra",
                    "origin_lga": "Onitsha North"
                }
            )
        
        # Mismatch scenario - completely different name order
        if nin == self.MISMATCH_NIN:
            return NINResult(
                success=True,
                nin=nin,
                full_name="TEMITOPE OLUWASEUN ADEBAYO",  # Different order
                first_name="TEMITOPE",
                middle_name="OLUWASEUN",
                last_name="ADEBAYO",
                date_of_birth="1990-07-22",
                gender="M",
                address="45 Ikorodu Road, Yaba, Lagos",
                state_of_origin="Oyo",
                lga="Ibadan North",
                raw_data={
                    "nin": nin,
                    "firstname": "TEMITOPE",
                    "middlename": "OLUWASEUN",
                    "surname": "ADEBAYO",
                    "birthdate": "1990-07-22"
                }
            )
        
        # NIN not found
        return NINResult(
            success=False,
            nin=nin,
            full_name="",
            error_code="NIN_NOT_FOUND",
            error_message="NIN record not found in NIMC database"
        )
    
    async def verify_cac(self, rc_number: str) -> CACResult:
        """
        Mock CAC verification with predefined corporate structures.
        Returns different company types for testing UBO analysis.
        """
        logger.info(f"Mock CAC verification for: {rc_number}")
        
        # Valid Ltd company with clear UBOs
        if rc_number.upper() == self.VALID_RC or rc_number.upper() == "RC123456":
            return CACResult(
                success=True,
                rc_number=rc_number,
                company_name="ALPHA TRADING LIMITED",
                company_type="Ltd",
                status="ACTIVE",
                incorporation_date="2018-06-12",
                registered_address="Plot 15, Adeola Odeku Street, Victoria Island, Lagos",
                share_capital=1000000.00,
                directors=[
                    DirectorInfo(
                        name="John Paul Obi",
                        position="Managing Director",
                        appointment_date="2018-06-12"
                    ),
                    DirectorInfo(
                        name="Amaka Nwosu",
                        position="Director",
                        appointment_date="2018-06-12"
                    )
                ],
                shareholders=[
                    ShareholderInfo(
                        name="John Paul Obi",
                        percentage=60.0,
                        is_corporate=False
                    ),
                    ShareholderInfo(
                        name="Amaka Nwosu",
                        percentage=40.0,
                        is_corporate=False
                    )
                ],
                raw_data={
                    "rc_number": rc_number,
                    "company_name": "ALPHA TRADING LIMITED",
                    "registration_date": "2018-06-12",
                    "company_type": "LIMITED BY SHARES",
                    "status": "ACTIVE",
                    "share_capital_authorized": 1000000,
                    "share_capital_issued": 1000000
                }
            )
        
        # PLC with corporate shareholder (tests 2-level UBO tracing)
        if rc_number.upper() == "RC789012":
            return CACResult(
                success=True,
                rc_number=rc_number,
                company_name="BETA INDUSTRIES PLC",
                company_type="PLC",
                status="ACTIVE",
                incorporation_date="2015-01-20",
                registered_address="12 Broad Street, Lagos Island, Lagos",
                share_capital=50000000.00,
                directors=[
                    DirectorInfo(name="Chukwuma Okafor", position="Chairman"),
                    DirectorInfo(name="Ngozi Eze", position="Managing Director"),
                    DirectorInfo(name="Ibrahim Musa", position="Finance Director")
                ],
                shareholders=[
                    ShareholderInfo(
                        name="GAMMA HOLDINGS LIMITED",
                        percentage=55.0,
                        is_corporate=True,
                        corporate_rc="RC456789"
                    ),
                    ShareholderInfo(
                        name="Chukwuma Okafor",
                        percentage=25.0,
                        is_corporate=False
                    ),
                    ShareholderInfo(
                        name="Ngozi Eze",
                        percentage=20.0,
                        is_corporate=False
                    )
                ],
                raw_data={"rc_number": rc_number, "company_type": "PUBLIC LIMITED COMPANY"}
            )
        
        # Business Name (sole proprietorship)
        if rc_number.upper().startswith("BN"):
            return CACResult(
                success=True,
                rc_number=rc_number,
                company_name="PRECIOUS VENTURES",
                company_type="Business Name",
                status="ACTIVE",
                incorporation_date="2020-09-05",
                registered_address="23 Market Road, Aba, Abia State",
                directors=[
                    DirectorInfo(name="Precious Okoro", position="Proprietor")
                ],
                shareholders=[
                    ShareholderInfo(name="Precious Okoro", percentage=100.0, is_corporate=False)
                ],
                raw_data={"bn_number": rc_number, "company_type": "BUSINESS NAME"}
            )
        
        # RC not found
        return CACResult(
            success=False,
            rc_number=rc_number,
            company_name="",
            error_code="RC_NOT_FOUND",
            error_message="Company not found in CAC registry"
        )
    
    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "mock"

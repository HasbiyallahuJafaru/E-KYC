"""
Verification orchestrator service.
Coordinates the complete verification workflow from provider calls to report generation.
"""

import asyncio
from uuid import UUID
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.services.providers.factory import get_verification_provider
from app.services.cross_validator import CrossValidator, ValidationResult
from app.services.ubo_analyzer import UBOAnalyzer, UBOAnalysisResult
from app.services.risk_engine import RiskEngine, RiskFactors, RiskScore
from app.models.verification_result import VerificationResult, VerificationStatus, VerificationType
from app.models.customer import Customer
from app.core.logging import get_logger
from app.core.exceptions import ProviderUnavailableError

logger = get_logger(__name__)


class VerificationOrchestrator:
    """
    Orchestrates the complete verification workflow.
    Handles provider calls, cross-validation, UBO analysis, and risk scoring.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.provider = get_verification_provider()
        self.cross_validator = CrossValidator()
        self.ubo_analyzer = UBOAnalyzer()
        self.risk_engine = RiskEngine()
    
    async def verify_individual(
        self,
        customer: Customer,
        client_id: Optional[UUID] = None
    ) -> VerificationResult:
        """
        Perform individual verification (BVN + NIN cross-validation).
        
        Args:
            customer: Customer record with BVN and NIN
            client_id: API client ID (if external request)
            
        Returns:
            VerificationResult with complete validation data
        """
        logger.info(f"Starting individual verification for customer {customer.id}")
        start_time = datetime.utcnow()
        
        # Create verification record
        verification = VerificationResult(
            customer_id=customer.id,
            client_id=client_id,
            verification_type=VerificationType.INDIVIDUAL,
            status=VerificationStatus.PROCESSING,
            provider_name=self.provider.provider_name
        )
        self.db.add(verification)
        self.db.commit()
        
        try:
            # Call provider for BVN and NIN in parallel
            bvn_result, nin_result = await asyncio.gather(
                self.provider.verify_bvn(customer.bvn),
                self.provider.verify_nin(customer.nin)
            )
            
            # Check if both verifications succeeded
            if not bvn_result.success or not nin_result.success:
                verification.status = VerificationStatus.FAILED
                verification.error_code = bvn_result.error_code or nin_result.error_code
                verification.error_message = bvn_result.error_message or nin_result.error_message
                self.db.commit()
                return verification
            
            # Store BVN data
            verification.bvn_verified = True
            verification.bvn_data = bvn_result.raw_data
            verification.bvn_name = bvn_result.full_name
            verification.bvn_dob = bvn_result.date_of_birth
            verification.bvn_phone = bvn_result.phone_number
            
            # Store NIN data
            verification.nin_verified = True
            verification.nin_data = nin_result.raw_data
            verification.nin_name = nin_result.full_name
            verification.nin_dob = nin_result.date_of_birth
            verification.nin_address = nin_result.address
            
            # Perform cross-validation
            validation_result = self.cross_validator.validate(bvn_result, nin_result)
            
            verification.cross_validation_passed = validation_result.overall_match
            verification.cross_validation_confidence = validation_result.confidence
            verification.cross_validation_issues = validation_result.issues
            verification.cross_validation_details = validation_result.explanation
            
            # Calculate risk score
            risk_factors = RiskFactors(
                customer_type=customer.customer_type.value,
                occupation=customer.occupation,
                industry_sector=customer.industry_sector,
                is_pep=customer.is_pep,
                nationality=customer.nationality or "Nigeria",
                residence_country=customer.country or "Nigeria",
                onboarding_channel="IN_PERSON"  # Default, override from request if available
            )
            
            risk_score = self.risk_engine.calculate_risk(risk_factors)
            
            verification.risk_score = risk_score.total_score
            verification.risk_category = risk_score.category
            verification.risk_breakdown = risk_score.breakdown
            
            # Update customer risk rating
            customer.risk_score = risk_score.total_score
            customer.risk_rating = risk_score.category
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            verification.processing_time_ms = int(processing_time)
            
            verification.status = VerificationStatus.COMPLETED
            self.db.commit()
            
            logger.info(f"Individual verification completed for customer {customer.id}")
            return verification
        
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}", exc_info=True)
            verification.status = VerificationStatus.FAILED
            verification.error_code = "VERIFICATION_ERROR"
            verification.error_message = str(e)
            self.db.commit()
            raise
    
    async def verify_corporate(
        self,
        customer: Customer,
        client_id: Optional[UUID] = None
    ) -> VerificationResult:
        """
        Perform corporate verification (CAC + UBO analysis).
        
        Args:
            customer: Customer record with RC number
            client_id: API client ID (if external request)
            
        Returns:
            VerificationResult with CAC and UBO data
        """
        logger.info(f"Starting corporate verification for customer {customer.id}")
        start_time = datetime.utcnow()
        
        # Create verification record
        verification = VerificationResult(
            customer_id=customer.id,
            client_id=client_id,
            verification_type=VerificationType.CORPORATE,
            status=VerificationStatus.PROCESSING,
            provider_name=self.provider.provider_name
        )
        self.db.add(verification)
        self.db.commit()
        
        try:
            # Call provider for CAC lookup
            cac_result = await self.provider.verify_cac(customer.rc_number)
            
            if not cac_result.success:
                verification.status = VerificationStatus.FAILED
                verification.error_code = cac_result.error_code
                verification.error_message = cac_result.error_message
                self.db.commit()
                return verification
            
            # Store CAC data
            verification.cac_verified = True
            verification.cac_data = cac_result.raw_data
            verification.cac_company_name = cac_result.company_name
            verification.cac_incorporation_date = cac_result.incorporation_date
            verification.cac_status = cac_result.status
            
            # Perform UBO analysis
            ubo_result = self.ubo_analyzer.analyze(cac_result)
            
            verification.ubo_identified = ubo_result.identified
            verification.ubo_count = len(ubo_result.primary_ubos)
            verification.ubo_data = {
                "primary_ubos": [
                    {
                        "name": ubo.name,
                        "ownership_percentage": ubo.ownership_percentage,
                        "ownership_type": ubo.ownership_type,
                        "trace_depth": ubo.trace_depth,
                        "is_verified": ubo.is_verified
                    }
                    for ubo in ubo_result.primary_ubos
                ],
                "corporate_shareholders": ubo_result.corporate_shareholders,
                "total_percentage": ubo_result.total_identified_percentage,
                "issues": ubo_result.issues
            }
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            verification.processing_time_ms = int(processing_time)
            
            verification.status = VerificationStatus.COMPLETED
            self.db.commit()
            
            logger.info(f"Corporate verification completed for customer {customer.id}")
            return verification
        
        except Exception as e:
            logger.error(f"Corporate verification failed: {str(e)}", exc_info=True)
            verification.status = VerificationStatus.FAILED
            verification.error_code = "VERIFICATION_ERROR"
            verification.error_message = str(e)
            self.db.commit()
            raise
    
    async def verify_complete(
        self,
        customer: Customer,
        client_id: Optional[UUID] = None
    ) -> VerificationResult:
        """
        Perform complete verification (Individual + Corporate + Risk).
        
        Args:
            customer: Customer record with all required fields
            client_id: API client ID (if external request)
            
        Returns:
            VerificationResult with all verification data
        """
        logger.info(f"Starting complete verification for customer {customer.id}")
        start_time = datetime.utcnow()
        
        # Create verification record
        verification = VerificationResult(
            customer_id=customer.id,
            client_id=client_id,
            verification_type=VerificationType.COMPLETE,
            status=VerificationStatus.PROCESSING,
            provider_name=self.provider.provider_name
        )
        self.db.add(verification)
        self.db.commit()
        
        try:
            # Call provider for all verifications in parallel
            bvn_task = self.provider.verify_bvn(customer.bvn)
            nin_task = self.provider.verify_nin(customer.nin)
            cac_task = self.provider.verify_cac(customer.rc_number) if customer.rc_number else None
            
            if cac_task:
                bvn_result, nin_result, cac_result = await asyncio.gather(bvn_task, nin_task, cac_task)
            else:
                bvn_result, nin_result = await asyncio.gather(bvn_task, nin_task)
                cac_result = None
            
            # Process individual verification
            if bvn_result.success and nin_result.success:
                verification.bvn_verified = True
                verification.bvn_data = bvn_result.raw_data
                verification.bvn_name = bvn_result.full_name
                verification.bvn_dob = bvn_result.date_of_birth
                verification.bvn_phone = bvn_result.phone_number
                
                verification.nin_verified = True
                verification.nin_data = nin_result.raw_data
                verification.nin_name = nin_result.full_name
                verification.nin_dob = nin_result.date_of_birth
                verification.nin_address = nin_result.address
                
                # Cross-validation
                validation_result = self.cross_validator.validate(bvn_result, nin_result)
                verification.cross_validation_passed = validation_result.overall_match
                verification.cross_validation_confidence = validation_result.confidence
                verification.cross_validation_issues = validation_result.issues
                verification.cross_validation_details = validation_result.explanation
            
            # Process corporate verification
            if cac_result and cac_result.success:
                verification.cac_verified = True
                verification.cac_data = cac_result.raw_data
                verification.cac_company_name = cac_result.company_name
                verification.cac_incorporation_date = cac_result.incorporation_date
                verification.cac_status = cac_result.status
                
                # UBO analysis
                ubo_result = self.ubo_analyzer.analyze(cac_result)
                verification.ubo_identified = ubo_result.identified
                verification.ubo_count = len(ubo_result.primary_ubos)
                verification.ubo_data = {
                    "primary_ubos": [
                        {
                            "name": ubo.name,
                            "ownership_percentage": ubo.ownership_percentage,
                            "ownership_type": ubo.ownership_type
                        }
                        for ubo in ubo_result.primary_ubos
                    ],
                    "total_percentage": ubo_result.total_identified_percentage
                }
            
            # Calculate risk score
            risk_factors = RiskFactors(
                customer_type=customer.customer_type.value,
                occupation=customer.occupation,
                industry_sector=customer.industry_sector,
                is_pep=customer.is_pep,
                nationality=customer.nationality or "Nigeria",
                residence_country=customer.country or "Nigeria"
            )
            
            risk_score = self.risk_engine.calculate_risk(risk_factors)
            verification.risk_score = risk_score.total_score
            verification.risk_category = risk_score.category
            verification.risk_breakdown = risk_score.breakdown
            
            # Update customer
            customer.risk_score = risk_score.total_score
            customer.risk_rating = risk_score.category
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            verification.processing_time_ms = int(processing_time)
            
            verification.status = VerificationStatus.COMPLETED
            self.db.commit()
            
            logger.info(f"Complete verification finished for customer {customer.id}")
            return verification
        
        except Exception as e:
            logger.error(f"Complete verification failed: {str(e)}", exc_info=True)
            verification.status = VerificationStatus.FAILED
            verification.error_code = "VERIFICATION_ERROR"
            verification.error_message = str(e)
            self.db.commit()
            raise

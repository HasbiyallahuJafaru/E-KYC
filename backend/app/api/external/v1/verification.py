"""
External verification API endpoints.
These are the revenue-generating endpoints used by bank/fintech clients.
"""

from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_api_client
from app.core.exceptions import VerificationProviderError, InvalidInputError
from app.api.schemas import (
    IndividualVerificationRequest,
    CorporateVerificationRequest,
    CompleteVerificationRequest,
    VerificationResponse,
    BVNData,
    NINData,
    CrossValidationData,
    CACData,
    UBOInfo,
    RiskAssessment
)
from app.models.api_client import ApiClient
from app.models.customer import Customer, CustomerType, RiskRating
from app.models.verification_result import VerificationResult, VerificationStatus
from app.models.verification_log import VerificationLog
from app.services.verification_orchestrator import VerificationOrchestrator


router = APIRouter(prefix="/verify", tags=["Verification"])


@router.post("/individual", response_model=VerificationResponse, status_code=201)
async def verify_individual(
    request: IndividualVerificationRequest,
    client: ApiClient = Depends(get_api_client),
    db: Session = Depends(get_db)
):
    """
    Verify an individual using BVN and NIN.
    
    Process:
    1. Validate request data
    2. Call VerifyMe.ng API for BVN and NIN verification
    3. Cross-validate names between BVN and NIN
    4. Calculate risk score
    5. Generate verification report
    6. Return results
    
    Pricing: ₦1000 per verification (regardless of success/failure)
    """
    try:
        # Initialize orchestrator
        orchestrator = VerificationOrchestrator(db)
        
        # Create or get customer
        customer = db.query(Customer).filter(
            Customer.bvn == request.bvn
        ).first()
        
        if not customer:
            customer = Customer(
                id=uuid4(),
                customer_type=CustomerType.INDIVIDUAL,
                bvn=request.bvn,
                nin=request.nin,
                first_name=request.first_name,
                last_name=request.last_name,
                date_of_birth=request.date_of_birth,
                phone_number=request.phone_number or "N/A",  # Ensure required field is set
                country="Nigeria"
            )
            db.add(customer)
            db.flush()
        
        # Perform verification
        result = await orchestrator.verify_individual(
            customer=customer,
            client_id=client.id
        )
        
        # Log the verification for billing
        log = VerificationLog(
            id=uuid4(),
            client_id=client.id,
            verification_id=result.id,
            request_type="INDIVIDUAL",
            endpoint="/api/v1/verify/individual",
            request_id=uuid4(),
            response_time_ms=result.processing_time_ms,
            success=True,
            status_code=201,
            cost_ngn=1000,  # ₦1000 per verification
            billed=False,
            billing_month=datetime.utcnow().strftime("%Y-%m")
        )
        db.add(log)
        db.commit()
        
        # Build response from verification result
        response = VerificationResponse(
            verification_id=result.id,
            status=result.status.value,
            verification_type="INDIVIDUAL",
            bvn_data=BVNData(
                verified=result.bvn_verified,
                full_name=result.bvn_name,
                date_of_birth=result.bvn_dob,
                phone_number=result.bvn_phone
            ),
            nin_data=NINData(
                verified=result.nin_verified,
                full_name=result.nin_name,
                date_of_birth=result.nin_dob,
                address=result.nin_address
            ),
            cross_validation=CrossValidationData(
                passed=result.cross_validation_passed,
                confidence=result.cross_validation_confidence,
                issues=result.cross_validation_issues or [],
                explanation=result.cross_validation_details or ""
            ),
            risk_assessment=RiskAssessment(
                score=result.risk_score,
                category=result.risk_category,
                breakdown=result.risk_breakdown or {},
                risk_drivers=[],
                required_actions=[]
            ),
            report_url=f"/api/v1/reports/{result.id}",
            processing_time_ms=result.processing_time_ms,
            created_at=result.created_at.isoformat()
        )
        
        return response
        
    except VerificationProviderError as e:
        # Log failed verification (still billable)
        log = VerificationLog(
            id=uuid4(),
            client_id=client.id,
            verification_id=None,  # No verification ID if failed early
            request_type="INDIVIDUAL",
            endpoint="/api/v1/verify/individual",
            request_id=uuid4(),
            response_time_ms=0,
            success=False,
            status_code=502,
            error_code=getattr(e, "error_code", "PROVIDER_ERROR"),
            cost_ngn=1000,
            billed=False,
            billing_month=datetime.utcnow().strftime("%Y-%m")
        )
        db.add(log)
        db.commit()
        
        raise HTTPException(
            status_code=502,
            detail={
                "error_code": getattr(e, "error_code", "PROVIDER_ERROR"),
                "message": str(e)
            }
        )
        
    except Exception as e:
        # Log error
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {str(e)}"
        )


@router.post("/corporate", response_model=VerificationResponse, status_code=201)
async def verify_corporate(
    request: CorporateVerificationRequest,
    client: ApiClient = Depends(get_api_client),
    db: Session = Depends(get_db)
):
    """
    Verify a corporate entity using CAC registration number.
    
    Process:
    1. Validate request data
    2. Call VerifyMe.ng API for CAC verification
    3. Analyze Ultimate Beneficial Owners (≥25% ownership)
    4. Calculate corporate risk score
    5. Generate verification report
    6. Return results
    
    Pricing: ₦1000 per verification
    """
    try:
        orchestrator = VerificationOrchestrator(db)
        
        # Create or get customer
        customer = db.query(Customer).filter(
            Customer.rc_number == request.rc_number
        ).first()
        
        if not customer:
            customer = Customer(
                id=uuid4(),
                customer_type=CustomerType.CORPORATE,
                rc_number=request.rc_number,
                business_name=request.business_name,
                phone_number="N/A",  # Required field - will be updated from CAC data if available
                country="Nigeria"
            )
            db.add(customer)
            db.flush()
        
        # Perform verification
        result = await orchestrator.verify_corporate(
            customer=customer,
            client_id=client.id
        )
        
        # Log for billing
        log = VerificationLog(
            id=uuid4(),
            client_id=client.id,
            verification_id=result.id,
            request_type="CORPORATE",
            endpoint="/api/v1/verify/corporate",
            request_id=uuid4(),
            response_time_ms=result.processing_time_ms,
            success=True,
            status_code=201,
            cost_ngn=1000,
            billed=False,
            billing_month=datetime.utcnow().strftime("%Y-%m")
        )
        db.add(log)
        db.commit()
        
        # Build response from verification result
        ubos = []
        if result.ubo_data and "primary_ubos" in result.ubo_data:
            ubos = [
                UBOInfo(
                    name=ubo["name"],
                    ownership_percentage=ubo["ownership_percentage"],
                    ownership_type=ubo["ownership_type"],
                    is_verified=ubo.get("is_verified", False)
                )
                for ubo in result.ubo_data["primary_ubos"]
            ]
        
        response = VerificationResponse(
            verification_id=result.id,
            status=result.status.value,
            verification_type="CORPORATE",
            cac_data=CACData(
                verified=result.cac_verified,
                company_name=result.cac_company_name,
                incorporation_date=result.cac_incorporation_date,
                status=result.cac_status,
                ubo_count=result.ubo_count,
                ubos=ubos
            ),
            risk_assessment=RiskAssessment(
                score=result.risk_score or 0,
                category=result.risk_category or "UNKNOWN",
                breakdown=result.risk_breakdown or {},
                risk_drivers=[],
                required_actions=[]
            ),
            report_url=f"/api/v1/reports/{result.id}",
            processing_time_ms=result.processing_time_ms,
            created_at=result.created_at.isoformat()
        )
        
        return response
        
    except VerificationProviderError as e:
        # Still billable
        log = VerificationLog(
            id=uuid4(),
            client_id=client.id,
            verification_id=None,
            request_type="CORPORATE",
            endpoint="/api/v1/verify/corporate",
            request_id=uuid4(),
            response_time_ms=0,
            success=False,
            status_code=502,
            error_code=getattr(e, "error_code", "PROVIDER_ERROR"),
            cost_ngn=1000,
            billed=False,
            billing_month=datetime.utcnow().strftime("%Y-%m")
        )
        db.add(log)
        db.commit()
        
        raise HTTPException(
            status_code=502,
            detail={
                "error_code": getattr(e, "error_code", "PROVIDER_ERROR"),
                "message": str(e)
            }
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {str(e)}"
        )


@router.get("/{verification_id}", response_model=VerificationResponse)
async def get_verification(
    verification_id: str,
    client: ApiClient = Depends(get_api_client),
    db: Session = Depends(get_db)
):
    """
    Retrieve a previous verification result.
    
    Note: Clients can only access their own verifications (enforced by RLS).
    """
    verification = db.query(VerificationResult).filter(
        VerificationResult.id == verification_id,
        VerificationResult.client_id == client.id  # Ensure client owns this verification
    ).first()
    
    if not verification:
        raise HTTPException(
            status_code=404,
            detail="Verification not found"
        )
    
    # Build response from stored data
    response = VerificationResponse(
        verification_id=verification.id,
        status=verification.status.value,
        verification_type=verification.verification_type,
        processing_time_ms=verification.processing_time_ms,
        created_at=verification.created_at.isoformat()
    )
    
    # Add BVN/NIN data if available
    if verification.bvn_verified:
        response.bvn_data = BVNData(
            verified=verification.bvn_verified,
            full_name=verification.bvn_name,
            date_of_birth=verification.bvn_dob,
            phone_number=verification.bvn_phone
        )
    
    if verification.nin_verified:
        response.nin_data = NINData(
            verified=verification.nin_verified,
            full_name=verification.nin_name,
            date_of_birth=verification.nin_dob,
            address=verification.nin_address
        )
    
    if verification.cross_validation_passed is not None:
        response.cross_validation = CrossValidationData(
            passed=verification.cross_validation_passed,
            confidence=verification.cross_validation_confidence or 0,
            issues=verification.cross_validation_issues or [],
            explanation=verification.cross_validation_details or ""
        )
    
    # Add CAC data if available
    if verification.cac_verified:
        ubos = []
        if verification.ubo_data and "primary_ubos" in verification.ubo_data:
            ubos = [
                UBOInfo(
                    name=ubo["name"],
                    ownership_percentage=ubo["ownership_percentage"],
                    ownership_type=ubo["ownership_type"],
                    is_verified=ubo.get("is_verified", False)
                )
                for ubo in verification.ubo_data["primary_ubos"]
            ]
        
        response.cac_data = CACData(
            verified=verification.cac_verified,
            company_name=verification.cac_company_name,
            incorporation_date=verification.cac_incorporation_date,
            status=verification.cac_status,
            ubo_count=verification.ubo_count,
            ubos=ubos
        )
    
    # Add risk assessment if available
    if verification.risk_score is not None:
        response.risk_assessment = RiskAssessment(
            score=verification.risk_score,
            category=verification.risk_category or "UNKNOWN",
            breakdown=verification.risk_breakdown or {},
            risk_drivers=verification.risk_breakdown.get("risk_drivers", []) if verification.risk_breakdown else [],
            required_actions=verification.risk_breakdown.get("required_actions", []) if verification.risk_breakdown else []
        )
    
    response.report_url = f"/api/v1/reports/{verification_id}"
    
    return response

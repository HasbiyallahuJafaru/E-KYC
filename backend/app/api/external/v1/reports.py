"""
Reports API endpoints.
Serves print-ready verification reports.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_api_client
from app.models.api_client import ApiClient
from app.models.verification_result import VerificationResult
from app.services.report_generator import ReportGenerator
from app.services.report_generator_compact import CompactReportGenerator
from app.core.exceptions import ResourceNotFoundError


router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{verification_id}", response_class=HTMLResponse)
async def get_report_html(
    verification_id: UUID,
    client: ApiClient = Depends(get_api_client),
    db: Session = Depends(get_db)
):
    """
    Get HTML verification report.
    
    Returns a print-ready HTML report that can be printed directly from browser
    or converted to PDF by the client.
    """
    # Verify ownership
    verification = db.query(VerificationResult).filter(
        VerificationResult.id == verification_id,
        VerificationResult.client_id == client.id
    ).first()
    
    if not verification:
        raise HTTPException(
            status_code=404,
            detail="Report not found or access denied"
        )
    
    # Generate report
    generator = ReportGenerator(db)
    
    try:
        html_content = await generator.generate_html_report(verification_id)
        return HTMLResponse(content=html_content)
    except ResourceNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Verification not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/{verification_id}/pdf")
async def get_report_pdf(
    verification_id: UUID,
    client: ApiClient = Depends(get_api_client),
    db: Session = Depends(get_db)
):
    """
    Get PDF verification report using ReportLab.
    
    Returns a professionally formatted PDF report.
    """
    # Verify ownership
    verification = db.query(VerificationResult).filter(
        VerificationResult.id == verification_id,
        VerificationResult.client_id == client.id
    ).first()
    
    if not verification:
        raise HTTPException(
            status_code=404,
            detail="Report not found or access denied"
        )
    
    # Generate compact PDF
    generator = CompactReportGenerator(db)
    
    try:
        pdf_content = await generator.generate_pdf_report(verification_id)
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=verification_{verification_id}.pdf"
            }
        )
    except ResourceNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Verification not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {str(e)}"
        )

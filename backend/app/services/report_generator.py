"""
Report generation service.
Generates print-ready PDF verification reports.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from jinja2 import Template
from sqlalchemy.orm import Session
from app.models.verification_result import VerificationResult
from app.models.customer import Customer
from app.core.exceptions import ResourceNotFoundError


class ReportGenerator:
    """
    Generates branded verification reports in HTML/PDF format.
    
    Reports include:
    - E-KYC Check branding
    - Verification summary
    - BVN/NIN/CAC data
    - Cross-validation results
    - Risk assessment breakdown
    - Compliance recommendations
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_html_report(self, verification_id: UUID) -> str:
        """
        Generate HTML verification report.
        
        Args:
            verification_id: The verification to report on
            
        Returns:
            str: HTML content
            
        Raises:
            ResourceNotFoundError: If verification not found
        """
        # Get verification data
        verification = self.db.query(VerificationResult).filter(
            VerificationResult.id == verification_id
        ).first()
        
        if not verification:
            raise ResourceNotFoundError("Verification", str(verification_id))
        
        # Get customer data
        customer = self.db.query(Customer).filter(
            Customer.id == verification.customer_id
        ).first()
        
        # Prepare template data
        context = {
            "verification_id": str(verification.id),
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "verification_type": verification.verification_type,
            "status": verification.status.value,
            "customer": {
                "type": customer.customer_type.value if customer else "UNKNOWN",
                "name": self._get_customer_name(customer, verification),
                "bvn": customer.bvn if customer and customer.bvn else None,
                "nin": customer.nin if customer and customer.nin else None,
                "rc_number": customer.rc_number if customer and customer.rc_number else None,
            },
            "bvn_data": verification.bvn_data,
            "nin_data": verification.nin_data,
            "cac_data": verification.cac_data,
            "cross_validation": {
                "passed": verification.cross_validation_passed,
                "confidence": verification.cross_validation_confidence,
                "issues": verification.cross_validation_issues,
                "details": verification.cross_validation_details
            } if verification.cross_validation_passed is not None else None,
            "risk": {
                "score": verification.risk_score,
                "category": verification.risk_category,
                "breakdown": verification.risk_breakdown
            },
            "processing_time_ms": verification.processing_time_ms
        }
        
        # Render HTML template
        html_content = self._render_template(context)
        
        return html_content
    
    def _get_customer_name(self, customer: Optional[Customer], verification: VerificationResult) -> str:
        """Extract customer name from various sources."""
        if customer:
            if customer.customer_type.value == "INDIVIDUAL":
                if customer.first_name and customer.last_name:
                    return f"{customer.first_name} {customer.last_name}"
            elif customer.customer_type.value == "CORPORATE":
                if customer.business_name:
                    return customer.business_name
        
        # Fallback to verification data
        if verification.bvn_data and verification.bvn_data.get("full_name"):
            return verification.bvn_data["full_name"]
        
        if verification.cac_data and verification.cac_data.get("company_name"):
            return verification.cac_data["company_name"]
        
        return "UNKNOWN"
    
    def _render_template(self, context: dict) -> str:
        """
        Render HTML template with context data.
        
        Note: Using inline template for now. In production, move to app/templates/
        """
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-KYC Verification Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        .header {
            border-bottom: 4px solid #0066cc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #0066cc;
            font-size: 28px;
            margin-bottom: 5px;
        }
        
        .header .subtitle {
            color: #666;
            font-size: 14px;
        }
        
        .meta-info {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        
        .meta-info .row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
        }
        
        .meta-info .label {
            font-weight: 600;
            color: #555;
        }
        
        .section {
            margin-bottom: 30px;
        }
        
        .section h2 {
            color: #0066cc;
            font-size: 20px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }
        
        .data-table td {
            padding: 10px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .data-table td:first-child {
            font-weight: 600;
            color: #555;
            width: 40%;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-completed {
            background: #d4edda;
            color: #155724;
        }
        
        .status-failed {
            background: #f8d7da;
            color: #721c24;
        }
        
        .risk-low {
            background: #d4edda;
            color: #155724;
        }
        
        .risk-medium {
            background: #fff3cd;
            color: #856404;
        }
        
        .risk-high {
            background: #f8d7da;
            color: #721c24;
        }
        
        .risk-prohibited {
            background: #000;
            color: #fff;
        }
        
        .risk-score {
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            padding: 20px;
        }
        
        .verification-icon {
            text-align: center;
            font-size: 48px;
            margin: 10px 0;
        }
        
        .verified { color: #28a745; }
        .failed { color: #dc3545; }
        
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 12px;
        }
        
        @media print {
            body {
                background: white;
                padding: 0;
            }
            
            .container {
                box-shadow: none;
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>E-KYC Check</h1>
            <p class="subtitle">Verification Report</p>
        </div>
        
        <div class="meta-info">
            <div class="row">
                <span class="label">Verification ID:</span>
                <span>{{ verification_id }}</span>
            </div>
            <div class="row">
                <span class="label">Generated:</span>
                <span>{{ generated_at }}</span>
            </div>
            <div class="row">
                <span class="label">Type:</span>
                <span>{{ verification_type }}</span>
            </div>
            <div class="row">
                <span class="label">Status:</span>
                <span class="status-badge status-{{ status|lower }}">{{ status }}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>Customer Information</h2>
            <table class="data-table">
                <tr>
                    <td>Name:</td>
                    <td>{{ customer.name }}</td>
                </tr>
                <tr>
                    <td>Type:</td>
                    <td>{{ customer.type }}</td>
                </tr>
                {% if customer.bvn %}
                <tr>
                    <td>BVN:</td>
                    <td>{{ customer.bvn }}</td>
                </tr>
                {% endif %}
                {% if customer.nin %}
                <tr>
                    <td>NIN:</td>
                    <td>{{ customer.nin }}</td>
                </tr>
                {% endif %}
                {% if customer.rc_number %}
                <tr>
                    <td>RC Number:</td>
                    <td>{{ customer.rc_number }}</td>
                </tr>
                {% endif %}
            </table>
        </div>
        
        {% if bvn_data %}
        <div class="section">
            <h2>BVN Verification</h2>
            <div class="verification-icon {% if bvn_data.verified %}verified{% else %}failed{% endif %}">
                {% if bvn_data.verified %}✓{% else %}✗{% endif %}
            </div>
            <table class="data-table">
                <tr>
                    <td>Verified:</td>
                    <td>{% if bvn_data.verified %}YES{% else %}NO{% endif %}</td>
                </tr>
                {% if bvn_data.full_name %}
                <tr>
                    <td>Full Name:</td>
                    <td>{{ bvn_data.full_name }}</td>
                </tr>
                {% endif %}
            </table>
        </div>
        {% endif %}
        
        {% if nin_data %}
        <div class="section">
            <h2>NIN Verification</h2>
            <div class="verification-icon {% if nin_data.verified %}verified{% else %}failed{% endif %}">
                {% if nin_data.verified %}✓{% else %}✗{% endif %}
            </div>
            <table class="data-table">
                <tr>
                    <td>Verified:</td>
                    <td>{% if nin_data.verified %}YES{% else %}NO{% endif %}</td>
                </tr>
                {% if nin_data.full_name %}
                <tr>
                    <td>Full Name:</td>
                    <td>{{ nin_data.full_name }}</td>
                </tr>
                {% endif %}
            </table>
        </div>
        {% endif %}
        
        {% if cross_validation %}
        <div class="section">
            <h2>Cross-Validation</h2>
            <table class="data-table">
                <tr>
                    <td>Passed:</td>
                    <td>{% if cross_validation.passed %}YES{% else %}NO{% endif %}</td>
                </tr>
                <tr>
                    <td>Confidence:</td>
                    <td>{{ cross_validation.confidence }}%</td>
                </tr>
                <tr>
                    <td>Explanation:</td>
                    <td>{{ cross_validation.explanation }}</td>
                </tr>
            </table>
        </div>
        {% endif %}
        
        {% if cac_data %}
        <div class="section">
            <h2>CAC Verification</h2>
            <table class="data-table">
                <tr>
                    <td>Company Name:</td>
                    <td>{{ cac_data.company_name }}</td>
                </tr>
                <tr>
                    <td>Status:</td>
                    <td>{{ cac_data.status }}</td>
                </tr>
                {% if cac_data.ubos %}
                <tr>
                    <td>Ultimate Beneficial Owners:</td>
                    <td>{{ cac_data.ubos|length }}</td>
                </tr>
                {% endif %}
            </table>
        </div>
        {% endif %}
        
        {% if risk %}
        <div class="section">
            <h2>Risk Assessment</h2>
            <div class="risk-score risk-{{ risk.category|lower }}">
                {{ risk.score }}/100
            </div>
            <table class="data-table">
                <tr>
                    <td>Risk Category:</td>
                    <td><span class="status-badge risk-{{ risk.category|lower }}">{{ risk.category }}</span></td>
                </tr>
                {% if risk.breakdown %}
                <tr>
                    <td>Customer Risk:</td>
                    <td>{{ risk.breakdown.customer_score }}</td>
                </tr>
                <tr>
                    <td>Geographic Risk:</td>
                    <td>{{ risk.breakdown.geographic_score }}</td>
                </tr>
                <tr>
                    <td>Product Risk:</td>
                    <td>{{ risk.breakdown.product_score }}</td>
                </tr>
                <tr>
                    <td>Channel Risk:</td>
                    <td>{{ risk.breakdown.channel_score }}</td>
                </tr>
                {% endif %}
            </table>
        </div>
        {% endif %}
        
        <div class="footer">
            <p><strong>E-KYC Check</strong> - Automated KYC Verification Platform</p>
            <p>This report was generated automatically. Processing time: {{ processing_time_ms }}ms</p>
            <p>© 2024 E-KYC Check. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        return template.render(**context)
    
    async def generate_pdf_report(self, verification_id: UUID) -> bytes:
        """
        Generate PDF verification report.
        
        Args:
            verification_id: The verification to report on
            
        Returns:
            bytes: PDF content
            
        Note:
            PDF generation requires additional library (WeasyPrint or similar).
            For now, return HTML. In production, use browser print or WeasyPrint.
        """
        html_content = await self.generate_html_report(verification_id)
        
        # TODO: Convert HTML to PDF using WeasyPrint or similar
        # For now, return HTML bytes
        return html_content.encode('utf-8')

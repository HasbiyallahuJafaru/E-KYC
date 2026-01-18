"""
Report generation service.
Generates print-ready PDF verification reports using HTML templates.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from io import BytesIO
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session
from app.models.verification_result import VerificationResult
from app.models.customer import Customer
from app.core.exceptions import ResourceNotFoundError


class ReportGenerator:
    """
    Generates branded verification reports in HTML/PDF format using templates.
    
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
        # Set up Jinja2 template environment
        template_dir = Path(__file__).parent.parent / 'templates'
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    async def generate_html_report(self, verification_id: UUID) -> str:
        """
        Generate HTML verification report using template.
        
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
        
        # Prepare template context
        context = self._prepare_template_context(verification, customer)
        
        # Load and render template
        template = self.jinja_env.get_template('reports/verification_report.html')
        html_content = template.render(**context)
        
        return html_content
    
    def _prepare_template_context(self, verification: VerificationResult, customer: Optional[Customer]) -> dict:
        """Prepare context data for template rendering."""
        # Determine risk colors
        if verification.risk_category == 'LOW':
            status_color = '#10b981'
            risk_bg_color = '#f0fdf4'
            risk_border_color = '#86efac'
            risk_text_color = '#15803d'
        elif verification.risk_category == 'MEDIUM':
            status_color = '#f59e0b'
            risk_bg_color = '#fef3c7'
            risk_border_color = '#fde047'
            risk_text_color = '#d97706'
        else:  # HIGH
            status_color = '#ef4444'
            risk_bg_color = '#fee2e2'
            risk_border_color = '#fca5a5'
            risk_text_color = '#dc2626'
        
        # Get UBOs
        ubos = []
        if verification.ubo_data and verification.ubo_data.get('primary_ubos'):
            ubos = verification.ubo_data['primary_ubos']
        
        return {
            'verification_id': str(verification.id),
            'report_date': datetime.utcnow().strftime("%B %d, %Y at %H:%M:%S UTC"),
            'status': verification.status.value.upper(),
            'status_color': status_color,
            'verification_type': verification.verification_type.value.upper(),
            'customer_name': self._get_customer_name(customer, verification),
            'customer_type': customer.customer_type.value.upper() if customer else 'UNKNOWN',
            'rc_number': customer.rc_number if customer and customer.rc_number else None,
            'risk_score': verification.risk_score,
            'risk_category': verification.risk_category,
            'risk_bg_color': risk_bg_color,
            'risk_border_color': risk_border_color,
            'risk_text_color': risk_text_color,
            'risk_breakdown': verification.risk_breakdown,
            'cac_verified': verification.cac_verified,
            'cac_company_name': verification.cac_company_name,
            'cac_entity_type': verification.cac_entity_type,
            'cac_status': verification.cac_status,
            'cac_incorporation_date': verification.cac_incorporation_date,
            'cac_registered_address': verification.cac_registered_address,
            'ubos': ubos,
            'processing_time': verification.processing_time_ms
        }
    
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
        
        # Use the explicitly set company name field
        if verification.cac_company_name:
            return verification.cac_company_name
        
        return "UNKNOWN"
    
    def _prepare_cac_data(self, verification: VerificationResult) -> Optional[dict]:
        """Prepare CAC data for report, combining cac_data and cac_entity_data."""
        if not verification.cac_verified:
            return None
        
        cac_data = {
            "company_name": verification.cac_company_name,
            "entity_type": verification.cac_entity_type,
            "status": verification.cac_status,
            "incorporation_date": verification.cac_incorporation_date,
            "registered_address": verification.cac_registered_address
        }
        
        # Merge entity-specific data if available
        if verification.cac_entity_data:
            cac_data.update(verification.cac_entity_data)
        
        # Add UBO data if available
        if verification.ubo_data and verification.ubo_data.get("primary_ubos"):
            cac_data["ubos"] = verification.ubo_data["primary_ubos"]
        
        return cac_data
    
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
                {% if cac_data.entity_type %}
                <tr>
                    <td>Entity Type:</td>
                    <td>{{ cac_data.entity_type }}</td>
                </tr>
                {% endif %}
                <tr>
                    <td>Status:</td>
                    <td>{{ cac_data.status }}</td>
                </tr>
                {% if cac_data.incorporation_date %}
                <tr>
                    <td>Incorporation Date:</td>
                    <td>{{ cac_data.incorporation_date }}</td>
                </tr>
                {% endif %}
                {% if cac_data.registered_address %}
                <tr>
                    <td>Registered Address:</td>
                    <td>{{ cac_data.registered_address }}</td>
                </tr>
                {% endif %}
            </table>
            
            {% if cac_data.directors %}
            <h3 style="margin-top: 20px; color: #0066cc; font-size: 16px;">Directors</h3>
            <table class="data-table">
                {% for director in cac_data.directors %}
                <tr>
                    <td>{{ director.name }}</td>
                    <td>{{ director.position }}{% if director.status %} - {{ director.status }}{% endif %}</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}
            
            {% if cac_data.shareholders %}
            <h3 style="margin-top: 20px; color: #0066cc; font-size: 16px;">Shareholders</h3>
            <table class="data-table">
                {% for shareholder in cac_data.shareholders %}
                <tr>
                    <td>{{ shareholder.name }}{% if shareholder.is_corporate %} (Corporate){% endif %}</td>
                    <td>{{ shareholder.percentage }}%</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}
            
            {% if cac_data.proprietors %}
            <h3 style="margin-top: 20px; color: #0066cc; font-size: 16px;">Proprietors</h3>
            <table class="data-table">
                {% for proprietor in cac_data.proprietors %}
                <tr>
                    <td>{{ proprietor.name }}</td>
                    <td>{% if proprietor.percentage %}{{ proprietor.percentage }}%{% endif %}</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}
            
            {% if cac_data.trustees %}
            <h3 style="margin-top: 20px; color: #0066cc; font-size: 16px;">Trustees</h3>
            <table class="data-table">
                {% for trustee in cac_data.trustees %}
                <tr>
                    <td>{{ trustee.name }}</td>
                    <td>{% if trustee.appointment_date %}Appointed: {{ trustee.appointment_date }}{% endif %}</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}
            
            {% if cac_data.ubos %}
            <h3 style="margin-top: 20px; color: #0066cc; font-size: 16px;">Ultimate Beneficial Owners (≥25%)</h3>
            <table class="data-table">
                {% for ubo in cac_data.ubos %}
                <tr>
                    <td>{{ ubo.name }}</td>
                    <td>{{ ubo.ownership_percentage }}% ({{ ubo.ownership_type }})</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}
        </div>
        {% endif %}
        
        {% if risk %}
        <div class="section">
            <h2>Risk Assessment (1-30 Scale)</h2>
            <div class="risk-score risk-{{ risk.category|lower }}">
                {{ risk.score }}/30
            </div>
            <table class="data-table">
                <tr>
                    <td>Risk Category:</td>
                    <td><span class="status-badge risk-{{ risk.category|lower }}">{{ risk.category }}</span></td>
                </tr>
                {% if risk.breakdown %}
                <tr>
                    <td colspan="2"><strong>Risk Breakdown (Each category 0-5 points)</strong></td>
                </tr>
                {% for key, value in risk.breakdown.items() %}
                <tr>
                    <td>{{ key.replace('_', ' ').title() }}:</td>
                    <td>{{ value }}/5</td>
                </tr>
                {% endfor %}
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
        Generate PDF verification report using HTML template.
        
        Args:
            verification_id: The verification to report on
            
        Returns:
            bytes: PDF content
        """
        try:
            from xhtml2pdf import pisa
            
            # Get HTML content
            html_content = await self.generate_html_report(verification_id)
            
            # Create PDF from HTML
            pdf_buffer = BytesIO()
            pisa_status = pisa.CreatePDF(
                src=html_content,
                dest=pdf_buffer,
                encoding='utf-8'
            )
            
            if pisa_status.err:
                raise Exception(f"PDF generation error code: {pisa_status.err}")
            
            # Get PDF bytes
            pdf_bytes = pdf_buffer.getvalue()
            pdf_buffer.close()
            
            return pdf_bytes
            
        except ImportError as e:
            # Fallback: Return HTML as bytes if xhtml2pdf not installed
            from app.core.logging import get_logger
            logger = get_logger(__name__)
            logger.warning(f"xhtml2pdf not available: {str(e)}. Falling back to HTML.")
            html_content = await self.generate_html_report(verification_id)
            return html_content.encode('utf-8')
        except Exception as e:
            # Log error and fallback to HTML
            from app.core.logging import get_logger
            logger = get_logger(__name__)
            logger.error(f"PDF generation failed: {str(e)}. Falling back to HTML.")
            html_content = await self.generate_html_report(verification_id)
            return html_content.encode('utf-8')

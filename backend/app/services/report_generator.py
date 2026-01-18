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
            "verification_type": verification.verification_type.value if hasattr(verification.verification_type, 'value') else str(verification.verification_type),
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
            "cac_data": self._prepare_cac_data(verification),
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
        Generate PDF verification report.
        
        Args:
            verification_id: The verification to report on
            
        Returns:
            bytes: PDF content
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            from io import BytesIO
            
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
            
            # Create PDF buffer
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter,
                                  rightMargin=50, leftMargin=50,
                                  topMargin=50, bottomMargin=40)
            
            # Container for PDF elements
            elements = []
            styles = getSampleStyleSheet()
            
            # Define corporate color palette
            PRIMARY_BLUE = colors.HexColor('#1a365d')  # Dark blue
            ACCENT_BLUE = colors.HexColor('#2563eb')   # Bright blue
            SUCCESS_GREEN = colors.HexColor('#059669')
            WARNING_ORANGE = colors.HexColor('#d97706')
            DANGER_RED = colors.HexColor('#dc2626')
            LIGHT_BG = colors.HexColor('#f8fafc')
            BORDER_GRAY = colors.HexColor('#cbd5e1')
            TEXT_GRAY = colors.HexColor('#475569')
            
            # Professional header banner
            header_data = [[
                Paragraph(
                    '<para align="left"><font size="28" color="#ffffff"><b>E-KYC</b></font><br/><font size="10" color="#e2e8f0">Enterprise Verification Platform</font></para>',
                    styles['Normal']
                ),
                Paragraph(
                    f'<para align="right"><font size="10" color="#e2e8f0">Report Generated</font><br/><font size="9" color="#cbd5e1">{datetime.utcnow().strftime("%B %d, %Y")}</font></para>',
                    styles['Normal']
                )
            ]]
            header_table = Table(header_data, colWidths=[4.5*inch, 2.5*inch])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), PRIMARY_BLUE),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 20),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
                ('LEFTPADDING', (0, 0), (-1, -1), 25),
                ('RIGHTPADDING', (0, 0), (-1, -1), 25),
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=22,
                textColor=PRIMARY_BLUE,
                spaceAfter=8,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=PRIMARY_BLUE,
                spaceAfter=10,
                spaceBefore=15,
                fontName='Helvetica-Bold',
                borderWidth=0,
                borderColor=ACCENT_BLUE,
                borderPadding=8,
                backColor=LIGHT_BG,
                leftIndent=10
            )
            
            subheading_style = ParagraphStyle(
                'SubHeading',
                parent=styles['Heading3'],
                fontSize=11,
                textColor=TEXT_GRAY,
                spaceAfter=8,
                spaceBefore=10,
                fontName='Helvetica-Bold'
            )
            
            # Report Title
            elements.append(Paragraph("VERIFICATION REPORT", title_style))
            
            # Status Badge
            status_color = SUCCESS_GREEN if verification.status.value == 'COMPLETED' else WARNING_ORANGE
            status_badge = [[
                Paragraph(
                    f'<para align="center"><font size="12" color="#ffffff"><b>{verification.status.value}</b></font></para>',
                    styles['Normal']
                )
            ]]
            status_table = Table(status_badge, colWidths=[1.5*inch])
            status_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), status_color),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ROUNDCORNER', (0, 0), (-1, -1), 5)
            ]))
            elements.append(status_table)
            elements.append(Spacer(1, 0.25*inch))
            
            # Meta information in professional card
            meta_data = [
                ['Verification ID', str(verification.id)],
                ['Report Date', datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")],
                ['Verification Type', verification.verification_type.value.replace('_', ' ').title()],
                ['Customer Name', self._get_customer_name(customer, verification)]
            ]
            meta_table = Table(meta_data, colWidths=[2.2*inch, 4.8*inch])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), LIGHT_BG),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (0, -1), TEXT_GRAY),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER_GRAY),
                ('BOX', (0, 0), (-1, -1), 1.5, BORDER_GRAY)
            ]))
            elements.append(meta_table)
            elements.append(Spacer(1, 0.35*inch))
            
            # Customer Information Section
            elements.append(Paragraph("Customer Information", heading_style))
            elements.append(Spacer(1, 0.1*inch))
            
            customer_data = []
            if customer:
                if customer.customer_type.value == 'CORPORATE':
                    customer_data.append(['Customer Type', 'Corporate Entity'])
                    if customer.rc_number:
                        customer_data.append(['RC Number', customer.rc_number])
                else:
                    customer_data.append(['Customer Type', 'Individual'])
                    if customer.bvn:
                        customer_data.append(['BVN', customer.bvn])
                    if customer.nin:
                        customer_data.append(['NIN', customer.nin])
            
            if customer_data:
                customer_table = Table(customer_data, colWidths=[2.2*inch, 4.8*inch])
                customer_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), LIGHT_BG),
                    ('BACKGROUND', (1, 0), (1, -1), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('TEXTCOLOR', (0, 0), (0, -1), TEXT_GRAY),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 15),
                    ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER_GRAY),
                    ('BOX', (0, 0), (-1, -1), 1, BORDER_GRAY)
                ]))
                elements.append(customer_table)
            elements.append(Spacer(1, 0.25*inch))
            
            # Risk Assessment with visual score indicator
            if verification.risk_score is not None:
                elements.append(Paragraph("Risk Assessment", heading_style))
                elements.append(Spacer(1, 0.1*inch))
                
                # Determine risk color
                if verification.risk_category == 'LOW':
                    risk_color = SUCCESS_GREEN
                    risk_bg = colors.HexColor('#d1fae5')
                elif verification.risk_category == 'MEDIUM':
                    risk_color = WARNING_ORANGE
                    risk_bg = colors.HexColor('#fef3c7')
                else:
                    risk_color = DANGER_RED
                    risk_bg = colors.HexColor('#fee2e2')
                
                # Risk score card with prominent display
                risk_header_data = [[
                    Paragraph(
                        f'<para align="center"><font size="32" color="{risk_color.hexval()}"><b>{verification.risk_score}</b></font><font size="16" color="{TEXT_GRAY.hexval()}">/30</font><br/><font size="10" color="{TEXT_GRAY.hexval()}">RISK SCORE</font></para>',
                        styles['Normal']
                    ),
                    Paragraph(
                        f'<para align="center"><font size="14" color="{risk_color.hexval()}"><b>{verification.risk_category}</b></font><br/><font size="9" color="{TEXT_GRAY.hexval()}">RISK CATEGORY</font></para>',
                        styles['Normal']
                    )
                ]]
                risk_header_table = Table(risk_header_data, colWidths=[3.5*inch, 3.5*inch])
                risk_header_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), risk_bg),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 20),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
                    ('BOX', (0, 0), (-1, -1), 2, risk_color),
                    ('LINEAFTER', (0, 0), (0, -1), 1, BORDER_GRAY)
                ]))
                elements.append(risk_header_table)
                elements.append(Spacer(1, 0.15*inch))
                
                # Risk breakdown in modern table
                if verification.risk_breakdown:
                    elements.append(Paragraph("Risk Breakdown", subheading_style))
                    risk_data = [['Category', 'Score', 'Max']]
                    for key, value in verification.risk_breakdown.items():
                        label = key.replace('_', ' ').title()
                        risk_data.append([label, str(value), '5'])
                    
                    risk_table = Table(risk_data, colWidths=[4*inch, 1.5*inch, 1.5*inch])
                    risk_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), ACCENT_BLUE),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('TOPPADDING', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
                        ('BOX', (0, 0), (-1, -1), 1, BORDER_GRAY),
                        ('LINEBELOW', (0, 0), (-1, 0), 1.5, ACCENT_BLUE)
                    ]))
                    elements.append(risk_table)
                elements.append(Spacer(1, 0.25*inch))
            
            # CAC Verification Section
            if verification.cac_verified and verification.cac_company_name:
                elements.append(Paragraph("CAC Verification", heading_style))
                elements.append(Spacer(1, 0.1*inch))
                
                cac_basic = [
                    ['Company Name', verification.cac_company_name or 'N/A'],
                    ['RC Number', customer.rc_number if customer and customer.rc_number else 'N/A'],
                    ['Entity Type', verification.cac_entity_type or 'N/A'],
                    ['Status', verification.cac_status or 'N/A']
                ]
                if verification.cac_incorporation_date:
                    cac_basic.append(['Incorporation Date', verification.cac_incorporation_date])
                if verification.cac_registered_address:
                    cac_basic.append(['Registered Address', verification.cac_registered_address])
                
                cac_table = Table(cac_basic, colWidths=[2.2*inch, 4.8*inch])
                cac_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), LIGHT_BG),
                    ('BACKGROUND', (1, 0), (1, -1), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('TEXTCOLOR', (0, 0), (0, -1), TEXT_GRAY),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 15),
                    ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER_GRAY),
                    ('BOX', (0, 0), (-1, -1), 1, BORDER_GRAY)
                ]))  
                elements.append(cac_table)
                elements.append(Spacer(1, 0.2*inch))
                
                # Directors Table with modern design
                if verification.cac_entity_data and verification.cac_entity_data.get('directors'):
                    elements.append(Paragraph("Directors", subheading_style))
                    dir_data = [['Name', 'Position', 'Status', 'Contact']]
                    for director in verification.cac_entity_data['directors']:
                        contact_info = []
                        if director.get('email'):
                            contact_info.append(director['email'])
                        if director.get('phone'):
                            contact_info.append(director['phone'])
                        dir_data.append([
                            director.get('name', 'N/A'),
                            director.get('position', 'N/A'),
                            director.get('status', 'ACTIVE'),
                            ', '.join(contact_info) if contact_info else 'N/A'
                        ])
                    dir_table = Table(dir_data, colWidths=[2*inch, 1.5*inch, 1*inch, 2.5*inch])
                    dir_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), ACCENT_BLUE),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
                        ('BOX', (0, 0), (-1, -1), 1, BORDER_GRAY),
                        ('LINEBELOW', (0, 0), (-1, 0), 1.5, ACCENT_BLUE)
                    ]))
                    elements.append(dir_table)
                    elements.append(Spacer(1, 0.15*inch))
                
                # Shareholders Table with modern design
                if verification.cac_entity_data and verification.cac_entity_data.get('shareholders'):
                    elements.append(Paragraph("Shareholders", subheading_style))
                    sh_data = [['Shareholder Name', 'Ownership %', 'Type']]
                    for sh in verification.cac_entity_data['shareholders']:
                        sh_type = 'Corporate' if sh.get('is_corporate') else 'Individual'
                        sh_data.append([
                            sh.get('name', 'N/A'),
                            f"{sh.get('percentage', 0):.1f}%",
                            sh_type
                        ])
                    sh_table = Table(sh_data, colWidths=[3.5*inch, 2*inch, 1.5*inch])
                    sh_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), ACCENT_BLUE),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
                        ('BOX', (0, 0), (-1, -1), 1, BORDER_GRAY),
                        ('LINEBELOW', (0, 0), (-1, 0), 1.5, ACCENT_BLUE)
                    ]))
                    elements.append(sh_table)
                    elements.append(Spacer(1, 0.15*inch))
                
                # Ultimate Beneficial Owners with modern design
                if verification.ubo_data and verification.ubo_data.get('primary_ubos'):
                    elements.append(Paragraph("Ultimate Beneficial Owners (≥25%)", subheading_style))
                    ubo_data = [['Name', 'Ownership %', 'Type']]
                    for ubo in verification.ubo_data['primary_ubos']:
                        ubo_data.append([
                            ubo.get('name', 'N/A'),
                            f"{ubo.get('ownership_percentage', 0):.1f}%",
                            ubo.get('ownership_type', 'N/A')
                        ])
                    ubo_table = Table(ubo_data, colWidths=[3.5*inch, 2*inch, 1.5*inch])
                    ubo_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), ACCENT_BLUE),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
                        ('BOX', (0, 0), (-1, -1), 1, BORDER_GRAY),
                        ('LINEBELOW', (0, 0), (-1, 0), 1.5, ACCENT_BLUE)
                    ]))
                    elements.append(ubo_table)
                    elements.append(Spacer(1, 0.15*inch))
            
            # Professional Footer
            elements.append(Spacer(1, 0.5*inch))
            
            # Footer banner
            footer_data = [[
                Paragraph(
                    f'<para align="left"><font size="8" color="{TEXT_GRAY.hexval()}"><b>E-KYC Enterprise Platform</b><br/>Automated Verification & Compliance</font></para>',
                    styles['Normal']
                ),
                Paragraph(
                    f'<para align="right"><font size="7" color="{TEXT_GRAY.hexval()}">Report ID: {str(verification.id)[:8]}<br/>Processing: {verification.processing_time_ms}ms<br/>© 2026 E-KYC Check</font></para>',
                    styles['Normal']
                )
            ]]
            footer_table = Table(footer_data, colWidths=[4*inch, 3*inch])
            footer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('LINEABOVE', (0, 0), (-1, 0), 1, BORDER_GRAY)
            ]))
            elements.append(footer_table)
            
            # Build PDF
            doc.build(elements)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except ImportError:
            # Fallback: If reportlab not installed, return HTML
            html_content = await self.generate_html_report(verification_id)
            return html_content.encode('utf-8')
        except Exception as e:
            # Log error and fallback to HTML
            from app.core.logging import get_logger
            logger = get_logger(__name__)
            logger.error(f"PDF generation failed: {str(e)}. Falling back to HTML.")
            html_content = await self.generate_html_report(verification_id)
            return html_content.encode('utf-8')

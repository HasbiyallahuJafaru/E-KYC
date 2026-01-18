"""
Compact PDF Report Generator - Simple, space-efficient design
Fits all content in 1-2 pages with minimal spacing
"""

from datetime import datetime
from typing import List
from uuid import UUID
from io import BytesIO
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from app.models.verification_result import VerificationResult
from app.models.customer import Customer
from app.core.exceptions import ResourceNotFoundError


class CompactReportGenerator:
    """Generates compact, space-efficient PDF reports"""
    
    COLORS = {
        'primary': colors.HexColor('#2563eb'),
        'success': colors.HexColor('#10b981'),
        'warning': colors.HexColor('#f59e0b'),
        'danger': colors.HexColor('#ef4444'),
        'gray_dark': colors.HexColor('#374151'),
        'gray_medium': colors.HexColor('#6b7280'),
        'gray_light': colors.HexColor('#d1d5db'),
        'gray_bg': colors.HexColor('#f9fafb'),
    }
    
    def __init__(self, db: Session):
        self.db = db
        self._init_styles()
    
    def _init_styles(self):
        """Initialize compact paragraph styles"""
        base = getSampleStyleSheet()
        
        # Title
        self.style_title = ParagraphStyle(
            'Title',
            parent=base['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            textColor=self.COLORS['primary'],
            spaceAfter=6,
            spaceBefore=0,
            alignment=TA_CENTER,
        )
        
        # Section heading
        self.style_heading = ParagraphStyle(
            'Heading',
            parent=base['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=self.COLORS['primary'],
            spaceAfter=4,
            spaceBefore=8,
            borderColor=self.COLORS['primary'],
            borderWidth=0,
            borderPadding=0,
        )
        
        # Normal text
        self.style_normal = ParagraphStyle(
            'Normal',
            parent=base['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=self.COLORS['gray_dark'],
            leading=12,
        )
        
        # Label (small)
        self.style_label = ParagraphStyle(
            'Label',
            parent=base['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=self.COLORS['gray_medium'],
            leading=10,
        )
        
        # Value
        self.style_value = ParagraphStyle(
            'Value',
            parent=base['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=self.COLORS['gray_dark'],
            leading=12,
        )
    
    def _create_header(self, verification: VerificationResult) -> List:
        """Create compact header"""
        elements = []
        
        # Title with underline
        title = Paragraph("E-KYC Verification Report", self.style_title)
        elements.append(title)
        
        # Separator line
        line = Table([['']], colWidths=[6.2*inch])
        line.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 2, self.COLORS['primary']),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(line)
        elements.append(Spacer(1, 6))
        
        # Meta info in compact table
        timestamp = datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")
        
        # Determine status color and text
        if verification.status == 'COMPLETED':
            status_text = "COMPLETED"
            status_color = self.COLORS['success']
        else:
            status_text = verification.status
            status_color = self.COLORS['warning']
        
        meta_data = [
            [
                Paragraph(f"<b>Report ID:</b> {str(verification.id)[:8]}", self.style_normal),
                Paragraph(f"<b>Generated:</b> {timestamp}", self.style_normal),
                Paragraph(f"<b>Status:</b> <font color='{status_color}'>{status_text}</font>", self.style_normal),
            ]
        ]
        
        meta_table = Table(meta_data, colWidths=[2.0*inch, 2.7*inch, 1.5*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['gray_bg']),
            ('BOX', (0, 0), (-1, -1), 1, self.COLORS['gray_light']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(meta_table)
        elements.append(Spacer(1, 10))
        
        return elements
    
    def _create_info_section(self, customer: Customer, verification: VerificationResult) -> List:
        """Create compact customer info section"""
        elements = []
        
        # Section header with underline
        heading = Paragraph("Customer Information", self.style_heading)
        elements.append(heading)
        
        # Underline for section
        line = Table([['']], colWidths=[6.2*inch])
        line.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1, self.COLORS['gray_light']),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(line)
        
        # Get customer name - prioritize verification data for individuals
        if customer.business_name:
            customer_name = customer.business_name
        elif customer.first_name and customer.last_name:
            customer_name = f"{customer.first_name} {customer.last_name}"
        elif verification.bvn_name:
            customer_name = verification.bvn_name
        elif verification.nin_name:
            customer_name = verification.nin_name
        else:
            customer_name = "N/A"
        
        # Determine what to show in the info table based on verification type
        if verification.verification_type.value == 'INDIVIDUAL':
            # For individual verification, show BVN/NIN instead of RC number
            info_data = [
                [Paragraph("<b>Name:</b>", self.style_label), 
                 Paragraph(customer_name, self.style_value),
                 Paragraph("<b>Type:</b>", self.style_label), 
                 Paragraph(verification.verification_type.value, self.style_value)],
                [Paragraph("<b>BVN:</b>", self.style_label), 
                 Paragraph(customer.bvn or "N/A", self.style_value),
                 Paragraph("<b>NIN:</b>", self.style_label), 
                 Paragraph(customer.nin or "N/A", self.style_value)],
                [Paragraph("<b>Date of Birth:</b>", self.style_label), 
                 Paragraph(verification.bvn_dob or verification.nin_dob or "N/A", self.style_value),
                 Paragraph("<b>Phone:</b>", self.style_label), 
                 Paragraph(verification.bvn_phone or customer.phone_number or "N/A", self.style_value)],
            ]
        else:
            # For corporate verification
            info_data = [
                [Paragraph("<b>Name:</b>", self.style_label), 
                 Paragraph(customer_name, self.style_value),
                 Paragraph("<b>Type:</b>", self.style_label), 
                 Paragraph(verification.verification_type.value, self.style_value)],
                [Paragraph("<b>RC Number:</b>", self.style_label), 
                 Paragraph(customer.rc_number or "N/A", self.style_value),
                 Paragraph("<b>Phone:</b>", self.style_label), 
                 Paragraph(customer.phone_number or "N/A", self.style_value)],
            ]
        
        if customer.email:
            info_data.append([
                Paragraph("<b>Email:</b>", self.style_label), 
                Paragraph(customer.email, self.style_value),
                '', ''
            ])
        
        info_table = Table(info_data, colWidths=[1.0*inch, 2.1*inch, 0.8*inch, 2.3*inch])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['gray_bg']),
            ('BOX', (0, 0), (-1, -1), 1, self.COLORS['gray_light']),
        ]))
        
        elements.append(info_table)
        
        return elements
    
    def _create_individual_verification_section(self, verification: VerificationResult) -> List:
        """Create BVN/NIN verification details section"""
        elements = []
        
        # Only show for individual verification types
        if not hasattr(verification, 'bvn_name') or not verification.bvn_name:
            return elements
        
        # Section header
        elements.append(Paragraph("Identity Verification", self.style_heading))
        
        # Underline
        line = Table([['']], colWidths=[6.2*inch])
        line.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1, self.COLORS['gray_light']),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(line)
        
        # BVN and NIN data side by side
        verification_data = []
        
        # Create white text style for headers
        header_style = ParagraphStyle(
            'VerificationHeader',
            parent=self.style_label,
            textColor=colors.white,
            fontSize=10,
            fontName='Helvetica-Bold'
        )
        
        # Headers
        verification_data.append([
            Paragraph("BVN Verification", header_style),
            Paragraph("NIN Verification", header_style),
        ])
        
        # Extract name components from JSONB data
        bvn_data_json = verification.bvn_data or {}
        nin_data_json = verification.nin_data or {}
        
        # Note: BVN uses camelCase (firstName, middleName, lastName)
        bvn_first = bvn_data_json.get('firstName', '') or ''
        bvn_middle = bvn_data_json.get('middleName', '') or ''
        bvn_last = bvn_data_json.get('lastName', '') or ''
        
        # Note: NIN uses lowercase (firstname, middlename) and surname
        nin_first = nin_data_json.get('firstname', '') or ''
        nin_middle = nin_data_json.get('middlename', '') or ''
        nin_last = nin_data_json.get('surname', '') or ''
        
        # First Name
        verification_data.append([
            Paragraph(f"<b>First Name:</b> {bvn_first or 'N/A'}", self.style_normal),
            Paragraph(f"<b>First Name:</b> {nin_first or 'N/A'}", self.style_normal),
        ])
        
        # Middle Name
        verification_data.append([
            Paragraph(f"<b>Middle Name:</b> {bvn_middle or 'N/A'}", self.style_normal),
            Paragraph(f"<b>Middle Name:</b> {nin_middle or 'N/A'}", self.style_normal),
        ])
        
        # Last Name
        verification_data.append([
            Paragraph(f"<b>Last Name:</b> {bvn_last or 'N/A'}", self.style_normal),
            Paragraph(f"<b>Last Name:</b> {nin_last or 'N/A'}", self.style_normal),
        ])
        
        # Date of Birth
        bvn_dob = verification.bvn_dob or "N/A"
        nin_dob = verification.nin_dob or "N/A"
        verification_data.append([
            Paragraph(f"<b>DOB:</b> {bvn_dob}", self.style_normal),
            Paragraph(f"<b>DOB:</b> {nin_dob}", self.style_normal),
        ])
        
        # Phone (BVN) and Address (NIN)
        bvn_phone = verification.bvn_phone or "N/A"
        nin_address = verification.nin_address or "N/A"
        verification_data.append([
            Paragraph(f"<b>Phone:</b> {bvn_phone}", self.style_normal),
            Paragraph(f"<b>Address:</b> {nin_address}", self.style_normal),
        ])
        
        verification_table = Table(verification_data, colWidths=[3.1*inch, 3.1*inch])
        verification_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, self.COLORS['gray_light']),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, self.COLORS['gray_light']),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(verification_table)
        
        return elements
    
    def _create_risk_section(self, verification: VerificationResult) -> List:
        """Create compact risk assessment section"""
        elements = []
        
        risk_score = verification.risk_score or 0
        risk_category = verification.risk_category or 'UNKNOWN'
        
        # Determine color
        if risk_score < 10:
            risk_color = self.COLORS['success']
        elif risk_score < 20:
            risk_color = self.COLORS['warning']
        else:
            risk_color = self.COLORS['danger']
        
        # Section header
        elements.append(Paragraph("Risk Assessment", self.style_heading))
        
        # Underline
        line = Table([['']], colWidths=[6.2*inch])
        line.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1, self.COLORS['gray_light']),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(line)
        
        # Risk summary in colored box
        risk_summary_style = ParagraphStyle(
            'RiskSummary', 
            parent=self.style_normal, 
            fontSize=11, 
            textColor=risk_color,
            alignment=TA_CENTER,
            leading=14,
        )
        
        risk_summary = Paragraph(
            f"<b>Score: {risk_score}/30 | Category: {risk_category}</b>",
            risk_summary_style
        )
        
        risk_box = Table([[risk_summary]], colWidths=[6.2*inch])
        risk_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['gray_bg']),
            ('BOX', (0, 0), (-1, -1), 2, risk_color),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(risk_box)
        elements.append(Spacer(1, 6))
        
        # Breakdown table
        breakdown = verification.risk_breakdown or {}
        
        breakdown_data = [
            [Paragraph("<b>Category</b>", self.style_label), 
             Paragraph("<b>Score</b>", self.style_label),
             Paragraph("<b>Max</b>", self.style_label)]
        ]
        
        categories = [
            ('Customer Profile', 'customer_profile', 5),
            ('Geographic Exposure', 'geographic_exposure', 5),
            ('Business Sector', 'business_sector', 5),
            ('PEP Influence', 'pep_influence', 5),
            ('Product Relationship', 'product_relationship', 5),
            ('Adverse Media', 'adverse_media', 5),
        ]
        
        for display_name, key, max_score in categories:
            score = breakdown.get(key, 0)
            breakdown_data.append([
                Paragraph(display_name, self.style_normal),
                Paragraph(str(score), self.style_normal),
                Paragraph(str(max_score), self.style_normal),
            ])
        
        breakdown_data.append([
            Paragraph("<b>Total</b>", self.style_value),
            Paragraph(f"<b>{risk_score}</b>", self.style_value),
            Paragraph("<b>30</b>", self.style_value),
        ])
        
        breakdown_table = Table(breakdown_data, colWidths=[4.2*inch, 1.0*inch, 1.0*inch])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), self.COLORS['gray_bg']),
            ('BOX', (0, 0), (-1, -1), 1, self.COLORS['gray_light']),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, self.COLORS['gray_light']),
            ('LINEBELOW', (0, -1), (-1, -1), 1.5, self.COLORS['gray_dark']),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(breakdown_table)
        
        return elements
    
    def _create_cac_section(self, verification: VerificationResult, customer: Customer) -> List:
        """Create compact CAC section with entity-specific details"""
        elements = []
        
        if not verification.cac_company_name:
            return elements
        
        # Section header
        elements.append(Paragraph("CAC Verification", self.style_heading))
        
        # Underline
        line = Table([['']], colWidths=[6.2*inch])
        line.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1, self.COLORS['gray_light']),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(line)
        
        # Format date
        inc_date = verification.cac_incorporation_date
        if inc_date:
            inc_date_str = inc_date if isinstance(inc_date, str) else inc_date.strftime("%B %d, %Y")
        else:
            inc_date_str = "N/A"
        
        # Basic CAC info
        cac_data = [
            [Paragraph("<b>Company Name:</b>", self.style_label), 
             Paragraph(verification.cac_company_name or "N/A", self.style_value)],
            [Paragraph("<b>RC Number:</b>", self.style_label), 
             Paragraph(customer.rc_number or "N/A", self.style_value)],
            [Paragraph("<b>Entity Type:</b>", self.style_label), 
             Paragraph(verification.cac_entity_type or "N/A", self.style_value)],
            [Paragraph("<b>Status:</b>", self.style_label), 
             Paragraph(verification.cac_status or "N/A", self.style_value)],
            [Paragraph("<b>Incorporated:</b>", self.style_label), 
             Paragraph(inc_date_str, self.style_value)],
            [Paragraph("<b>Address:</b>", self.style_label), 
             Paragraph(verification.cac_registered_address or "N/A", self.style_value)],
        ]
        
        cac_table = Table(cac_data, colWidths=[1.4*inch, 4.8*inch])
        cac_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['gray_bg']),
            ('BOX', (0, 0), (-1, -1), 1, self.COLORS['gray_light']),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, self.COLORS['gray_light']),
        ]))
        
        elements.append(cac_table)
        
        # Get entity-specific data
        entity_data = verification.cac_entity_data or {}
        entity_type = verification.cac_entity_type
        
        # Add entity-specific sections
        if entity_type in ['LIMITED', 'PLC']:
            # Directors
            directors = entity_data.get('directors', [])
            if directors:
                elements.append(Spacer(1, 6))
                elements.append(Paragraph("<b>Directors</b>", self.style_label))
                
                dir_data = [[Paragraph("<b>Name</b>", self.style_label), 
                            Paragraph("<b>Position</b>", self.style_label)]]
                
                for director in directors:
                    dir_data.append([
                        Paragraph(director.get('name', 'N/A'), self.style_normal),
                        Paragraph(director.get('position', 'N/A'), self.style_normal),
                    ])
                
                dir_table = Table(dir_data, colWidths=[3.5*inch, 2.7*inch])
                dir_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['gray_bg']),
                    ('BOX', (0, 0), (-1, -1), 1, self.COLORS['gray_light']),
                    ('LINEBELOW', (0, 0), (-1, -2), 0.5, self.COLORS['gray_light']),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ]))
                elements.append(dir_table)
            
            # Shareholders
            shareholders = entity_data.get('shareholders', [])
            if shareholders:
                elements.append(Spacer(1, 6))
                elements.append(Paragraph("<b>Shareholders</b>", self.style_label))
                
                sh_data = [[Paragraph("<b>Name</b>", self.style_label), 
                           Paragraph("<b>Ownership %</b>", self.style_label)]]
                
                for shareholder in shareholders:
                    sh_data.append([
                        Paragraph(shareholder.get('name', 'N/A'), self.style_normal),
                        Paragraph(f"{shareholder.get('percentage', 0)}%", self.style_normal),
                    ])
                
                sh_table = Table(sh_data, colWidths=[4.5*inch, 1.7*inch])
                sh_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['gray_bg']),
                    ('BOX', (0, 0), (-1, -1), 1, self.COLORS['gray_light']),
                    ('LINEBELOW', (0, 0), (-1, -2), 0.5, self.COLORS['gray_light']),
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ]))
                elements.append(sh_table)
            
            # Share capital
            share_capital = entity_data.get('share_capital')
            if share_capital:
                elements.append(Spacer(1, 4))
                cap_text = Paragraph(f"<b>Share Capital:</b> ₦{share_capital:,.2f}", self.style_normal)
                elements.append(cap_text)
        
        elif entity_type == 'BUSINESS_NAME':
            # Proprietors
            proprietors = entity_data.get('proprietors', [])
            if proprietors:
                elements.append(Spacer(1, 6))
                elements.append(Paragraph("<b>Proprietors</b>", self.style_label))
                
                prop_data = [[Paragraph("<b>Name</b>", self.style_label), 
                             Paragraph("<b>Ownership %</b>", self.style_label)]]
                
                for proprietor in proprietors:
                    prop_data.append([
                        Paragraph(proprietor.get('name', 'N/A'), self.style_normal),
                        Paragraph(f"{proprietor.get('percentage', 100)}%", self.style_normal),
                    ])
                
                prop_table = Table(prop_data, colWidths=[4.5*inch, 1.7*inch])
                prop_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['gray_bg']),
                    ('BOX', (0, 0), (-1, -1), 1, self.COLORS['gray_light']),
                    ('LINEBELOW', (0, 0), (-1, -2), 0.5, self.COLORS['gray_light']),
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ]))
                elements.append(prop_table)
            
            # Nature of business
            nature = entity_data.get('nature_of_business')
            if nature:
                elements.append(Spacer(1, 4))
                nature_text = Paragraph(f"<b>Nature of Business:</b> {nature}", self.style_normal)
                elements.append(nature_text)
        
        elif entity_type in ['NGO', 'INCORPORATED_TRUSTEES']:
            # Trustees
            trustees = entity_data.get('trustees', [])
            if trustees:
                elements.append(Spacer(1, 6))
                elements.append(Paragraph("<b>Trustees</b>", self.style_label))
                
                trustee_data = [[Paragraph("<b>Name</b>", self.style_label)]]
                
                for trustee in trustees:
                    trustee_data.append([
                        Paragraph(trustee.get('name', 'N/A'), self.style_normal),
                    ])
                
                trustee_table = Table(trustee_data, colWidths=[6.2*inch])
                trustee_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['gray_bg']),
                    ('BOX', (0, 0), (-1, -1), 1, self.COLORS['gray_light']),
                    ('LINEBELOW', (0, 0), (-1, -2), 0.5, self.COLORS['gray_light']),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ]))
                elements.append(trustee_table)
            
            # Aims and objectives
            aims = entity_data.get('aims_and_objectives')
            if aims:
                elements.append(Spacer(1, 4))
                aims_text = Paragraph(f"<b>Aims & Objectives:</b> {aims}", self.style_normal)
                elements.append(aims_text)
        
        return elements
    
    def _create_ubo_section(self, verification: VerificationResult) -> List:
        """Create compact UBO section"""
        elements = []
        
        ubo_data_dict = verification.ubo_data or {}
        ubos = ubo_data_dict.get('beneficial_owners', [])
        
        if not ubos:
            return elements
        
        # Section header
        elements.append(Paragraph("Ultimate Beneficial Owners", self.style_heading))
        
        # Underline
        line = Table([['']], colWidths=[6.2*inch])
        line.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1, self.COLORS['gray_light']),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(line)
        
        # UBO table
        ubo_table_data = [
            [Paragraph("<b>Name</b>", self.style_label),
             Paragraph("<b>Ownership</b>", self.style_label),
             Paragraph("<b>Type</b>", self.style_label)]
        ]
        
        for ubo in ubos:
            ubo_table_data.append([
                Paragraph(ubo.get('name', 'N/A'), self.style_normal),
                Paragraph(f"{ubo.get('ownership_percentage', 0)}%", self.style_normal),
                Paragraph(ubo.get('type', 'N/A'), self.style_normal),
            ])
        
        ubo_table = Table(ubo_table_data, colWidths=[3.2*inch, 1.5*inch, 1.5*inch])
        ubo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, self.COLORS['gray_light']),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, self.COLORS['gray_light']),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(ubo_table)
        
        return elements
    
    def _create_footer(self) -> List:
        """Create compact footer"""
        elements = []
        
        elements.append(Spacer(1, 10))
        
        footer = Paragraph(
            "E-KYC Check • Automated Verification Platform • © 2026 All Rights Reserved",
            ParagraphStyle('Footer', parent=self.style_normal, fontSize=7, textColor=self.COLORS['gray_medium'], alignment=TA_CENTER)
        )
        
        elements.append(footer)
        
        return elements
    
    async def generate_pdf_report(self, verification_id: UUID) -> bytes:
        """Generate compact PDF report"""
        
        # Get verification
        verification = self.db.query(VerificationResult).filter(
            VerificationResult.id == verification_id
        ).first()
        
        if not verification:
            raise ResourceNotFoundError("Verification", str(verification_id))
        
        # Get customer
        customer = self.db.query(Customer).filter(
            Customer.id == verification.customer_id
        ).first()
        
        # Create PDF with tight margins
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30,
        )
        
        elements = []
        
        # Header
        elements.extend(self._create_header(verification))
        
        # Customer info
        elements.extend(self._create_info_section(customer, verification))
        elements.append(Spacer(1, 10))
        
        # Individual verification details (BVN/NIN)
        elements.extend(self._create_individual_verification_section(verification))
        if verification.bvn_name:
            elements.append(Spacer(1, 10))
        
        # Risk assessment
        if verification.risk_score is not None:
            elements.extend(self._create_risk_section(verification))
            elements.append(Spacer(1, 10))
        
        # CAC verification
        elements.extend(self._create_cac_section(verification, customer))
        if verification.cac_company_name:
            elements.append(Spacer(1, 10))
        
        # UBO
        elements.extend(self._create_ubo_section(verification))
        
        # Footer
        elements.extend(self._create_footer())
        
        # Build
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

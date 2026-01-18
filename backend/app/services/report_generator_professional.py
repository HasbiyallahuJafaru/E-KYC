"""
Professional PDF Report Generator using ReportLab
Generates E-KYC verification reports with modern, corporate design
NO GRADIENTS - Solid colors only
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from io import BytesIO
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, KeepTogether
)

from app.models.verification_result import VerificationResult
from app.models.customer import Customer
from app.core.exceptions import ResourceNotFoundError


class ProfessionalReportGenerator:
    """
    Generates professional E-KYC verification reports in PDF format
    Follows exact design specification with no gradients
    """
    
    # Color palette - exact hex colors
    COLORS = {
        'primary': colors.HexColor('#1e40af'),           # Dark blue (header background)
        'primary_light': colors.HexColor('#3b82f6'),     # Medium blue (accents)
        'success': colors.HexColor('#10b981'),           # Green (low risk)
        'success_light': colors.HexColor('#86efac'),     # Light green (borders)
        'success_bg': colors.HexColor('#f0fdf4'),        # Very light green (backgrounds)
        'warning': colors.HexColor('#fde047'),           # Yellow (CAC border)
        'warning_bg': colors.HexColor('#fefce8'),        # Light yellow (CAC background)
        'warning_text': colors.HexColor('#854d0e'),      # Dark yellow/brown (CAC title)
        'warning_dark': colors.HexColor('#422006'),      # Very dark brown (CAC values)
        'gray_50': colors.HexColor('#f8fafc'),           # Very light gray (table headers)
        'gray_100': colors.HexColor('#f1f5f9'),          # Light gray (table row lines)
        'gray_200': colors.HexColor('#e2e8f0'),          # Medium-light gray (borders)
        'gray_500': colors.HexColor('#64748b'),          # Medium gray (labels)
        'gray_600': colors.HexColor('#475569'),          # Dark-medium gray (table headers)
        'gray_800': colors.HexColor('#1e293b'),          # Dark gray (headings)
        'gray_900': colors.HexColor('#0f172a'),          # Very dark gray (values)
        'white': colors.HexColor('#FFFFFF'),
    }
    
    def __init__(self, db: Session):
        """Initialize report generator with database session"""
        self.db = db
        self._init_styles()
    
    def _init_styles(self):
        """Initialize custom paragraph styles"""
        base_styles = getSampleStyleSheet()
        
        # Logo style (E-KYC in header)
        self.style_logo = ParagraphStyle(
            'Logo',
            parent=base_styles['Heading1'],
            fontName='Times-Bold',
            fontSize=32,
            textColor=self.COLORS['white'],
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=4,
            letterSpacing=-0.5,
        )
        
        # Tagline style
        self.style_tagline = ParagraphStyle(
            'Tagline',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.Color(1, 1, 1, 0.9),  # White 90% opacity
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=12,
            letterSpacing=0.5,
        )
        
        # Section title style
        self.style_section_title = ParagraphStyle(
            'SectionTitle',
            parent=base_styles['Heading2'],
            fontName='Times-Bold',
            fontSize=16,
            textColor=self.COLORS['gray_800'],
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=8,
        )
        
        # Info label style (small uppercase)
        self.style_info_label = ParagraphStyle(
            'InfoLabel',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=self.COLORS['gray_500'],
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=6,
            letterSpacing=0.5,
        )
        
        # Info value style (bold)
        self.style_info_value = ParagraphStyle(
            'InfoValue',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=self.COLORS['gray_900'],
            alignment=TA_LEFT,
        )
        
        # Company name style
        self.style_company_name = ParagraphStyle(
            'CompanyName',
            parent=base_styles['Heading2'],
            fontName='Times-Bold',
            fontSize=18,
            textColor=self.COLORS['gray_800'],
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=4,
        )
        
        # Risk score large number
        self.style_risk_score = ParagraphStyle(
            'RiskScore',
            parent=base_styles['Normal'],
            fontName='Times-Bold',
            fontSize=36,
            textColor=self.COLORS['success'],
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=8,
        )
        
        # CAC title style
        self.style_cac_title = ParagraphStyle(
            'CACTitle',
            parent=base_styles['Heading3'],
            fontName='Times-Bold',
            fontSize=14,
            textColor=self.COLORS['warning_text'],
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=12,
        )
        
        # UBO title style
        self.style_ubo_title = ParagraphStyle(
            'UBOTitle',
            parent=base_styles['Heading3'],
            fontName='Times-Bold',
            fontSize=13,
            textColor=self.COLORS['gray_800'],
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=8,
        )
    
    def _create_header(self, verification: VerificationResult) -> List:
        """
        Create full-width blue header section
        Dimensions: Full page width × ~120mm height
        Background: Solid primary (#1e40af) - NO GRADIENTS
        """
        elements = []
        
        # Logo
        logo = Paragraph("E-KYC", self.style_logo)
        
        # Tagline
        tagline = Paragraph("Automated KYC Verification Platform", self.style_tagline)
        
        # Divider line (created using a table)
        divider_style = ParagraphStyle(
            'Divider',
            fontSize=1,
            textColor=colors.Color(1, 1, 1, 0.2),
        )
        divider = Table([['']], colWidths=[A4[0]])
        divider.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.Color(1, 1, 1, 0.2)),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        # Meta information (two columns)
        meta_label_style = ParagraphStyle(
            'MetaLabel',
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.Color(1, 1, 1, 0.7),
            alignment=TA_LEFT,
        )
        meta_value_style = ParagraphStyle(
            'MetaValue',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.Color(1, 1, 1, 0.95),
            alignment=TA_LEFT,
        )
        
        # Format timestamp
        timestamp = datetime.utcnow().strftime("%B %d, %Y at %H:%M:%S UTC")
        
        meta_left = Table([
            [Paragraph("Report Generated", meta_label_style)],
            [Paragraph(timestamp, meta_value_style)]
        ], colWidths=[3.5*inch])
        meta_left.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        # Status pill
        status_text = "COMPLETED"
        status_style = ParagraphStyle(
            'Status',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=self.COLORS['white'],
            alignment=TA_CENTER,
        )
        status_pill = Table([[Paragraph(status_text, status_style)]], colWidths=[1.5*inch])
        status_pill.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['success']),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Meta row (left info + right status)
        meta_row = Table([[meta_left, status_pill]], colWidths=[5.5*inch, 2.5*inch])
        meta_row.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Combine all header elements
        header_content = Table([
            [logo],
            [tagline],
            [divider],
            [meta_row]
        ], colWidths=[A4[0] - 40])
        
        header_content.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        # Wrapper with background and padding
        header_wrapper = Table([[header_content]], colWidths=[A4[0]])
        header_wrapper.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['primary']),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        elements.append(header_wrapper)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_section_title(self, title: str) -> List:
        """
        Create section title with underline
        Font: Times-Bold, 16pt
        Underline: 2pt solid gray_200
        """
        elements = []
        
        # Title text
        title_para = Paragraph(title, self.style_section_title)
        
        # Underline
        underline = Table([['']], colWidths=[5.3*inch])
        underline.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 2, self.COLORS['gray_200']),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        elements.append(title_para)
        elements.append(underline)
        elements.append(Spacer(1, 12))
        
        return elements
    
    def _create_info_box(self, label: str, value: str) -> Table:
        """
        Create single info box with label and value
        Background: gray_50
        Border Left: 3pt solid primary_light
        """
        label_para = Paragraph(label.upper(), self.style_info_label)
        value_para = Paragraph(value, self.style_info_value)
        
        box = Table([[label_para], [value_para]], colWidths=[2.5*inch])
        box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['gray_50']),
            ('LINEAFTER', (0, 0), (0, -1), 3, self.COLORS['primary_light']),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        return box
    
    def _create_info_grid(self, items: List[tuple]) -> List:
        """
        Create 2-column info grid
        Each item is (label, value) tuple
        """
        elements = []
        
        # Create boxes in pairs
        for i in range(0, len(items), 2):
            left_box = self._create_info_box(items[i][0], items[i][1])
            
            if i + 1 < len(items):
                right_box = self._create_info_box(items[i+1][0], items[i+1][1])
                row = Table([[left_box, right_box]], colWidths=[2.5*inch, 2.5*inch], spaceBefore=0, spaceAfter=0)
                row.setStyle(TableStyle([
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
            else:
                row = left_box
            
            elements.append(row)
            if i + 2 < len(items):
                elements.append(Spacer(1, 8))
        
        return elements
    
    def _create_company_header(self, customer: Customer, verification: VerificationResult) -> List:
        """
        Create company header box
        Background: gray_50
        Border: 2pt solid gray_200
        """
        elements = []
        
        # Get customer name (business_name for corporate, full name for individual)
        if customer.business_name:
            customer_name = customer.business_name.upper()
        elif customer.first_name and customer.last_name:
            customer_name = f"{customer.first_name} {customer.last_name}".upper()
        else:
            customer_name = "N/A"
        
        # Company name
        name_para = Paragraph(customer_name, self.style_company_name)
        
        # Company type line
        type_text = f"Type: {verification.verification_type.value.upper()} • RC Number: {customer.rc_number or 'N/A'}"
        type_style = ParagraphStyle(
            'CompanyType',
            fontName='Helvetica',
            fontSize=11,
            textColor=self.COLORS['gray_500'],
        )
        type_para = Paragraph(type_text, type_style)
        
        # Company box
        company_box = Table([[name_para], [type_para]], colWidths=[5.3*inch])
        company_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['gray_50']),
            ('BOX', (0, 0), (-1, -1), 2, self.COLORS['gray_200']),
            ('TOPPADDING', (0, 0), (-1, -1), 16),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
            ('LEFTPADDING', (0, 0), (-1, -1), 16),
            ('RIGHTPADDING', (0, 0), (-1, -1), 16),
        ]))
        
        elements.append(company_box)
        
        return elements
    
    def _create_progress_bar(self, score: int, maximum: int) -> Table:
        """
        Create progress bar showing score/maximum ratio
        Container: 1.2 inches × 8pt, gray_200 background
        Fill: success color, width based on percentage
        """
        if maximum == 0:
            percentage = 0
        else:
            percentage = score / maximum
        
        fill_width = 1.2 * inch * percentage
        empty_width = 1.2 * inch - fill_width
        
        # Create fill and empty parts
        if fill_width > 0:
            fill = Table([['']], colWidths=[fill_width], rowHeights=[8])
            fill.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['success']),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
        
        if empty_width > 0:
            empty = Table([['']], colWidths=[empty_width], rowHeights=[8])
            empty.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['gray_200']),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
        
        # Combine
        if fill_width > 0 and empty_width > 0:
            bar = Table([[fill, empty]], colWidths=[fill_width, empty_width])
        elif fill_width > 0:
            bar = Table([[fill]], colWidths=[fill_width])
        else:
            bar = Table([[empty]], colWidths=[1.2*inch])
        
        bar.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        return bar
    
    def _create_risk_assessment(self, verification: VerificationResult) -> List:
        """
        Create risk assessment section
        Part A: Risk score card
        Part B: Risk breakdown table with progress bars
        """
        elements = []
        
        # Part A: Risk Score Card
        risk_score = verification.risk_score or 0
        risk_category = verification.risk_category or 'UNKNOWN'
        
        # Large score
        score_para = Paragraph(f"{risk_score}/30", self.style_risk_score)
        
        # Category
        category_style = ParagraphStyle(
            'RiskCategory',
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=self.COLORS['success'],
            alignment=TA_CENTER,
            letterSpacing=1,
        )
        category_para = Paragraph(risk_category.upper(), category_style)
        
        # Label
        label_style = ParagraphStyle(
            'RiskLabel',
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.Color(0.0627, 0.7255, 0.5059, 0.8),  # success with 80% opacity
            alignment=TA_CENTER,
        )
        label_para = Paragraph("Risk Category", label_style)
        
        # Risk card
        risk_card = Table([
            [score_para],
            [category_para],
            [Spacer(1, 4)],
            [label_para]
        ], colWidths=[5.3*inch])
        
        risk_card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['success_bg']),
            ('BOX', (0, 0), (-1, -1), 2, self.COLORS['success_light']),
            ('TOPPADDING', (0, 0), (-1, -1), 18),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 18),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        
        elements.append(risk_card)
        elements.append(Spacer(1, 16))
        
        # Part B: Risk Breakdown Table
        breakdown = verification.risk_breakdown or {}
        
        # Table header style
        header_style = ParagraphStyle(
            'TableHeader',
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=self.COLORS['gray_600'],
            alignment=TA_LEFT,
            letterSpacing=0.5,
        )
        
        # Data row style
        data_style = ParagraphStyle(
            'TableData',
            fontName='Helvetica',
            fontSize=11,
            textColor=self.COLORS['gray_800'],
            alignment=TA_LEFT,
        )
        
        # Create table data
        table_data = [
            # Header row
            [
                Paragraph("CATEGORY", header_style),
                Paragraph("SCORE", header_style),
                Paragraph("MAXIMUM", header_style),
                Paragraph("PROGRESS", header_style),
            ]
        ]
        
        # Data rows
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
            table_data.append([
                Paragraph(display_name, data_style),
                Paragraph(str(score), ParagraphStyle('Center', parent=data_style, alignment=TA_CENTER)),
                Paragraph(str(max_score), ParagraphStyle('Center', parent=data_style, alignment=TA_CENTER)),
                self._create_progress_bar(score, max_score),
            ])
        
        # Total row
        total_style = ParagraphStyle(
            'TableTotal',
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=self.COLORS['gray_800'],
            alignment=TA_LEFT,
        )
        table_data.append([
            Paragraph("Total", total_style),
            Paragraph(str(risk_score), ParagraphStyle('Center', parent=total_style, alignment=TA_CENTER)),
            Paragraph("30", ParagraphStyle('Center', parent=total_style, alignment=TA_CENTER)),
            self._create_progress_bar(risk_score, 30),
        ])
        
        # Create table
        breakdown_table = Table(
            table_data,
            colWidths=[2.2*inch, 0.7*inch, 0.8*inch, 1.4*inch]
        )
        
        # Apply styling
        style_commands = [
            # Border around entire table
            ('BOX', (0, 0), (-1, -1), 1, self.COLORS['gray_200']),
            
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['gray_50']),
            ('LINEBELOW', (0, 0), (-1, 0), 2, self.COLORS['gray_200']),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            
            # Data rows
            ('TOPPADDING', (0, 1), (-1, -2), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -2), 10),
            ('LINEBELOW', (0, 1), (-1, -2), 1, self.COLORS['gray_100']),
            
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), self.COLORS['gray_50']),
            ('TOPPADDING', (0, -1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
            
            # All cells
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Center alignment for score and max columns
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
        ]
        
        breakdown_table.setStyle(TableStyle(style_commands))
        
        elements.append(breakdown_table)
        
        return elements
    
    def _create_cac_section(self, verification: VerificationResult) -> List:
        """
        Create CAC verification section
        Part A: CAC details box (yellow theme)
        Part B: UBO table
        """
        elements = []
        
        # Get customer for RC number
        customer = self.db.query(Customer).filter(
            Customer.id == verification.customer_id
        ).first()
        
        # Part A: CAC Details Box
        cac_title = Paragraph("Corporate Affairs Commission Details", self.style_cac_title)
        
        # CAC label/value styles
        cac_label_style = ParagraphStyle(
            'CACLabel',
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=colors.HexColor('#713f12'),
            letterSpacing=0.5,
        )
        cac_value_style = ParagraphStyle(
            'CACValue',
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=self.COLORS['warning_dark'],
        )
        
        # Helper function to create CAC item
        def cac_item(label, value):
            return Table([
                [Paragraph(label.upper(), cac_label_style)],
                [Spacer(1, 4)],
                [Paragraph(str(value), cac_value_style)]
            ], colWidths=[2.4*inch])
        
        # Format incorporation date
        inc_date = verification.cac_incorporation_date
        if inc_date:
            inc_date_str = inc_date if isinstance(inc_date, str) else inc_date.strftime("%B %d, %Y")
        else:
            inc_date_str = "N/A"
        
        # Create CAC items
        company_name_item = cac_item("Company Name", verification.cac_company_name or "N/A")
        rc_number_item = cac_item("RC Number", customer.rc_number if customer else "N/A")
        entity_type_item = cac_item("Entity Type", verification.cac_entity_type or "N/A")
        status_item = cac_item("Status", verification.cac_status or "N/A")
        incorporated_item = cac_item("Incorporated", inc_date_str)
        
        # Address (full width)
        address_item = cac_item("Address", verification.cac_registered_address or "N/A")
        
        # Create grid
        cac_grid = Table([
            [cac_title],
            [Spacer(1, 12)],
            [Table([[company_name_item, rc_number_item]], colWidths=[2.4*inch, 2.4*inch])],
            [Spacer(1, 8)],
            [Table([[entity_type_item, status_item]], colWidths=[2.4*inch, 2.4*inch])],
            [Spacer(1, 8)],
            [Table([[incorporated_item, Table([['']], colWidths=[2.4*inch])]], colWidths=[2.4*inch, 2.4*inch])],
            [Spacer(1, 8)],
            [address_item],
        ], colWidths=[5.1*inch])
        
        cac_grid.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['warning_bg']),
            ('BOX', (0, 0), (-1, -1), 2, self.COLORS['warning']),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        elements.append(cac_grid)
        elements.append(Spacer(1, 16))
        
        # Part B: UBO Table
        ubo_title = Paragraph("Ultimate Beneficial Owners (≥25%)", self.style_ubo_title)
        elements.append(ubo_title)
        elements.append(Spacer(1, 8))
        
        # Get UBO data
        ubo_data = verification.ubo_data or {}
        ubos = ubo_data.get('beneficial_owners', [])
        
        # Table header
        header_style = ParagraphStyle(
            'UBOHeader',
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=self.COLORS['gray_600'],
            letterSpacing=0.5,
        )
        
        data_style = ParagraphStyle(
            'UBOData',
            fontName='Helvetica',
            fontSize=11,
            textColor=self.COLORS['gray_800'],
        )
        
        ubo_table_data = [
            [
                Paragraph("NAME", header_style),
                Paragraph("OWNERSHIP %", header_style),
                Paragraph("TYPE", header_style),
            ]
        ]
        
        # Add UBO rows
        for ubo in ubos:
            ubo_table_data.append([
                Paragraph(ubo.get('name', 'N/A'), data_style),
                Paragraph(f"{ubo.get('ownership_percentage', 0)}%", data_style),
                Paragraph(ubo.get('type', 'N/A').upper(), data_style),
            ])
        
        # If no UBOs, add placeholder
        if not ubos:
            ubo_table_data.append([
                Paragraph("No beneficial owners found", data_style),
                Paragraph("—", data_style),
                Paragraph("—", data_style),
            ])
        
        ubo_table = Table(ubo_table_data, colWidths=[2.8*inch, 1.2*inch, 1.3*inch])
        
        ubo_table.setStyle(TableStyle([
            # Border
            ('BOX', (0, 0), (-1, -1), 1, self.COLORS['gray_200']),
            
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['gray_50']),
            ('LINEBELOW', (0, 0), (-1, 0), 2, self.COLORS['gray_200']),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('LINEBELOW', (0, 1), (-1, -2), 1, self.COLORS['gray_100']),
            
            # All cells
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(ubo_table)
        
        return elements
    
    def _create_footer(self, verification: VerificationResult) -> List:
        """
        Create full-width footer
        Background: gray_50
        Border Top: 1pt solid gray_200
        """
        elements = []
        
        # Left side
        left_style = ParagraphStyle(
            'FooterLeft',
            fontName='Times-Bold',
            fontSize=9,
            textColor=self.COLORS['gray_800'],
            alignment=TA_LEFT,
        )
        left_text = Paragraph("E-KYC Check", left_style)
        
        # Right side
        right_style = ParagraphStyle(
            'FooterRight',
            fontName='Helvetica',
            fontSize=9,
            textColor=self.COLORS['gray_500'],
            alignment=TA_RIGHT,
        )
        verification_id_short = str(verification.id)[:8]
        right_text = Paragraph(
            f"Report ID: {verification_id_short} • Processing: 129ms • © 2026 E-KYC Check. All rights reserved.",
            right_style
        )
        
        # Footer content
        footer_content = Table([[left_text, right_text]], colWidths=[3*inch, 5*inch])
        footer_content.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Footer wrapper
        footer_wrapper = Table([[footer_content]], colWidths=[A4[0]])
        footer_wrapper.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['gray_50']),
            ('LINEABOVE', (0, 0), (-1, -1), 1, self.COLORS['gray_200']),
            ('TOPPADDING', (0, 0), (-1, -1), 16),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        elements.append(footer_wrapper)
        
        return elements
    
    async def generate_pdf_report(self, verification_id: UUID) -> bytes:
        """
        Generate professional PDF verification report
        
        Args:
            verification_id: The verification to report on
            
        Returns:
            bytes: PDF content
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
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0,
            leftMargin=0,
            topMargin=0,
            bottomMargin=0,
        )
        
        elements = []
        
        # 1. Header (full-width blue bar)
        elements.extend(self._create_header(verification))
        
        # Content wrapper helper (30pt margins)
        def wrap_content(content_elements):
            wrapper = Table([[Table([[e] for e in content_elements], colWidths=[5.3*inch])]], colWidths=[A4[0]])
            wrapper.setStyle(TableStyle([
                ('LEFTPADDING', (0, 0), (-1, -1), 30),
                ('RIGHTPADDING', (0, 0), (-1, -1), 30),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            return wrapper
        
        # 2. Verification Details
        section = []
        section.extend(self._create_section_title('Verification Details'))
        section.extend(self._create_info_grid([
            ('Verification ID', str(verification.id)),
            ('Verification Type', verification.verification_type.value.upper()),
        ]))
        elements.append(wrap_content(section))
        elements.append(Spacer(1, 16))
        
        # 3. Customer Information
        section = []
        section.extend(self._create_section_title('Customer Information'))
        section.extend(self._create_company_header(customer, verification))
        elements.append(wrap_content(section))
        elements.append(Spacer(1, 12))
        
        # 4. Risk Assessment
        if verification.risk_score is not None:
            section = []
            section.extend(self._create_section_title('Risk Assessment'))
            section.extend(self._create_risk_assessment(verification))
            elements.append(wrap_content(section))
            elements.append(Spacer(1, 16))
        
        # 5. CAC Verification
        if verification.cac_company_name:
            section = []
            section.extend(self._create_section_title('CAC Verification'))
            section.extend(self._create_cac_section(verification))
            elements.append(wrap_content(section))
            elements.append(Spacer(1, 16))
        
        # 6. Footer (full-width gray bar)
        elements.extend(self._create_footer(verification))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

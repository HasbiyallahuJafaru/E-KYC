"""
Report generation service using ReportLab.
Generates professional PDF verification reports programmatically.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from io import BytesIO
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, PageBreak, KeepTogether
)

from app.models.verification_result import VerificationResult
from app.models.customer import Customer
from app.core.exceptions import ResourceNotFoundError


class ReportGeneratorReportLab:
    """
    Generates E-KYC verification reports in PDF format using ReportLab
    """
    
    # Color scheme
    COLORS = {
        'primary': colors.HexColor('#1e40af'),
        'primary_light': colors.HexColor('#3b82f6'),
        'success': colors.HexColor('#10b981'),
        'success_light': colors.HexColor('#86efac'),
        'success_bg': colors.HexColor('#f0fdf4'),
        'warning': colors.HexColor('#f59e0b'),
        'warning_light': colors.HexColor('#fde047'),
        'warning_bg': colors.HexColor('#fefce8'),
        'warning_text': colors.HexColor('#854d0e'),
        'warning_dark': colors.HexColor('#422006'),
        'danger': colors.HexColor('#ef4444'),
        'danger_light': colors.HexColor('#fca5a5'),
        'danger_bg': colors.HexColor('#fef2f2'),
        'page_bg': colors.HexColor('#f5f7fb'),
        'card_bg': colors.HexColor('#ffffff'),
        'card_border': colors.HexColor('#d7e1f5'),
        'card_shadow': colors.HexColor('#e2e8f0'),
        'gray_50': colors.HexColor('#f8fafc'),
        'gray_100': colors.HexColor('#f1f5f9'),
        'gray_200': colors.HexColor('#e2e8f0'),
        'gray_400': colors.HexColor('#94a3b8'),
        'gray_500': colors.HexColor('#64748b'),
        'gray_600': colors.HexColor('#475569'),
        'gray_800': colors.HexColor('#1e293b'),
        'gray_900': colors.HexColor('#0f172a'),
        'white': colors.white,
    }
    
    def __init__(self, db: Session):
        """Initialize the report generator"""
        self.db = db
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        
        # Logo style
        self.styles.add(ParagraphStyle(
            name='Logo',
            parent=self.styles['Heading1'],
            fontName='Times-Bold',
            fontSize=32,
            textColor=self.COLORS['white'],
            spaceAfter=4,
            letterSpacing=-0.5,
        ))
        
        # Tagline style
        self.styles.add(ParagraphStyle(
            name='Tagline',
            fontName='Helvetica',
            fontSize=11,
            textColor=self.COLORS['white'],
            spaceAfter=12,
        ))
        
        # Section title style
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            fontName='Helvetica-Bold',
            fontSize=17,
            textColor=self.COLORS['gray_800'],
            spaceAfter=2,
            spaceBefore=10,
        ))
        
        # Info label/value styles
        self.styles.add(ParagraphStyle(
            name='InfoLabel',
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=self.COLORS['gray_500'],
            spaceAfter=2,
        ))
        
        self.styles.add(ParagraphStyle(
            name='InfoValue',
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=self.COLORS['gray_900'],
        ))
        
        # Company name style
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            fontName='Times-Bold',
            fontSize=18,
            textColor=self.COLORS['gray_800'],
            spaceAfter=4,
        ))
        
        # Risk score style
        self.styles.add(ParagraphStyle(
            name='RiskScore',
            fontName='Times-Bold',
            fontSize=36,
            alignment=TA_CENTER,
        ))
        
        # Footer text style
        self.styles.add(ParagraphStyle(
            name='Footer',
            fontName='Helvetica',
            fontSize=9,
            textColor=self.COLORS['gray_500'],
        ))
    
    def _create_header(self, verification: VerificationResult):
        """Create the top hero card with modern styling"""
        elements = []
        status_color = self.COLORS['success'] if verification.status.value == 'COMPLETED' else self.COLORS['warning']
        report_date = datetime.utcnow().strftime("%B %d, %Y at %H:%M:%S UTC")
        
        title_para = Paragraph(
            '<font size=30 color="#ffffff"><b>E-KYC</b></font>',
            ParagraphStyle(name='HeroTitle', fontName='Helvetica-Bold')
        )
        subtitle_para = Paragraph(
            '<font size=12 color="#e0e7ff">Automated KYC Verification Platform</font>',
            ParagraphStyle(name='HeroSubtitle', fontName='Helvetica')
        )
        meta_para = Paragraph(
            f'<font size=10 color="#cbd5ff">Report Generated</font><br/>'
            f'<font size=13 color="#ffffff"><b>{report_date}</b></font>',
            ParagraphStyle(name='HeroMeta', fontName='Helvetica', leading=16)
        )
        status_para = Paragraph(
            f'<font size=11 color="#ffffff"><b>{verification.status.value.upper()}</b></font>',
            ParagraphStyle(name='StatusPill', fontName='Helvetica-Bold', alignment=TA_CENTER)
        )
        status_pill = Table([[status_para]], colWidths=[1.3*inch])
        status_pill.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), status_color),
            ('LEFTPADDING', (0, 0), (-1, -1), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), 14),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 0, colors.transparent),
        ]))
        
        hero_table = Table(
            [
                [title_para, status_pill],
                [subtitle_para, ''],
                [meta_para, '']
            ],
            colWidths=[4.8*inch, 1.4*inch]
        )
        hero_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['primary']),
            ('BOX', (0, 0), (-1, -1), 0, colors.transparent),
            ('LEFTPADDING', (0, 0), (-1, -1), 26),
            ('RIGHTPADDING', (0, 0), (-1, -1), 26),
            ('TOPPADDING', (0, 0), (-1, -1), 18),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 18),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        
        # Surround hero with rounded card illusion using lighter background
        hero_wrapper = Table([[hero_table]], colWidths=[6.3*inch])
        hero_wrapper.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['page_bg']),
            ('BOX', (0, 0), (-1, -1), 0, colors.transparent),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(hero_wrapper)
        elements.append(Spacer(1, 14))
        
        return elements
    
    def _create_section_title(self, title: str):
        """Create a section title with underline"""
        elements = []
        title_para = Paragraph(title, self.styles['SectionTitle'])
        elements.append(title_para)
        line_table = Table([['']], colWidths=[5.9*inch])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1.5, self.COLORS['gray_200']),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 10))
        
        return elements
    
    def _create_info_grid(self, info_items):
        """Create an information grid (2 columns) with clean design"""
        elements = []
        grid_data = []
        row = []
        
        for i, (label, value) in enumerate(info_items):
            # Create individual info box with blue left border
            cell_content = [
                [Paragraph(f'<font size=8 color="#64748b">{label.upper()}</font>',
                           ParagraphStyle(name=f'Label{i}', fontName='Helvetica', leading=13))],
                [Paragraph(f'<font size=14 color="#0f172a"><b>{str(value)}</b></font>',
                           ParagraphStyle(name=f'Value{i}', fontName='Helvetica'))]
            ]
            
            cell_table = Table(cell_content, colWidths=[2.7*inch])
            cell_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['card_bg']),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 14),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LINEABOVE', (0, 0), (-1, -1), 2, self.COLORS['primary_light']),
            ]))
            
            row.append(cell_table)
            
            if len(row) == 2 or i == len(info_items) - 1:
                while len(row) < 2:
                    row.append('')
                grid_data.append(row)
                row = []
        
        grid_table = Table(grid_data, colWidths=[2.95*inch, 2.95*inch], spaceBefore=0, spaceAfter=0)
        grid_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        grid_wrapper = Table([[grid_table]], colWidths=[6.0*inch])
        grid_wrapper.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['card_bg']),
            ('BOX', (0, 0), (-1, -1), 1, self.COLORS['card_border']),
            ('LEFTPADDING', (0, 0), (-1, -1), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), 14),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(grid_wrapper)
        elements.append(Spacer(1, 12))
        
        return elements
    
    def _create_company_header(self, customer: Optional[Customer], verification: VerificationResult):
        """Create company header box with clean styling"""
        elements = []
        
        # Get customer name
        customer_name = self._get_customer_name(customer, verification)
        customer_type = customer.customer_type.value.upper() if customer else 'UNKNOWN'
        rc_number = customer.rc_number if customer and customer.rc_number else 'N/A'
        
        name_para = Paragraph(
            f'<font size=20 color="#1e293b"><b>{customer_name}</b></font>',
            ParagraphStyle(name='CompName', fontName='Helvetica')
        )
        type_para = Paragraph(
            f'<font size=11 color="#64748b">Type: <b>{customer_type}</b> • RC Number: <b>{rc_number}</b></font>',
            ParagraphStyle(name='CompType', fontName='Helvetica')
        )
        
        company_data = [[name_para], [Spacer(1, 4)], [type_para]]
        company_table = Table(company_data, colWidths=[5.8*inch])
        company_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['card_bg']),
            ('BOX', (0, 0), (-1, -1), 1, self.COLORS['card_border']),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ]))
        
        elements.append(company_table)
        elements.append(Spacer(1, 14))
        
        return elements
    
    def _create_risk_assessment(self, verification: VerificationResult):
        """Create risk assessment section"""
        elements = []
        
        # Determine risk colors
        if verification.risk_category == 'LOW':
            risk_color = self.COLORS['success']
            risk_bg = self.COLORS['success_bg']
            risk_border = self.COLORS['success_light']
        elif verification.risk_category == 'MEDIUM':
            risk_color = self.COLORS['warning']
            risk_bg = self.COLORS['warning_bg']
            risk_border = self.COLORS['warning_light']
        else:  # HIGH
            risk_color = self.COLORS['danger']
            risk_bg = self.COLORS['danger_bg']
            risk_border = self.COLORS['danger_light']
        
        # Risk score card with large centered score
        # Combine all text into single paragraph for cleaner rendering
        risk_text = (
            f'<font size=48 color="{risk_color.hexval()}"><b>{verification.risk_score}/30</b></font><br/>'
            f'<font size=4> </font><br/>'  # Spacer line
            f'<font size=16 color="{risk_color.hexval()}"><b>{verification.risk_category} RISK</b></font><br/>'
            f'<font size=11 color="{risk_color.hexval()}">Risk Category</font>'
        )
        
        risk_para = Paragraph(
            risk_text,
            ParagraphStyle(
                name='RiskCardText', 
                fontName='Helvetica', 
                alignment=TA_CENTER,
                leading=20
            )
        )
        
        risk_card = Table([[risk_para]], colWidths=[5.2*inch])
        risk_card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), risk_bg),
            ('BOX', (0, 0), (-1, -1), 2, risk_border),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(risk_card)
        elements.append(Spacer(1, 12))
        
        # Risk breakdown table
        if verification.risk_breakdown:
            breakdown_data = [['Category', 'Score', 'Maximum', 'Progress']]
            
            for category, score in verification.risk_breakdown.items():
                # Create progress bar
                max_score = 5
                percentage = (score / max_score * 100) if max_score > 0 else 0
                bar_width = 1.2 * inch
                fill_width = bar_width * (percentage / 100)
                
                # Progress bar fill
                progress_bar = None
                if fill_width > 0:
                    progress_bar = Table([['']], colWidths=[fill_width])
                    progress_bar.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['success']),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ]))
                
                # Container for progress bar
                bar_container = Table([[progress_bar if progress_bar else '']], colWidths=[bar_width])
                bar_container.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['gray_200']),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
                
                row = [
                    category.replace('_', ' ').title(),
                    str(score),
                    str(max_score),
                    bar_container
                ]
                breakdown_data.append(row)
            
            # Total row
            total_row = [
                'Total',
                str(verification.risk_score),
                '30',
                Table([['']], colWidths=[1.2*inch])
            ]
            breakdown_data.append(total_row)
            
            breakdown_table = Table(breakdown_data, colWidths=[2.3*inch, 0.8*inch, 0.9*inch, 1.5*inch])
            
            style_commands = [
                ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['gray_100']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['gray_600']),
                ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('TOPPADDING', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
                ('LINEBELOW', (0, 0), (-1, 0), 2, self.COLORS['gray_200']),
                ('LINEBELOW', (0, 1), (-1, -2), 1, self.COLORS['gray_100']),
                ('BOX', (0, 0), (-1, -1), 1, self.COLORS['gray_200']),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [self.COLORS['card_bg'], self.COLORS['gray_50']]),
                ('BACKGROUND', (0, -1), (-1, -1), self.COLORS['gray_100']),
                ('FONTNAME', (0, -1), (0, -1), 'Helvetica-Bold'),
            ]
            
            breakdown_table.setStyle(TableStyle(style_commands))
            elements.append(breakdown_table)
            elements.append(Spacer(1, 16))
        
        return elements
    
    def _create_cac_section(self, verification: VerificationResult):
        """Create CAC verification section"""
        elements = []
        
        # CAC title with proper styling
        cac_title = Paragraph(
            '<font size=14 color="#854d0e"><b>Corporate Affairs Commission Details</b></font>',
            ParagraphStyle(name='CACTitle2', fontName='Helvetica')
        )
        
        # CAC info grid
        cac_items = [
            ('Company Name', verification.cac_company_name or 'N/A'),
            ('RC Number', verification.customer.rc_number if verification.customer else 'N/A'),
            ('Entity Type', verification.cac_entity_type or 'N/A'),
            ('Status', verification.cac_status or 'N/A'),
        ]
        
        if verification.cac_incorporation_date:
            cac_items.append(('Incorporated', verification.cac_incorporation_date))
        
        if verification.cac_registered_address:
            cac_items.append(('Address', verification.cac_registered_address))
        
        cac_grid_data = []
        row = []
        
        for i, (label, value) in enumerate(cac_items):
            cell_para = Paragraph(
                f'<font size=9 color="#713f12"><b>{label.upper()}</b></font><br/>'
                f'<font size=12 color="#422006"><b>{value}</b></font>',
                ParagraphStyle(name=f'CACCell{i}', fontName='Helvetica')
            )
            row.append(cell_para)
            
            # Address takes full width
            if label == 'Address' or len(row) == 2:
                if label == 'Address':
                    cac_grid_data.append([cell_para])
                else:
                    cac_grid_data.append(row)
                row = []
        
        cac_grid = Table(cac_grid_data, colWidths=[2.4*inch, 2.4*inch])
        cac_grid.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        # Wrap in yellow card with subtle border
        cac_box_data = [[cac_title], [Spacer(1, 10)], [cac_grid]]
        cac_box = Table(cac_box_data, colWidths=[5.6*inch])
        cac_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['warning_bg']),
            ('BOX', (0, 0), (-1, -1), 1.3, self.COLORS['warning_light']),
            ('LEFTPADDING', (0, 0), (-1, -1), 16),
            ('RIGHTPADDING', (0, 0), (-1, -1), 16),
            ('TOPPADDING', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ]))
        
        cac_wrapper = Table([[cac_box]], colWidths=[6.0*inch])
        cac_wrapper.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['card_bg']),
            ('BOX', (0, 0), (-1, -1), 1, self.COLORS['card_border']),
            ('LEFTPADDING', (0, 0), (-1, -1), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), 14),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(cac_wrapper)
        elements.append(Spacer(1, 18))
        
        # UBO section if exists
        ubo_data = verification.ubo_data
        if ubo_data and isinstance(ubo_data, dict):
            ubos = ubo_data.get('beneficial_owners', [])
            if ubos and len(ubos) > 0:
                ubo_title = Paragraph(
                    '<font size=14 color="#1e293b"><b>Ultimate Beneficial Owners (≥25%)</b></font>',
                    ParagraphStyle(name='UBOTitle2', fontName='Helvetica')
                )
                ubo_table_data = [['Name', 'Ownership %', 'Type']]
                for ubo in ubos:
                    ubo_table_data.append([
                        ubo.get('name', 'N/A'),
                        f"{ubo.get('ownership_percentage', 0):.2f}%",
                        ubo.get('ownership_type', 'N/A')
                    ])
                
                ubo_table = Table(ubo_table_data, colWidths=[3.2*inch, 1.0*inch, 1.2*inch])
                ubo_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['gray_100']),
                    ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['gray_600']),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 11),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('LINEBELOW', (0, 0), (-1, 0), 1.5, self.COLORS['gray_200']),
                    ('LINEBELOW', (0, 1), (-1, -2), 0.8, self.COLORS['gray_100']),
                    ('BOX', (0, 0), (-1, -1), 1, self.COLORS['gray_200']),
                ]))
                
                ubo_card = Table([[ubo_title], [Spacer(1, 6)], [ubo_table]], colWidths=[6.0*inch])
                ubo_card.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['card_bg']),
                    ('BOX', (0, 0), (-1, -1), 1, self.COLORS['card_border']),
                    ('LEFTPADDING', (0, 0), (-1, -1), 14),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 14),
                    ('TOPPADDING', (0, 0), (-1, -1), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ]))
                
                elements.append(ubo_card)
        
        return elements
    
    def _create_footer(self, verification: VerificationResult):
        """Create footer section"""
        footer_table = Table([
            [
                Paragraph(
                    '<b>E-KYC Check</b>',
                    ParagraphStyle(
                        name='FooterBrand',
                        fontName='Times-Bold',
                        fontSize=9,
                        textColor=self.COLORS['gray_800']
                    )
                ),
                Paragraph(
                    f'Report ID: {str(verification.id)[:8]} • '
                    f'Processing: {verification.processing_time_ms}ms • '
                    f'© 2026 E-KYC Check',
                    self.styles['Footer']
                )
            ]
        ], colWidths=[1.8*inch, 3.9*inch])
        
        footer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['card_bg']),
            ('LINEABOVE', (0, 0), (-1, -1), 1, self.COLORS['gray_200']),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 24),
            ('RIGHTPADDING', (0, 0), (-1, -1), 24),
            ('TOPPADDING', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ]))
        
        return footer_table
    
    def _get_customer_name(self, customer: Optional[Customer], verification: VerificationResult) -> str:
        """Extract customer name from various sources"""
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
        
        if verification.cac_company_name:
            return verification.cac_company_name
        
        return "UNKNOWN"
    
    async def generate_pdf_report(self, verification_id: UUID) -> bytes:
        """
        Generate a PDF verification report using ReportLab
        
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
        
        # Header
        elements.extend(self._create_header(verification))
        
        # Helper function to wrap section in margin container
        def wrap_section(section_elements):
            """Wrap section elements in a padded container"""
            content_table = Table([[c] for c in section_elements], colWidths=[5.6*inch])
            content_table.setStyle(TableStyle([
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            wrapper = Table([[content_table]], colWidths=[5.9*inch])
            wrapper.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['page_bg']),
                ('LEFTPADDING', (0, 0), (-1, -1), 24),
                ('RIGHTPADDING', (0, 0), (-1, -1), 24),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            return wrapper
        
        # Verification Details
        section = []
        section.extend(self._create_section_title('Verification Details'))
        section.extend(self._create_info_grid([
            ('Verification ID', str(verification.id)),
            ('Verification Type', verification.verification_type.value.upper()),
        ]))
        elements.append(wrap_section(section))
        
        # Customer Information
        section = []
        section.extend(self._create_section_title('Customer Information'))
        section.extend(self._create_company_header(customer, verification))
        elements.append(wrap_section(section))
        
        # Risk Assessment
        if verification.risk_score is not None:
            section = []
            section.extend(self._create_section_title('Risk Assessment'))
            section.extend(self._create_risk_assessment(verification))
            elements.append(wrap_section(section))
        
        # CAC Verification
        if verification.cac_company_name:
            section = []
            section.extend(self._create_section_title('CAC Verification'))
            section.extend(self._create_cac_section(verification))
            elements.append(wrap_section(section))
        
        elements.append(Spacer(1, 12))
        
        # Footer
        elements.append(self._create_footer(verification))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

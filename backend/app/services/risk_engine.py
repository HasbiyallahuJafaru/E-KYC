"""
Deterministic risk scoring engine per FATF/CBN requirements.
Returns transparent calculation breakdown for regulatory explainability.
"""

from dataclasses import dataclass
from typing import Optional
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RiskFactors:
    """Input factors for risk calculation."""
    # Customer Risk (35%)
    customer_type: str  # INDIVIDUAL, CORPORATE, NGO, GOVERNMENT
    occupation: Optional[str] = None
    industry_sector: Optional[str] = None
    is_pep: bool = False
    source_of_funds_clarity: str = "CLEAR"  # CLEAR, UNCLEAR, SUSPICIOUS
    
    # Corporate/Entity-specific factors
    cac_entity_type: Optional[str] = None  # LIMITED, PLC, BUSINESS_NAME, NGO, INCORPORATED_TRUSTEES
    directors_count: int = 0
    inactive_directors_count: int = 0  # Directors with REMOVED/RESIGNED status
    directors_missing_contacts: int = 0  # Directors without email or phone
    shareholders_count: int = 0
    corporate_shareholders_count: int = 0
    ownership_concentration: float = 0.0  # Highest single shareholder percentage
    ubo_count: int = 0
    has_incomplete_ownership: bool = False  # Total ownership < 100%
    
    # Geographic Risk (25%)
    nationality: str = "Nigeria"
    residence_country: str = "Nigeria"
    transaction_countries: list[str] = None
    
    # Product/Service Risk (20%)
    product_type: str = "CURRENT_ACCOUNT"
    expected_turnover: int = 0  # Monthly in NGN
    cash_intensity: str = "LOW"  # LOW, MEDIUM, HIGH
    
    # Channel Risk (20%)
    onboarding_channel: str = "IN_PERSON"  # IN_PERSON, REMOTE, INTERMEDIARY
    
    def __post_init__(self):
        if self.transaction_countries is None:
            self.transaction_countries = [self.residence_country]


@dataclass
class RiskScore:
    """Complete risk assessment result."""
    total_score: int  # 1-30
    category: str  # LOW, MEDIUM, HIGH
    breakdown: dict[str, int]  # Detailed score by component (each 0-5)
    risk_drivers: list[str]  # Key factors contributing to risk
    required_actions: list[str]  # Compliance actions required
    calculation_sheet: list[str]  # Human-readable calculation breakdown


class RiskEngine:
    """
    Transparent risk scoring engine using 1-30 scale.
    Each category contributes 0-5 points for human readability.
    All calculations are explicit and auditable.
    """
    
    # Risk category thresholds (1-30 scale)
    THRESHOLD_LOW = 10      # 1-10: Standard Due Diligence
    THRESHOLD_MEDIUM = 20   # 11-20: Enhanced Monitoring
    THRESHOLD_HIGH = 30     # 21-30: Enhanced Due Diligence
    
    # High-risk sectors (cash-intensive or high-risk per FATF)
    HIGH_RISK_SECTORS = {
        "SALARY_EARNER": 1,
        "RETAIL": 1,
        "CONSULTANCY": 2,
        "SERVICES": 2,
        "NGO": 3,
        "EXPORT": 3,
        "IMPORT_EXPORT": 3,
        "LOGISTICS": 3,
        "GOLD_TRADING": 5,
        "CRYPTOCURRENCY": 5,
        "MONEY_TRANSFER": 5,
        "REAL_ESTATE": 4,
        "OIL_GAS": 5,
        "GAMING_BETTING": 5,
        "ART_ANTIQUITIES": 4,
        "PRECIOUS_METALS": 5,
        "CASH_INTENSIVE": 5
    }
    
    # FATF grey/black list countries (as of 2025)
    FATF_GREY_LIST = [
        "BULGARIA", "CAMEROON", "CROATIA", "VIETNAM", "TURKEY",
        "SOUTH_AFRICA", "UGANDA", "UAE", "SENEGAL", "MOZAMBIQUE"
    ]
    FATF_BLACK_LIST = ["IRAN", "NORTH_KOREA", "MYANMAR"]
    
    def calculate_risk(self, factors: RiskFactors) -> RiskScore:
        """
        Calculate risk score on 1-30 scale with transparent breakdown.
        Each category contributes 0-5 points.
        
        Args:
            factors: Risk calculation input factors
            
        Returns:
            RiskScore with total score and detailed breakdown
        """
        logger.info("Calculating risk score (1-30 scale)")
        
        # Calculate each category (0-5 points each)
        customer_score = self._calculate_customer_profile_risk(factors)
        geographic_score = self._calculate_geographic_risk(factors)
        business_score = self._calculate_business_sector_risk(factors)
        pep_score = self._calculate_pep_risk(factors)
        product_score = self._calculate_product_risk(factors)
        adverse_score = self._calculate_adverse_media_risk(factors)
        
        # Calculate total (max 30)
        total_score = (
            customer_score +
            geographic_score +
            business_score +
            pep_score +
            product_score +
            adverse_score
        )
        
        # Determine category
        category = self._determine_category(total_score)
        
        # Build calculation sheet for UI
        calculation_sheet = self._build_calculation_sheet(
            customer_score, geographic_score, business_score,
            pep_score, product_score, adverse_score, factors
        )
        
        # Identify risk drivers
        risk_drivers = self._identify_risk_drivers(
            factors, customer_score, geographic_score, business_score,
            pep_score, product_score, adverse_score
        )
        
        # Determine required actions
        required_actions = self._determine_actions(category, factors)
        
        breakdown = {
            "customer_profile": customer_score,
            "geographic_exposure": geographic_score,
            "business_sector": business_score,
            "pep_influence": pep_score,
            "product_relationship": product_score,
            "adverse_media": adverse_score,
            "total": total_score
        }
        
        logger.info(f"Risk calculation complete: {total_score}/30 ({category})")
        
        return RiskScore(
            total_score=total_score,
            category=category,
            breakdown=breakdown,
            risk_drivers=risk_drivers,
            required_actions=required_actions,
            calculation_sheet=calculation_sheet
        )
    
    def _calculate_customer_profile_risk(self, factors: RiskFactors) -> int:
        """
        Calculate customer profile risk (0-5 points).
        
        Scoring:
        - Nigerian individual: 1
        - Non-resident Nigerian: 2
        - Nigerian corporate: 3
        - Foreign-owned / complex structure: 5
        """
        score = 0
        
        if factors.customer_type == "INDIVIDUAL":
            # Nigerian individual
            if factors.nationality == "Nigeria" and factors.residence_country == "Nigeria":
                score = 1
            else:
                # Non-resident Nigerian
                score = 2
        elif factors.customer_type == "CORPORATE":
            score = 3  # Base for Nigerian corporate
            
            # Assess corporate structure complexity
            if factors.cac_entity_type:
                # Foreign-owned or complex structure indicators
                if factors.corporate_shareholders_count > 0:
                    corp_ratio = factors.corporate_shareholders_count / max(factors.shareholders_count, 1)
                    if corp_ratio >= 0.8:  # Mostly corporate shareholders
                        score = 5
                    elif corp_ratio >= 0.5:
                        score = 4
                
                # Additional complexity factors
                if factors.directors_count == 0 or factors.ubo_count == 0:
                    score = max(score, 5)  # Missing governance = complex/opaque
                elif factors.has_incomplete_ownership:
                    score = max(score, 4)  # Incomplete ownership = elevated risk
        elif factors.customer_type == "NGO":
            score = 3
        elif factors.customer_type == "GOVERNMENT":
            score = 2
        
        return min(score, 5)
    
    def _calculate_business_sector_risk(self, factors: RiskFactors) -> int:
        """
        Calculate business/sector risk (0-5 points).
        
        Scoring:
        - Salary earner/retail: 1
        - Consultancy/services: 2
        - NGO/export/logistics: 3
        - Cash-intensive (gold, oil, crypto): 5
        """
        if not factors.industry_sector:
            return 1  # Default low if not specified
        
        sector_score = self.HIGH_RISK_SECTORS.get(
            factors.industry_sector.upper(),
            2  # Default medium for unknown sectors
        )
        
        return min(sector_score, 5)
    
    def _calculate_pep_risk(self, factors: RiskFactors) -> int:
        """
        Calculate PEP/Influence risk (0-5 points).
        
        Scoring:
        - Not a PEP: 0
        - Domestic PEP: 3
        - Foreign PEP: 4
        - PEP + senior role: 5
        """
        if not factors.is_pep:
            return 0
        
        # Base PEP score
        if factors.nationality != "Nigeria":
            return 4  # Foreign PEP
        else:
            return 3  # Domestic PEP
        
        # Note: Senior role detection would require additional field in factors
    
    def _calculate_adverse_media_risk(self, factors: RiskFactors) -> int:
        """
        Calculate adverse media/watchlist risk (0-5 points).
        
        Scoring:
        - No adverse information: 0
        - Investigation/allegation: 3
        - Conviction/confirmed issue: 5
        
        Note: Sanctions matches bypass scoring and halt onboarding
        """
        # Currently no adverse media data in factors
        # This would be populated from watchlist screening
        return 0
    
    def _assess_corporate_structure_risk(self, factors: RiskFactors) -> int:
        """
        Assess risk based on corporate governance structure.
        Evaluates directors, shareholders, and ownership transparency.
        """
        score = 0
        
        # Director-related risks
        if factors.directors_count == 0:
            # No directors listed is highly suspicious
            score += 25
        elif factors.directors_count == 1:
            # Single director increases risk (less oversight)
            score += 10
        
        # Inactive/removed directors
        if factors.inactive_directors_count > 0:
            if factors.directors_count > 0:
                inactive_ratio = factors.inactive_directors_count / factors.directors_count
                if inactive_ratio > 0.5:  # More than 50% inactive
                    score += 20
                elif inactive_ratio > 0.3:  # More than 30% inactive
                    score += 10
        
        # Missing director contact information
        if factors.directors_missing_contacts > 0:
            if factors.directors_count > 0:
                missing_ratio = factors.directors_missing_contacts / factors.directors_count
                if missing_ratio > 0.7:  # More than 70% missing contacts
                    score += 15
                elif missing_ratio > 0.4:  # More than 40% missing contacts
                    score += 8
        
        # Shareholder-related risks
        if factors.shareholders_count == 0 and factors.cac_entity_type in ["LIMITED", "PLC"]:
            # Limited company with no shareholders is unusual
            score += 20
        
        # Corporate shareholders (potential shell companies)
        if factors.corporate_shareholders_count > 0:
            if factors.shareholders_count > 0:
                corporate_ratio = factors.corporate_shareholders_count / factors.shareholders_count
                if corporate_ratio == 1.0:  # All corporate shareholders
                    score += 20
                elif corporate_ratio > 0.5:  # More than 50% corporate
                    score += 15
                elif corporate_ratio > 0:
                    score += 5
        
        # Ownership concentration risk (very high concentration = control risk)
        if factors.ownership_concentration >= 90.0:
            score += 10
        elif factors.ownership_concentration >= 75.0:
            score += 5
        
        # Incomplete ownership structure
        if factors.has_incomplete_ownership:
            score += 15
        
        # UBO identification issues
        if factors.ubo_count == 0 and factors.cac_entity_type in ["LIMITED", "PLC"]:
            # No identified UBOs is a major red flag
            score += 25
        
        return min(score, 50)  # Cap at 50 to allow other factors
    
    def _calculate_geographic_risk(self, factors: RiskFactors) -> int:
        """
        Calculate geographic exposure risk (0-5 points).
        
        Scoring:
        - Nigeria only: 1
        - Cross-border exposure: 3
        - FATF high-risk jurisdiction: 5
        """
        score = 1  # Base: Nigeria only
        
        # Check if there's cross-border exposure
        has_cross_border = False
        if factors.nationality.upper() != "NIGERIA":
            has_cross_border = True
        if factors.residence_country.upper() != "NIGERIA":
            has_cross_border = True
        if any(c.upper() != "NIGERIA" for c in factors.transaction_countries):
            has_cross_border = True
        
        # FATF black list = auto high risk
        for location in [factors.nationality, factors.residence_country] + factors.transaction_countries:
            if location.upper() in self.FATF_BLACK_LIST:
                return 5
        
        # FATF grey list
        for location in [factors.nationality, factors.residence_country] + factors.transaction_countries:
            if location.upper() in self.FATF_GREY_LIST:
                return 5
        
        # Cross-border but not high-risk jurisdictions
        if has_cross_border:
            score = 3
        
        return min(score, 5)
    
    def _calculate_product_risk(self, factors: RiskFactors) -> int:
        """
        Calculate product/relationship risk (0-5 points).
        
        Scoring:
        - Basic account: 1
        - Corporate account: 2
        - High transaction limits: 4
        - Correspondent/nested exposure: 5
        """
        score = 1  # Base: basic account
        
        # Product type assessment
        if factors.customer_type == "CORPORATE":
            score = 2  # Corporate account
        
        # High transaction limits based on expected turnover
        if factors.expected_turnover > 10_000_000:  # >10M NGN/month
            score = 4
        elif factors.expected_turnover > 5_000_000:  # >5M NGN/month
            score = max(score, 3)
        
        # Cash intensity increases risk
        if factors.cash_intensity == "HIGH":
            score = min(score + 2, 5)
        elif factors.cash_intensity == "MEDIUM":
            score = min(score + 1, 5)
        
        return min(score, 5)
    
    def _build_calculation_sheet(
        self, customer_score: int, geographic_score: int, business_score: int,
        pep_score: int, product_score: int, adverse_score: int, factors: RiskFactors
    ) -> list[str]:
        """Build human-readable calculation breakdown for UI."""
        sheet = []
        
        if customer_score > 0:
            if factors.customer_type == "INDIVIDUAL":
                sheet.append(f"Customer Type (Individual): +{customer_score}")
            elif factors.customer_type == "CORPORATE":
                sheet.append(f"Customer Type (Corporate): +{customer_score}")
            elif factors.customer_type == "NGO":
                sheet.append(f"Customer Type (NGO): +{customer_score}")
        
        if geographic_score > 0:
            if geographic_score >= 5:
                sheet.append(f"Geographic Exposure (High-risk jurisdiction): +{geographic_score}")
            elif geographic_score >= 3:
                sheet.append(f"Geographic Exposure (Cross-border): +{geographic_score}")
            else:
                sheet.append(f"Geographic Exposure (Nigeria only): +{geographic_score}")
        
        if business_score > 0:
            sector = factors.industry_sector or "Unspecified"
            sheet.append(f"Business Sector ({sector}): +{business_score}")
        
        if pep_score > 0:
            sheet.append(f"PEP Status: +{pep_score}")
        
        if product_score > 0:
            if factors.customer_type == "CORPORATE":
                sheet.append(f"Product Type (Corporate Account): +{product_score}")
            else:
                sheet.append(f"Product Type (Basic Account): +{product_score}")
        
        if adverse_score > 0:
            sheet.append(f"Adverse Media/Watchlist: +{adverse_score}")
        
        total = customer_score + geographic_score + business_score + pep_score + product_score + adverse_score
        sheet.append("-" * 40)
        sheet.append(f"Total Risk Score: {total}/30")
        
        return sheet
    
        return sheet
    
    def _determine_category(self, score: int) -> str:
        """
        Determine risk category from score (1-30 scale).
        
        1-10: Low Risk (Standard Due Diligence)
        11-20: Medium Risk (Enhanced Monitoring)
        21-30: High Risk (Enhanced Due Diligence)
        """
        if score <= self.THRESHOLD_LOW:
            return "LOW"
        elif score <= self.THRESHOLD_MEDIUM:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _identify_risk_drivers(
        self,
        factors: RiskFactors,
        customer_score: int,
        geographic_score: int,
        business_score: int,
        pep_score: int,
        product_score: int,
        adverse_score: int
    ) -> list[str]:
        """Identify key risk drivers for explanation."""
        drivers = []
        
        # PEP is always a key driver if present
        if pep_score > 0:
            drivers.append(f"Politically Exposed Person (PEP) - Score: {pep_score}/5")
        
        # Geographic risks
        if geographic_score >= 5:
            drivers.append(f"High-risk jurisdiction exposure - Score: {geographic_score}/5")
        elif geographic_score >= 3:
            drivers.append(f"Cross-border operations - Score: {geographic_score}/5")
        
        # Business sector risks
        if business_score >= 5:
            sector = factors.industry_sector or "Unspecified"
            drivers.append(f"Cash-intensive sector ({sector}) - Score: {business_score}/5")
        elif business_score >= 3:
            sector = factors.industry_sector or "Unspecified"
            drivers.append(f"Elevated-risk sector ({sector}) - Score: {business_score}/5")
        
        # Corporate structure risks
        if factors.customer_type == "CORPORATE" and customer_score >= 4:
            if factors.corporate_shareholders_count > 0:
                corp_ratio = factors.corporate_shareholders_count / max(factors.shareholders_count, 1)
                if corp_ratio >= 0.5:
                    drivers.append(f"Complex corporate structure - Score: {customer_score}/5")
            
            if factors.directors_count == 0 or factors.ubo_count == 0:
                drivers.append(f"Missing governance information - Score: {customer_score}/5")
            elif factors.inactive_directors_count > 0:
                inactive_ratio = factors.inactive_directors_count / max(factors.directors_count, 1)
                if inactive_ratio > 0.5:
                    drivers.append(f"High proportion of inactive directors ({inactive_ratio*100:.0f}%) - Score: {customer_score}/5")
            
            if factors.directors_missing_contacts > 0:
                missing_ratio = factors.directors_missing_contacts / max(factors.directors_count, 1)
                if missing_ratio > 0.4:
                    drivers.append(f"Missing director contacts ({missing_ratio*100:.0f}%) - Score: {customer_score}/5")
        
        # Product/relationship risks
        if product_score >= 4:
            if factors.expected_turnover > 10_000_000:
                drivers.append(f"High transaction volume (NGN {factors.expected_turnover:,}/month) - Score: {product_score}/5")
            if factors.cash_intensity == "HIGH":
                drivers.append(f"High cash intensity - Score: {product_score}/5")
        
        # Adverse media
        if adverse_score > 0:
            drivers.append(f"Adverse media/watchlist findings - Score: {adverse_score}/5")
        
        return drivers if drivers else ["Standard risk profile"]
    
    def _determine_actions(self, category: str, factors: RiskFactors) -> list[str]:
        """
        Determine required compliance actions based on risk category (1-30 scale).
        
        Low (1-10): Standard Due Diligence
        Medium (11-20): Enhanced Monitoring
        High (21-30): Enhanced Due Diligence
        """
        actions = []
        
        if category == "HIGH":
            actions.append("Enhanced Due Diligence (EDD) mandatory")
            actions.append("Maker + Checker + Approver approval required")
            actions.append("Source of wealth and source of funds documentation required")
            actions.append("Quarterly account review")
            actions.append("Enhanced transaction monitoring")
            actions.append("Senior management approval (Zonal Head)")
        elif category == "MEDIUM":
            actions.append("Enhanced Monitoring required")
            actions.append("Maker + Checker approval required")
            actions.append("Bi-annual account review")
            actions.append("Periodic transaction monitoring")
        else:  # LOW
            actions.append("Standard Due Diligence (SDD)")
            actions.append("Maker approval only")
            actions.append("Annual account review")
        
        if factors.is_pep:
            actions.append("PEP approval workflow mandatory")
            actions.append("Ongoing PEP status monitoring")
        
        return actions

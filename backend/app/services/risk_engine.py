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
    total_score: int  # 0-100
    category: str  # LOW, MEDIUM, HIGH, PROHIBITED
    breakdown: dict[str, int]  # Detailed score by component
    risk_drivers: list[str]  # Key factors contributing to risk
    required_actions: list[str]  # Compliance actions required


class RiskEngine:
    """
    Transparent risk scoring engine with weighted factors.
    All calculations are explicit and auditable.
    """
    
    # Risk category thresholds
    THRESHOLD_LOW = 30
    THRESHOLD_MEDIUM = 60
    THRESHOLD_HIGH = 100
    
    # Component weights (must sum to 1.0)
    WEIGHT_CUSTOMER = 0.35
    WEIGHT_GEOGRAPHIC = 0.25
    WEIGHT_PRODUCT = 0.20
    WEIGHT_CHANNEL = 0.20
    
    # High-risk sectors (cash-intensive or high-risk per FATF)
    HIGH_RISK_SECTORS = {
        "GOLD_TRADING": 30,
        "CRYPTOCURRENCY": 40,
        "MONEY_TRANSFER": 35,
        "REAL_ESTATE": 25,
        "OIL_GAS": 20,
        "CONSULTING": 15,
        "IMPORT_EXPORT": 20,
        "GAMING_BETTING": 30,
        "ART_ANTIQUITIES": 25,
        "PRECIOUS_METALS": 30
    }
    
    # FATF grey/black list countries (as of 2025)
    FATF_GREY_LIST = [
        "BULGARIA", "CAMEROON", "CROATIA", "VIETNAM", "TURKEY",
        "SOUTH_AFRICA", "UGANDA", "UAE", "SENEGAL", "MOZAMBIQUE"
    ]
    FATF_BLACK_LIST = ["IRAN", "NORTH_KOREA", "MYANMAR"]
    
    def calculate_risk(self, factors: RiskFactors) -> RiskScore:
        """
        Calculate risk score with transparent breakdown.
        
        Args:
            factors: Risk calculation input factors
            
        Returns:
            RiskScore with total score and detailed breakdown
        """
        logger.info("Calculating risk score")
        
        # Calculate each component
        customer_score = self._calculate_customer_risk(factors)
        geographic_score = self._calculate_geographic_risk(factors)
        product_score = self._calculate_product_risk(factors)
        channel_score = self._calculate_channel_risk(factors)
        
        # Apply weights
        weighted_customer = int(customer_score * self.WEIGHT_CUSTOMER)
        weighted_geographic = int(geographic_score * self.WEIGHT_GEOGRAPHIC)
        weighted_product = int(product_score * self.WEIGHT_PRODUCT)
        weighted_channel = int(channel_score * self.WEIGHT_CHANNEL)
        
        # Calculate total
        total_score = (
            weighted_customer +
            weighted_geographic +
            weighted_product +
            weighted_channel
        )
        
        # Determine category
        category = self._determine_category(total_score)
        
        # Identify risk drivers
        risk_drivers = self._identify_risk_drivers(
            factors,
            customer_score,
            geographic_score,
            product_score,
            channel_score
        )
        
        # Determine required actions
        required_actions = self._determine_actions(category, factors)
        
        breakdown = {
            "customer_risk": weighted_customer,
            "customer_risk_raw": customer_score,
            "geographic_risk": weighted_geographic,
            "geographic_risk_raw": geographic_score,
            "product_risk": weighted_product,
            "product_risk_raw": product_score,
            "channel_risk": weighted_channel,
            "channel_risk_raw": channel_score
        }
        
        logger.info(f"Risk calculation complete: {total_score}/100 ({category})")
        
        return RiskScore(
            total_score=total_score,
            category=category,
            breakdown=breakdown,
            risk_drivers=risk_drivers,
            required_actions=required_actions
        )
    
    def _calculate_customer_risk(self, factors: RiskFactors) -> int:
        """Calculate customer risk component (0-100)."""
        score = 0
        
        # Base score by customer type
        if factors.customer_type == "INDIVIDUAL":
            score += 0
        elif factors.customer_type == "CORPORATE":
            score += 10
        elif factors.customer_type == "NGO":
            score += 15
        elif factors.customer_type == "GOVERNMENT":
            score += 5
        
        # PEP status (automatic high risk)
        if factors.is_pep:
            score += 50
        
        # Industry sector risk
        if factors.industry_sector:
            sector_risk = self.HIGH_RISK_SECTORS.get(
                factors.industry_sector.upper(),
                0
            )
            score += sector_risk
        
        # Source of funds clarity
        if factors.source_of_funds_clarity == "UNCLEAR":
            score += 15
        elif factors.source_of_funds_clarity == "SUSPICIOUS":
            score += 40
        
        return min(score, 100)
    
    def _calculate_geographic_risk(self, factors: RiskFactors) -> int:
        """Calculate geographic risk component (0-100)."""
        score = 0
        
        # Nationality risk
        nationality_upper = factors.nationality.upper()
        if nationality_upper in self.FATF_BLACK_LIST:
            return 100  # Auto-prohibit
        if nationality_upper in self.FATF_GREY_LIST:
            score += 30
        elif nationality_upper != "NIGERIA":
            score += 10
        
        # Residence country risk
        residence_upper = factors.residence_country.upper()
        if residence_upper in self.FATF_BLACK_LIST:
            return 100
        if residence_upper in self.FATF_GREY_LIST:
            score += 20
        elif residence_upper != "NIGERIA":
            score += 10
        
        # Transaction countries risk
        for country in factors.transaction_countries:
            country_upper = country.upper()
            if country_upper in self.FATF_BLACK_LIST:
                return 100
            if country_upper in self.FATF_GREY_LIST:
                score += 15
                break  # Don't stack penalties
        
        return min(score, 100)
    
    def _calculate_product_risk(self, factors: RiskFactors) -> int:
        """Calculate product/service risk component (0-100)."""
        score = 0
        
        # Product type risk
        product_risks = {
            "CURRENT_ACCOUNT": 0,
            "SAVINGS_ACCOUNT": 0,
            "INTERNATIONAL_TRANSFERS": 20,
            "PRIVATE_BANKING": 30,
            "CASH_MANAGEMENT": 25,
            "TRADE_FINANCE": 15
        }
        score += product_risks.get(factors.product_type, 10)
        
        # Expected turnover risk
        if factors.expected_turnover > 10_000_000:  # >10M NGN/month
            score += 25
        elif factors.expected_turnover > 5_000_000:  # >5M NGN/month
            score += 15
        elif factors.expected_turnover > 1_000_000:  # >1M NGN/month
            score += 5
        
        # Cash intensity
        if factors.cash_intensity == "HIGH":
            score += 30
        elif factors.cash_intensity == "MEDIUM":
            score += 15
        
        return min(score, 100)
    
    def _calculate_channel_risk(self, factors: RiskFactors) -> int:
        """Calculate delivery channel risk component (0-100)."""
        score = 0
        
        # Onboarding channel risk
        channel_risks = {
            "IN_PERSON": 0,
            "REMOTE": 20,
            "INTERMEDIARY": 30,
            "DIGITAL_ONLY": 25
        }
        score += channel_risks.get(factors.onboarding_channel, 15)
        
        return min(score, 100)
    
    def _determine_category(self, score: int) -> str:
        """Determine risk category from score."""
        if score >= 90:
            return "PROHIBITED"
        elif score >= self.THRESHOLD_MEDIUM:
            return "HIGH"
        elif score >= self.THRESHOLD_LOW:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _identify_risk_drivers(
        self,
        factors: RiskFactors,
        customer_score: int,
        geographic_score: int,
        product_score: int,
        channel_score: int
    ) -> list[str]:
        """Identify key risk drivers for explanation."""
        drivers = []
        
        if factors.is_pep:
            drivers.append("Politically Exposed Person (PEP)")
        
        if customer_score >= 30:
            if factors.industry_sector in self.HIGH_RISK_SECTORS:
                drivers.append(f"High-risk sector: {factors.industry_sector}")
        
        if geographic_score >= 20:
            if factors.nationality.upper() in self.FATF_GREY_LIST:
                drivers.append(f"FATF grey-list nationality: {factors.nationality}")
            if factors.residence_country.upper() in self.FATF_GREY_LIST:
                drivers.append(f"FATF grey-list residence: {factors.residence_country}")
        
        if product_score >= 25:
            if factors.cash_intensity == "HIGH":
                drivers.append("High cash intensity")
            if factors.expected_turnover > 10_000_000:
                drivers.append(f"High expected turnover: NGN {factors.expected_turnover:,}/month")
        
        if channel_score >= 20:
            if factors.onboarding_channel != "IN_PERSON":
                drivers.append(f"Remote onboarding: {factors.onboarding_channel}")
        
        return drivers if drivers else ["Standard risk profile"]
    
    def _determine_actions(self, category: str, factors: RiskFactors) -> list[str]:
        """Determine required compliance actions based on risk category."""
        actions = []
        
        if category == "PROHIBITED":
            actions.append("Account opening PROHIBITED - do not proceed")
            actions.append("Report to MLRO immediately")
            return actions
        
        if category == "HIGH":
            actions.append("Enhanced Due Diligence (EDD) mandatory")
            actions.append("Senior management approval required (Zonal Head)")
            actions.append("Source of wealth and source of funds documentation required")
            actions.append("Quarterly account review")
            actions.append("Enhanced transaction monitoring")
        elif category == "MEDIUM":
            actions.append("Standard Customer Due Diligence (CDD)")
            actions.append("Branch Head approval required")
            actions.append("Bi-annual account review")
        else:  # LOW
            actions.append("Simplified Due Diligence permitted")
            actions.append("Annual account review")
        
        if factors.is_pep:
            actions.append("PEP approval workflow mandatory")
            actions.append("Ongoing PEP status monitoring")
        
        return actions

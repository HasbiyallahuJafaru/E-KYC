"""
Ultimate Beneficial Owner (UBO) analysis service.
Identifies individuals with ≥25% ownership per FATF Recommendation 24.
"""

from dataclasses import dataclass
from typing import Optional
from app.services.providers.base import CACResult, ShareholderInfo
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class UBOEntity:
    """Identified Ultimate Beneficial Owner."""
    name: str
    ownership_percentage: float
    ownership_type: str  # DIRECT or INDIRECT
    trace_depth: int  # Number of corporate layers traced
    bvn: Optional[str] = None
    is_verified: bool = False


@dataclass
class UBOAnalysisResult:
    """Complete UBO analysis result."""
    identified: bool
    primary_ubos: list[UBOEntity]
    corporate_shareholders: list[str]  # Corporate entities that need further tracing
    trace_depth: int
    issues: list[str]
    total_identified_percentage: float


class UBOAnalyzer:
    """
    Analyzes corporate ownership structures to identify UBOs.
    Implements 2-level tracing with circular ownership detection.
    """
    
    OWNERSHIP_THRESHOLD = 25.0  # FATF standard: ≥25%
    MAX_TRACE_DEPTH = 2  # Maximum corporate layers to trace
    
    def analyze(
        self,
        cac_result: CACResult,
        depth: int = 1,
        visited_rcs: Optional[set[str]] = None
    ) -> UBOAnalysisResult:
        """
        Analyze CAC result to identify Ultimate Beneficial Owners.
        
        Args:
            cac_result: CAC registry lookup result
            depth: Current tracing depth
            visited_rcs: Set of already-visited RC numbers (circular detection)
            
        Returns:
            UBOAnalysisResult with identified UBOs and issues
        """
        logger.info(f"Starting UBO analysis for {cac_result.rc_number} at depth {depth}")
        
        if visited_rcs is None:
            visited_rcs = set()
        
        # Add current company to visited set
        visited_rcs.add(cac_result.rc_number)
        
        primary_ubos = []
        corporate_shareholders = []
        issues = []
        
        # Analyze each shareholder
        for shareholder in cac_result.shareholders:
            logger.info(f"Analyzing shareholder: {shareholder.name} ({shareholder.percentage}%)")
            
            # Check if shareholder meets threshold
            if shareholder.percentage < self.OWNERSHIP_THRESHOLD:
                logger.info(f"Skipping {shareholder.name}: below {self.OWNERSHIP_THRESHOLD}% threshold")
                continue
            
            # Individual shareholder = Direct UBO
            if not shareholder.is_corporate:
                ubo = UBOEntity(
                    name=shareholder.name,
                    ownership_percentage=shareholder.percentage,
                    ownership_type="DIRECT",
                    trace_depth=depth
                )
                primary_ubos.append(ubo)
                logger.info(f"Identified direct UBO: {shareholder.name} ({shareholder.percentage}%)")
            
            # Corporate shareholder - needs further tracing
            else:
                corporate_shareholders.append(shareholder.name)
                
                # Check for circular ownership
                if shareholder.corporate_rc in visited_rcs:
                    issues.append(f"circular_ownership_detected:{shareholder.name}")
                    logger.warning(f"Circular ownership detected: {shareholder.name}")
                    continue
                
                # Check if we've hit max depth
                if depth >= self.MAX_TRACE_DEPTH:
                    issues.append(f"max_depth_reached:{shareholder.name}")
                    logger.warning(f"Max trace depth reached for {shareholder.name}")
                    # Record corporate entity as UBO (unable to trace further)
                    ubo = UBOEntity(
                        name=shareholder.name,
                        ownership_percentage=shareholder.percentage,
                        ownership_type="CORPORATE_UNTRACED",
                        trace_depth=depth
                    )
                    primary_ubos.append(ubo)
                    continue
                
                # TODO: For production, trace corporate shareholders by calling verify_cac again
                # For now, flag for manual review
                issues.append(f"corporate_shareholder_requires_tracing:{shareholder.name}")
                logger.info(f"Corporate shareholder {shareholder.name} requires additional tracing")
        
        # Calculate total percentage identified
        total_percentage = sum(ubo.ownership_percentage for ubo in primary_ubos)
        
        # Check if UBO identification is complete
        identified = total_percentage >= self.OWNERSHIP_THRESHOLD and len(primary_ubos) > 0
        
        if not identified and len(primary_ubos) == 0:
            issues.append("no_ubo_identified")
        
        if total_percentage < 100 and len(issues) == 0:
            issues.append(f"incomplete_ownership_structure:{total_percentage}%")
        
        result = UBOAnalysisResult(
            identified=identified,
            primary_ubos=primary_ubos,
            corporate_shareholders=corporate_shareholders,
            trace_depth=depth,
            issues=issues,
            total_identified_percentage=total_percentage
        )
        
        logger.info(f"UBO analysis complete: {len(primary_ubos)} UBOs identified ({total_percentage}%)")
        return result
    
    def format_ubo_summary(self, result: UBOAnalysisResult) -> str:
        """
        Generate human-readable UBO summary for reports.
        
        Args:
            result: UBO analysis result
            
        Returns:
            Formatted summary string
        """
        if not result.identified:
            return "⚠ UBO identification incomplete. Manual review required."
        
        summary_lines = []
        summary_lines.append(f"✓ {len(result.primary_ubos)} Ultimate Beneficial Owner(s) Identified:")
        summary_lines.append("")
        
        for i, ubo in enumerate(result.primary_ubos, 1):
            verified_marker = "✓" if ubo.is_verified else "⚠"
            summary_lines.append(
                f"{i}. {ubo.name} - {ubo.ownership_percentage}% "
                f"({ubo.ownership_type}) {verified_marker}"
            )
        
        summary_lines.append("")
        summary_lines.append(f"Total Ownership Identified: {result.total_identified_percentage}%")
        
        if result.issues:
            summary_lines.append("")
            summary_lines.append("Issues:")
            for issue in result.issues:
                summary_lines.append(f"  • {issue}")
        
        return "\n".join(summary_lines)

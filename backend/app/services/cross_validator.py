"""
Cross-validation service for reconciling BVN and NIN data.
Implements transparent name matching logic per PRD requirements.
"""

from dataclasses import dataclass
from typing import Optional
from app.services.providers.base import BVNResult, NINResult
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Cross-validation result with confidence scoring."""
    overall_match: bool
    confidence: int  # 0-100
    name_match: bool
    dob_match: bool
    issues: list[str]
    bvn_format: str
    nin_format: str
    normalized_format: str
    explanation: str


class CrossValidator:
    """
    Validates consistency between BVN and NIN records.
    Uses explicit, transparent logic for regulatory explainability.
    """
    
    def validate(self, bvn_result: BVNResult, nin_result: NINResult) -> ValidationResult:
        """
        Cross-validate BVN and NIN data for consistency.
        
        Args:
            bvn_result: BVN verification result
            nin_result: NIN verification result
            
        Returns:
            ValidationResult with match status and confidence score
        """
        logger.info("Starting BVN/NIN cross-validation")
        
        issues = []
        
        # Validate DOB (exact match required)
        dob_match = self._validate_dob(
            bvn_result.date_of_birth,
            nin_result.date_of_birth
        )
        
        if not dob_match:
            issues.append("dob_mismatch")
        
        # Validate names (intelligent matching)
        name_result = self._validate_names(
            bvn_result.full_name,
            nin_result.full_name
        )
        
        name_match = name_result["match"]
        confidence = name_result["confidence"]
        
        if not name_match:
            issues.append(name_result["issue_type"])
        
        # Calculate overall match
        overall_match = dob_match and name_match
        
        # Generate human-readable explanation
        explanation = self._generate_explanation(
            name_match, dob_match, name_result, issues
        )
        
        return ValidationResult(
            overall_match=overall_match,
            confidence=confidence,
            name_match=name_match,
            dob_match=dob_match,
            issues=issues,
            bvn_format=bvn_result.full_name,
            nin_format=nin_result.full_name,
            normalized_format=name_result["normalized"],
            explanation=explanation
        )
    
    def _validate_dob(
        self,
        bvn_dob: Optional[str],
        nin_dob: Optional[str]
    ) -> bool:
        """
        Validate date of birth exact match.
        
        Args:
            bvn_dob: DOB from BVN (YYYY-MM-DD format)
            nin_dob: DOB from NIN (YYYY-MM-DD format)
            
        Returns:
            True if DOBs match exactly
        """
        if not bvn_dob or not nin_dob:
            logger.warning("Missing DOB in BVN or NIN result")
            return False
        
        # Normalize formats (handle different date formats)
        bvn_normalized = bvn_dob.strip()
        nin_normalized = nin_dob.strip()
        
        match = bvn_normalized == nin_normalized
        
        logger.info(f"DOB validation: BVN={bvn_dob}, NIN={nin_dob}, Match={match}")
        return match
    
    def _validate_names(
        self,
        bvn_name: str,
        nin_name: str
    ) -> dict:
        """
        Validate names with intelligent matching.
        Handles surname-first vs first-name-first variations.
        
        Args:
            bvn_name: Full name from BVN
            nin_name: Full name from NIN
            
        Returns:
            Dict with match status, confidence, and details
        """
        if not bvn_name or not nin_name:
            return {
                "match": False,
                "confidence": 0,
                "issue_type": "missing_name",
                "normalized": ""
            }
        
        # Detect surname-first pattern (comma or ALL CAPS surname)
        bvn_surname_first = self._is_surname_first(bvn_name)
        nin_surname_first = self._is_surname_first(nin_name)
        
        # Normalize both names to "Firstname Middlename Lastname" format
        bvn_normalized = self._normalize_name(bvn_name, bvn_surname_first)
        nin_normalized = self._normalize_name(nin_name, nin_surname_first)
        
        logger.info(f"Name normalization: BVN='{bvn_normalized}', NIN='{nin_normalized}'")
        
        # Tokenize and sort for comparison
        bvn_tokens = set(self._tokenize_name(bvn_normalized))
        nin_tokens = set(self._tokenize_name(nin_normalized))
        
        # Calculate match confidence
        if bvn_tokens == nin_tokens:
            # Perfect match
            return {
                "match": True,
                "confidence": 100,
                "issue_type": None,
                "normalized": bvn_normalized
            }
        
        # Check for subset matches (middle name differences)
        common_tokens = bvn_tokens & nin_tokens
        total_tokens = bvn_tokens | nin_tokens
        
        if len(common_tokens) >= 2 and len(total_tokens) == len(common_tokens) + 1:
            # Likely middle name variation (e.g., "John Paul Obi" vs "John Obi")
            return {
                "match": True,
                "confidence": 95,
                "issue_type": "middle_name_variation",
                "normalized": bvn_normalized
            }
        
        # Calculate Levenshtein distance for typos
        distance = self._levenshtein_distance(bvn_normalized, nin_normalized)
        
        if distance <= 2:
            return {
                "match": True,
                "confidence": 90,
                "issue_type": "minor_typo",
                "normalized": bvn_normalized
            }
        
        if distance <= 3:
            return {
                "match": True,
                "confidence": 85,
                "issue_type": "possible_typo",
                "normalized": bvn_normalized
            }
        
        # Names don't match
        return {
            "match": False,
            "confidence": 0,
            "issue_type": "name_mismatch",
            "normalized": bvn_normalized
        }
    
    def _is_surname_first(self, name: str) -> bool:
        """
        Detect if name is in surname-first format.
        
        Args:
            name: Full name string
            
        Returns:
            True if surname appears first
        """
        # Check for comma (clear indicator: "SURNAME, Firstname")
        if "," in name:
            return True
        
        # Check if first word is all uppercase (common pattern: "SURNAME Firstname Middlename")
        tokens = name.split()
        if tokens and tokens[0].isupper() and len(tokens[0]) > 2:
            # Check if other tokens are not all uppercase
            if len(tokens) > 1 and not tokens[1].isupper():
                return True
        
        return False
    
    def _normalize_name(self, name: str, surname_first: bool) -> str:
        """
        Normalize name to "Firstname Middlename Lastname" format.
        
        Args:
            name: Original name string
            surname_first: Whether surname appears first
            
        Returns:
            Normalized name string
        """
        # Remove punctuation and extra spaces
        clean_name = name.replace(",", "").strip()
        clean_name = " ".join(clean_name.split())  # Normalize whitespace
        
        # Convert to title case for consistent comparison
        clean_name = clean_name.title()
        
        if not surname_first:
            return clean_name
        
        # Rearrange from "Surname Firstname Middlename" to "Firstname Middlename Surname"
        tokens = clean_name.split()
        if len(tokens) < 2:
            return clean_name
        
        # Move first token (surname) to end
        surname = tokens[0]
        given_names = tokens[1:]
        
        return " ".join(given_names + [surname])
    
    def _tokenize_name(self, name: str) -> list[str]:
        """
        Tokenize name into individual components, sorted alphabetically.
        
        Args:
            name: Normalized name string
            
        Returns:
            List of name tokens, sorted
        """
        tokens = name.split()
        # Sort alphabetically for order-independent comparison
        return sorted([t.lower() for t in tokens if len(t) > 1])
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance between two strings.
        Measures minimum edit operations needed to transform s1 to s2.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Edit distance (integer)
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _generate_explanation(
        self,
        name_match: bool,
        dob_match: bool,
        name_result: dict,
        issues: list[str]
    ) -> str:
        """
        Generate human-readable explanation of validation results.
        
        Args:
            name_match: Whether names match
            dob_match: Whether DOBs match
            name_result: Name validation details
            issues: List of identified issues
            
        Returns:
            Explanation string for display
        """
        if name_match and dob_match:
            if name_result["confidence"] == 100:
                return "✓ Perfect match: All fields match exactly."
            elif name_result["issue_type"] == "middle_name_variation":
                return f"✓ Match confirmed ({name_result['confidence']}% confidence): Names match with minor middle name variation."
            elif name_result["issue_type"] == "minor_typo":
                return f"✓ Match confirmed ({name_result['confidence']}% confidence): Names match with minor spelling variation."
            else:
                return f"✓ Match confirmed ({name_result['confidence']}% confidence)."
        
        if not dob_match and not name_match:
            return "✗ No match: Both name and date of birth differ significantly. Possible identity mismatch."
        
        if not dob_match:
            return "⚠ Partial match: Names match but date of birth differs. Requires manual review."
        
        if not name_match:
            return "⚠ Partial match: Date of birth matches but names differ. May indicate name change or data entry error."
        
        return "Validation incomplete."

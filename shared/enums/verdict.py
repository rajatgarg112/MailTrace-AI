"""
shared/enums/verdict.py
─────────────────────────────────────────────────────────────────────────────
Canonical Verdict enum — represents a module-level assessment of threat
severity, used by both the Security Engine (Member 4) and ML Engine
(Member 5) as a common vocabulary.
─────────────────────────────────────────────────────────────────────────────
"""

from enum import Enum
from typing import List


class Verdict(str, Enum):
    """
    Threat severity assessment produced by individual analysis modules.

    Used by Security Engine signals and ML predictions.
    NOT to be confused with RiskDecision (the final gateway action).
    """

    SAFE = "SAFE"
    """No threat indicators detected."""

    SUSPICIOUS = "SUSPICIOUS"
    """Moderate risk — some threat signals present, not conclusive."""

    MALICIOUS = "MALICIOUS"
    """High confidence threat — strong attack indicators present."""

    UNKNOWN = "UNKNOWN"
    """Insufficient data to determine a verdict — safe fallback."""

    @classmethod
    def list_values(cls) -> List[str]:
        return [v.value for v in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls._value2member_map_

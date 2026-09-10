"""
shared/enums/decision.py
─────────────────────────────────────────────────────────────────────────────
Risk Engine delivery-decision enum.

Every final decision emitted by the Risk Engine MUST be one of these values.
─────────────────────────────────────────────────────────────────────────────
"""

from enum import Enum
from typing import List


class RiskDecision(str, Enum):
    """
    Final delivery verdict produced by the MailTrace Risk Engine.

    These values are a strict subset of EmailStatus terminal states.
    """

    DELIVERED = "DELIVERED"
    """Email is clean — deliver to inbox."""

    WARNING = "WARNING"
    """Email is suspicious — deliver with a security warning badge."""

    QUARANTINED = "QUARANTINED"
    """Email is dangerous — move to quarantine."""

    REJECTED = "REJECTED"
    """Email is confirmed malicious — reject outright."""

    FAILED = "FAILED"
    """Risk engine encountered an unrecoverable error."""

    @classmethod
    def list_values(cls) -> List[str]:
        return [d.value for d in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls._value2member_map_

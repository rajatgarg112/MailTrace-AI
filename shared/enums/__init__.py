"""
shared/enums/__init__.py
Convenience re-exports for the shared enums package.
"""

from shared.enums.email_status import EmailStatus, DEFAULT_EMAIL_STATUS
from shared.enums.decision import RiskDecision
from shared.enums.verdict import Verdict

__all__ = [
    "EmailStatus",
    "DEFAULT_EMAIL_STATUS",
    "RiskDecision",
    "Verdict",
]

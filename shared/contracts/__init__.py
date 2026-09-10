"""
shared/contracts/__init__.py
Convenience re-exports for the shared contracts package.
"""

from shared.contracts.email_contract import EmailContract, AttachmentContract
from shared.contracts.security_result import SecurityResultContract, SecuritySignal
from shared.contracts.ml_result import MLResultContract
from shared.contracts.risk_decision import RiskDecisionContract
from shared.contracts.email_event import EmailEventContract

__all__ = [
    # Email
    "EmailContract",
    "AttachmentContract",
    # Security
    "SecurityResultContract",
    "SecuritySignal",
    # ML
    "MLResultContract",
    # Risk
    "RiskDecisionContract",
    # Events
    "EmailEventContract",
]

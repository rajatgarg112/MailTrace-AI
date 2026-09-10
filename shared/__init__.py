"""
shared/__init__.py
Top-level shared package for MailTrace AI.

Quick-import everything from one place:

    from shared import EmailStatus, EmailContract, SecurityResultContract, MLResultContract
    from shared import RiskDecisionContract, EmailEventContract
    from shared import RISK_THRESHOLD_QUARANTINE
"""

from shared.enums import EmailStatus, DEFAULT_EMAIL_STATUS, RiskDecision, Verdict
from shared.contracts import (
    EmailContract,
    AttachmentContract,
    SecurityResultContract,
    SecuritySignal,
    MLResultContract,
    RiskDecisionContract,
    EmailEventContract,
)
from shared.constants import (
    RISK_SCORE_MIN,
    RISK_SCORE_MAX,
    RISK_THRESHOLD_WARNING,
    RISK_THRESHOLD_QUARANTINE,
    RISK_THRESHOLD_REJECT,
    ML_CONFIDENCE_HIGH,
    ML_CONFIDENCE_LOW,
    SOURCE_SECURITY,
    SOURCE_ML,
    SOURCE_RISK,
    PHASE,
    IS_MOCK_MODE,
)

__all__ = [
    # Enums
    "EmailStatus",
    "DEFAULT_EMAIL_STATUS",
    "RiskDecision",
    "Verdict",
    # Contracts
    "EmailContract",
    "AttachmentContract",
    "SecurityResultContract",
    "SecuritySignal",
    "MLResultContract",
    "RiskDecisionContract",
    "EmailEventContract",
    # Constants
    "RISK_SCORE_MIN",
    "RISK_SCORE_MAX",
    "RISK_THRESHOLD_WARNING",
    "RISK_THRESHOLD_QUARANTINE",
    "RISK_THRESHOLD_REJECT",
    "ML_CONFIDENCE_HIGH",
    "ML_CONFIDENCE_LOW",
    "SOURCE_SECURITY",
    "SOURCE_ML",
    "SOURCE_RISK",
    "PHASE",
    "IS_MOCK_MODE",
]

"""
MailTrace AI Security & Forensics Analysis Modules
"""

from backend.analysis.header_forensics import HeaderForensics, HeaderAnalysisResult
from backend.analysis.authentication import AuthenticationAnalyzer, AuthenticationResult, AuthStatus
from backend.analysis.evidence_preservation import EvidencePreserver, EvidenceDossier
from backend.analysis.pii_redaction import PIIRedactor, PIIRedactionResult
from backend.analysis.security_policy import SecurityPolicyEngine, PolicyDecision, RiskLevel, DeliveryAction

__all__ = [
    "HeaderForensics",
    "HeaderAnalysisResult",
    "AuthenticationAnalyzer",
    "AuthenticationResult",
    "AuthStatus",
    "EvidencePreserver",
    "EvidenceDossier",
    "PIIRedactor",
    "PIIRedactionResult",
    "SecurityPolicyEngine",
    "PolicyDecision",
    "RiskLevel",
    "DeliveryAction",
]

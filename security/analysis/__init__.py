"""
MailTrace AI Security & Forensics Analysis Modules
"""

from security.analysis.header_forensics import HeaderForensics, HeaderAnalysisResult
from security.analysis.authentication import AuthenticationAnalyzer, AuthenticationResult, AuthStatus
from security.analysis.evidence_preservation import EvidencePreserver, EvidenceDossier
from security.analysis.pii_redaction import PIIRedactor, PIIRedactionResult
from security.analysis.security_policy import SecurityPolicyEngine, PolicyDecision, RiskLevel, DeliveryAction

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

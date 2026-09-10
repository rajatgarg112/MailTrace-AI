"""
MailTrace AI — Pre-Delivery Security Policy Engine

Evaluates forensic header anomalies, cryptographic authentication status, PII findings,
URL analysis, attachment inspection, NLP threat signals, and evidence preservation integrity
to compute final risk scores, risk levels, and deterministic delivery policies (DELIVER, WARN, QUARANTINE, REJECT, HOLD).
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Any

from backend.analysis.header_forensics import HeaderAnalysisResult
from backend.analysis.authentication import AuthenticationResult, AuthStatus
from backend.analysis.pii_redaction import PIIRedactionResult
from backend.analysis.evidence_preservation import EvidenceDossier

try:
    from backend.analysis.url_analysis import URLAnalysisResult
except ImportError:
    URLAnalysisResult = Any

try:
    from backend.analysis.attachment_analysis import AttachmentAnalysisResult
except ImportError:
    AttachmentAnalysisResult = Any

try:
    from backend.analysis.detection import NLPThreatResult
except ImportError:
    NLPThreatResult = Any



class RiskLevel(str, Enum):
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    MALICIOUS = "MALICIOUS"
    UNKNOWN = "UNKNOWN"


class DeliveryAction(str, Enum):
    DELIVER = "DELIVER"
    WARN = "WARN"
    QUARANTINE = "QUARANTINE"
    REJECT = "REJECT"
    HOLD = "HOLD"


@dataclass
class PolicyDecision:
    risk_level: RiskLevel
    delivery_action: DeliveryAction
    threat_score: float  # 0.0 (Safe) to 100.0 (Malicious)
    confidence_score: float  # 0.0 to 100.0
    summary: str
    rule_triggers: List[str]
    is_quarantined: bool
    requires_warning_badge: bool


class SecurityPolicyEngine:
    """Delivery-Time Security Policy Evaluator"""

    def __init__(
        self,
        quarantine_threshold: float = 55.0,
        warning_threshold: float = 25.0,
    ):
        self.quarantine_threshold = quarantine_threshold
        self.warning_threshold = warning_threshold

    def evaluate(
        self,
        header_result: HeaderAnalysisResult,
        auth_result: AuthenticationResult,
        pii_result: Optional[PIIRedactionResult] = None,
        url_result: Optional[URLAnalysisResult] = None,
        attachment_result: Optional[AttachmentAnalysisResult] = None,
        nlp_result: Optional[NLPThreatResult] = None,
        dossier: Optional[EvidenceDossier] = None,
    ) -> PolicyDecision:
        """Evaluates overall security stance and returns delivery policy decision."""
        triggers: List[str] = []
        threat_score = 0.0

        # 1. Header Anomaly Impact (up to 40 points)
        if header_result.anomaly_score > 0:
            impact = (header_result.anomaly_score / 100.0) * 40.0
            threat_score += impact
            for anomaly in header_result.anomalies:
                triggers.append(f"HEADER: {anomaly}")

        # 2. Lookalike Domain Spoofing (Hard Trigger -> +45 points)
        if header_result.is_spoofed_domain:
            threat_score += 45.0
            triggers.append("CRITICAL SPOOFING: From domain matches lookalike/typosquatting target pattern")

        # 3. Domain Mismatch (From vs Return-Path) (+25 points)
        if header_result.domain_mismatch:
            threat_score += 25.0
            triggers.append("SPOOFING: From header domain does not match Return-Path domain")

        # 4. Authentication Failure Impact (up to 35 points)
        if auth_result.spf_status in (AuthStatus.FAIL, AuthStatus.SOFTFAIL):
            threat_score += 20.0
            triggers.append(f"AUTH: SPF authentication failed ({auth_result.spf_status.value})")

        if auth_result.dkim_status == AuthStatus.FAIL:
            threat_score += 20.0
            triggers.append("AUTH: DKIM cryptographic signature verification failed")

        if auth_result.dmarc_status == AuthStatus.FAIL:
            threat_score += 15.0
            triggers.append("AUTH: DMARC policy alignment check failed")

        # 5. URL Phishing & Homoglyph Impact
        if url_result and url_result.overall_url_risk_score > 0:
            impact = (url_result.overall_url_risk_score / 100.0) * 45.0
            threat_score += impact
            for summary_item in url_result.findings_summary:
                triggers.append(summary_item)

        # 6. Dangerous Attachment Impact
        if attachment_result and attachment_result.overall_attachment_risk_score > 0:
            impact = (attachment_result.overall_attachment_risk_score / 100.0) * 50.0
            threat_score += impact
            for summary_item in attachment_result.findings_summary:
                triggers.append(summary_item)

        # 7. NLP BEC & Executive Impersonation Impact
        if nlp_result and nlp_result.nlp_risk_score > 0:
            impact = (nlp_result.nlp_risk_score / 100.0) * 40.0
            threat_score += impact
            for summary_item in nlp_result.nlp_summary:
                triggers.append(summary_item)

        # 8. PII Presence Signals (Privacy Risk)
        if pii_result and pii_result.is_pii_present:
            threat_score += 10.0
            triggers.append(
                f"PRIVACY: Sensitive PII detected ({', '.join(pii_result.pii_types_found)})"
            )

        # Cap threat score at 100.0
        threat_score = min(100.0, threat_score)

        # Determine Risk Level and Delivery Action
        if (
            (header_result.is_spoofed_domain and (auth_result.spf_status == AuthStatus.FAIL or auth_result.dkim_status == AuthStatus.FAIL))
            or (url_result and url_result.malicious_urls_count > 0)
            or (attachment_result and attachment_result.malicious_attachments_count > 0)
        ):
            risk_level = RiskLevel.MALICIOUS
            delivery_action = DeliveryAction.QUARANTINE
        elif threat_score >= self.quarantine_threshold:
            risk_level = RiskLevel.MALICIOUS
            delivery_action = DeliveryAction.QUARANTINE
        elif threat_score >= self.warning_threshold:
            risk_level = RiskLevel.SUSPICIOUS
            delivery_action = DeliveryAction.WARN
        elif auth_result.spf_status == AuthStatus.UNKNOWN and auth_result.dkim_status == AuthStatus.UNKNOWN and len(header_result.anomalies) > 0:
            risk_level = RiskLevel.UNKNOWN
            delivery_action = DeliveryAction.HOLD
        else:
            risk_level = RiskLevel.SAFE
            delivery_action = DeliveryAction.DELIVER

        is_quarantined = delivery_action in (DeliveryAction.QUARANTINE, DeliveryAction.REJECT)
        requires_warning_badge = delivery_action == DeliveryAction.WARN

        # Confidence calculation
        confidence = 98.0 if dossier else 88.0

        summary = f"Risk Stance: {risk_level.value} (Threat Score: {threat_score:.1f}/100) -> Policy Action: {delivery_action.value}"

        return PolicyDecision(
            risk_level=risk_level,
            delivery_action=delivery_action,
            threat_score=round(threat_score, 1),
            confidence_score=confidence,
            summary=summary,
            rule_triggers=triggers,
            is_quarantined=is_quarantined,
            requires_warning_badge=requires_warning_badge,
        )

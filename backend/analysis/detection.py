"""
MailTrace AI — Pre-Delivery NLP Phishing & Threat Intelligence Detector

Analyzes text body and subject lines for high-urgency pressure language, BEC payment diversion,
executive impersonation (AICTE, GOV, CEO), and credential harvesting intent.
"""

from dataclasses import dataclass, field
import re
from typing import List, Dict, Set


@dataclass
class NLPThreatResult:
    urgency_score: float  # 0.0 to 100.0
    threat_category: str  # CLEAN | BEC_PAYMENT_DIVERSION | EXECUTIVE_IMPERSONATION | URGENT_CREDENTIAL_HARVEST | HIGH_RISK
    detected_phrases: List[str]
    is_executive_impersonation: bool
    is_payment_diversion: bool
    nlp_risk_score: float
    nlp_summary: List[str]


class NLPThreatDetector:
    """Pre-Delivery NLP Threat & BEC Intent Engine"""

    URGENCY_KEYWORDS = [
        r"immediate(?:ly)?\s+action", r"wire\s+transfer", r"account\s+suspended",
        r"within\s+\d+\s+hours", r"urgent\s+mandate", r"password\s+expir(?:ed|ation)",
        r"transfer\s+funds", r"verify\s+immediately", r"action\s+required"
    ]

    EXECUTIVE_TITLES = [
        "aicte director", "aicte chairman", "nic administrator", "sih director",
        "chief executive officer", "managing director", "head of department", "hr payroll"
    ]

    PAYMENT_DIVERSION_PATTERNS = [
        r"wire\s+transfer", r"bank\s+account\s+details", r"transfer\s+₹?\d+",
        r"fund\s+release", r"account\s+confirmation", r"payment\s+remittance"
    ]

    def analyze(self, subject: str, body: str, sender_display_name: str = "") -> NLPThreatResult:
        """Evaluates text signals for urgency, impersonation, and payment diversion."""
        combined_text = f"{subject}\n{body}\n{sender_display_name}".lower()

        detected_phrases: List[str] = []
        findings: List[str] = []
        urgency_hits = 0

        # 1. Check Urgency Keywords
        for pattern in self.URGENCY_KEYWORDS:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            if matches:
                urgency_hits += len(matches)
                detected_phrases.append(matches[0])

        # 2. Check Executive Impersonation
        is_impersonation = False
        for title in self.EXECUTIVE_TITLES:
            if title in combined_text:
                is_impersonation = True
                findings.append(f"NLP SIGNAL: High-authority executive/institutional title matched ('{title}')")
                break

        # 3. Check Payment Diversion Intent
        is_payment = False
        for pattern in self.PAYMENT_DIVERSION_PATTERNS:
            if re.search(pattern, combined_text, re.IGNORECASE):
                is_payment = True
                findings.append("NLP SIGNAL: Business Email Compromise (BEC) payment diversion intent detected")
                break

        # Calculate scores
        urgency_score = min(100.0, urgency_hits * 25.0)
        nlp_risk = 0.0

        if is_impersonation and is_payment:
            nlp_risk += 60.0
            category = "BEC_PAYMENT_DIVERSION"
        elif is_impersonation:
            nlp_risk += 35.0
            category = "EXECUTIVE_IMPERSONATION"
        elif urgency_score > 50:
            nlp_risk += 40.0
            category = "URGENT_CREDENTIAL_HARVEST"
        elif urgency_score > 0 or is_payment:
            nlp_risk += 20.0
            category = "HIGH_RISK"
        else:
            category = "CLEAN"

        if urgency_score > 0:
            findings.append(f"NLP SIGNAL: High-urgency intimidation language detected (Urgency Score: {urgency_score}/100)")

        return NLPThreatResult(
            urgency_score=urgency_score,
            threat_category=category,
            detected_phrases=detected_phrases,
            is_executive_impersonation=is_impersonation,
            is_payment_diversion=is_payment,
            nlp_risk_score=min(100.0, nlp_risk),
            nlp_summary=findings if findings else ["NLP text threat score verified clean."],
        )

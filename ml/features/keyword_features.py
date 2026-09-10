"""
Extracts threat-related keyword signals across specified categories:
- Urgent language & pressure
- Phishing & Credential harvesting
- Social engineering & Authority
- Malicious payload/link cues
- Impersonation & Executive spoofing
"""

import re
from typing import Dict, List, Set
from .base import BaseFeatureExtractor, FeatureVector
from ..preprocessing.base import ProcessedEmail


class KeywordFeatureExtractor(BaseFeatureExtractor):
    """
    Scans text for security threat indicators and suspicious semantic patterns.
    """

    KEYWORD_BANK: Dict[str, Set[str]] = {
        "urgency": {
            "urgent", "immediately", "immediate action", "account suspended",
            "suspended within", "24 hours", "48 hours", "expire soon", "action required",
            "critical update", "final notice", "deadline", "security alert"
        },
        "phishing_credentials": {
            "verify account", "confirm password", "login now", "click here",
            "update billing", "re-activate", "security check", "mailbox full",
            "reset credentials", "verify identity", "validate your account"
        },
        "social_engineering": {
            "confidential", "do not share", "wire transfer", "gift card", "payroll",
            "direct deposit", "executive request", "request for proposal", "urgent favor",
            "are you available", "vendor payment", "invoice attached"
        },
        "malicious_cues": {
            "download attached", "enable macros", "executable", "payment receipt.pdf.exe",
            "secure document link", "encrypted file", "view statement"
        },
        "impersonation": {
            "ceo", "cfo", "administrator", "it support", "helpdesk", "security team",
            "payroll department", "human resources", "microsoft support", "bank admin"
        }
    }

    def extract(self, processed_email: ProcessedEmail) -> FeatureVector:
        text = processed_email.combined_text.lower()

        signal_counts: Dict[str, int] = {}
        numerical: Dict[str, float] = {}
        booleans: Dict[str, bool] = {}

        for category, keywords in self.KEYWORD_BANK.items():
            matches = 0
            for kw in keywords:
                if kw in text:
                    matches += 1
            signal_counts[f"{category}_count"] = matches
            numerical[f"{category}_density"] = round(matches / max(len(processed_email.tokens), 1), 4)
            booleans[f"has_{category}_keywords"] = matches > 0

        raw_vec = [float(v) for v in signal_counts.values()] + list(numerical.values())

        return FeatureVector(
            numerical_features=numerical,
            boolean_features=booleans,
            signal_counts=signal_counts,
            feature_names=list(signal_counts.keys()) + list(numerical.keys()),
            raw_vector=raw_vec
        )

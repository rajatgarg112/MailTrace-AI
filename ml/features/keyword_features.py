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
    Outputs deterministic keyword signal counts and keyword density ratios.
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
        text = (processed_email.combined_text or "").lower()
        token_count = max(len(processed_email.tokens), 1)

        signal_counts: Dict[str, int] = {}
        numerical: Dict[str, float] = {}
        booleans: Dict[str, bool] = {}

        total_matches = 0
        for category, keywords in self.KEYWORD_BANK.items():
            matches = 0
            for kw in keywords:
                if kw in text:
                    matches += 1
            total_matches += matches
            signal_counts[f"{category}_count"] = matches
            numerical[f"{category}_density"] = round(matches / token_count, 4)
            booleans[f"has_{category}_keywords"] = matches > 0

        # Combined pressure score (sum of matches normalized)
        combined_pressure_score = round(min(1.0, total_matches * 0.15), 4)
        numerical["combined_threat_pressure_score"] = combined_pressure_score

        feature_names = list(signal_counts.keys()) + list(numerical.keys()) + list(booleans.keys())
        raw_vec = [float(v) for v in signal_counts.values()] + list(numerical.values()) + [1.0 if v else 0.0 for v in booleans.values()]

        return FeatureVector(
            numerical_features=numerical,
            boolean_features=booleans,
            signal_counts=signal_counts,
            feature_names=feature_names,
            raw_vector=raw_vec
        )

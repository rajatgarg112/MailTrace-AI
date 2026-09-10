"""
Feature extractor for sender-related indicators.
"""

from typing import Dict, Any, List, Set
from .base import BaseFeatureExtractor, FeatureVector
from ..preprocessing.base import ProcessedEmail


class SenderFeatureExtractor(BaseFeatureExtractor):
    """
    Extracts sender presence, sender domain characteristics, freemail flags,
    and sender vs recipient domain relationships.
    """

    FREEMAIL_PROVIDERS: Set[str] = {
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
        "aol.com", "icloud.com", "protonmail.com", "mail.com", "gmx.com"
    }

    def extract(self, processed_email: ProcessedEmail) -> FeatureVector:
        sender_email = processed_email.sender_email
        sender_domain = processed_email.sender_domain
        recipient_domains = processed_email.recipient_domains or []

        has_sender = bool(sender_email)
        is_missing_sender = processed_email.text_indicators.get("is_missing_sender", not has_sender)

        domain_len = float(len(sender_domain)) if sender_domain else 0.0
        is_freemail = sender_domain.lower() in self.FREEMAIL_PROVIDERS if sender_domain else False

        # Domain mismatch check (is sender domain external/different from all recipient domains?)
        domain_mismatch = False
        if sender_domain and recipient_domains:
            domain_mismatch = not any(sender_domain.lower() == rd.lower() for rd in recipient_domains)

        numerical = {
            "sender_domain_length": domain_len,
            "recipient_domain_count": float(len(recipient_domains))
        }

        booleans = {
            "has_sender": has_sender,
            "is_missing_sender": is_missing_sender,
            "is_freemail_provider": is_freemail,
            "has_domain_mismatch": domain_mismatch
        }

        feature_names = list(numerical.keys()) + list(booleans.keys())
        raw_vec = list(numerical.values()) + [1.0 if v else 0.0 for v in booleans.values()]

        return FeatureVector(
            numerical_features=numerical,
            boolean_features=booleans,
            feature_names=feature_names,
            raw_vector=raw_vec
        )

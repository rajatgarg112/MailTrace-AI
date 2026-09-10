"""
Feature extractor for message structure indicators.
"""

from typing import Dict, Any, List
from .base import BaseFeatureExtractor, FeatureVector
from ..preprocessing.base import ProcessedEmail


class StructureFeatureExtractor(BaseFeatureExtractor):
    """
    Extracts structural metadata indicators (recipients count, HTML formatting, headers).
    """

    def extract(self, processed_email: ProcessedEmail) -> FeatureVector:
        recipients = processed_email.recipients or []
        num_recipients = len(recipients)

        extracted_emails = processed_email.extracted_emails or []
        num_extracted_emails = len(extracted_emails)

        has_html = processed_email.metadata.get("has_html", False)
        headers_present = processed_email.metadata.get("headers_present", False)

        numerical = {
            "recipient_count": float(num_recipients),
            "extracted_email_count": float(num_extracted_emails)
        }

        booleans = {
            "has_recipients": num_recipients > 0,
            "has_multiple_recipients": num_recipients > 1,
            "has_html": has_html,
            "headers_present": headers_present
        }

        feature_names = list(numerical.keys()) + list(booleans.keys())
        raw_vec = list(numerical.values()) + [1.0 if v else 0.0 for v in booleans.values()]

        return FeatureVector(
            numerical_features=numerical,
            boolean_features=booleans,
            feature_names=feature_names,
            raw_vector=raw_vec
        )

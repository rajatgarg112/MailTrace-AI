"""
Feature extractor for URL-related security indicators.
"""

import re
from typing import Dict, Any, List
from .base import BaseFeatureExtractor, FeatureVector
from ..preprocessing.base import ProcessedEmail


class UrlFeatureExtractor(BaseFeatureExtractor):
    """
    Extracts URL frequency, IP-host presence, suspicious TLD counts, and length metrics.
    """

    IP_URL_REGEX = re.compile(
        r'https?://(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:/[^\s]*)?',
        re.IGNORECASE
    )
    SUSPICIOUS_TLDS = {
        ".xyz", ".top", ".tk", ".zip", ".ru", ".cn", ".cc", ".work",
        ".click", ".link", ".download", ".racing", ".party", ".bit"
    }

    def extract(self, processed_email: ProcessedEmail) -> FeatureVector:
        urls = processed_email.extracted_urls or []
        num_urls = len(urls)
        has_urls = num_urls > 0

        ip_urls = [u for u in urls if self.IP_URL_REGEX.search(u)]
        ip_url_count = len(ip_urls)

        suspicious_tld_urls = [
            u for u in urls if any(u.lower().split('/')[2].endswith(tld) if len(u.split('/')) > 2 else u.lower().endswith(tld) for tld in self.SUSPICIOUS_TLDS)
        ]
        suspicious_tld_count = len(suspicious_tld_urls)

        url_lengths = [len(u) for u in urls]
        avg_url_len = round(sum(url_lengths) / num_urls, 2) if num_urls > 0 else 0.0
        max_url_len = float(max(url_lengths)) if num_urls > 0 else 0.0

        word_count = len(processed_email.tokens)
        url_to_word_ratio = round(num_urls / word_count, 4) if word_count > 0 else float(num_urls)

        numerical = {
            "num_urls": float(num_urls),
            "ip_url_count": float(ip_url_count),
            "suspicious_tld_count": float(suspicious_tld_count),
            "avg_url_length": avg_url_len,
            "max_url_length": max_url_len,
            "url_to_word_ratio": url_to_word_ratio
        }

        booleans = {
            "has_urls": has_urls,
            "has_ip_urls": ip_url_count > 0,
            "has_suspicious_tld": suspicious_tld_count > 0,
            "has_multiple_urls": num_urls > 1
        }

        feature_names = list(numerical.keys()) + list(booleans.keys())
        raw_vec = list(numerical.values()) + [1.0 if v else 0.0 for v in booleans.values()]

        return FeatureVector(
            numerical_features=numerical,
            boolean_features=booleans,
            feature_names=feature_names,
            raw_vector=raw_vec
        )

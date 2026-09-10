"""
Phase 1 Mock / Placeholder Classifier Model implementation.
Computes deterministic rule-assisted probability distributions for development and testing.
Explicitly tagged as a placeholder implementation.
"""

from typing import Dict, Any, Optional
from .base import BaseModel
from ..features.base import FeatureVector
from ..config.ml_config import ModelConfig


class MockClassifierModel(BaseModel):
    """
    Deterministic Mock Classifier Model.
    Designed for development, unit testing, and pipeline verification.
    Explicitly identified as a placeholder implementation (is_placeholder = True).
    """

    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig(
            model_name="mock_classifier_placeholder",
            model_version="mock-v1.0.0-phase1"
        )
        self.version = self.config.model_version
        self.name = self.config.model_name

    def is_placeholder(self) -> bool:
        """Explicitly returns True to indicate this is not a trained AI model."""
        return True

    def predict(self, feature_vector: FeatureVector) -> int:
        proba = self.predict_proba(feature_vector)
        phishing_p = proba.get("phishing", proba.get("malicious", 0.0))
        suspicious_p = proba.get("suspicious", 0.0)
        
        if phishing_p >= self.config.threshold_malicious:
            return 2  # Phishing
        elif (phishing_p + suspicious_p) >= self.config.threshold_suspicious:
            return 1  # Suspicious
        return 0  # Benign

    def predict_proba(self, feature_vector: FeatureVector) -> Dict[str, float]:
        signal_counts = feature_vector.signal_counts
        num_features = feature_vector.numerical_features
        bool_features = feature_vector.boolean_features

        phish_c = signal_counts.get("phishing_credentials_count", 0)
        urgency_c = signal_counts.get("urgency_count", 0)
        social_c = signal_counts.get("social_engineering_count", 0)
        mal_c = signal_counts.get("malicious_cues_count", 0)
        imp_c = signal_counts.get("impersonation_count", 0)

        num_urls = num_features.get("num_urls", 0.0)
        upper_ratio = num_features.get("body_uppercase_ratio", num_features.get("uppercase_ratio", 0.0))
        has_ip_urls = bool_features.get("has_ip_urls", False)

        score = 0.0
        score += phish_c * 0.35
        score += urgency_c * 0.20
        score += social_c * 0.25
        score += mal_c * 0.40
        score += imp_c * 0.30

        if num_urls > 2:
            score += 0.15
        if upper_ratio > 0.3:
            score += 0.10
        if has_ip_urls:
            score += 0.25

        phishing_p = min(max(score, 0.05), 0.95)
        remaining = 1.0 - phishing_p

        if urgency_c > 0 or social_c > 0:
            suspicious_p = round(remaining * 0.6, 4)
            benign_p = round(remaining * 0.4, 4)
        else:
            suspicious_p = round(remaining * 0.2, 4)
            benign_p = round(remaining * 0.8, 4)

        phishing_p = round(1.0 - (benign_p + suspicious_p), 4)

        return {
            "benign": benign_p,
            "suspicious": suspicious_p,
            "phishing": phishing_p,
            "safe": benign_p,
            "malicious": phishing_p
        }

    def save(self, filepath: str) -> bool:
        """Placeholder save artifact operation."""
        return True

    def load(self, filepath: str) -> bool:
        """Placeholder load artifact operation."""
        return True

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "model_name": self.name,
            "model_version": self.version,
            "type": "MockPlaceholderClassifier",
            "is_placeholder": True,
            "phase": "Phase 1 Foundation"
        }

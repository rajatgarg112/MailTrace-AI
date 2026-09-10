"""
Phase 1 Placeholder Model implementation.
Uses rule-assisted score aggregation to compute mock risk probabilities
without external heavy ML frameworks.
"""

from typing import Dict, Any, Optional
from .base import BaseModel
from ..features.base import FeatureVector
from ..config.ml_config import ModelConfig


class PlaceholderModel(BaseModel):
    """
    Modular placeholder model that satisfies the BaseModel contract.
    Computes heuristic threat probability based on extracted feature vectors.
    """

    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig()
        self.version = self.config.model_version
        self.name = self.config.model_name

    def predict(self, feature_vector: FeatureVector) -> int:
        proba = self.predict_proba(feature_vector)
        malicious_p = proba.get("malicious", 0.0)
        suspicious_p = proba.get("suspicious", 0.0)
        
        if malicious_p >= self.config.threshold_malicious:
            return 2  # Malicious
        elif (malicious_p + suspicious_p) >= self.config.threshold_suspicious:
            return 1  # Suspicious
        return 0  # Safe

    def predict_proba(self, feature_vector: FeatureVector) -> Dict[str, float]:
        signal_counts = feature_vector.signal_counts
        num_features = feature_vector.numerical_features
        bool_features = feature_vector.boolean_features

        # Heuristic scoring
        phish_c = signal_counts.get("phishing_credentials_count", 0)
        urgency_c = signal_counts.get("urgency_count", 0)
        social_c = signal_counts.get("social_engineering_count", 0)
        mal_c = signal_counts.get("malicious_cues_count", 0)
        imp_c = signal_counts.get("impersonation_count", 0)

        num_urls = num_features.get("num_urls", 0.0)
        upper_ratio = num_features.get("uppercase_ratio", 0.0)

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

        # Cap score between 0.05 and 0.95
        malicious_p = min(max(score, 0.05), 0.95)
        remaining = 1.0 - malicious_p
        
        # Split remaining between suspicious and safe based on urgency
        if urgency_c > 0 or social_c > 0:
            suspicious_p = round(remaining * 0.6, 4)
            safe_p = round(remaining * 0.4, 4)
        else:
            suspicious_p = round(remaining * 0.2, 4)
            safe_p = round(remaining * 0.8, 4)

        malicious_p = round(1.0 - (safe_p + suspicious_p), 4)

        return {
            "safe": safe_p,
            "suspicious": suspicious_p,
            "malicious": malicious_p
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
            "type": "PlaceholderRuleModel",
            "phase": "Phase 1 Foundation"
        }

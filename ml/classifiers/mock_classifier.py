"""
Deterministic Mock Classifier implementation for development, testing, and UI integration.
Produces standardized ClassifierOutput verdicts ("phishing", "suspicious", "benign", "unknown").
Explicitly tagged as a placeholder implementation.
"""

from typing import Any, Dict, List, Optional
from .base import BaseClassifier
from .schemas import (
    ClassifierOutput,
    ClassifierLabel,
    MLPredictionResult
)
from ..preprocessing.email_preprocessor import EmailPreprocessor
from ..features.composite_extractor import EmailFeatureExtractor
from ..models.mock_model import MockClassifierModel
from ..models.base import BaseModel
from ..config.ml_config import MLConfig


class MockClassifier(BaseClassifier):
    """
    Deterministic Mock Classifier.
    Designed for development, testing, and API integration.
    Explicitly identified as a placeholder (is_placeholder = True).
    """

    def __init__(
        self,
        config: Optional[MLConfig] = None,
        model: Optional[BaseModel] = None,
        preprocessor: Optional[EmailPreprocessor] = None,
        feature_extractor: Optional[EmailFeatureExtractor] = None
    ):
        self.config = config or MLConfig()
        self.preprocessor = preprocessor or EmailPreprocessor()
        self.feature_extractor = feature_extractor or EmailFeatureExtractor()
        self.model = model or MockClassifierModel(config=self.config.model)

    def classify(self, email_input: Any) -> ClassifierOutput:
        """Runs pipeline and returns standardized ClassifierOutput."""
        return self.predict_verdict(email_input)

    def predict_verdict(self, email_input: Any) -> ClassifierOutput:
        """
        Runs preprocessor, feature extractor, and mock model to return ClassifierOutput:
        {
            "label": "phishing | suspicious | benign | unknown",
            "confidence": 0.85,
            "signals": ["..."]
        }
        """
        # Step 1: Preprocessing
        processed = self.preprocessor.preprocess(email_input)

        # Step 2: Feature Extraction
        feature_vector = self.feature_extractor.extract(processed)

        # Step 3: Model Prediction
        probabilities = self.model.predict_proba(feature_vector)
        phishing_p = probabilities.get("phishing", probabilities.get("malicious", 0.0))
        suspicious_p = probabilities.get("suspicious", 0.0)
        benign_p = probabilities.get("benign", probabilities.get("safe", 0.0))

        # Determine Label and Confidence
        if phishing_p >= self.config.model.threshold_malicious:
            label = ClassifierLabel.PHISHING.value
            confidence = min(max(phishing_p, 0.50), 0.99)
        elif (phishing_p + suspicious_p) >= self.config.model.threshold_suspicious:
            label = ClassifierLabel.SUSPICIOUS.value
            confidence = min(max(phishing_p + suspicious_p, 0.40), 0.88)
        else:
            label = ClassifierLabel.BENIGN.value
            confidence = min(max(benign_p, 0.60), 0.99)

        # Extract Signals
        signals: List[str] = []
        counts = feature_vector.signal_counts
        bools = feature_vector.boolean_features

        if counts.get("phishing_credentials_count", 0) > 0:
            signals.append("Credential harvesting language or login verification cues detected.")
        if counts.get("urgency_count", 0) > 0 or bools.get("has_subject_urgency_keyword"):
            signals.append("High urgency or immediate action pressure detected in text.")
        if counts.get("social_engineering_count", 0) > 0:
            signals.append("Social engineering, wire transfer, or payroll authority request detected.")
        if counts.get("malicious_cues_count", 0) > 0:
            signals.append("Malicious document/attachment references detected.")
        if counts.get("impersonation_count", 0) > 0:
            signals.append("Executive/admin role impersonation cues detected.")
        if bools.get("has_ip_urls"):
            signals.append("Direct IP address URL detected in email content.")
        if bools.get("has_suspicious_tld"):
            signals.append("Suspicious TLD link detected in email content.")
        if bools.get("is_missing_sender"):
            signals.append("Sender email address is missing.")
        if bools.get("is_missing_subject"):
            signals.append("Subject line is missing.")

        if not signals:
            signals.append("No overt security threat indicators detected.")

        return ClassifierOutput(
            label=label,
            confidence=round(confidence, 4),
            signals=signals,
            model_version=self.model.get_metadata().get("model_version", "mock-v1.0.0-phase1"),
            is_placeholder=True,
            metadata={
                "model_name": self.model.get_metadata().get("model_name", "mock_classifier_placeholder"),
                "is_placeholder": True,
                "url_count": len(processed.extracted_urls),
                "word_count": len(processed.tokens)
            }
        )

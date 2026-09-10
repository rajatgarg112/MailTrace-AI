"""
Concrete Email Classifier orchestrating Preprocessing, Feature Extractors,
and Model prediction to produce multi-signal verdicts.
"""

from typing import Any, Dict, List, Optional
from .base import BaseClassifier
from .schemas import (
    ClassificationCategory,
    ClassifierLabel,
    ClassifierOutput,
    SignalVerdict,
    MLPredictionResult
)
from ..preprocessing.email_preprocessor import EmailPreprocessor
from ..features.composite_extractor import EmailFeatureExtractor
from ..models.placeholder_model import PlaceholderModel
from ..models.base import BaseModel
from ..config.ml_config import MLConfig


class EmailClassifier(BaseClassifier):
    """
    Main Classifier implementation for Phase 1.
    Integrates Preprocessor + EmailFeatureExtractor + Model.
    Produces verdicts across all 5 required signal categories:
    1. Phishing classification
    2. Suspicious-language detection
    3. Social-engineering detection
    4. Malicious-content classification
    5. Impersonation signals
    """

    def __init__(
        self,
        config: Optional[MLConfig] = None,
        model: Optional[BaseModel] = None,
        feature_extractor: Optional[EmailFeatureExtractor] = None
    ):
        self.config = config or MLConfig()
        self.preprocessor = EmailPreprocessor()
        self.feature_extractor = feature_extractor or EmailFeatureExtractor()
        self.model = model or PlaceholderModel(config=self.config.model)

    def predict_verdict(self, email_input: Any) -> ClassifierOutput:
        """Returns standardized ClassifierOutput dictionary representation."""
        result = self.classify(email_input)
        label_map = {
            ClassificationCategory.MALICIOUS.value: ClassifierLabel.PHISHING.value,
            ClassificationCategory.SUSPICIOUS.value: ClassifierLabel.SUSPICIOUS.value,
            ClassificationCategory.SAFE.value: ClassifierLabel.BENIGN.value,
            ClassificationCategory.UNKNOWN.value: ClassifierLabel.UNKNOWN.value
        }
        mapped_label = label_map.get(result.classification, ClassifierLabel.UNKNOWN.value)
        return ClassifierOutput(
            label=mapped_label,
            confidence=round(min(max(result.confidence, 0.0), 1.0), 4),
            signals=result.signals or ["No overt threat indicators detected."],
            model_version=result.model_version,
            is_placeholder=self.model.is_placeholder(),
            metadata=result.metadata
        )

    def classify(self, email_input: Any) -> MLPredictionResult:
        # Step 1: Preprocessing
        processed = self.preprocessor.preprocess(email_input)

        # Step 2: Unified Feature Extraction
        feature_vector = self.feature_extractor.extract(processed)

        merged_signals = feature_vector.signal_counts
        merged_numerics = feature_vector.numerical_features
        merged_booleans = feature_vector.boolean_features

        # Step 3: Model Probability Prediction
        probabilities = self.model.predict_proba(feature_vector)
        malicious_p = probabilities.get("malicious", 0.0)
        suspicious_p = probabilities.get("suspicious", 0.0)

        # Overall risk score calculation
        overall_risk = round(malicious_p * 100.0, 2)
        confidence = 0.85  # Standard baseline confidence for Phase 1

        # Classify overall category
        if malicious_p >= self.config.model.threshold_malicious:
            category = ClassificationCategory.MALICIOUS
        elif (malicious_p + suspicious_p) >= self.config.model.threshold_suspicious:
            category = ClassificationCategory.SUSPICIOUS
        else:
            category = ClassificationCategory.SAFE

        # Step 4: Multi-signal individual verdicts
        phishing_verdict = self._evaluate_phishing(merged_signals, merged_booleans, malicious_p)
        suspicious_lang_verdict = self._evaluate_suspicious_language(merged_signals, merged_numerics, suspicious_p)
        social_eng_verdict = self._evaluate_social_engineering(merged_signals, merged_booleans)
        malicious_content_verdict = self._evaluate_malicious_content(merged_signals, merged_booleans, processed)
        impersonation_verdict = self._evaluate_impersonation(merged_signals, processed)

        # Aggregate explanation signals
        active_signals = []
        for verdict in [phishing_verdict, suspicious_lang_verdict, social_eng_verdict, malicious_content_verdict, impersonation_verdict]:
            if verdict.detected:
                active_signals.append(f"{verdict.signal_name}: {verdict.explanation}")

        return MLPredictionResult(
            classification=category.value,
            overall_risk_score=overall_risk,
            confidence=confidence,
            model_version=self.model.get_metadata().get("model_version", "1.0.0-phase1"),
            phishing_verdict=phishing_verdict,
            suspicious_language_verdict=suspicious_lang_verdict,
            social_engineering_verdict=social_eng_verdict,
            malicious_content_verdict=malicious_content_verdict,
            impersonation_verdict=impersonation_verdict,
            signals=active_signals,
            metadata={
                "url_count": processed.metadata.get("url_count", 0),
                "word_count": feature_vector.numerical_features.get("body_word_count", feature_vector.numerical_features.get("word_count", 0)),
                "has_html": processed.metadata.get("has_html", False)
            }
        )

    def _evaluate_phishing(self, signals: Dict[str, int], booleans: Dict[str, bool], score_p: float) -> SignalVerdict:
        count = signals.get("phishing_credentials_count", 0)
        detected = count > 0 or booleans.get("has_urls", False) and score_p > 0.5
        score = min(1.0, count * 0.4 + (0.3 if booleans.get("has_urls") else 0.0))
        return SignalVerdict(
            signal_name="phishing_classification",
            score=round(score, 2),
            confidence=0.88,
            detected=detected,
            explanation="Credential harvesting or login link cues detected." if detected else "No phishing credential harvesting signals detected.",
            metadata={"credential_keyword_count": count}
        )

    def _evaluate_suspicious_language(self, signals: Dict[str, int], numerics: Dict[str, float], score_s: float) -> SignalVerdict:
        urgency = signals.get("urgency_count", 0)
        upper_ratio = numerics.get("body_uppercase_ratio", numerics.get("uppercase_ratio", 0.0))
        exclamations = numerics.get("body_exclamation_count", numerics.get("exclamation_count", 0.0))

        detected = urgency > 0 or upper_ratio > 0.25 or exclamations >= 3
        score = min(1.0, urgency * 0.3 + upper_ratio * 0.8 + (exclamations * 0.1))
        return SignalVerdict(
            signal_name="suspicious_language",
            score=round(score, 2),
            confidence=0.85,
            detected=detected,
            explanation="High urgency, pressure tactics, or excessive capitalization detected." if detected else "Standard language tone.",
            metadata={"urgency_count": urgency, "uppercase_ratio": upper_ratio}
        )

    def _evaluate_social_engineering(self, signals: Dict[str, int], booleans: Dict[str, bool]) -> SignalVerdict:
        count = signals.get("social_engineering_count", 0)
        detected = count > 0
        score = min(1.0, count * 0.35)
        return SignalVerdict(
            signal_name="social_engineering",
            score=round(score, 2),
            confidence=0.82,
            detected=detected,
            explanation="Authority pressure, financial request, or secrecy language detected." if detected else "No social engineering signals detected.",
            metadata={"social_engineering_count": count}
        )

    def _evaluate_malicious_content(self, signals: Dict[str, int], booleans: Dict[str, bool], processed: Any) -> SignalVerdict:
        count = signals.get("malicious_cues_count", 0)
        detected = count > 0
        score = min(1.0, count * 0.5)
        return SignalVerdict(
            signal_name="malicious_content",
            score=round(score, 2),
            confidence=0.80,
            detected=detected,
            explanation="Malicious download cues or suspicious attachment references detected." if detected else "No malicious text/link content cues.",
            metadata={"malicious_keyword_count": count}
        )

    def _evaluate_impersonation(self, signals: Dict[str, int], processed: Any) -> SignalVerdict:
        count = signals.get("impersonation_count", 0)
        detected = count > 0
        score = min(1.0, count * 0.4)
        return SignalVerdict(
            signal_name="impersonation_signals",
            score=round(score, 2),
            confidence=0.85,
            detected=detected,
            explanation="Executive, admin, or support role impersonation cues detected." if detected else "No role impersonation cues detected.",
            metadata={"impersonation_keyword_count": count}
        )

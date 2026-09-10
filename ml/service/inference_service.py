"""
High-level ML Inference Service for MailTrace AI.
Orchestrates the 4-stage ML inference pipeline:
Email Input -> Preprocessing -> Feature Extraction -> Classifier -> MLInferenceResult

Maintains strict separation of concerns:
- Pure ML signal analysis (source="ml")
- Does NOT perform database persistence, delivery decisions, quarantine actions, or external threat intel calls.
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from ..preprocessing.email_preprocessor import EmailPreprocessor
from ..preprocessing.base import BasePreprocessor, ProcessedEmail
from ..features.composite_extractor import EmailFeatureExtractor
from ..features.base import BaseFeatureExtractor, FeatureVector
from ..classifiers.mock_classifier import MockClassifier
from ..classifiers.base import BaseClassifier
from ..classifiers.schemas import (
    ClassifierOutput,
    ClassifierLabel,
    MLPredictionResult,
    ClassificationCategory,
    SignalVerdict
)
from ..config.ml_config import MLConfig

logger = logging.getLogger("MailTrace.MLInferenceService")


@dataclass
class MLInferenceResult:
    """
    Standardized result structure returned by MLInferenceService.
    Format:
    {
        "source": "ml",
        "label": "phishing | suspicious | benign | unknown",
        "confidence": 0.85,
        "signals": ["..."],
        "execution_time_ms": 1.42,
        "model_version": "mock-v1.0.0-phase1",
        "is_placeholder": true
    }
    """
    source: str = "ml"
    label: str = ClassifierLabel.UNKNOWN.value
    confidence: float = 0.0
    signals: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    model_version: str = "1.0.0-phase1"
    is_placeholder: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert MLInferenceResult to a JSON-serializable dictionary."""
        return {
            "source": self.source,
            "label": self.label,
            "confidence": round(self.confidence, 4),
            "signals": self.signals,
            "execution_time_ms": self.execution_time_ms,
            "model_version": self.model_version,
            "is_placeholder": self.is_placeholder,
            "metadata": self.metadata
        }


class MLInferenceService:
    """
    Modular ML Inference Service orchestrating email preprocessing,
    feature extraction, and classifier predictions.
    Designed to be queried by backend orchestrators or risk integration layers.
    """

    def __init__(
        self,
        config: Optional[MLConfig] = None,
        preprocessor: Optional[BasePreprocessor] = None,
        feature_extractor: Optional[BaseFeatureExtractor] = None,
        classifier: Optional[BaseClassifier] = None
    ):
        self.config = config or MLConfig()
        self.preprocessor = preprocessor or EmailPreprocessor()
        self.feature_extractor = feature_extractor or EmailFeatureExtractor()
        self.classifier = classifier or MockClassifier(config=self.config)

    def run_inference_pipeline(self, email_input: Any) -> MLInferenceResult:
        """
        Executes explicit 4-stage pipeline:
        Email Input -> Preprocessing -> Feature Extraction -> Classifier -> MLInferenceResult
        """
        start_time = time.perf_counter()

        try:
            # Stage 1: Preprocessing
            processed_email: ProcessedEmail = self.preprocessor.preprocess(email_input)

            # Stage 2: Feature Extraction
            feature_vector: FeatureVector = self.feature_extractor.extract(processed_email)

            # Stage 3: Classifier Verdict Prediction
            if hasattr(self.classifier, "predict_verdict"):
                verdict: ClassifierOutput = self.classifier.predict_verdict(email_input)
            else:
                raw_verdict = self.classifier.classify(email_input)
                if isinstance(raw_verdict, ClassifierOutput):
                    verdict = raw_verdict
                else:
                    verdict = self._convert_prediction_result_to_verdict(raw_verdict)

            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

            # Stage 4: Structured Result Construction
            return MLInferenceResult(
                source="ml",
                label=verdict.label,
                confidence=verdict.confidence,
                signals=verdict.signals,
                execution_time_ms=elapsed_ms,
                model_version=verdict.model_version,
                is_placeholder=verdict.is_placeholder,
                metadata={
                    **verdict.metadata,
                    "url_count": len(processed_email.extracted_urls),
                    "word_count": len(processed_email.tokens),
                    "has_sender": bool(processed_email.sender_email)
                }
            )

        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(f"Error executing MLInferenceService pipeline: {exc}", exc_info=True)

            if self.config.failsafe_fallback_enabled:
                return self._build_failsafe_fallback(str(exc), elapsed_ms)
            raise exc

    def analyze_email(self, email_input: Any) -> MLInferenceResult:
        """Alias for run_inference_pipeline for backward compatibility and backend callers."""
        return self.run_inference_pipeline(email_input)

    def _convert_prediction_result_to_verdict(self, res: MLPredictionResult) -> ClassifierOutput:
        """Helper to convert legacy MLPredictionResult to ClassifierOutput."""
        label_map = {
            ClassificationCategory.MALICIOUS.value: ClassifierLabel.PHISHING.value,
            ClassificationCategory.SUSPICIOUS.value: ClassifierLabel.SUSPICIOUS.value,
            ClassificationCategory.SAFE.value: ClassifierLabel.BENIGN.value,
            ClassificationCategory.UNKNOWN.value: ClassifierLabel.UNKNOWN.value
        }
        label = label_map.get(res.classification, ClassifierLabel.UNKNOWN.value)
        return ClassifierOutput(
            label=label,
            confidence=min(max(res.confidence, 0.0), 1.0),
            signals=res.signals or ["No overt threat indicators detected."],
            model_version=res.model_version,
            is_placeholder=True,
            metadata=res.metadata
        )

    def _build_failsafe_fallback(self, error_message: str, elapsed_ms: float) -> MLInferenceResult:
        """Constructs a safe default MLInferenceResult when analysis fails unexpectedly."""
        return MLInferenceResult(
            source="ml",
            label=ClassifierLabel.UNKNOWN.value,
            confidence=0.0,
            signals=[f"FAILSAFE: {error_message}"],
            execution_time_ms=elapsed_ms,
            model_version=self.config.model.model_version,
            is_placeholder=True,
            metadata={"error": error_message, "failsafe": True}
        )

"""
High-level Inference Service wrapper for MailTrace backend orchestration.
Provides execution latency tracking, fail-safe fallback exception handling,
and single-point entry for email analysis.
"""

import time
import logging
from typing import Any, Dict, Optional
from ..classifiers.email_classifier import EmailClassifier
from ..classifiers.schemas import (
    MLPredictionResult,
    ClassificationCategory,
    SignalVerdict
)
from ..config.ml_config import MLConfig

logger = logging.getLogger("MailTrace.MLInferenceService")


class MLInferenceService:
    """
    Inference Service wrapper designed for production backend usage.
    Handles execution timing, logging, and safe fallback defaults on error.
    """

    def __init__(
        self,
        config: Optional[MLConfig] = None,
        classifier: Optional[EmailClassifier] = None
    ):
        self.config = config or MLConfig()
        self.classifier = classifier or EmailClassifier(config=self.config)

    def analyze_email(self, email_payload: Any) -> MLPredictionResult:
        """
        Main entry point for analyzing an email payload.
        
        Args:
            email_payload: Dict, raw string, or email structure.
            
        Returns:
            MLPredictionResult object containing verdicts, scores, and signals.
        """
        start_time = time.perf_counter()

        try:
            result = self.classifier.classify(email_payload)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            result.execution_time_ms = elapsed_ms
            return result

        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(f"Error during ML inference analysis: {exc}", exc_info=True)

            if self.config.failsafe_fallback_enabled:
                return self._build_failsafe_fallback(str(exc), elapsed_ms)
            raise exc

    def _build_failsafe_fallback(self, error_message: str, elapsed_ms: float) -> MLPredictionResult:
        """Constructs a safe default verdict when analysis fails unexpectedly."""
        dummy_verdict = SignalVerdict(
            signal_name="failsafe_fallback",
            score=0.0,
            confidence=0.0,
            detected=False,
            explanation=f"Failsafe mode activated due to error: {error_message}"
        )

        return MLPredictionResult(
            classification=ClassificationCategory.UNKNOWN.value,
            overall_risk_score=0.0,
            confidence=0.0,
            model_version=self.config.model.model_version,
            phishing_verdict=dummy_verdict,
            suspicious_language_verdict=dummy_verdict,
            social_engineering_verdict=dummy_verdict,
            malicious_content_verdict=dummy_verdict,
            impersonation_verdict=dummy_verdict,
            signals=[f"FAILSAFE: {error_message}"],
            execution_time_ms=elapsed_ms,
            metadata={"error": error_message, "failsafe": True}
        )

"""
Structured schemas and verdicts for ML classification results.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional


class ClassificationCategory(str, Enum):
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    MALICIOUS = "MALICIOUS"
    UNKNOWN = "UNKNOWN"


class ClassifierLabel(str, Enum):
    PHISHING = "phishing"
    SUSPICIOUS = "suspicious"
    BENIGN = "benign"
    UNKNOWN = "unknown"


@dataclass
class ClassifierOutput:
    """
    Standardized, serializable output model for ML classifiers.
    Format:
    {
        "label": "phishing | suspicious | benign | unknown",
        "confidence": 0.85,
        "signals": ["High urgency pressure detected", "Credential harvesting cues present"]
    }
    """
    label: str
    confidence: float
    signals: List[str] = field(default_factory=list)
    model_version: str = "mock-v1.0.0-phase1"
    is_placeholder: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate label enum and confidence bounds [0.0, 1.0]."""
        # Validate confidence score bounds
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence score must be between 0.0 and 1.0, got {self.confidence}")

        # Normalize label string if valid
        valid_labels = {item.value for item in ClassifierLabel}
        if self.label.lower() in valid_labels:
            self.label = self.label.lower()

    def to_dict(self) -> Dict[str, Any]:
        """Convert ClassifierOutput to serializable dictionary."""
        return {
            "label": self.label,
            "confidence": round(self.confidence, 4),
            "signals": self.signals,
            "model_version": self.model_version,
            "is_placeholder": self.is_placeholder,
            "metadata": self.metadata
        }


@dataclass
class SignalVerdict:
    """Individual security threat signal breakdown."""
    signal_name: str
    score: float
    confidence: float
    detected: bool
    explanation: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MLPredictionResult:
    """Master output schema from the ML module to backend services."""
    classification: str  # SAFE | SUSPICIOUS | MALICIOUS | UNKNOWN
    overall_risk_score: float
    confidence: float
    model_version: str
    phishing_verdict: SignalVerdict
    suspicious_language_verdict: SignalVerdict
    social_engineering_verdict: SignalVerdict
    malicious_content_verdict: SignalVerdict
    impersonation_verdict: SignalVerdict
    signals: List[str] = field(default_factory=list)
    execution_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert MLPredictionResult to JSON-serializable dictionary."""
        return {
            "classification": self.classification,
            "overall_risk_score": self.overall_risk_score,
            "confidence": self.confidence,
            "model_version": self.model_version,
            "signals": self.signals,
            "execution_time_ms": self.execution_time_ms,
            "verdicts": {
                "phishing": self.phishing_verdict.__dict__,
                "suspicious_language": self.suspicious_language_verdict.__dict__,
                "social_engineering": self.social_engineering_verdict.__dict__,
                "malicious_content": self.malicious_content_verdict.__dict__,
                "impersonation": self.impersonation_verdict.__dict__
            },
            "metadata": self.metadata
        }

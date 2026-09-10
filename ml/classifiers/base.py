"""
Base abstract classifier interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Union
from .schemas import MLPredictionResult, ClassifierOutput


class BaseClassifier(ABC):
    """
    Abstract Base Class for high-level email security classifiers.
    Enforces unified prediction interfaces for future trained models.
    """

    @abstractmethod
    def classify(self, email_input: Any) -> Union[ClassifierOutput, MLPredictionResult]:
        """
        Runs full email classification pipeline.
        
        Returns:
            ClassifierOutput or MLPredictionResult containing label, confidence, and signals.
        """
        pass

    @abstractmethod
    def predict_verdict(self, email_input: Any) -> ClassifierOutput:
        """
        Returns standardized ClassifierOutput dictionary containing:
        {
            "label": "phishing | suspicious | benign | unknown",
            "confidence": 0.85,
            "signals": ["..."]
        }
        """
        pass

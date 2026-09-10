"""
Base abstract classifier interface.
"""

from abc import ABC, abstractmethod
from typing import Any
from .schemas import MLPredictionResult


class BaseClassifier(ABC):
    """
    Abstract Base Class for high-level email security classifiers.
    """

    @abstractmethod
    def classify(self, email_input: Any) -> MLPredictionResult:
        """
        Runs full pre-processing, feature extraction, and multi-signal model prediction
        to generate an MLPredictionResult.
        """
        pass

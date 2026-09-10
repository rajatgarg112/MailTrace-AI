"""
Abstract base class defining the model interface contract.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional
from ..features.base import FeatureVector


class BaseModel(ABC):
    """
    Standard interface for all ML models in MailTrace AI.
    Future trained models (scikit-learn, PyTorch, HuggingFace transformers, XGBoost)
    must implement this interface.
    """

    @abstractmethod
    def predict(self, feature_vector: FeatureVector) -> int:
        """
        Predict binary or multi-class class label index (0=Benign, 1=Suspicious, 2=Phishing).
        """
        pass

    @abstractmethod
    def predict_proba(self, feature_vector: FeatureVector) -> Dict[str, float]:
        """
        Predict probability distribution across target categories/classes.
        Returns e.g. {"benign": 0.1, "suspicious": 0.3, "phishing": 0.6}
        """
        pass

    def is_placeholder(self) -> bool:
        """
        Returns True if this model is a mock/placeholder implementation.
        Trained production models should return False.
        """
        return False

    @abstractmethod
    def save(self, filepath: str) -> bool:
        """Serialize model weights/artifacts to disk."""
        pass

    @abstractmethod
    def load(self, filepath: str) -> bool:
        """Deserialize model weights/artifacts from disk."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Return model metadata (name, version, parameters, training date)."""
        pass

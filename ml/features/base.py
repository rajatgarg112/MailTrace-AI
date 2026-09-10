"""
Base interfaces and vector schemas for Feature Extractors.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Union
from ..preprocessing.base import ProcessedEmail


@dataclass
class FeatureVector:
    """Standardized representation of extracted features."""
    numerical_features: Dict[str, float] = field(default_factory=dict)
    categorical_features: Dict[str, str] = field(default_factory=dict)
    boolean_features: Dict[str, bool] = field(default_factory=dict)
    signal_counts: Dict[str, int] = field(default_factory=dict)
    feature_names: List[str] = field(default_factory=list)
    raw_vector: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Flatten features into a single dictionary."""
        merged = {}
        merged.update(self.numerical_features)
        merged.update(self.categorical_features)
        merged.update(self.boolean_features)
        merged.update(self.signal_counts)
        return merged


class BaseFeatureExtractor(ABC):
    """Abstract Base Class for Feature Extractors."""

    @abstractmethod
    def extract(self, processed_email: ProcessedEmail) -> FeatureVector:
        """
        Extract features from a processed email.
        
        Args:
            processed_email: Normalized ProcessedEmail dataclass.
            
        Returns:
            FeatureVector containing numeric/boolean/categorical features.
        """
        pass

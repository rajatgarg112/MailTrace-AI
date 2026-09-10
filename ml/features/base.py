"""
Base interfaces and vector schemas for Feature Extractors.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import json
from typing import Dict, List, Any, Union
from ..preprocessing.base import ProcessedEmail


@dataclass
class FeatureVector:
    """Standardized, serializable representation of extracted features for ML models."""
    numerical_features: Dict[str, float] = field(default_factory=dict)
    categorical_features: Dict[str, str] = field(default_factory=dict)
    boolean_features: Dict[str, bool] = field(default_factory=dict)
    signal_counts: Dict[str, int] = field(default_factory=dict)
    feature_names: List[str] = field(default_factory=list)
    raw_vector: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Flatten features into a single serializable dictionary."""
        merged: Dict[str, Any] = {}
        merged.update(self.numerical_features)
        merged.update(self.categorical_features)
        merged.update(self.boolean_features)
        merged.update(self.signal_counts)
        return merged

    def to_json(self) -> str:
        """Serialize FeatureVector to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def to_flat_vector(self) -> List[float]:
        """Returns ordered numerical feature values for vector-based ML models."""
        if self.raw_vector:
            return self.raw_vector
        vec = []
        for name in self.feature_names:
            if name in self.numerical_features:
                vec.append(float(self.numerical_features[name]))
            elif name in self.signal_counts:
                vec.append(float(self.signal_counts[name]))
            elif name in self.boolean_features:
                vec.append(1.0 if self.boolean_features[name] else 0.0)
        return vec


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

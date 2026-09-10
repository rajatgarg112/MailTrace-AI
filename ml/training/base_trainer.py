"""
Abstract base class defining training pipeline interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional


class BaseTrainer(ABC):
    """
    Abstract interface for model training components.
    Future Phase 2 trainers (e.g. ScikitLearnTrainer, PyTorchTrainer) implement this.
    """

    @abstractmethod
    def train(self, train_data: Any, validation_data: Optional[Any] = None) -> Dict[str, float]:
        """Runs model training loop and returns training metrics."""
        pass

    @abstractmethod
    def evaluate(self, test_data: Any) -> Dict[str, float]:
        """Evaluates model performance on test dataset."""
        pass

    @abstractmethod
    def export_artifacts(self, export_dir: str) -> str:
        """Exports trained model weights and feature vocabularies to disk."""
        pass

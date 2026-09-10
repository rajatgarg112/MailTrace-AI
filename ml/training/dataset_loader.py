"""
Dataset loading interface and placeholder implementation for email security datasets.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional


@dataclass
class DatasetSplit:
    """Encapsulates dataset features and ground truth labels."""
    inputs: List[Dict[str, Any]]
    labels: List[int]
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseDatasetLoader(ABC):
    """Abstract interface for dataset loaders."""

    @abstractmethod
    def load_dataset(self, data_path: str) -> Tuple[DatasetSplit, DatasetSplit, DatasetSplit]:
        """
        Loads dataset and returns (train_split, val_split, test_split).
        """
        pass


class EmailDatasetLoader(BaseDatasetLoader):
    """
    Placeholder dataset loader for loading raw email samples from JSON/CSV files in Phase 2.
    """

    def load_dataset(self, data_path: str) -> Tuple[DatasetSplit, DatasetSplit, DatasetSplit]:
        # Return mock split for Phase 1 architecture verification
        mock_inputs = [
            {"subject": "Urgent update", "body_text": "Please verify account credentials now."},
            {"subject": "Meeting notes", "body_text": "Hi team, here are the notes from today."}
        ]
        mock_labels = [1, 0]

        train_split = DatasetSplit(inputs=mock_inputs, labels=mock_labels)
        val_split = DatasetSplit(inputs=mock_inputs[:1], labels=mock_labels[:1])
        test_split = DatasetSplit(inputs=mock_inputs[1:], labels=mock_labels[1:])

        return train_split, val_split, test_split

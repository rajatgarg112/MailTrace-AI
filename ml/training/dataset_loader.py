"""
Dataset loading interface and implementation for email security datasets.
Reads dataset splits (train, val, test) from file system or provides safe stubs.
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
from ..config.training_config import TrainingConfig


@dataclass
class DatasetSplit:
    """Encapsulates dataset features, inputs, and ground truth labels."""
    name: str
    inputs: List[Dict[str, Any]]
    labels: List[int]
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseDatasetLoader(ABC):
    """Abstract interface for dataset loaders."""

    @abstractmethod
    def load_dataset(self, config: Optional[TrainingConfig] = None) -> Tuple[DatasetSplit, DatasetSplit, DatasetSplit]:
        """
        Loads dataset and returns (train_split, val_split, test_split).
        """
        pass


class EmailDatasetLoader(BaseDatasetLoader):
    """
    Dataset loader for loading raw email samples from train/val/test directories.
    Provides safe stubs if dataset files are missing during Phase 1 development.
    """

    def load_dataset(self, config: Optional[TrainingConfig] = None) -> Tuple[DatasetSplit, DatasetSplit, DatasetSplit]:
        cfg = config or TrainingConfig()

        train_split = self._load_split("train", cfg.train_data_dir)
        val_split = self._load_split("val", cfg.val_data_dir)
        test_split = self._load_split("test", cfg.test_data_dir)

        return train_split, val_split, test_split

    def _load_split(self, split_name: str, directory_path: str) -> DatasetSplit:
        """Loads split from directory if files exist, otherwise returns safe placeholder split."""
        if os.path.exists(directory_path) and any(os.path.isfile(os.path.join(directory_path, f)) for f in os.listdir(directory_path) if not f.startswith('.')):
            # Future Phase 2 dataset loading logic
            return DatasetSplit(name=split_name, inputs=[], labels=[], metadata={"directory": directory_path, "status": "loaded"})

        # Safe Phase 1 placeholder split
        mock_inputs = [
            {"subject": "Urgent update", "body_text": "Please verify account credentials now."},
            {"subject": "Meeting notes", "body_text": "Hi team, here are the notes from today."}
        ]
        mock_labels = [1, 0]

        return DatasetSplit(
            name=split_name,
            inputs=mock_inputs,
            labels=mock_labels,
            metadata={"directory": directory_path, "placeholder": True}
        )

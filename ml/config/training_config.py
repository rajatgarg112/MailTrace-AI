"""
Configuration model for offline model training pipelines.
Provides safe placeholder default values for dataset directories and training hyperparameters.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class TrainingConfig:
    """Safe placeholder configuration for future model training pipelines."""
    dataset_name: str = "placeholder_email_dataset"
    train_data_dir: str = "ml/data/train/"
    val_data_dir: str = "ml/data/val/"
    test_data_dir: str = "ml/data/test/"
    artifact_export_dir: str = "ml/artifacts/"
    model_architecture: str = "tfidf_xgboost_placeholder"
    epochs: int = 1
    batch_size: int = 16
    learning_rate: float = 0.001
    random_seed: int = 42
    save_artifacts: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "TrainingConfig":
        """Factory method to construct TrainingConfig from a dictionary."""
        return cls(
            dataset_name=config_dict.get("dataset_name", "placeholder_email_dataset"),
            train_data_dir=config_dict.get("train_data_dir", "ml/data/train/"),
            val_data_dir=config_dict.get("val_data_dir", "ml/data/val/"),
            test_data_dir=config_dict.get("test_data_dir", "ml/data/test/"),
            artifact_export_dir=config_dict.get("artifact_export_dir", "ml/artifacts/"),
            model_architecture=config_dict.get("model_architecture", "tfidf_xgboost_placeholder"),
            epochs=config_dict.get("epochs", 1),
            batch_size=config_dict.get("batch_size", 16),
            learning_rate=config_dict.get("learning_rate", 0.001),
            random_seed=config_dict.get("random_seed", 42),
            save_artifacts=config_dict.get("save_artifacts", True),
            metadata=config_dict.get("metadata", {})
        )

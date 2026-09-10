"""
Configuration models for MailTrace AI ML components.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import os


@dataclass
class ModelConfig:
    """Model-specific configuration settings."""
    model_name: str = "placeholder_detector"
    model_version: str = "1.0.0-phase1"
    artifact_path: Optional[str] = None
    threshold_suspicious: float = 0.40
    threshold_malicious: float = 0.70
    max_sequence_length: int = 512
    batch_size: int = 16


@dataclass
class FeatureConfig:
    """Feature extraction configuration settings."""
    enable_keyword_matching: bool = True
    enable_text_statistics: bool = True
    enable_embeddings: bool = False
    max_features: int = 1000
    n_gram_range: tuple = (1, 2)


@dataclass
class MLConfig:
    """Master configuration for the ML module."""
    model: ModelConfig = field(default_factory=ModelConfig)
    features: FeatureConfig = field(default_factory=FeatureConfig)
    environment: str = "development"
    debug_mode: bool = False
    failsafe_fallback_enabled: bool = True
    timeout_ms: float = 2000.0

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "MLConfig":
        """Factory method to construct MLConfig from a dictionary."""
        model_dict = config_dict.get("model", {})
        feat_dict = config_dict.get("features", {})
        
        return cls(
            model=ModelConfig(**model_dict),
            features=FeatureConfig(**feat_dict),
            environment=config_dict.get("environment", "development"),
            debug_mode=config_dict.get("debug_mode", False),
            failsafe_fallback_enabled=config_dict.get("failsafe_fallback_enabled", True),
            timeout_ms=config_dict.get("timeout_ms", 2000.0)
        )

"""
Base classes for ML models in the AI Employee system.

Provides common functionality for model training, prediction, and management.
"""

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class MLModelConfig:
    """Configuration for ML models."""
    model_name: str
    model_version: str
    model_type: str  # 'classifier', 'regressor', 'clusterer'
    created_at: str
    last_trained: Optional[str] = None
    training_samples: int = 0
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    feature_names: Optional[List[str]] = None
    hyperparameters: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MLModelConfig':
        """Create config from dictionary."""
        return cls(**data)

    def save(self, path: Path) -> None:
        """Save config to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> 'MLModelConfig':
        """Load config from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


class BaseMLModel(ABC):
    """Base class for all ML models in the AI Employee system."""

    def __init__(self, vault_path: str, model_name: str):
        """
        Initialize base ML model.

        Args:
            vault_path: Path to AI_Employee_Vault
            model_name: Name of the model (e.g., 'email_classifier')
        """
        self.vault_path = Path(vault_path)
        self.model_name = model_name
        self.model_dir = self.vault_path / "ML_Models" / model_name
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.model = None
        self.config: Optional[MLModelConfig] = None
        self.is_trained = False

        # Try to load existing model
        self._load_model()

    @abstractmethod
    def train(self, training_data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Train the model on provided data.

        Args:
            training_data: List of training examples
            **kwargs: Additional training parameters

        Returns:
            Dictionary with training metrics
        """
        pass

    @abstractmethod
    def predict(self, input_data: Any) -> Any:
        """
        Make prediction on input data.

        Args:
            input_data: Input for prediction

        Returns:
            Prediction result
        """
        pass

    @abstractmethod
    def _save_model(self) -> None:
        """Save model to disk."""
        pass

    @abstractmethod
    def _load_model(self) -> bool:
        """
        Load model from disk.

        Returns:
            True if model loaded successfully, False otherwise
        """
        pass

    def get_model_path(self, filename: str) -> Path:
        """Get full path for model file."""
        return self.model_dir / filename

    def save_config(self) -> None:
        """Save model configuration."""
        if self.config:
            config_path = self.get_model_path("config.json")
            self.config.save(config_path)
            logger.info(f"Saved config for {self.model_name}")

    def load_config(self) -> bool:
        """
        Load model configuration.

        Returns:
            True if config loaded successfully, False otherwise
        """
        config_path = self.get_model_path("config.json")
        if config_path.exists():
            try:
                self.config = MLModelConfig.load(config_path)
                logger.info(f"Loaded config for {self.model_name}")
                return True
            except Exception as e:
                logger.error(f"Error loading config for {self.model_name}: {e}")
                return False
        return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get model performance metrics."""
        if not self.config:
            return {}

        return {
            'model_name': self.config.model_name,
            'model_version': self.config.model_version,
            'is_trained': self.is_trained,
            'training_samples': self.config.training_samples,
            'accuracy': self.config.accuracy,
            'precision': self.config.precision,
            'recall': self.config.recall,
            'f1_score': self.config.f1_score,
            'last_trained': self.config.last_trained,
        }

    def validate_input(self, input_data: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate input data before prediction.

        Args:
            input_data: Input to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.is_trained:
            return False, "Model is not trained"

        if input_data is None:
            return False, "Input data is None"

        return True, None

    def get_training_data_path(self) -> Path:
        """Get path to training data directory."""
        return self.vault_path / "ML_Models" / "training_data" / self.model_name

    def ensure_training_data_dir(self) -> None:
        """Ensure training data directory exists."""
        training_dir = self.get_training_data_path()
        training_dir.mkdir(parents=True, exist_ok=True)

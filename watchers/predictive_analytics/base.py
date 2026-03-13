"""
Base classes for Predictive Analytics models.

Provides common functionality for time-series forecasting and predictive models.
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PredictionConfig:
    """Configuration for predictive models."""
    model_name: str
    model_version: str
    prediction_type: str  # 'time_series', 'classification', 'regression'
    created_at: str
    last_trained: Optional[str] = None
    training_samples: int = 0
    forecast_horizon: int = 30  # days
    confidence_interval: float = 0.95
    metrics: Optional[Dict[str, float]] = None
    hyperparameters: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PredictionConfig':
        """Create config from dictionary."""
        return cls(**data)

    def save(self, path: Path) -> None:
        """Save config to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> 'PredictionConfig':
        """Load config from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass
class Prediction:
    """A single prediction result."""
    timestamp: str
    predicted_value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    confidence: float = 0.95
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ForecastResult:
    """Result of a forecasting operation."""
    model_name: str
    forecast_start: str
    forecast_end: str
    predictions: List[Prediction]
    metrics: Dict[str, float]
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'model_name': self.model_name,
            'forecast_start': self.forecast_start,
            'forecast_end': self.forecast_end,
            'predictions': [p.to_dict() for p in self.predictions],
            'metrics': self.metrics,
            'metadata': self.metadata
        }


class BasePredictiveModel(ABC):
    """Base class for all predictive analytics models."""

    def __init__(self, vault_path: str, model_name: str):
        """
        Initialize base predictive model.

        Args:
            vault_path: Path to AI_Employee_Vault
            model_name: Name of the model
        """
        self.vault_path = Path(vault_path)
        self.model_name = model_name
        self.model_dir = self.vault_path / "Predictive_Analytics" / model_name
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.model = None
        self.config: Optional[PredictionConfig] = None
        self.is_trained = False
        self.historical_data: List[Dict[str, Any]] = []

        # Try to load existing model
        self._load_model()

    @abstractmethod
    def train(self, historical_data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Train the predictive model.

        Args:
            historical_data: Historical data for training
            **kwargs: Additional training parameters

        Returns:
            Dictionary with training metrics
        """
        pass

    @abstractmethod
    def predict(self, forecast_horizon: int = 30, **kwargs) -> ForecastResult:
        """
        Make predictions.

        Args:
            forecast_horizon: Number of days to forecast
            **kwargs: Additional prediction parameters

        Returns:
            ForecastResult with predictions
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
                self.config = PredictionConfig.load(config_path)
                logger.info(f"Loaded config for {self.model_name}")
                return True
            except Exception as e:
                logger.error(f"Error loading config for {self.model_name}: {e}")
                return False
        return False

    def save_historical_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Save historical data for future training.

        Args:
            data: Historical data to save
        """
        data_path = self.get_model_path("historical_data.json")
        try:
            with open(data_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved historical data for {self.model_name}")
        except Exception as e:
            logger.error(f"Error saving historical data: {e}")

    def load_historical_data(self) -> List[Dict[str, Any]]:
        """
        Load historical data.

        Returns:
            List of historical data points
        """
        data_path = self.get_model_path("historical_data.json")
        if data_path.exists():
            try:
                with open(data_path, 'r') as f:
                    data = json.load(f)
                logger.info(f"Loaded {len(data)} historical data points for {self.model_name}")
                return data
            except Exception as e:
                logger.error(f"Error loading historical data: {e}")
                return []
        return []

    def get_metrics(self) -> Dict[str, Any]:
        """Get model performance metrics."""
        if not self.config:
            return {}

        return {
            'model_name': self.config.model_name,
            'model_version': self.config.model_version,
            'is_trained': self.is_trained,
            'training_samples': self.config.training_samples,
            'forecast_horizon': self.config.forecast_horizon,
            'metrics': self.config.metrics or {},
            'last_trained': self.config.last_trained,
        }

    def validate_historical_data(self, data: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """
        Validate historical data before training.

        Args:
            data: Historical data to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not data:
            return False, "No historical data provided"

        if len(data) < 10:
            return False, f"Need at least 10 data points, got {len(data)}"

        # Check for required fields
        required_fields = ['timestamp', 'value']
        for i, item in enumerate(data):
            for field in required_fields:
                if field not in item:
                    return False, f"Missing '{field}' in data point {i}"

        return True, None

    def generate_date_range(self, start_date: datetime, days: int) -> List[str]:
        """
        Generate list of dates for forecasting.

        Args:
            start_date: Starting date
            days: Number of days

        Returns:
            List of date strings in ISO format
        """
        dates = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            dates.append(date.isoformat())
        return dates

    def calculate_confidence_interval(
        self,
        predictions: np.ndarray,
        confidence: float = 0.95
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate confidence intervals for predictions.

        Args:
            predictions: Array of predictions
            confidence: Confidence level (0-1)

        Returns:
            Tuple of (lower_bounds, upper_bounds)
        """
        # Simple approach: use standard deviation
        std = np.std(predictions)
        margin = std * 1.96  # 95% confidence interval

        lower_bounds = predictions - margin
        upper_bounds = predictions + margin

        return lower_bounds, upper_bounds

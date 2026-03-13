"""
Model Manager for centralized ML model management.

Handles model lifecycle, versioning, and coordination.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base import BaseMLModel

logger = logging.getLogger(__name__)


class ModelManager:
    """Centralized manager for all ML models."""

    def __init__(self, vault_path: str):
        """
        Initialize Model Manager.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.vault_path = Path(vault_path)
        self.models: Dict[str, BaseMLModel] = {}
        self.ml_models_dir = self.vault_path / "ML_Models"
        self.ml_models_dir.mkdir(parents=True, exist_ok=True)

    def register_model(self, model_name: str, model: BaseMLModel) -> None:
        """
        Register a model with the manager.

        Args:
            model_name: Name of the model
            model: Model instance
        """
        self.models[model_name] = model
        logger.info(f"Registered model: {model_name}")

    def get_model(self, model_name: str) -> Optional[BaseMLModel]:
        """
        Get a registered model.

        Args:
            model_name: Name of the model

        Returns:
            Model instance or None if not found
        """
        return self.models.get(model_name)

    def list_models(self) -> List[str]:
        """
        List all registered models.

        Returns:
            List of model names
        """
        return list(self.models.keys())

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics for all registered models.

        Returns:
            Dictionary mapping model names to their metrics
        """
        metrics = {}
        for model_name, model in self.models.items():
            metrics[model_name] = model.get_metrics()
        return metrics

    def get_trained_models(self) -> List[str]:
        """
        Get list of trained models.

        Returns:
            List of trained model names
        """
        return [name for name, model in self.models.items() if model.is_trained]

    def get_untrained_models(self) -> List[str]:
        """
        Get list of untrained models.

        Returns:
            List of untrained model names
        """
        return [name for name, model in self.models.items() if not model.is_trained]

    def train_all_models(self, training_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        """
        Train all registered models with provided data.

        Args:
            training_data: Dictionary mapping model names to their training data

        Returns:
            Dictionary mapping model names to training results
        """
        results = {}
        for model_name, model in self.models.items():
            if model_name in training_data:
                try:
                    logger.info(f"Training model: {model_name}")
                    result = model.train(training_data[model_name])
                    results[model_name] = {
                        'success': True,
                        'metrics': result
                    }
                except Exception as e:
                    logger.error(f"Error training {model_name}: {e}")
                    results[model_name] = {
                        'success': False,
                        'error': str(e)
                    }
            else:
                logger.warning(f"No training data provided for {model_name}")
                results[model_name] = {
                    'success': False,
                    'error': 'No training data provided'
                }
        return results

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall ML system status.

        Returns:
            Dictionary with system status information
        """
        total_models = len(self.models)
        trained_models = len(self.get_trained_models())
        untrained_models = len(self.get_untrained_models())

        return {
            'total_models': total_models,
            'trained_models': trained_models,
            'untrained_models': untrained_models,
            'training_percentage': (trained_models / total_models * 100) if total_models > 0 else 0,
            'models': self.get_all_metrics(),
            'timestamp': datetime.now().isoformat()
        }

    def save_all_models(self) -> Dict[str, bool]:
        """
        Save all registered models.

        Returns:
            Dictionary mapping model names to save success status
        """
        results = {}
        for model_name, model in self.models.items():
            try:
                model._save_model()
                model.save_config()
                results[model_name] = True
                logger.info(f"Saved model: {model_name}")
            except Exception as e:
                logger.error(f"Error saving {model_name}: {e}")
                results[model_name] = False
        return results

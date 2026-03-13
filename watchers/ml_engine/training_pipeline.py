"""
ML Training Pipeline

Manages the complete training lifecycle for all ML models.
Handles data collection, training, evaluation, and model versioning.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import sys

from .model_manager import ModelManager
from .email_classifier import EmailClassifier
from .task_predictor import TaskPredictor
from .expense_categorizer import ExpenseCategorizer
from .content_optimizer import ContentOptimizer

logger = logging.getLogger(__name__)


class TrainingPipeline:
    """Manages ML model training pipeline."""

    def __init__(self, vault_path: str):
        """
        Initialize Training Pipeline.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.vault_path = Path(vault_path)
        self.manager = ModelManager(str(vault_path))

        # Initialize all models
        self.email_classifier = EmailClassifier(str(vault_path))
        self.task_predictor = TaskPredictor(str(vault_path))
        self.expense_categorizer = ExpenseCategorizer(str(vault_path))
        self.content_optimizer = ContentOptimizer(str(vault_path))

        # Register models
        self.manager.register_model('email_classifier', self.email_classifier)
        self.manager.register_model('task_predictor', self.task_predictor)
        self.manager.register_model('expense_categorizer', self.expense_categorizer)
        self.manager.register_model('content_optimizer', self.content_optimizer)

        # Training history
        self.training_history_path = self.vault_path / "ML_Models" / "training_history.json"
        self.training_history: List[Dict[str, Any]] = []
        self._load_training_history()

    def _load_training_history(self) -> None:
        """Load training history from disk."""
        if self.training_history_path.exists():
            try:
                with open(self.training_history_path, 'r') as f:
                    self.training_history = json.load(f)
                logger.info(f"Loaded {len(self.training_history)} training records")
            except Exception as e:
                logger.error(f"Error loading training history: {e}")
                self.training_history = []

    def _save_training_history(self) -> None:
        """Save training history to disk."""
        try:
            with open(self.training_history_path, 'w') as f:
                json.dump(self.training_history, f, indent=2)
            logger.info("Saved training history")
        except Exception as e:
            logger.error(f"Error saving training history: {e}")

    def collect_training_data(self, use_sample_data: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        Collect training data for all models.

        Args:
            use_sample_data: If True, use generated sample data

        Returns:
            Dictionary mapping model names to training data
        """
        training_data = {}

        if use_sample_data:
            logger.info("Generating sample training data")
            training_data['email_classifier'] = self.email_classifier.generate_sample_training_data(50)
            training_data['task_predictor'] = self.task_predictor.generate_sample_training_data(50)
            training_data['expense_categorizer'] = self.expense_categorizer.generate_sample_training_data(50)
            training_data['content_optimizer'] = self.content_optimizer.generate_sample_training_data(50)
        else:
            # TODO: Implement real data collection from vault
            logger.info("Collecting real training data from vault")
            training_data['email_classifier'] = self._collect_email_data()
            training_data['task_predictor'] = self._collect_task_data()
            training_data['expense_categorizer'] = self._collect_expense_data()
            training_data['content_optimizer'] = self._collect_content_data()

        return training_data

    def _collect_email_data(self) -> List[Dict[str, Any]]:
        """Collect email training data from vault."""
        # TODO: Implement real email data collection
        logger.warning("Real email data collection not implemented, using sample data")
        return self.email_classifier.generate_sample_training_data(50)

    def _collect_task_data(self) -> List[Dict[str, Any]]:
        """Collect task training data from vault."""
        # TODO: Implement real task data collection
        logger.warning("Real task data collection not implemented, using sample data")
        return self.task_predictor.generate_sample_training_data(50)

    def _collect_expense_data(self) -> List[Dict[str, Any]]:
        """Collect expense training data from vault."""
        # TODO: Implement real expense data collection
        logger.warning("Real expense data collection not implemented, using sample data")
        return self.expense_categorizer.generate_sample_training_data(50)

    def _collect_content_data(self) -> List[Dict[str, Any]]:
        """Collect content training data from vault."""
        # TODO: Implement real content data collection
        logger.warning("Real content data collection not implemented, using sample data")
        return self.content_optimizer.generate_sample_training_data(50)

    def train_all_models(self, use_sample_data: bool = True) -> Dict[str, Any]:
        """
        Train all ML models.

        Args:
            use_sample_data: If True, use generated sample data

        Returns:
            Dictionary with training results
        """
        logger.info("Starting training pipeline")
        start_time = datetime.now()

        # Collect training data
        training_data = self.collect_training_data(use_sample_data)

        # Train all models
        results = self.manager.train_all_models(training_data)

        # Record training session
        training_record = {
            'timestamp': start_time.isoformat(),
            'duration_seconds': (datetime.now() - start_time).total_seconds(),
            'use_sample_data': use_sample_data,
            'results': results,
            'system_status': self.manager.get_system_status()
        }
        self.training_history.append(training_record)
        self._save_training_history()

        logger.info(f"Training pipeline completed in {training_record['duration_seconds']:.2f}s")

        return training_record

    def train_single_model(self, model_name: str, training_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Train a single model.

        Args:
            model_name: Name of the model to train
            training_data: Training data (if None, will collect automatically)

        Returns:
            Dictionary with training results
        """
        model = self.manager.get_model(model_name)
        if not model:
            raise ValueError(f"Model not found: {model_name}")

        logger.info(f"Training model: {model_name}")
        start_time = datetime.now()

        # Get training data
        if training_data is None:
            all_data = self.collect_training_data(use_sample_data=True)
            training_data = all_data.get(model_name, [])

        if not training_data:
            raise ValueError(f"No training data available for {model_name}")

        # Train model
        try:
            metrics = model.train(training_data)
            success = True
            error = None
        except Exception as e:
            logger.error(f"Error training {model_name}: {e}")
            metrics = {}
            success = False
            error = str(e)

        # Record training
        training_record = {
            'timestamp': start_time.isoformat(),
            'model_name': model_name,
            'duration_seconds': (datetime.now() - start_time).total_seconds(),
            'success': success,
            'metrics': metrics,
            'error': error
        }
        self.training_history.append(training_record)
        self._save_training_history()

        return training_record

    def evaluate_all_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Evaluate all trained models.

        Returns:
            Dictionary with evaluation results for each model
        """
        logger.info("Evaluating all models")
        return self.manager.get_all_metrics()

    def get_training_status(self) -> Dict[str, Any]:
        """
        Get current training status.

        Returns:
            Dictionary with training status information
        """
        system_status = self.manager.get_system_status()

        # Get latest training record
        latest_training = None
        if self.training_history:
            latest_training = self.training_history[-1]

        return {
            'system_status': system_status,
            'latest_training': latest_training,
            'total_training_sessions': len(self.training_history),
            'models': {
                'total': system_status['total_models'],
                'trained': system_status['trained_models'],
                'untrained': system_status['untrained_models'],
                'training_percentage': system_status['training_percentage']
            }
        }

    def retrain_model(self, model_name: str, new_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Retrain a model with new data.

        Args:
            model_name: Name of the model to retrain
            new_data: New training data

        Returns:
            Dictionary with retraining results
        """
        logger.info(f"Retraining model: {model_name}")
        return self.train_single_model(model_name, new_data)

    def export_models(self, export_path: Optional[Path] = None) -> Dict[str, bool]:
        """
        Export all trained models.

        Args:
            export_path: Path to export models (if None, uses default location)

        Returns:
            Dictionary mapping model names to export success status
        """
        logger.info("Exporting all models")
        return self.manager.save_all_models()

    def get_model_recommendations(self) -> List[str]:
        """
        Get recommendations for model improvements.

        Returns:
            List of recommendation strings
        """
        recommendations = []
        metrics = self.manager.get_all_metrics()

        for model_name, model_metrics in metrics.items():
            if not model_metrics.get('is_trained'):
                recommendations.append(f"Train {model_name} - model is not trained yet")
            elif model_metrics.get('training_samples', 0) < 100:
                recommendations.append(f"Collect more training data for {model_name} - currently only {model_metrics['training_samples']} samples")
            elif model_metrics.get('accuracy', 0) < 0.7:
                recommendations.append(f"Improve {model_name} accuracy - currently {model_metrics['accuracy']:.2%}")

        if not recommendations:
            recommendations.append("All models are performing well!")

        return recommendations


def main():
    """Main function for running training pipeline from command line."""
    import argparse

    parser = argparse.ArgumentParser(description='ML Training Pipeline')
    parser.add_argument('--vault-path', default='AI_Employee_Vault', help='Path to AI Employee Vault')
    parser.add_argument('--train-all', action='store_true', help='Train all models')
    parser.add_argument('--train-model', type=str, help='Train specific model')
    parser.add_argument('--evaluate', action='store_true', help='Evaluate all models')
    parser.add_argument('--status', action='store_true', help='Show training status')
    parser.add_argument('--use-real-data', action='store_true', help='Use real data instead of sample data')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize pipeline
    pipeline = TrainingPipeline(args.vault_path)

    if args.train_all:
        print("Training all models...")
        results = pipeline.train_all_models(use_sample_data=not args.use_real_data)
        print(json.dumps(results, indent=2))

    elif args.train_model:
        print(f"Training model: {args.train_model}")
        results = pipeline.train_single_model(args.train_model)
        print(json.dumps(results, indent=2))

    elif args.evaluate:
        print("Evaluating all models...")
        results = pipeline.evaluate_all_models()
        print(json.dumps(results, indent=2))

    elif args.status:
        print("Training status:")
        status = pipeline.get_training_status()
        print(json.dumps(status, indent=2))
        print("\nRecommendations:")
        for rec in pipeline.get_model_recommendations():
            print(f"  - {rec}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()

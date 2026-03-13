"""
Task Priority Prediction Model

Predicts task priority (high, medium, low) based on task description, context, and metadata.
Uses Random Forest classifier for robust predictions.
"""

import logging
import joblib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np

from .base import BaseMLModel, MLModelConfig

logger = logging.getLogger(__name__)


class TaskPredictor(BaseMLModel):
    """ML model for task priority prediction."""

    PRIORITIES = ['high', 'medium', 'low']

    def __init__(self, vault_path: str):
        """
        Initialize Task Predictor.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.vectorizer = None
        super().__init__(vault_path, 'task_predictor')

    def _extract_features(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features from task data.

        Args:
            task_data: Task information

        Returns:
            Dictionary of extracted features
        """
        features = {
            'text': task_data.get('description', ''),
            'has_deadline': 1 if task_data.get('deadline') else 0,
            'word_count': len(task_data.get('description', '').split()),
            'has_urgent_keywords': 1 if any(
                keyword in task_data.get('description', '').lower()
                for keyword in ['urgent', 'asap', 'critical', 'emergency', 'immediately']
            ) else 0,
            'estimated_hours': task_data.get('estimated_hours', 1),
            'dependencies_count': len(task_data.get('dependencies', [])),
        }
        return features

    def train(self, training_data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Train the task priority predictor.

        Args:
            training_data: List of dicts with task info and 'priority' label
            **kwargs: Additional training parameters

        Returns:
            Dictionary with training metrics
        """
        if len(training_data) < 15:
            raise ValueError("Need at least 15 training examples")

        # Extract features
        texts = []
        numeric_features = []
        labels = []

        for item in training_data:
            features = self._extract_features(item)
            texts.append(features['text'])
            numeric_features.append([
                features['has_deadline'],
                features['word_count'],
                features['has_urgent_keywords'],
                features['estimated_hours'],
                features['dependencies_count']
            ])
            labels.append(item['priority'])

        # Validate priorities
        invalid_priorities = set(labels) - set(self.PRIORITIES)
        if invalid_priorities:
            raise ValueError(f"Invalid priorities: {invalid_priorities}")

        # Split data
        X_text_train, X_text_test, X_num_train, X_num_test, y_train, y_test = train_test_split(
            texts, numeric_features, labels, test_size=0.2, random_state=42
        )

        # Create and train text vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=kwargs.get('max_features', 500),
            ngram_range=(1, 2),
            stop_words='english'
        )
        X_text_train_vec = self.vectorizer.fit_transform(X_text_train)
        X_text_test_vec = self.vectorizer.transform(X_text_test)

        # Combine text and numeric features
        X_train_combined = np.hstack([
            X_text_train_vec.toarray(),
            np.array(X_num_train)
        ])
        X_test_combined = np.hstack([
            X_text_test_vec.toarray(),
            np.array(X_num_test)
        ])

        # Train classifier
        self.model = RandomForestClassifier(
            n_estimators=kwargs.get('n_estimators', 100),
            max_depth=kwargs.get('max_depth', 10),
            random_state=42
        )
        self.model.fit(X_train_combined, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_combined)
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average='weighted', zero_division=0
        )

        # Update config
        self.config = MLModelConfig(
            model_name='task_predictor',
            model_version='1.0',
            model_type='classifier',
            created_at=datetime.now().isoformat(),
            last_trained=datetime.now().isoformat(),
            training_samples=len(training_data),
            accuracy=float(accuracy),
            precision=float(precision),
            recall=float(recall),
            f1_score=float(f1),
            feature_names=['text_features', 'has_deadline', 'word_count', 'has_urgent_keywords',
                          'estimated_hours', 'dependencies_count'],
            hyperparameters={
                'max_features': kwargs.get('max_features', 500),
                'n_estimators': kwargs.get('n_estimators', 100),
                'max_depth': kwargs.get('max_depth', 10)
            }
        )

        self.is_trained = True
        self._save_model()
        self.save_config()

        logger.info(f"Task predictor trained: accuracy={accuracy:.3f}, f1={f1:.3f}")

        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'training_samples': len(training_data),
            'test_samples': len(X_test_combined)
        }

    def predict(self, input_data: Any) -> Dict[str, Any]:
        """
        Predict task priority.

        Args:
            input_data: Task data dictionary

        Returns:
            Dictionary with prediction results
        """
        # Validate input
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            return {'error': error, 'priority': 'medium', 'confidence': 0.0}

        if not isinstance(input_data, dict):
            return {'error': 'Input must be a dictionary', 'priority': 'medium', 'confidence': 0.0}

        try:
            # Extract features
            features = self._extract_features(input_data)
            text = features['text']
            numeric = [
                features['has_deadline'],
                features['word_count'],
                features['has_urgent_keywords'],
                features['estimated_hours'],
                features['dependencies_count']
            ]

            # Vectorize text
            text_vec = self.vectorizer.transform([text])

            # Combine features
            X_combined = np.hstack([text_vec.toarray(), np.array([numeric])])

            # Predict
            priority = self.model.predict(X_combined)[0]
            probabilities = self.model.predict_proba(X_combined)[0]
            confidence = float(max(probabilities))

            # Get all predictions with probabilities
            predictions = [
                {
                    'priority': self.model.classes_[i],
                    'confidence': float(probabilities[i])
                }
                for i in range(len(self.model.classes_))
            ]
            predictions.sort(key=lambda x: x['confidence'], reverse=True)

            return {
                'priority': priority,
                'confidence': confidence,
                'all_predictions': predictions,
                'features_used': features,
                'model_version': self.config.model_version if self.config else 'unknown'
            }

        except Exception as e:
            logger.error(f"Error predicting task priority: {e}")
            return {'error': str(e), 'priority': 'medium', 'confidence': 0.0}

    def _save_model(self) -> None:
        """Save model and vectorizer to disk."""
        if self.model is None or self.vectorizer is None:
            return

        model_path = self.get_model_path('model.pkl')
        vectorizer_path = self.get_model_path('vectorizer.pkl')

        joblib.dump(self.model, model_path)
        joblib.dump(self.vectorizer, vectorizer_path)

        logger.info(f"Saved task predictor to {self.model_dir}")

    def _load_model(self) -> bool:
        """
        Load model and vectorizer from disk.

        Returns:
            True if loaded successfully, False otherwise
        """
        model_path = self.get_model_path('model.pkl')
        vectorizer_path = self.get_model_path('vectorizer.pkl')

        if not model_path.exists() or not vectorizer_path.exists():
            return False

        try:
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
            self.is_trained = True
            self.load_config()
            logger.info(f"Loaded task predictor from {self.model_dir}")
            return True
        except Exception as e:
            logger.error(f"Error loading task predictor: {e}")
            return False

    def generate_sample_training_data(self, count: int = 50) -> List[Dict[str, Any]]:
        """
        Generate sample training data for testing.

        Args:
            count: Number of samples to generate

        Returns:
            List of training examples
        """
        samples = [
            # High priority
            {'description': 'URGENT: Fix critical production bug', 'priority': 'high', 'deadline': '2026-03-01', 'estimated_hours': 4},
            {'description': 'Security vulnerability needs immediate patch', 'priority': 'high', 'deadline': '2026-03-01', 'estimated_hours': 6},
            {'description': 'Client escalation - system down', 'priority': 'high', 'deadline': '2026-03-01', 'estimated_hours': 3},
            {'description': 'Emergency deployment required ASAP', 'priority': 'high', 'deadline': '2026-03-01', 'estimated_hours': 2},
            {'description': 'Critical data loss prevention', 'priority': 'high', 'deadline': '2026-03-01', 'estimated_hours': 5},

            # Medium priority
            {'description': 'Implement new feature for dashboard', 'priority': 'medium', 'deadline': '2026-03-15', 'estimated_hours': 8},
            {'description': 'Review and update documentation', 'priority': 'medium', 'estimated_hours': 4},
            {'description': 'Optimize database queries', 'priority': 'medium', 'deadline': '2026-03-10', 'estimated_hours': 6},
            {'description': 'Add unit tests for new module', 'priority': 'medium', 'estimated_hours': 5},
            {'description': 'Refactor authentication logic', 'priority': 'medium', 'deadline': '2026-03-20', 'estimated_hours': 10},

            # Low priority
            {'description': 'Update color scheme in UI', 'priority': 'low', 'estimated_hours': 2},
            {'description': 'Research new framework options', 'priority': 'low', 'estimated_hours': 4},
            {'description': 'Clean up old log files', 'priority': 'low', 'estimated_hours': 1},
            {'description': 'Update team wiki', 'priority': 'low', 'estimated_hours': 2},
            {'description': 'Organize project files', 'priority': 'low', 'estimated_hours': 1},
        ]

        # Repeat samples to reach desired count
        while len(samples) < count:
            samples.extend(samples[:min(len(samples), count - len(samples))])

        return samples[:count]

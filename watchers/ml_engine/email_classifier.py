"""
Email Classification Model

Classifies emails into categories: urgent, important, spam, promotional, informational.
Uses TF-IDF vectorization and Naive Bayes classification.
"""

import logging
import joblib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from .base import BaseMLModel, MLModelConfig

logger = logging.getLogger(__name__)


class EmailClassifier(BaseMLModel):
    """ML model for email classification."""

    CATEGORIES = ['urgent', 'important', 'spam', 'promotional', 'informational']

    def __init__(self, vault_path: str):
        """
        Initialize Email Classifier.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.vectorizer = None
        super().__init__(vault_path, 'email_classifier')

    def train(self, training_data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Train the email classifier.

        Args:
            training_data: List of dicts with 'text' and 'category' keys
            **kwargs: Additional training parameters

        Returns:
            Dictionary with training metrics
        """
        if len(training_data) < 10:
            raise ValueError("Need at least 10 training examples")

        # Extract texts and labels
        texts = [item['text'] for item in training_data]
        labels = [item['category'] for item in training_data]

        # Validate categories
        invalid_categories = set(labels) - set(self.CATEGORIES)
        if invalid_categories:
            raise ValueError(f"Invalid categories: {invalid_categories}")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )

        # Create and train vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=kwargs.get('max_features', 1000),
            ngram_range=(1, 2),
            stop_words='english'
        )
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)

        # Train classifier
        self.model = MultinomialNB(alpha=kwargs.get('alpha', 1.0))
        self.model.fit(X_train_vec, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average='weighted', zero_division=0
        )

        # Update config
        self.config = MLModelConfig(
            model_name='email_classifier',
            model_version='1.0',
            model_type='classifier',
            created_at=datetime.now().isoformat(),
            last_trained=datetime.now().isoformat(),
            training_samples=len(training_data),
            accuracy=float(accuracy),
            precision=float(precision),
            recall=float(recall),
            f1_score=float(f1),
            feature_names=self.vectorizer.get_feature_names_out().tolist()[:100],  # Store top 100
            hyperparameters={
                'max_features': kwargs.get('max_features', 1000),
                'alpha': kwargs.get('alpha', 1.0)
            }
        )

        self.is_trained = True
        self._save_model()
        self.save_config()

        logger.info(f"Email classifier trained: accuracy={accuracy:.3f}, f1={f1:.3f}")

        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'training_samples': len(training_data),
            'test_samples': len(X_test)
        }

    def predict(self, input_data: Any) -> Dict[str, Any]:
        """
        Classify an email.

        Args:
            input_data: Email text (string) or dict with 'text' key

        Returns:
            Dictionary with prediction results
        """
        # Validate input
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            return {'error': error, 'category': 'informational', 'confidence': 0.0}

        # Extract text
        if isinstance(input_data, dict):
            text = input_data.get('text', '')
        else:
            text = str(input_data)

        if not text:
            return {'error': 'Empty text', 'category': 'informational', 'confidence': 0.0}

        try:
            # Vectorize and predict
            text_vec = self.vectorizer.transform([text])
            category = self.model.predict(text_vec)[0]
            probabilities = self.model.predict_proba(text_vec)[0]
            confidence = float(max(probabilities))

            # Get top 3 predictions
            top_indices = probabilities.argsort()[-3:][::-1]
            top_predictions = [
                {
                    'category': self.model.classes_[i],
                    'confidence': float(probabilities[i])
                }
                for i in top_indices
            ]

            return {
                'category': category,
                'confidence': confidence,
                'top_predictions': top_predictions,
                'model_version': self.config.model_version if self.config else 'unknown'
            }

        except Exception as e:
            logger.error(f"Error predicting email category: {e}")
            return {'error': str(e), 'category': 'informational', 'confidence': 0.0}

    def _save_model(self) -> None:
        """Save model and vectorizer to disk."""
        if self.model is None or self.vectorizer is None:
            return

        model_path = self.get_model_path('model.pkl')
        vectorizer_path = self.get_model_path('vectorizer.pkl')

        joblib.dump(self.model, model_path)
        joblib.dump(self.vectorizer, vectorizer_path)

        logger.info(f"Saved email classifier to {self.model_dir}")

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
            logger.info(f"Loaded email classifier from {self.model_dir}")
            return True
        except Exception as e:
            logger.error(f"Error loading email classifier: {e}")
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
            # Urgent
            {'text': 'URGENT: Server down, production affected', 'category': 'urgent'},
            {'text': 'Critical bug in payment system', 'category': 'urgent'},
            {'text': 'Emergency meeting in 10 minutes', 'category': 'urgent'},
            {'text': 'Security breach detected', 'category': 'urgent'},
            {'text': 'Immediate action required: data loss', 'category': 'urgent'},

            # Important
            {'text': 'Quarterly review meeting tomorrow', 'category': 'important'},
            {'text': 'Please review and approve budget', 'category': 'important'},
            {'text': 'Contract needs your signature', 'category': 'important'},
            {'text': 'Project deadline approaching', 'category': 'important'},
            {'text': 'Client feedback on proposal', 'category': 'important'},

            # Spam
            {'text': 'You won a million dollars! Click here', 'category': 'spam'},
            {'text': 'Enlarge your business today!!!', 'category': 'spam'},
            {'text': 'Free money waiting for you', 'category': 'spam'},
            {'text': 'Nigerian prince needs your help', 'category': 'spam'},
            {'text': 'Congratulations! You are a winner', 'category': 'spam'},

            # Promotional
            {'text': '50% off all products this weekend', 'category': 'promotional'},
            {'text': 'New features in our latest release', 'category': 'promotional'},
            {'text': 'Subscribe to our newsletter', 'category': 'promotional'},
            {'text': 'Special offer just for you', 'category': 'promotional'},
            {'text': 'Join our webinar next week', 'category': 'promotional'},

            # Informational
            {'text': 'Weekly team update', 'category': 'informational'},
            {'text': 'FYI: New office hours', 'category': 'informational'},
            {'text': 'Documentation has been updated', 'category': 'informational'},
            {'text': 'Reminder: company holiday next week', 'category': 'informational'},
            {'text': 'Monthly newsletter', 'category': 'informational'},
        ]

        # Repeat samples to reach desired count
        while len(samples) < count:
            samples.extend(samples[:min(len(samples), count - len(samples))])

        return samples[:count]

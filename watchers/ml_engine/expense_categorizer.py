"""
Expense Categorization Model

Automatically categorizes expenses into accounting categories.
Uses Logistic Regression for fast and interpretable classification.
"""

import logging
import joblib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np

from .base import BaseMLModel, MLModelConfig

logger = logging.getLogger(__name__)


class ExpenseCategorizer(BaseMLModel):
    """ML model for expense categorization."""

    CATEGORIES = [
        'office_supplies',
        'software_subscriptions',
        'marketing',
        'travel',
        'meals_entertainment',
        'utilities',
        'professional_services',
        'equipment',
        'other'
    ]

    def __init__(self, vault_path: str):
        """
        Initialize Expense Categorizer.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.vectorizer = None
        super().__init__(vault_path, 'expense_categorizer')

    def _extract_features(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features from expense data.

        Args:
            expense_data: Expense information

        Returns:
            Dictionary of extracted features
        """
        description = expense_data.get('description', '')
        vendor = expense_data.get('vendor', '')
        combined_text = f"{description} {vendor}"

        features = {
            'text': combined_text,
            'amount': expense_data.get('amount', 0),
            'is_recurring': 1 if expense_data.get('is_recurring', False) else 0,
            'has_receipt': 1 if expense_data.get('has_receipt', False) else 0,
        }
        return features

    def train(self, training_data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Train the expense categorizer.

        Args:
            training_data: List of dicts with expense info and 'category' label
            **kwargs: Additional training parameters

        Returns:
            Dictionary with training metrics
        """
        if len(training_data) < 20:
            raise ValueError("Need at least 20 training examples")

        # Extract features
        texts = []
        numeric_features = []
        labels = []

        for item in training_data:
            features = self._extract_features(item)
            texts.append(features['text'])
            numeric_features.append([
                features['amount'],
                features['is_recurring'],
                features['has_receipt']
            ])
            labels.append(item['category'])

        # Validate categories
        invalid_categories = set(labels) - set(self.CATEGORIES)
        if invalid_categories:
            raise ValueError(f"Invalid categories: {invalid_categories}")

        # Split data
        X_text_train, X_text_test, X_num_train, X_num_test, y_train, y_test = train_test_split(
            texts, numeric_features, labels, test_size=0.2, random_state=42
        )

        # Create and train text vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=kwargs.get('max_features', 300),
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
        self.model = LogisticRegression(
            max_iter=kwargs.get('max_iter', 1000),
            C=kwargs.get('C', 1.0),
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
            model_name='expense_categorizer',
            model_version='1.0',
            model_type='classifier',
            created_at=datetime.now().isoformat(),
            last_trained=datetime.now().isoformat(),
            training_samples=len(training_data),
            accuracy=float(accuracy),
            precision=float(precision),
            recall=float(recall),
            f1_score=float(f1),
            feature_names=['text_features', 'amount', 'is_recurring', 'has_receipt'],
            hyperparameters={
                'max_features': kwargs.get('max_features', 300),
                'max_iter': kwargs.get('max_iter', 1000),
                'C': kwargs.get('C', 1.0)
            }
        )

        self.is_trained = True
        self._save_model()
        self.save_config()

        logger.info(f"Expense categorizer trained: accuracy={accuracy:.3f}, f1={f1:.3f}")

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
        Categorize an expense.

        Args:
            input_data: Expense data dictionary

        Returns:
            Dictionary with prediction results
        """
        # Validate input
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            return {'error': error, 'category': 'other', 'confidence': 0.0}

        if not isinstance(input_data, dict):
            return {'error': 'Input must be a dictionary', 'category': 'other', 'confidence': 0.0}

        try:
            # Extract features
            features = self._extract_features(input_data)
            text = features['text']
            numeric = [
                features['amount'],
                features['is_recurring'],
                features['has_receipt']
            ]

            # Vectorize text
            text_vec = self.vectorizer.transform([text])

            # Combine features
            X_combined = np.hstack([text_vec.toarray(), np.array([numeric])])

            # Predict
            category = self.model.predict(X_combined)[0]
            probabilities = self.model.predict_proba(X_combined)[0]
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
            logger.error(f"Error categorizing expense: {e}")
            return {'error': str(e), 'category': 'other', 'confidence': 0.0}

    def _save_model(self) -> None:
        """Save model and vectorizer to disk."""
        if self.model is None or self.vectorizer is None:
            return

        model_path = self.get_model_path('model.pkl')
        vectorizer_path = self.get_model_path('vectorizer.pkl')

        joblib.dump(self.model, model_path)
        joblib.dump(self.vectorizer, vectorizer_path)

        logger.info(f"Saved expense categorizer to {self.model_dir}")

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
            logger.info(f"Loaded expense categorizer from {self.model_dir}")
            return True
        except Exception as e:
            logger.error(f"Error loading expense categorizer: {e}")
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
            # Office supplies
            {'description': 'Printer paper and pens', 'vendor': 'Office Depot', 'amount': 45.99, 'category': 'office_supplies'},
            {'description': 'Desk organizers', 'vendor': 'Staples', 'amount': 29.99, 'category': 'office_supplies'},
            {'description': 'Notebooks and folders', 'vendor': 'Amazon', 'amount': 35.50, 'category': 'office_supplies'},

            # Software subscriptions
            {'description': 'GitHub Enterprise', 'vendor': 'GitHub', 'amount': 21.00, 'is_recurring': True, 'category': 'software_subscriptions'},
            {'description': 'Adobe Creative Cloud', 'vendor': 'Adobe', 'amount': 52.99, 'is_recurring': True, 'category': 'software_subscriptions'},
            {'description': 'Slack Business Plan', 'vendor': 'Slack', 'amount': 12.50, 'is_recurring': True, 'category': 'software_subscriptions'},

            # Marketing
            {'description': 'Facebook Ads Campaign', 'vendor': 'Meta', 'amount': 500.00, 'category': 'marketing'},
            {'description': 'Google Ads', 'vendor': 'Google', 'amount': 750.00, 'category': 'marketing'},
            {'description': 'LinkedIn Sponsored Content', 'vendor': 'LinkedIn', 'amount': 300.00, 'category': 'marketing'},

            # Travel
            {'description': 'Flight to conference', 'vendor': 'United Airlines', 'amount': 450.00, 'category': 'travel'},
            {'description': 'Hotel accommodation', 'vendor': 'Marriott', 'amount': 320.00, 'category': 'travel'},
            {'description': 'Rental car', 'vendor': 'Enterprise', 'amount': 180.00, 'category': 'travel'},

            # Meals & Entertainment
            {'description': 'Client dinner', 'vendor': 'Restaurant', 'amount': 125.00, 'has_receipt': True, 'category': 'meals_entertainment'},
            {'description': 'Team lunch', 'vendor': 'Cafe', 'amount': 85.00, 'has_receipt': True, 'category': 'meals_entertainment'},
            {'description': 'Coffee meeting', 'vendor': 'Starbucks', 'amount': 15.00, 'category': 'meals_entertainment'},

            # Utilities
            {'description': 'Internet service', 'vendor': 'Comcast', 'amount': 89.99, 'is_recurring': True, 'category': 'utilities'},
            {'description': 'Electricity bill', 'vendor': 'PG&E', 'amount': 150.00, 'is_recurring': True, 'category': 'utilities'},
            {'description': 'Phone service', 'vendor': 'Verizon', 'amount': 75.00, 'is_recurring': True, 'category': 'utilities'},

            # Professional services
            {'description': 'Legal consultation', 'vendor': 'Law Firm', 'amount': 500.00, 'category': 'professional_services'},
            {'description': 'Accounting services', 'vendor': 'CPA', 'amount': 350.00, 'category': 'professional_services'},
            {'description': 'IT consulting', 'vendor': 'Tech Consultant', 'amount': 1200.00, 'category': 'professional_services'},

            # Equipment
            {'description': 'Laptop computer', 'vendor': 'Apple', 'amount': 2499.00, 'category': 'equipment'},
            {'description': 'Office desk', 'vendor': 'IKEA', 'amount': 399.00, 'category': 'equipment'},
            {'description': 'Monitor', 'vendor': 'Dell', 'amount': 349.00, 'category': 'equipment'},
        ]

        # Repeat samples to reach desired count
        while len(samples) < count:
            samples.extend(samples[:min(len(samples), count - len(samples))])

        return samples[:count]

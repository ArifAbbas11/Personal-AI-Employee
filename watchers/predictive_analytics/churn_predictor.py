"""
Client Churn Prediction Model

Predicts likelihood of client churn based on engagement patterns and behavior.
Uses classification to identify at-risk clients.
"""

import logging
import joblib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score

from .base import BasePredictiveModel, PredictionConfig

logger = logging.getLogger(__name__)


class ChurnPredictor(BasePredictiveModel):
    """Predictive model for client churn."""

    def __init__(self, vault_path: str):
        """
        Initialize Churn Predictor.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        super().__init__(vault_path, 'churn')

    def _extract_features(self, client_data: Dict[str, Any]) -> List[float]:
        """
        Extract features from client data.

        Args:
            client_data: Client information

        Returns:
            List of feature values
        """
        features = [
            client_data.get('days_since_last_contact', 0),
            client_data.get('total_interactions', 0),
            client_data.get('avg_response_time_hours', 0),
            client_data.get('payment_delays', 0),
            client_data.get('support_tickets', 0),
            client_data.get('contract_value', 0),
            client_data.get('months_as_client', 0),
            1 if client_data.get('has_complained', False) else 0,
            1 if client_data.get('payment_issues', False) else 0,
            client_data.get('engagement_score', 50) / 100.0  # Normalize to 0-1
        ]
        return features

    def train(self, historical_data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Train the churn prediction model.

        Args:
            historical_data: List of dicts with client data and 'churned' label
            **kwargs: Additional training parameters

        Returns:
            Dictionary with training metrics
        """
        if len(historical_data) < 20:
            raise ValueError("Need at least 20 training examples")

        # Extract features and labels
        X = []
        y = []

        for item in historical_data:
            features = self._extract_features(item)
            X.append(features)
            y.append(1 if item.get('churned', False) else 0)

        X = np.array(X)
        y = np.array(y)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
        )

        # Train model
        self.model = RandomForestClassifier(
            n_estimators=kwargs.get('n_estimators', 100),
            max_depth=kwargs.get('max_depth', 10),
            random_state=42
        )
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average='binary', zero_division=0
        )

        # Calculate AUC if we have both classes
        try:
            auc = roc_auc_score(y_test, y_proba)
        except:
            auc = 0.5

        # Get feature importance
        feature_names = [
            'days_since_last_contact', 'total_interactions', 'avg_response_time',
            'payment_delays', 'support_tickets', 'contract_value', 'months_as_client',
            'has_complained', 'payment_issues', 'engagement_score'
        ]
        feature_importance = dict(zip(feature_names, self.model.feature_importances_))

        # Update config
        self.config = PredictionConfig(
            model_name='churn_predictor',
            model_version='1.0',
            prediction_type='classification',
            created_at=datetime.now().isoformat(),
            last_trained=datetime.now().isoformat(),
            training_samples=len(historical_data),
            metrics={
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'auc': float(auc)
            },
            hyperparameters={
                'n_estimators': kwargs.get('n_estimators', 100),
                'max_depth': kwargs.get('max_depth', 10),
                'feature_importance': {k: float(v) for k, v in feature_importance.items()}
            }
        )

        self.is_trained = True
        self.historical_data = historical_data
        self._save_model()
        self.save_config()
        self.save_historical_data(historical_data)

        logger.info(f"Churn predictor trained: accuracy={accuracy:.3f}, AUC={auc:.3f}")

        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'auc': auc,
            'training_samples': len(historical_data),
            'feature_importance': feature_importance
        }

    def predict(self, client_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Predict churn probability for a client.

        Args:
            client_data: Client information
            **kwargs: Additional prediction parameters

        Returns:
            Dictionary with churn prediction
        """
        if not self.is_trained:
            return {
                'error': 'Model is not trained',
                'churn_probability': 0.5,
                'risk_level': 'unknown'
            }

        try:
            # Extract features
            features = self._extract_features(client_data)
            X = np.array([features])

            # Predict
            churn_probability = float(self.model.predict_proba(X)[0, 1])
            will_churn = bool(self.model.predict(X)[0])

            # Determine risk level
            if churn_probability >= 0.7:
                risk_level = 'high'
            elif churn_probability >= 0.4:
                risk_level = 'medium'
            else:
                risk_level = 'low'

            # Get top risk factors
            feature_names = [
                'days_since_last_contact', 'total_interactions', 'avg_response_time',
                'payment_delays', 'support_tickets', 'contract_value', 'months_as_client',
                'has_complained', 'payment_issues', 'engagement_score'
            ]
            feature_importance = self.config.hyperparameters.get('feature_importance', {})
            risk_factors = []

            for name, value in zip(feature_names, features):
                importance = feature_importance.get(name, 0)
                if importance > 0.1:  # Only include important features
                    risk_factors.append({
                        'factor': name,
                        'value': float(value),
                        'importance': float(importance)
                    })

            risk_factors.sort(key=lambda x: x['importance'], reverse=True)

            return {
                'churn_probability': churn_probability,
                'will_churn': will_churn,
                'risk_level': risk_level,
                'top_risk_factors': risk_factors[:5],
                'model_version': self.config.model_version if self.config else 'unknown'
            }

        except Exception as e:
            logger.error(f"Error predicting churn: {e}")
            return {
                'error': str(e),
                'churn_probability': 0.5,
                'risk_level': 'unknown'
            }

    def _save_model(self) -> None:
        """Save model to disk."""
        if self.model is None:
            return

        model_path = self.get_model_path('model.pkl')
        joblib.dump(self.model, model_path)
        logger.info(f"Saved churn predictor to {self.model_dir}")

    def _load_model(self) -> bool:
        """
        Load model from disk.

        Returns:
            True if loaded successfully, False otherwise
        """
        model_path = self.get_model_path('model.pkl')
        if not model_path.exists():
            return False

        try:
            self.model = joblib.load(model_path)
            self.is_trained = True
            self.load_config()
            self.historical_data = self.load_historical_data()
            logger.info(f"Loaded churn predictor from {self.model_dir}")
            return True
        except Exception as e:
            logger.error(f"Error loading churn predictor: {e}")
            return False

    def generate_sample_data(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Generate sample client data for testing.

        Args:
            count: Number of samples to generate

        Returns:
            List of client data points
        """
        data = []

        for i in range(count):
            # Generate realistic client data
            churned = np.random.random() < 0.3  # 30% churn rate

            if churned:
                # Churned clients have worse metrics
                days_since_contact = np.random.randint(30, 180)
                total_interactions = np.random.randint(1, 10)
                avg_response_time = np.random.uniform(48, 120)
                payment_delays = np.random.randint(2, 10)
                support_tickets = np.random.randint(5, 20)
                engagement_score = np.random.uniform(10, 40)
                has_complained = np.random.random() < 0.7
                payment_issues = np.random.random() < 0.6
            else:
                # Active clients have better metrics
                days_since_contact = np.random.randint(1, 30)
                total_interactions = np.random.randint(10, 100)
                avg_response_time = np.random.uniform(1, 24)
                payment_delays = np.random.randint(0, 2)
                support_tickets = np.random.randint(0, 5)
                engagement_score = np.random.uniform(60, 100)
                has_complained = np.random.random() < 0.2
                payment_issues = np.random.random() < 0.1

            data.append({
                'client_id': f'client_{i}',
                'days_since_last_contact': int(days_since_contact),
                'total_interactions': int(total_interactions),
                'avg_response_time_hours': float(avg_response_time),
                'payment_delays': int(payment_delays),
                'support_tickets': int(support_tickets),
                'contract_value': float(np.random.uniform(1000, 50000)),
                'months_as_client': int(np.random.randint(1, 60)),
                'has_complained': bool(has_complained),
                'payment_issues': bool(payment_issues),
                'engagement_score': float(engagement_score),
                'churned': bool(churned)
            })

        return data

    def identify_at_risk_clients(self, clients: List[Dict[str, Any]], threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Identify clients at risk of churning.

        Args:
            clients: List of client data
            threshold: Churn probability threshold

        Returns:
            List of at-risk clients with predictions
        """
        at_risk = []

        for client in clients:
            prediction = self.predict(client)
            if prediction.get('churn_probability', 0) >= threshold:
                at_risk.append({
                    'client_id': client.get('client_id', 'unknown'),
                    'churn_probability': prediction['churn_probability'],
                    'risk_level': prediction['risk_level'],
                    'top_risk_factors': prediction.get('top_risk_factors', [])
                })

        # Sort by churn probability (highest first)
        at_risk.sort(key=lambda x: x['churn_probability'], reverse=True)

        return at_risk

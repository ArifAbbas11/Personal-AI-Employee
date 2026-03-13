"""
Task Bottleneck Prediction Model

Predicts potential task bottlenecks and delays based on task patterns and resource allocation.
Helps identify workflow issues before they become critical.
"""

import logging
import joblib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from .base import BasePredictiveModel, PredictionConfig

logger = logging.getLogger(__name__)


class BottleneckPredictor(BasePredictiveModel):
    """Predictive model for task bottleneck detection."""

    def __init__(self, vault_path: str):
        """
        Initialize Bottleneck Predictor.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        super().__init__(vault_path, 'bottlenecks')

    def _extract_features(self, task_data: Dict[str, Any]) -> List[float]:
        """
        Extract features from task data.

        Args:
            task_data: Task information

        Returns:
            List of feature values
        """
        features = [
            task_data.get('estimated_hours', 1),
            task_data.get('actual_hours', 0),
            task_data.get('dependencies_count', 0),
            task_data.get('blocked_count', 0),
            task_data.get('team_size', 1),
            task_data.get('priority_score', 5) / 10.0,  # Normalize to 0-1
            task_data.get('complexity_score', 5) / 10.0,  # Normalize to 0-1
            1 if task_data.get('has_deadline', False) else 0,
            1 if task_data.get('is_overdue', False) else 0,
            task_data.get('days_in_progress', 0),
            task_data.get('reassignments', 0),
            task_data.get('comments_count', 0),
            1 if task_data.get('external_dependency', False) else 0,
            task_data.get('resource_utilization', 50) / 100.0  # Normalize to 0-1
        ]
        return features

    def train(self, historical_data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Train the bottleneck prediction model.

        Args:
            historical_data: List of dicts with task data and 'is_bottleneck' label
            **kwargs: Additional training parameters

        Returns:
            Dictionary with training metrics
        """
        if len(historical_data) < 30:
            raise ValueError("Need at least 30 training examples")

        # Extract features and labels
        X = []
        y = []

        for item in historical_data:
            features = self._extract_features(item)
            X.append(features)
            y.append(1 if item.get('is_bottleneck', False) else 0)

        X = np.array(X)
        y = np.array(y)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
        )

        # Train model
        self.model = GradientBoostingClassifier(
            n_estimators=kwargs.get('n_estimators', 100),
            max_depth=kwargs.get('max_depth', 5),
            learning_rate=kwargs.get('learning_rate', 0.1),
            random_state=42
        )
        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average='binary', zero_division=0
        )

        # Get feature importance
        feature_names = [
            'estimated_hours', 'actual_hours', 'dependencies_count', 'blocked_count',
            'team_size', 'priority_score', 'complexity_score', 'has_deadline',
            'is_overdue', 'days_in_progress', 'reassignments', 'comments_count',
            'external_dependency', 'resource_utilization'
        ]
        feature_importance = dict(zip(feature_names, self.model.feature_importances_))

        # Update config
        self.config = PredictionConfig(
            model_name='bottleneck_predictor',
            model_version='1.0',
            prediction_type='classification',
            created_at=datetime.now().isoformat(),
            last_trained=datetime.now().isoformat(),
            training_samples=len(historical_data),
            metrics={
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1)
            },
            hyperparameters={
                'n_estimators': kwargs.get('n_estimators', 100),
                'max_depth': kwargs.get('max_depth', 5),
                'learning_rate': kwargs.get('learning_rate', 0.1),
                'feature_importance': {k: float(v) for k, v in feature_importance.items()}
            }
        )

        self.is_trained = True
        self.historical_data = historical_data
        self._save_model()
        self.save_config()
        self.save_historical_data(historical_data)

        logger.info(f"Bottleneck predictor trained: accuracy={accuracy:.3f}, f1={f1:.3f}")

        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'training_samples': len(historical_data),
            'feature_importance': feature_importance
        }

    def predict(self, task_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Predict if a task will become a bottleneck.

        Args:
            task_data: Task information
            **kwargs: Additional prediction parameters

        Returns:
            Dictionary with bottleneck prediction
        """
        if not self.is_trained:
            return {
                'error': 'Model is not trained',
                'bottleneck_probability': 0.5,
                'risk_level': 'unknown'
            }

        try:
            # Extract features
            features = self._extract_features(task_data)
            X = np.array([features])

            # Predict
            bottleneck_probability = float(self.model.predict_proba(X)[0, 1])
            is_bottleneck = bool(self.model.predict(X)[0])

            # Determine risk level
            if bottleneck_probability >= 0.7:
                risk_level = 'high'
            elif bottleneck_probability >= 0.4:
                risk_level = 'medium'
            else:
                risk_level = 'low'

            # Get top contributing factors
            feature_names = [
                'estimated_hours', 'actual_hours', 'dependencies_count', 'blocked_count',
                'team_size', 'priority_score', 'complexity_score', 'has_deadline',
                'is_overdue', 'days_in_progress', 'reassignments', 'comments_count',
                'external_dependency', 'resource_utilization'
            ]
            feature_importance = self.config.hyperparameters.get('feature_importance', {})
            contributing_factors = []

            for name, value in zip(feature_names, features):
                importance = feature_importance.get(name, 0)
                if importance > 0.05:  # Only include significant features
                    contributing_factors.append({
                        'factor': name,
                        'value': float(value),
                        'importance': float(importance)
                    })

            contributing_factors.sort(key=lambda x: x['importance'], reverse=True)

            # Generate recommendations
            recommendations = self._generate_recommendations(task_data, contributing_factors)

            return {
                'bottleneck_probability': bottleneck_probability,
                'is_bottleneck': is_bottleneck,
                'risk_level': risk_level,
                'contributing_factors': contributing_factors[:5],
                'recommendations': recommendations,
                'model_version': self.config.model_version if self.config else 'unknown'
            }

        except Exception as e:
            logger.error(f"Error predicting bottleneck: {e}")
            return {
                'error': str(e),
                'bottleneck_probability': 0.5,
                'risk_level': 'unknown'
            }

    def _generate_recommendations(self, task_data: Dict[str, Any], factors: List[Dict[str, Any]]) -> List[str]:
        """
        Generate recommendations to prevent bottlenecks.

        Args:
            task_data: Task information
            factors: Contributing factors

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Check dependencies
        if task_data.get('dependencies_count', 0) > 3:
            recommendations.append("Reduce task dependencies or parallelize work where possible")

        # Check blocked status
        if task_data.get('blocked_count', 0) > 0:
            recommendations.append("Resolve blocking issues immediately to prevent delays")

        # Check team size
        if task_data.get('team_size', 1) < 2 and task_data.get('complexity_score', 5) > 7:
            recommendations.append("Consider adding team members for this complex task")

        # Check overdue status
        if task_data.get('is_overdue', False):
            recommendations.append("Task is overdue - escalate and reallocate resources")

        # Check days in progress
        if task_data.get('days_in_progress', 0) > 14:
            recommendations.append("Task has been in progress for too long - review scope and break down")

        # Check reassignments
        if task_data.get('reassignments', 0) > 2:
            recommendations.append("Multiple reassignments detected - clarify requirements and ownership")

        # Check external dependencies
        if task_data.get('external_dependency', False):
            recommendations.append("Monitor external dependencies closely and have contingency plans")

        # Check resource utilization
        if task_data.get('resource_utilization', 50) > 90:
            recommendations.append("Team is over-utilized - consider load balancing or additional resources")

        return recommendations[:5]  # Return top 5 recommendations

    def _save_model(self) -> None:
        """Save model to disk."""
        if self.model is None:
            return

        model_path = self.get_model_path('model.pkl')
        joblib.dump(self.model, model_path)
        logger.info(f"Saved bottleneck predictor to {self.model_dir}")

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
            logger.info(f"Loaded bottleneck predictor from {self.model_dir}")
            return True
        except Exception as e:
            logger.error(f"Error loading bottleneck predictor: {e}")
            return False

    def generate_sample_data(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Generate sample task data for testing.

        Args:
            count: Number of samples to generate

        Returns:
            List of task data points
        """
        data = []

        for i in range(count):
            # Generate realistic task data
            is_bottleneck = np.random.random() < 0.25  # 25% bottleneck rate

            if is_bottleneck:
                # Bottleneck tasks have worse metrics
                estimated_hours = np.random.uniform(20, 100)
                actual_hours = estimated_hours * np.random.uniform(1.5, 3.0)
                dependencies_count = np.random.randint(5, 15)
                blocked_count = np.random.randint(1, 5)
                team_size = np.random.randint(1, 3)
                priority_score = np.random.randint(7, 10)
                complexity_score = np.random.randint(7, 10)
                days_in_progress = np.random.randint(15, 60)
                reassignments = np.random.randint(2, 6)
                comments_count = np.random.randint(20, 100)
                resource_utilization = np.random.uniform(80, 100)
                has_deadline = True
                is_overdue = np.random.random() < 0.6
                external_dependency = np.random.random() < 0.7
            else:
                # Normal tasks have better metrics
                estimated_hours = np.random.uniform(1, 20)
                actual_hours = estimated_hours * np.random.uniform(0.8, 1.2)
                dependencies_count = np.random.randint(0, 3)
                blocked_count = 0
                team_size = np.random.randint(1, 5)
                priority_score = np.random.randint(1, 7)
                complexity_score = np.random.randint(1, 6)
                days_in_progress = np.random.randint(1, 10)
                reassignments = np.random.randint(0, 1)
                comments_count = np.random.randint(0, 15)
                resource_utilization = np.random.uniform(40, 70)
                has_deadline = np.random.random() < 0.5
                is_overdue = False
                external_dependency = np.random.random() < 0.2

            data.append({
                'task_id': f'task_{i}',
                'estimated_hours': float(estimated_hours),
                'actual_hours': float(actual_hours),
                'dependencies_count': int(dependencies_count),
                'blocked_count': int(blocked_count),
                'team_size': int(team_size),
                'priority_score': int(priority_score),
                'complexity_score': int(complexity_score),
                'has_deadline': bool(has_deadline),
                'is_overdue': bool(is_overdue),
                'days_in_progress': int(days_in_progress),
                'reassignments': int(reassignments),
                'comments_count': int(comments_count),
                'external_dependency': bool(external_dependency),
                'resource_utilization': float(resource_utilization),
                'is_bottleneck': bool(is_bottleneck)
            })

        return data

    def analyze_workflow(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze entire workflow for bottlenecks.

        Args:
            tasks: List of task data

        Returns:
            Dictionary with workflow analysis
        """
        if not self.is_trained:
            return {'error': 'Model is not trained'}

        bottlenecks = []
        high_risk = []
        medium_risk = []
        low_risk = []

        for task in tasks:
            prediction = self.predict(task)
            task_analysis = {
                'task_id': task.get('task_id', 'unknown'),
                'bottleneck_probability': prediction['bottleneck_probability'],
                'risk_level': prediction['risk_level'],
                'recommendations': prediction.get('recommendations', [])
            }

            if prediction['is_bottleneck']:
                bottlenecks.append(task_analysis)

            if prediction['risk_level'] == 'high':
                high_risk.append(task_analysis)
            elif prediction['risk_level'] == 'medium':
                medium_risk.append(task_analysis)
            else:
                low_risk.append(task_analysis)

        return {
            'total_tasks': len(tasks),
            'bottlenecks_detected': len(bottlenecks),
            'high_risk_tasks': len(high_risk),
            'medium_risk_tasks': len(medium_risk),
            'low_risk_tasks': len(low_risk),
            'bottleneck_rate': len(bottlenecks) / len(tasks) if tasks else 0,
            'bottlenecks': bottlenecks,
            'high_risk': high_risk[:10],  # Top 10
            'recommendations': self._generate_workflow_recommendations(bottlenecks, high_risk)
        }

    def _generate_workflow_recommendations(self, bottlenecks: List[Dict[str, Any]], high_risk: List[Dict[str, Any]]) -> List[str]:
        """
        Generate workflow-level recommendations.

        Args:
            bottlenecks: List of bottleneck tasks
            high_risk: List of high-risk tasks

        Returns:
            List of recommendations
        """
        recommendations = []

        if len(bottlenecks) > 5:
            recommendations.append("High number of bottlenecks detected - review resource allocation and task dependencies")

        if len(high_risk) > 10:
            recommendations.append("Many high-risk tasks - consider sprint planning adjustments")

        if bottlenecks:
            recommendations.append("Focus on resolving current bottlenecks before starting new work")

        return recommendations

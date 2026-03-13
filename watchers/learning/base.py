"""
Base classes for continuous learning systems.

Provides infrastructure for feedback collection, model retraining,
performance tracking, and A/B testing.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback."""
    EXPLICIT = "explicit"  # Direct user feedback
    IMPLICIT = "implicit"  # Inferred from behavior
    OUTCOME = "outcome"    # Actual outcome validation
    CORRECTION = "correction"  # User correction of prediction


class ModelPerformanceMetric(Enum):
    """Model performance metrics."""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    CONFIDENCE = "confidence"
    LATENCY = "latency"


@dataclass
class Feedback:
    """Feedback on a model prediction."""
    feedback_id: str
    model_name: str
    prediction_id: str
    feedback_type: FeedbackType
    timestamp: str

    # Original prediction
    predicted_value: Any
    predicted_confidence: float

    # Feedback data
    actual_value: Optional[Any] = None
    user_rating: Optional[float] = None  # 1-5 scale
    was_correct: Optional[bool] = None
    correction: Optional[Any] = None

    # Context
    input_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceSnapshot:
    """Snapshot of model performance at a point in time."""
    snapshot_id: str
    model_name: str
    timestamp: str

    # Metrics
    metrics: Dict[str, float] = field(default_factory=dict)

    # Sample statistics
    total_predictions: int = 0
    feedback_count: int = 0
    feedback_rate: float = 0.0

    # Performance indicators
    accuracy: Optional[float] = None
    avg_confidence: Optional[float] = None
    avg_latency_ms: Optional[float] = None

    # Trend
    trend: str = "stable"  # improving, declining, stable


@dataclass
class RetrainingTrigger:
    """Trigger for model retraining."""
    trigger_id: str
    model_name: str
    trigger_type: str  # performance_drop, data_drift, scheduled, manual
    timestamp: str

    # Trigger details
    reason: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"  # low, medium, high, critical

    # Status
    status: str = "pending"  # pending, in_progress, completed, failed
    completed_at: Optional[str] = None


class BaseLearningSystem(ABC):
    """Base class for continuous learning systems."""

    def __init__(self, vault_path: str, system_name: str):
        """
        Initialize learning system.

        Args:
            vault_path: Path to AI_Employee_Vault
            system_name: Name of the learning system
        """
        self.vault_path = Path(vault_path)
        self.system_name = system_name

        # Create system directory
        self.system_dir = self.vault_path / "learning" / system_name
        self.system_dir.mkdir(parents=True, exist_ok=True)

        # Initialize storage
        self.feedback_history: List[Feedback] = []
        self.performance_history: List[PerformanceSnapshot] = []
        self.retraining_triggers: List[RetrainingTrigger] = []

        # Load existing data
        self._load_data()

        logger.info(f"{system_name} learning system initialized")

    @abstractmethod
    def collect_feedback(self, feedback: Feedback) -> bool:
        """
        Collect feedback on a prediction.

        Args:
            feedback: Feedback data

        Returns:
            Success status
        """
        pass

    @abstractmethod
    def evaluate_performance(self) -> PerformanceSnapshot:
        """
        Evaluate current model performance.

        Returns:
            Performance snapshot
        """
        pass

    @abstractmethod
    def check_retraining_needed(self) -> Optional[RetrainingTrigger]:
        """
        Check if model retraining is needed.

        Returns:
            Retraining trigger if needed, None otherwise
        """
        pass

    def _load_data(self) -> None:
        """Load existing data from disk."""
        try:
            # Load feedback history
            feedback_path = self.system_dir / "feedback_history.json"
            if feedback_path.exists():
                with open(feedback_path, 'r') as f:
                    data = json.load(f)
                    self.feedback_history = [
                        Feedback(**item) for item in data
                    ]

            # Load performance history
            performance_path = self.system_dir / "performance_history.json"
            if performance_path.exists():
                with open(performance_path, 'r') as f:
                    data = json.load(f)
                    self.performance_history = [
                        PerformanceSnapshot(**item) for item in data
                    ]

            # Load retraining triggers
            triggers_path = self.system_dir / "retraining_triggers.json"
            if triggers_path.exists():
                with open(triggers_path, 'r') as f:
                    data = json.load(f)
                    self.retraining_triggers = [
                        RetrainingTrigger(**item) for item in data
                    ]

        except Exception as e:
            logger.error(f"Error loading learning data: {e}")

    def _save_feedback(self) -> None:
        """Save feedback history to disk."""
        try:
            feedback_path = self.system_dir / "feedback_history.json"
            with open(feedback_path, 'w') as f:
                json.dump(
                    [vars(fb) for fb in self.feedback_history],
                    f,
                    indent=2,
                    default=str
                )
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")

    def _save_performance(self) -> None:
        """Save performance history to disk."""
        try:
            performance_path = self.system_dir / "performance_history.json"
            with open(performance_path, 'w') as f:
                json.dump(
                    [vars(ps) for ps in self.performance_history],
                    f,
                    indent=2,
                    default=str
                )
        except Exception as e:
            logger.error(f"Error saving performance: {e}")

    def _save_triggers(self) -> None:
        """Save retraining triggers to disk."""
        try:
            triggers_path = self.system_dir / "retraining_triggers.json"
            with open(triggers_path, 'w') as f:
                json.dump(
                    [vars(rt) for rt in self.retraining_triggers],
                    f,
                    indent=2,
                    default=str
                )
        except Exception as e:
            logger.error(f"Error saving triggers: {e}")

    def get_recent_feedback(self, model_name: str, limit: int = 100) -> List[Feedback]:
        """
        Get recent feedback for a model.

        Args:
            model_name: Name of the model
            limit: Maximum number of feedback items

        Returns:
            List of recent feedback
        """
        model_feedback = [
            fb for fb in self.feedback_history
            if fb.model_name == model_name
        ]
        return model_feedback[-limit:]

    def get_performance_trend(self, model_name: str, metric: str, periods: int = 10) -> List[float]:
        """
        Get performance trend for a metric.

        Args:
            model_name: Name of the model
            metric: Metric name
            periods: Number of periods to include

        Returns:
            List of metric values over time
        """
        model_snapshots = [
            ps for ps in self.performance_history
            if ps.model_name == model_name
        ]

        recent_snapshots = model_snapshots[-periods:]
        return [
            ps.metrics.get(metric, 0.0)
            for ps in recent_snapshots
        ]

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get learning system status.

        Returns:
            Status dictionary
        """
        return {
            'system_name': self.system_name,
            'total_feedback': len(self.feedback_history),
            'performance_snapshots': len(self.performance_history),
            'pending_retraining': len([
                rt for rt in self.retraining_triggers
                if rt.status == 'pending'
            ]),
            'last_evaluation': (
                self.performance_history[-1].timestamp
                if self.performance_history else None
            )
        }

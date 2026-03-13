"""
Feedback Loop System

Collects feedback on model predictions, evaluates performance,
and triggers retraining when needed.
"""

import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from learning.base import (
    BaseLearningSystem,
    Feedback,
    FeedbackType,
    PerformanceSnapshot,
    RetrainingTrigger
)

logger = logging.getLogger(__name__)


class FeedbackLoopSystem(BaseLearningSystem):
    """System for collecting and processing feedback on model predictions."""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        """
        Initialize feedback loop system.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        super().__init__(vault_path, "feedback_loop")

        # Performance thresholds
        self.accuracy_threshold = 0.75  # Trigger retraining if accuracy drops below
        self.confidence_threshold = 0.60  # Trigger if avg confidence drops below
        self.feedback_rate_threshold = 0.10  # Minimum feedback rate

        # Retraining intervals
        self.min_retraining_interval_days = 7  # Minimum days between retraining
        self.scheduled_retraining_days = 30  # Scheduled retraining interval

        # Performance tracking
        self.model_last_retrained: Dict[str, str] = {}
        self.model_prediction_counts: Dict[str, int] = {}

    def collect_feedback(self, feedback: Feedback) -> bool:
        """
        Collect feedback on a prediction.

        Args:
            feedback: Feedback data

        Returns:
            Success status
        """
        try:
            # Validate feedback
            if not feedback.model_name or not feedback.prediction_id:
                logger.error("Invalid feedback: missing required fields")
                return False

            # Store feedback
            self.feedback_history.append(feedback)
            self._save_feedback()

            # Update prediction count
            if feedback.model_name not in self.model_prediction_counts:
                self.model_prediction_counts[feedback.model_name] = 0
            self.model_prediction_counts[feedback.model_name] += 1

            logger.info(
                f"Feedback collected for {feedback.model_name}: "
                f"{feedback.feedback_type.value}"
            )

            # Check if performance evaluation is needed
            if self._should_evaluate_performance(feedback.model_name):
                self.evaluate_performance(feedback.model_name)

            return True

        except Exception as e:
            logger.error(f"Error collecting feedback: {e}")
            return False

    def collect_explicit_feedback(
        self,
        model_name: str,
        prediction_id: str,
        predicted_value: Any,
        predicted_confidence: float,
        user_rating: float,
        input_data: Dict[str, Any]
    ) -> bool:
        """
        Collect explicit user feedback (rating).

        Args:
            model_name: Name of the model
            prediction_id: ID of the prediction
            predicted_value: Predicted value
            predicted_confidence: Prediction confidence
            user_rating: User rating (1-5)
            input_data: Original input data

        Returns:
            Success status
        """
        feedback = Feedback(
            feedback_id=str(uuid.uuid4()),
            model_name=model_name,
            prediction_id=prediction_id,
            feedback_type=FeedbackType.EXPLICIT,
            timestamp=datetime.now().isoformat(),
            predicted_value=predicted_value,
            predicted_confidence=predicted_confidence,
            user_rating=user_rating,
            was_correct=(user_rating >= 4.0),  # 4-5 stars = correct
            input_data=input_data
        )

        return self.collect_feedback(feedback)

    def collect_outcome_feedback(
        self,
        model_name: str,
        prediction_id: str,
        predicted_value: Any,
        predicted_confidence: float,
        actual_value: Any,
        input_data: Dict[str, Any]
    ) -> bool:
        """
        Collect outcome feedback (actual result validation).

        Args:
            model_name: Name of the model
            prediction_id: ID of the prediction
            predicted_value: Predicted value
            predicted_confidence: Prediction confidence
            actual_value: Actual outcome
            input_data: Original input data

        Returns:
            Success status
        """
        was_correct = (predicted_value == actual_value)

        feedback = Feedback(
            feedback_id=str(uuid.uuid4()),
            model_name=model_name,
            prediction_id=prediction_id,
            feedback_type=FeedbackType.OUTCOME,
            timestamp=datetime.now().isoformat(),
            predicted_value=predicted_value,
            predicted_confidence=predicted_confidence,
            actual_value=actual_value,
            was_correct=was_correct,
            input_data=input_data
        )

        return self.collect_feedback(feedback)

    def collect_correction_feedback(
        self,
        model_name: str,
        prediction_id: str,
        predicted_value: Any,
        predicted_confidence: float,
        corrected_value: Any,
        input_data: Dict[str, Any]
    ) -> bool:
        """
        Collect correction feedback (user corrects prediction).

        Args:
            model_name: Name of the model
            prediction_id: ID of the prediction
            predicted_value: Predicted value
            predicted_confidence: Prediction confidence
            corrected_value: User's correction
            input_data: Original input data

        Returns:
            Success status
        """
        feedback = Feedback(
            feedback_id=str(uuid.uuid4()),
            model_name=model_name,
            prediction_id=prediction_id,
            feedback_type=FeedbackType.CORRECTION,
            timestamp=datetime.now().isoformat(),
            predicted_value=predicted_value,
            predicted_confidence=predicted_confidence,
            actual_value=corrected_value,
            correction=corrected_value,
            was_correct=False,
            input_data=input_data
        )

        return self.collect_feedback(feedback)

    def evaluate_performance(self, model_name: Optional[str] = None) -> PerformanceSnapshot:
        """
        Evaluate current model performance.

        Args:
            model_name: Name of model to evaluate (None for all)

        Returns:
            Performance snapshot
        """
        try:
            if model_name:
                return self._evaluate_model_performance(model_name)
            else:
                # Evaluate all models
                snapshots = []
                for model in set(fb.model_name for fb in self.feedback_history):
                    snapshot = self._evaluate_model_performance(model)
                    snapshots.append(snapshot)
                return snapshots[-1] if snapshots else None

        except Exception as e:
            logger.error(f"Error evaluating performance: {e}")
            return None

    def _evaluate_model_performance(self, model_name: str) -> PerformanceSnapshot:
        """Evaluate performance for a specific model."""
        # Get recent feedback (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_feedback = [
            fb for fb in self.feedback_history
            if fb.model_name == model_name and
            datetime.fromisoformat(fb.timestamp) > cutoff_date
        ]

        if not recent_feedback:
            logger.warning(f"No recent feedback for {model_name}")
            return None

        # Calculate metrics
        total_predictions = self.model_prediction_counts.get(model_name, len(recent_feedback))
        feedback_count = len(recent_feedback)
        feedback_rate = feedback_count / total_predictions if total_predictions > 0 else 0.0

        # Calculate accuracy (from feedback with known correctness)
        correctness_feedback = [fb for fb in recent_feedback if fb.was_correct is not None]
        accuracy = None
        if correctness_feedback:
            correct_count = sum(1 for fb in correctness_feedback if fb.was_correct)
            accuracy = correct_count / len(correctness_feedback)

        # Calculate average confidence
        avg_confidence = sum(fb.predicted_confidence for fb in recent_feedback) / len(recent_feedback)

        # Calculate average rating (from explicit feedback)
        explicit_feedback = [fb for fb in recent_feedback if fb.user_rating is not None]
        avg_rating = None
        if explicit_feedback:
            avg_rating = sum(fb.user_rating for fb in explicit_feedback) / len(explicit_feedback)

        # Determine trend
        trend = self._calculate_trend(model_name, accuracy)

        # Create snapshot
        snapshot = PerformanceSnapshot(
            snapshot_id=str(uuid.uuid4()),
            model_name=model_name,
            timestamp=datetime.now().isoformat(),
            metrics={
                'accuracy': accuracy or 0.0,
                'avg_confidence': avg_confidence,
                'avg_rating': avg_rating or 0.0,
                'feedback_rate': feedback_rate
            },
            total_predictions=total_predictions,
            feedback_count=feedback_count,
            feedback_rate=feedback_rate,
            accuracy=accuracy,
            avg_confidence=avg_confidence,
            trend=trend
        )

        # Store snapshot
        self.performance_history.append(snapshot)
        self._save_performance()

        logger.info(
            f"Performance evaluated for {model_name}: "
            f"accuracy={(accuracy if accuracy is not None else 0.0):.2f}, "
            f"confidence={avg_confidence:.2f}, "
            f"trend={trend}"
        )

        return snapshot

    def _calculate_trend(self, model_name: str, current_accuracy: Optional[float]) -> str:
        """Calculate performance trend."""
        if current_accuracy is None:
            return "unknown"

        # Get previous snapshots
        previous_snapshots = [
            ps for ps in self.performance_history
            if ps.model_name == model_name and ps.accuracy is not None
        ]

        if len(previous_snapshots) < 2:
            return "stable"

        # Compare with previous snapshot
        prev_accuracy = previous_snapshots[-1].accuracy
        diff = current_accuracy - prev_accuracy

        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "declining"
        else:
            return "stable"

    def check_retraining_needed(self, model_name: Optional[str] = None) -> Optional[RetrainingTrigger]:
        """
        Check if model retraining is needed.

        Args:
            model_name: Name of model to check (None for all)

        Returns:
            Retraining trigger if needed, None otherwise
        """
        try:
            if model_name:
                return self._check_model_retraining(model_name)
            else:
                # Check all models
                for model in set(fb.model_name for fb in self.feedback_history):
                    trigger = self._check_model_retraining(model)
                    if trigger:
                        return trigger
                return None

        except Exception as e:
            logger.error(f"Error checking retraining: {e}")
            return None

    def _check_model_retraining(self, model_name: str) -> Optional[RetrainingTrigger]:
        """Check if a specific model needs retraining."""
        # Get latest performance snapshot
        model_snapshots = [
            ps for ps in self.performance_history
            if ps.model_name == model_name
        ]

        if not model_snapshots:
            return None

        latest_snapshot = model_snapshots[-1]

        # Check if minimum interval has passed since last retraining
        last_retrained = self.model_last_retrained.get(model_name)
        if last_retrained:
            last_retrained_date = datetime.fromisoformat(last_retrained)
            days_since_retraining = (datetime.now() - last_retrained_date).days
            if days_since_retraining < self.min_retraining_interval_days:
                return None

        # Check for performance drop
        if latest_snapshot.accuracy is not None:
            if latest_snapshot.accuracy < self.accuracy_threshold:
                return self._create_retraining_trigger(
                    model_name,
                    "performance_drop",
                    f"Accuracy dropped to {latest_snapshot.accuracy:.2f}",
                    {"accuracy": latest_snapshot.accuracy},
                    "high"
                )

        # Check for confidence drop
        if latest_snapshot.avg_confidence < self.confidence_threshold:
            return self._create_retraining_trigger(
                model_name,
                "confidence_drop",
                f"Average confidence dropped to {latest_snapshot.avg_confidence:.2f}",
                {"avg_confidence": latest_snapshot.avg_confidence},
                "medium"
            )

        # Check for declining trend
        if latest_snapshot.trend == "declining":
            return self._create_retraining_trigger(
                model_name,
                "declining_trend",
                "Performance showing declining trend",
                {"trend": "declining"},
                "medium"
            )

        # Check for scheduled retraining
        if last_retrained:
            last_retrained_date = datetime.fromisoformat(last_retrained)
            days_since_retraining = (datetime.now() - last_retrained_date).days
            if days_since_retraining >= self.scheduled_retraining_days:
                return self._create_retraining_trigger(
                    model_name,
                    "scheduled",
                    f"Scheduled retraining ({days_since_retraining} days since last)",
                    {"days_since_retraining": days_since_retraining},
                    "low"
                )

        return None

    def _create_retraining_trigger(
        self,
        model_name: str,
        trigger_type: str,
        reason: str,
        metrics: Dict[str, Any],
        priority: str
    ) -> RetrainingTrigger:
        """Create a retraining trigger."""
        trigger = RetrainingTrigger(
            trigger_id=str(uuid.uuid4()),
            model_name=model_name,
            trigger_type=trigger_type,
            timestamp=datetime.now().isoformat(),
            reason=reason,
            metrics=metrics,
            priority=priority,
            status="pending"
        )

        self.retraining_triggers.append(trigger)
        self._save_triggers()

        logger.warning(
            f"Retraining trigger created for {model_name}: "
            f"{trigger_type} ({priority} priority)"
        )

        return trigger

    def _should_evaluate_performance(self, model_name: str) -> bool:
        """Check if performance should be evaluated."""
        # Get latest snapshot
        model_snapshots = [
            ps for ps in self.performance_history
            if ps.model_name == model_name
        ]

        if not model_snapshots:
            return True  # First evaluation

        latest_snapshot = model_snapshots[-1]
        last_eval_date = datetime.fromisoformat(latest_snapshot.timestamp)
        hours_since_eval = (datetime.now() - last_eval_date).total_seconds() / 3600

        # Evaluate every 24 hours or after 100 new feedback items
        recent_feedback_count = len([
            fb for fb in self.feedback_history
            if fb.model_name == model_name and
            datetime.fromisoformat(fb.timestamp) > last_eval_date
        ])

        return hours_since_eval >= 24 or recent_feedback_count >= 100

    def mark_retraining_completed(self, trigger_id: str) -> bool:
        """
        Mark a retraining trigger as completed.

        Args:
            trigger_id: ID of the trigger

        Returns:
            Success status
        """
        try:
            for trigger in self.retraining_triggers:
                if trigger.trigger_id == trigger_id:
                    trigger.status = "completed"
                    trigger.completed_at = datetime.now().isoformat()

                    # Update last retrained timestamp
                    self.model_last_retrained[trigger.model_name] = trigger.completed_at

                    self._save_triggers()
                    logger.info(f"Retraining completed for {trigger.model_name}")
                    return True

            logger.error(f"Trigger not found: {trigger_id}")
            return False

        except Exception as e:
            logger.error(f"Error marking retraining completed: {e}")
            return False

    def get_model_statistics(self, model_name: str) -> Dict[str, Any]:
        """
        Get statistics for a model.

        Args:
            model_name: Name of the model

        Returns:
            Statistics dictionary
        """
        model_feedback = [fb for fb in self.feedback_history if fb.model_name == model_name]
        model_snapshots = [ps for ps in self.performance_history if ps.model_name == model_name]

        if not model_feedback:
            return {'error': 'No data available'}

        latest_snapshot = model_snapshots[-1] if model_snapshots else None

        return {
            'model_name': model_name,
            'total_feedback': len(model_feedback),
            'feedback_by_type': {
                ft.value: len([fb for fb in model_feedback if fb.feedback_type == ft])
                for ft in FeedbackType
            },
            'latest_performance': {
                'accuracy': latest_snapshot.accuracy if latest_snapshot else None,
                'avg_confidence': latest_snapshot.avg_confidence if latest_snapshot else None,
                'trend': latest_snapshot.trend if latest_snapshot else None
            },
            'last_retrained': self.model_last_retrained.get(model_name),
            'pending_retraining': len([
                rt for rt in self.retraining_triggers
                if rt.model_name == model_name and rt.status == 'pending'
            ])
        }


def main():
    """Main function for testing feedback loop system."""
    import argparse

    parser = argparse.ArgumentParser(description='Feedback Loop System')
    parser.add_argument('--vault-path', default='AI_Employee_Vault', help='Path to AI Employee Vault')
    parser.add_argument('--test', action='store_true', help='Run test scenarios')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize system
    system = FeedbackLoopSystem(args.vault_path)

    if args.test:
        print("Testing Feedback Loop System...")
        print("=" * 80)

        # Test 1: Collect explicit feedback
        print("\nTest 1: Collect Explicit Feedback")
        success = system.collect_explicit_feedback(
            model_name="email_classifier",
            prediction_id="pred_001",
            predicted_value="urgent",
            predicted_confidence=0.85,
            user_rating=5.0,
            input_data={'subject': 'URGENT: Server down', 'body': 'Need help'}
        )
        print(f"  Feedback collected: {success}")

        # Test 2: Collect outcome feedback
        print("\nTest 2: Collect Outcome Feedback")
        success = system.collect_outcome_feedback(
            model_name="task_predictor",
            prediction_id="pred_002",
            predicted_value="high",
            predicted_confidence=0.75,
            actual_value="high",
            input_data={'description': 'Fix critical bug'}
        )
        print(f"  Outcome feedback collected: {success}")

        # Test 3: Evaluate performance
        print("\nTest 3: Evaluate Performance")
        snapshot = system.evaluate_performance("email_classifier")
        if snapshot:
            print(f"  Accuracy: {snapshot.accuracy}")
            print(f"  Avg Confidence: {snapshot.avg_confidence:.2f}")
            print(f"  Trend: {snapshot.trend}")

        # Test 4: Check retraining
        print("\nTest 4: Check Retraining Needed")
        trigger = system.check_retraining_needed("email_classifier")
        if trigger:
            print(f"  Retraining needed: {trigger.reason}")
        else:
            print(f"  No retraining needed")

        # Test 5: System status
        print("\nTest 5: System Status")
        status = system.get_system_status()
        print(f"  Total Feedback: {status['total_feedback']}")
        print(f"  Performance Snapshots: {status['performance_snapshots']}")
        print(f"  Pending Retraining: {status['pending_retraining']}")

    else:
        print("Feedback Loop System initialized")
        print(f"System: {system.system_name}")
        status = system.get_system_status()
        print(f"Total Feedback: {status['total_feedback']}")


if __name__ == '__main__':
    main()

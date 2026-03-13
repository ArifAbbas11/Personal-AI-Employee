"""
A/B Testing Infrastructure

Enables controlled experiments to compare model versions and features.
Tracks experiment results and determines statistical significance.
"""

import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import random

from learning.base import (
    BaseLearningSystem,
    Feedback,
    PerformanceSnapshot,
    RetrainingTrigger
)

logger = logging.getLogger(__name__)


class ExperimentVariant:
    """Represents a variant in an A/B test."""

    def __init__(
        self,
        variant_id: str,
        name: str,
        description: str,
        traffic_allocation: float,  # 0.0 to 1.0
        model_version: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.variant_id = variant_id
        self.name = name
        self.description = description
        self.traffic_allocation = traffic_allocation
        self.model_version = model_version
        self.config = config or {}

        # Metrics
        self.total_requests = 0
        self.total_correct = 0
        self.total_confidence = 0.0
        self.total_latency_ms = 0.0
        self.user_ratings: List[float] = []


class Experiment:
    """Represents an A/B test experiment."""

    def __init__(
        self,
        experiment_id: str,
        name: str,
        description: str,
        model_name: str,
        hypothesis: str,
        start_date: str,
        end_date: str,
        status: str = "draft"  # draft, running, completed, cancelled
    ):
        self.experiment_id = experiment_id
        self.name = name
        self.description = description
        self.model_name = model_name
        self.hypothesis = hypothesis
        self.start_date = start_date
        self.end_date = end_date
        self.status = status

        # Variants
        self.variants: List[ExperimentVariant] = []

        # Results
        self.winner: Optional[str] = None
        self.confidence_level: Optional[float] = None
        self.results: Dict[str, Any] = {}


class ABTestingSystem(BaseLearningSystem):
    """System for A/B testing model versions and features."""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        """
        Initialize A/B testing system.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        super().__init__(vault_path, "ab_testing")

        # Experiments
        self.experiments: List[Experiment] = []
        self.active_experiments: Dict[str, Experiment] = {}  # model_name -> experiment

        # Statistical thresholds
        self.min_sample_size = 100  # Minimum samples per variant
        self.confidence_threshold = 0.95  # 95% confidence level
        self.min_effect_size = 0.02  # Minimum 2% improvement

        # Load existing data
        self._load_experiments()

    def collect_feedback(self, feedback: Feedback) -> bool:
        """Not used in A/B testing system."""
        return True

    def evaluate_performance(self) -> PerformanceSnapshot:
        """Not used in A/B testing system."""
        return None

    def check_retraining_needed(self) -> Optional[RetrainingTrigger]:
        """Not used in A/B testing system."""
        return None

    def create_experiment(
        self,
        name: str,
        description: str,
        model_name: str,
        hypothesis: str,
        duration_days: int,
        variants: List[Dict[str, Any]]
    ) -> Optional[Experiment]:
        """
        Create a new A/B test experiment.

        Args:
            name: Experiment name
            description: Experiment description
            model_name: Name of the model to test
            hypothesis: Hypothesis being tested
            duration_days: Duration in days
            variants: List of variant configurations

        Returns:
            Created experiment, or None if creation failed
        """
        try:
            # Validate traffic allocation
            total_allocation = sum(v.get('traffic_allocation', 0.0) for v in variants)
            if abs(total_allocation - 1.0) > 0.01:
                logger.error(f"Traffic allocation must sum to 1.0, got {total_allocation}")
                return None

            # Create experiment
            start_date = datetime.now()
            end_date = start_date + timedelta(days=duration_days)

            experiment = Experiment(
                experiment_id=str(uuid.uuid4()),
                name=name,
                description=description,
                model_name=model_name,
                hypothesis=hypothesis,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                status="draft"
            )

            # Create variants
            for variant_config in variants:
                variant = ExperimentVariant(
                    variant_id=str(uuid.uuid4()),
                    name=variant_config['name'],
                    description=variant_config.get('description', ''),
                    traffic_allocation=variant_config['traffic_allocation'],
                    model_version=variant_config.get('model_version'),
                    config=variant_config.get('config', {})
                )
                experiment.variants.append(variant)

            # Store experiment
            self.experiments.append(experiment)
            self._save_experiments()

            logger.info(f"Created experiment: {name} ({experiment.experiment_id})")

            return experiment

        except Exception as e:
            logger.error(f"Error creating experiment: {e}")
            return None

    def start_experiment(self, experiment_id: str) -> bool:
        """
        Start an experiment.

        Args:
            experiment_id: ID of the experiment

        Returns:
            Success status
        """
        try:
            experiment = self._get_experiment(experiment_id)
            if not experiment:
                logger.error(f"Experiment not found: {experiment_id}")
                return False

            if experiment.status != "draft":
                logger.error(f"Experiment must be in draft status to start")
                return False

            # Validate experiment
            if len(experiment.variants) < 2:
                logger.error("Experiment must have at least 2 variants")
                return False

            # Start experiment
            experiment.status = "running"
            experiment.start_date = datetime.now().isoformat()

            # Register as active experiment
            self.active_experiments[experiment.model_name] = experiment

            self._save_experiments()

            logger.info(f"Started experiment: {experiment.name}")

            return True

        except Exception as e:
            logger.error(f"Error starting experiment: {e}")
            return False

    def assign_variant(
        self,
        model_name: str,
        user_id: Optional[str] = None
    ) -> Optional[ExperimentVariant]:
        """
        Assign a variant for a request.

        Args:
            model_name: Name of the model
            user_id: Optional user ID for consistent assignment

        Returns:
            Assigned variant, or None if no active experiment
        """
        try:
            # Check for active experiment
            experiment = self.active_experiments.get(model_name)
            if not experiment or experiment.status != "running":
                return None

            # Check if experiment has ended
            end_date = datetime.fromisoformat(experiment.end_date)
            if datetime.now() > end_date:
                self.stop_experiment(experiment.experiment_id)
                return None

            # Assign variant based on traffic allocation
            if user_id:
                # Consistent assignment for same user
                random.seed(hash(user_id + experiment.experiment_id))

            rand_value = random.random()
            cumulative_allocation = 0.0

            for variant in experiment.variants:
                cumulative_allocation += variant.traffic_allocation
                if rand_value <= cumulative_allocation:
                    return variant

            # Fallback to first variant
            return experiment.variants[0]

        except Exception as e:
            logger.error(f"Error assigning variant: {e}")
            return None

    def record_result(
        self,
        experiment_id: str,
        variant_id: str,
        was_correct: bool,
        confidence: float,
        latency_ms: float,
        user_rating: Optional[float] = None
    ) -> bool:
        """
        Record a result for an experiment variant.

        Args:
            experiment_id: ID of the experiment
            variant_id: ID of the variant
            was_correct: Whether prediction was correct
            confidence: Prediction confidence
            latency_ms: Prediction latency
            user_rating: Optional user rating

        Returns:
            Success status
        """
        try:
            experiment = self._get_experiment(experiment_id)
            if not experiment:
                logger.error(f"Experiment not found: {experiment_id}")
                return False

            # Find variant
            variant = next(
                (v for v in experiment.variants if v.variant_id == variant_id),
                None
            )

            if not variant:
                logger.error(f"Variant not found: {variant_id}")
                return False

            # Update metrics
            variant.total_requests += 1
            if was_correct:
                variant.total_correct += 1
            variant.total_confidence += confidence
            variant.total_latency_ms += latency_ms

            if user_rating is not None:
                variant.user_ratings.append(user_rating)

            self._save_experiments()

            # Check if experiment should be analyzed
            if self._should_analyze_experiment(experiment):
                self.analyze_experiment(experiment.experiment_id)

            return True

        except Exception as e:
            logger.error(f"Error recording result: {e}")
            return False

    def analyze_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """
        Analyze experiment results.

        Args:
            experiment_id: ID of the experiment

        Returns:
            Analysis results, or None if analysis failed
        """
        try:
            experiment = self._get_experiment(experiment_id)
            if not experiment:
                logger.error(f"Experiment not found: {experiment_id}")
                return None

            # Calculate metrics for each variant
            variant_results = []

            for variant in experiment.variants:
                if variant.total_requests == 0:
                    continue

                accuracy = variant.total_correct / variant.total_requests
                avg_confidence = variant.total_confidence / variant.total_requests
                avg_latency = variant.total_latency_ms / variant.total_requests
                avg_rating = (
                    sum(variant.user_ratings) / len(variant.user_ratings)
                    if variant.user_ratings else None
                )

                variant_results.append({
                    'variant_id': variant.variant_id,
                    'variant_name': variant.name,
                    'total_requests': variant.total_requests,
                    'accuracy': accuracy,
                    'avg_confidence': avg_confidence,
                    'avg_latency_ms': avg_latency,
                    'avg_rating': avg_rating
                })

            if len(variant_results) < 2:
                logger.warning("Not enough variants with data for analysis")
                return None

            # Determine winner (based on accuracy)
            winner = max(variant_results, key=lambda x: x['accuracy'])
            control = variant_results[0]  # Assume first variant is control

            # Calculate improvement
            improvement = winner['accuracy'] - control['accuracy']
            improvement_pct = (improvement / control['accuracy'] * 100) if control['accuracy'] > 0 else 0

            # Check statistical significance (simplified)
            is_significant = (
                winner['total_requests'] >= self.min_sample_size and
                control['total_requests'] >= self.min_sample_size and
                improvement >= self.min_effect_size
            )

            # Calculate confidence level (simplified)
            confidence_level = 0.95 if is_significant else 0.80

            # Store results
            experiment.results = {
                'variants': variant_results,
                'winner': winner,
                'control': control,
                'improvement': improvement,
                'improvement_pct': improvement_pct,
                'is_significant': is_significant,
                'confidence_level': confidence_level,
                'analyzed_at': datetime.now().isoformat()
            }

            if is_significant:
                experiment.winner = winner['variant_id']
                experiment.confidence_level = confidence_level

            self._save_experiments()

            logger.info(
                f"Experiment analyzed: {experiment.name} - "
                f"Winner: {winner['variant_name']} "
                f"(+{improvement_pct:.1f}%, significant: {is_significant})"
            )

            return experiment.results

        except Exception as e:
            logger.error(f"Error analyzing experiment: {e}")
            return None

    def stop_experiment(self, experiment_id: str) -> bool:
        """
        Stop an experiment.

        Args:
            experiment_id: ID of the experiment

        Returns:
            Success status
        """
        try:
            experiment = self._get_experiment(experiment_id)
            if not experiment:
                logger.error(f"Experiment not found: {experiment_id}")
                return False

            if experiment.status != "running":
                logger.error("Experiment is not running")
                return False

            # Analyze final results
            self.analyze_experiment(experiment_id)

            # Stop experiment
            experiment.status = "completed"

            # Remove from active experiments
            if experiment.model_name in self.active_experiments:
                del self.active_experiments[experiment.model_name]

            self._save_experiments()

            logger.info(f"Stopped experiment: {experiment.name}")

            return True

        except Exception as e:
            logger.error(f"Error stopping experiment: {e}")
            return False

    def get_experiment_status(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get experiment status.

        Args:
            experiment_id: ID of the experiment

        Returns:
            Experiment status, or None if not found
        """
        experiment = self._get_experiment(experiment_id)
        if not experiment:
            return None

        # Calculate progress
        start_date = datetime.fromisoformat(experiment.start_date)
        end_date = datetime.fromisoformat(experiment.end_date)
        now = datetime.now()

        if experiment.status == "running":
            total_duration = (end_date - start_date).total_seconds()
            elapsed = (now - start_date).total_seconds()
            progress = min(100, (elapsed / total_duration * 100)) if total_duration > 0 else 0
        else:
            progress = 100 if experiment.status == "completed" else 0

        # Get variant statistics
        variant_stats = []
        for variant in experiment.variants:
            variant_stats.append({
                'variant_id': variant.variant_id,
                'name': variant.name,
                'traffic_allocation': variant.traffic_allocation,
                'total_requests': variant.total_requests,
                'accuracy': (
                    variant.total_correct / variant.total_requests
                    if variant.total_requests > 0 else 0
                )
            })

        return {
            'experiment_id': experiment.experiment_id,
            'name': experiment.name,
            'model_name': experiment.model_name,
            'status': experiment.status,
            'start_date': experiment.start_date,
            'end_date': experiment.end_date,
            'progress': progress,
            'variants': variant_stats,
            'winner': experiment.winner,
            'confidence_level': experiment.confidence_level,
            'results': experiment.results
        }

    def get_active_experiments(self) -> List[Dict[str, Any]]:
        """
        Get all active experiments.

        Returns:
            List of active experiments
        """
        active = [
            exp for exp in self.experiments
            if exp.status == "running"
        ]

        return [
            self.get_experiment_status(exp.experiment_id)
            for exp in active
        ]

    def get_experiment_history(
        self,
        model_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get experiment history.

        Args:
            model_name: Optional model name filter

        Returns:
            List of experiments
        """
        experiments = self.experiments
        if model_name:
            experiments = [e for e in experiments if e.model_name == model_name]

        return [
            {
                'experiment_id': e.experiment_id,
                'name': e.name,
                'model_name': e.model_name,
                'status': e.status,
                'start_date': e.start_date,
                'end_date': e.end_date,
                'winner': e.winner,
                'confidence_level': e.confidence_level
            }
            for e in experiments
        ]

    def _get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """Get experiment by ID."""
        return next(
            (e for e in self.experiments if e.experiment_id == experiment_id),
            None
        )

    def _should_analyze_experiment(self, experiment: Experiment) -> bool:
        """Check if experiment should be analyzed."""
        # Analyze every 100 requests or when experiment ends
        total_requests = sum(v.total_requests for v in experiment.variants)

        if total_requests > 0 and total_requests % 100 == 0:
            return True

        # Check if experiment has ended
        end_date = datetime.fromisoformat(experiment.end_date)
        if datetime.now() > end_date:
            return True

        return False

    def _load_experiments(self) -> None:
        """Load experiments from disk."""
        try:
            experiments_path = self.system_dir / "experiments.json"
            if experiments_path.exists():
                with open(experiments_path, 'r') as f:
                    data = json.load(f)

                    for exp_data in data:
                        experiment = Experiment(
                            experiment_id=exp_data['experiment_id'],
                            name=exp_data['name'],
                            description=exp_data['description'],
                            model_name=exp_data['model_name'],
                            hypothesis=exp_data['hypothesis'],
                            start_date=exp_data['start_date'],
                            end_date=exp_data['end_date'],
                            status=exp_data['status']
                        )

                        experiment.winner = exp_data.get('winner')
                        experiment.confidence_level = exp_data.get('confidence_level')
                        experiment.results = exp_data.get('results', {})

                        # Load variants
                        for var_data in exp_data.get('variants', []):
                            variant = ExperimentVariant(
                                variant_id=var_data['variant_id'],
                                name=var_data['name'],
                                description=var_data['description'],
                                traffic_allocation=var_data['traffic_allocation'],
                                model_version=var_data.get('model_version'),
                                config=var_data.get('config', {})
                            )

                            variant.total_requests = var_data.get('total_requests', 0)
                            variant.total_correct = var_data.get('total_correct', 0)
                            variant.total_confidence = var_data.get('total_confidence', 0.0)
                            variant.total_latency_ms = var_data.get('total_latency_ms', 0.0)
                            variant.user_ratings = var_data.get('user_ratings', [])

                            experiment.variants.append(variant)

                        self.experiments.append(experiment)

                        # Register active experiments
                        if experiment.status == "running":
                            self.active_experiments[experiment.model_name] = experiment

        except Exception as e:
            logger.error(f"Error loading experiments: {e}")

    def _save_experiments(self) -> None:
        """Save experiments to disk."""
        try:
            experiments_path = self.system_dir / "experiments.json"

            data = []
            for experiment in self.experiments:
                exp_data = {
                    'experiment_id': experiment.experiment_id,
                    'name': experiment.name,
                    'description': experiment.description,
                    'model_name': experiment.model_name,
                    'hypothesis': experiment.hypothesis,
                    'start_date': experiment.start_date,
                    'end_date': experiment.end_date,
                    'status': experiment.status,
                    'winner': experiment.winner,
                    'confidence_level': experiment.confidence_level,
                    'results': experiment.results,
                    'variants': []
                }

                for variant in experiment.variants:
                    var_data = {
                        'variant_id': variant.variant_id,
                        'name': variant.name,
                        'description': variant.description,
                        'traffic_allocation': variant.traffic_allocation,
                        'model_version': variant.model_version,
                        'config': variant.config,
                        'total_requests': variant.total_requests,
                        'total_correct': variant.total_correct,
                        'total_confidence': variant.total_confidence,
                        'total_latency_ms': variant.total_latency_ms,
                        'user_ratings': variant.user_ratings
                    }
                    exp_data['variants'].append(var_data)

                data.append(exp_data)

            with open(experiments_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving experiments: {e}")


def main():
    """Main function for testing A/B testing system."""
    import argparse

    parser = argparse.ArgumentParser(description='A/B Testing System')
    parser.add_argument('--vault-path', default='AI_Employee_Vault', help='Path to AI Employee Vault')
    parser.add_argument('--test', action='store_true', help='Run test scenarios')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize system
    system = ABTestingSystem(args.vault_path)

    if args.test:
        print("Testing A/B Testing System...")
        print("=" * 80)

        # Test 1: Create experiment
        print("\nTest 1: Create Experiment")
        experiment = system.create_experiment(
            name="Email Classifier v2 Test",
            description="Test new email classifier model",
            model_name="email_classifier",
            hypothesis="New model will improve accuracy by 5%",
            duration_days=7,
            variants=[
                {
                    'name': 'Control (v1)',
                    'description': 'Current production model',
                    'traffic_allocation': 0.5,
                    'model_version': 'v1'
                },
                {
                    'name': 'Treatment (v2)',
                    'description': 'New optimized model',
                    'traffic_allocation': 0.5,
                    'model_version': 'v2'
                }
            ]
        )

        if experiment:
            print(f"  ✓ Experiment created: {experiment.experiment_id}")
            print(f"  Variants: {len(experiment.variants)}")

            # Test 2: Start experiment
            print("\nTest 2: Start Experiment")
            success = system.start_experiment(experiment.experiment_id)
            print(f"  Started: {success}")

            # Test 3: Assign variants
            print("\nTest 3: Assign Variants")
            for i in range(10):
                variant = system.assign_variant("email_classifier", f"user_{i}")
                if variant:
                    print(f"  User {i}: {variant.name}")

            # Test 4: Record results
            print("\nTest 4: Record Results")
            for variant in experiment.variants:
                for i in range(50):
                    # Simulate results (treatment performs better)
                    is_treatment = variant.name.startswith("Treatment")
                    was_correct = random.random() < (0.85 if is_treatment else 0.80)

                    system.record_result(
                        experiment.experiment_id,
                        variant.variant_id,
                        was_correct=was_correct,
                        confidence=random.uniform(0.7, 0.95),
                        latency_ms=random.uniform(50, 150),
                        user_rating=random.uniform(3.5, 5.0) if random.random() < 0.3 else None
                    )

            print(f"  ✓ Recorded 100 results")

            # Test 5: Analyze experiment
            print("\nTest 5: Analyze Experiment")
            results = system.analyze_experiment(experiment.experiment_id)
            if results:
                print(f"  Winner: {results['winner']['variant_name']}")
                print(f"  Improvement: {results['improvement_pct']:.1f}%")
                print(f"  Significant: {results['is_significant']}")

            # Test 6: Get status
            print("\nTest 6: Get Experiment Status")
            status = system.get_experiment_status(experiment.experiment_id)
            if status:
                print(f"  Status: {status['status']}")
                print(f"  Progress: {status['progress']:.1f}%")

        # Test 7: System status
        print("\nTest 7: System Status")
        status = system.get_system_status()
        print(f"  System: {status['system_name']}")
        print(f"  Total Experiments: {len(system.experiments)}")
        print(f"  Active Experiments: {len(system.active_experiments)}")

    else:
        print("A/B Testing System initialized")
        print(f"System: {system.system_name}")
        print(f"Experiments: {len(system.experiments)}")


if __name__ == '__main__':
    main()

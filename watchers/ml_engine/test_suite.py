"""
ML Testing and Validation Suite

Comprehensive testing for all ML models and pipeline components.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import sys

from .training_pipeline import TrainingPipeline
from .model_manager import ModelManager
from .email_classifier import EmailClassifier
from .task_predictor import TaskPredictor
from .expense_categorizer import ExpenseCategorizer
from .content_optimizer import ContentOptimizer

logger = logging.getLogger(__name__)


class MLTestSuite:
    """Comprehensive testing suite for ML models."""

    def __init__(self, vault_path: str):
        """
        Initialize ML Test Suite.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.vault_path = Path(vault_path)
        self.pipeline = TrainingPipeline(str(vault_path))
        self.test_results: List[Dict[str, Any]] = []

    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all tests.

        Returns:
            Dictionary with test results
        """
        logger.info("Running ML test suite")
        start_time = datetime.now()

        results = {
            'timestamp': start_time.isoformat(),
            'tests': {},
            'summary': {}
        }

        # Test each component
        results['tests']['model_initialization'] = self.test_model_initialization()
        results['tests']['sample_data_generation'] = self.test_sample_data_generation()
        results['tests']['model_training'] = self.test_model_training()
        results['tests']['model_prediction'] = self.test_model_prediction()
        results['tests']['model_persistence'] = self.test_model_persistence()
        results['tests']['pipeline_integration'] = self.test_pipeline_integration()

        # Calculate summary
        total_tests = 0
        passed_tests = 0
        failed_tests = 0

        for test_name, test_result in results['tests'].items():
            total_tests += 1
            if test_result.get('passed', False):
                passed_tests += 1
            else:
                failed_tests += 1

        results['summary'] = {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'duration_seconds': (datetime.now() - start_time).total_seconds()
        }

        logger.info(f"Test suite completed: {passed_tests}/{total_tests} passed")

        return results

    def test_model_initialization(self) -> Dict[str, Any]:
        """Test that all models can be initialized."""
        logger.info("Testing model initialization")

        try:
            email_classifier = EmailClassifier(str(self.vault_path))
            task_predictor = TaskPredictor(str(self.vault_path))
            expense_categorizer = ExpenseCategorizer(str(self.vault_path))
            content_optimizer = ContentOptimizer(str(self.vault_path))

            return {
                'test_name': 'model_initialization',
                'passed': True,
                'message': 'All models initialized successfully',
                'models_tested': ['email_classifier', 'task_predictor', 'expense_categorizer', 'content_optimizer']
            }
        except Exception as e:
            logger.error(f"Model initialization test failed: {e}")
            return {
                'test_name': 'model_initialization',
                'passed': False,
                'error': str(e)
            }

    def test_sample_data_generation(self) -> Dict[str, Any]:
        """Test sample data generation for all models."""
        logger.info("Testing sample data generation")

        try:
            results = {}

            # Test email classifier
            email_data = self.pipeline.email_classifier.generate_sample_training_data(50)
            results['email_classifier'] = {
                'count': len(email_data),
                'has_required_fields': all('text' in item and 'category' in item for item in email_data)
            }

            # Test task predictor
            task_data = self.pipeline.task_predictor.generate_sample_training_data(50)
            results['task_predictor'] = {
                'count': len(task_data),
                'has_required_fields': all('description' in item and 'priority' in item for item in task_data)
            }

            # Test expense categorizer
            expense_data = self.pipeline.expense_categorizer.generate_sample_training_data(50)
            results['expense_categorizer'] = {
                'count': len(expense_data),
                'has_required_fields': all('description' in item and 'category' in item for item in expense_data)
            }

            # Test content optimizer
            content_data = self.pipeline.content_optimizer.generate_sample_training_data(50)
            results['content_optimizer'] = {
                'count': len(content_data),
                'has_required_fields': all('text' in item and 'engagement_score' in item for item in content_data)
            }

            all_passed = all(r['count'] == 50 and r['has_required_fields'] for r in results.values())

            return {
                'test_name': 'sample_data_generation',
                'passed': all_passed,
                'message': 'Sample data generation successful' if all_passed else 'Some data generation failed',
                'details': results
            }
        except Exception as e:
            logger.error(f"Sample data generation test failed: {e}")
            return {
                'test_name': 'sample_data_generation',
                'passed': False,
                'error': str(e)
            }

    def test_model_training(self) -> Dict[str, Any]:
        """Test training all models."""
        logger.info("Testing model training")

        try:
            # Train all models with sample data
            training_results = self.pipeline.train_all_models(use_sample_data=True)

            # Check if all models trained successfully
            all_success = all(
                result.get('success', False)
                for result in training_results['results'].values()
            )

            return {
                'test_name': 'model_training',
                'passed': all_success,
                'message': 'All models trained successfully' if all_success else 'Some models failed to train',
                'training_results': training_results
            }
        except Exception as e:
            logger.error(f"Model training test failed: {e}")
            return {
                'test_name': 'model_training',
                'passed': False,
                'error': str(e)
            }

    def test_model_prediction(self) -> Dict[str, Any]:
        """Test predictions from all models."""
        logger.info("Testing model predictions")

        try:
            results = {}

            # Test email classifier
            email_result = self.pipeline.email_classifier.predict({
                'text': 'URGENT: Server down, need immediate attention'
            })
            results['email_classifier'] = {
                'has_category': 'category' in email_result,
                'has_confidence': 'confidence' in email_result,
                'category': email_result.get('category'),
                'confidence': email_result.get('confidence')
            }

            # Test task predictor
            task_result = self.pipeline.task_predictor.predict({
                'description': 'Fix critical production bug ASAP',
                'deadline': '2026-03-01',
                'estimated_hours': 4
            })
            results['task_predictor'] = {
                'has_priority': 'priority' in task_result,
                'has_confidence': 'confidence' in task_result,
                'priority': task_result.get('priority'),
                'confidence': task_result.get('confidence')
            }

            # Test expense categorizer
            expense_result = self.pipeline.expense_categorizer.predict({
                'description': 'Adobe Creative Cloud subscription',
                'vendor': 'Adobe',
                'amount': 52.99,
                'is_recurring': True
            })
            results['expense_categorizer'] = {
                'has_category': 'category' in expense_result,
                'has_confidence': 'confidence' in expense_result,
                'category': expense_result.get('category'),
                'confidence': expense_result.get('confidence')
            }

            # Test content optimizer
            content_result = self.pipeline.content_optimizer.predict({
                'text': 'Check out our new product! 🚀 #innovation',
                'platform': 'twitter',
                'has_image': True,
                'post_hour': 14
            })
            results['content_optimizer'] = {
                'has_score': 'engagement_score' in content_result,
                'has_suggestions': 'suggestions' in content_result,
                'engagement_score': content_result.get('engagement_score'),
                'suggestions_count': len(content_result.get('suggestions', []))
            }

            all_passed = all(
                r.get('has_category') or r.get('has_priority') or r.get('has_score')
                for r in results.values()
            )

            return {
                'test_name': 'model_prediction',
                'passed': all_passed,
                'message': 'All predictions successful' if all_passed else 'Some predictions failed',
                'details': results
            }
        except Exception as e:
            logger.error(f"Model prediction test failed: {e}")
            return {
                'test_name': 'model_prediction',
                'passed': False,
                'error': str(e)
            }

    def test_model_persistence(self) -> Dict[str, Any]:
        """Test model saving and loading."""
        logger.info("Testing model persistence")

        try:
            # Save all models
            save_results = self.pipeline.export_models()

            # Check if all models saved successfully
            all_saved = all(save_results.values())

            # Try to load models
            new_pipeline = TrainingPipeline(str(self.vault_path))

            # Check if models are loaded and trained
            metrics = new_pipeline.manager.get_all_metrics()
            all_loaded = all(
                m.get('is_trained', False)
                for m in metrics.values()
            )

            return {
                'test_name': 'model_persistence',
                'passed': all_saved and all_loaded,
                'message': 'Models saved and loaded successfully' if (all_saved and all_loaded) else 'Persistence failed',
                'save_results': save_results,
                'load_results': {name: m.get('is_trained', False) for name, m in metrics.items()}
            }
        except Exception as e:
            logger.error(f"Model persistence test failed: {e}")
            return {
                'test_name': 'model_persistence',
                'passed': False,
                'error': str(e)
            }

    def test_pipeline_integration(self) -> Dict[str, Any]:
        """Test complete pipeline integration."""
        logger.info("Testing pipeline integration")

        try:
            # Get training status
            status = self.pipeline.get_training_status()

            # Get recommendations
            recommendations = self.pipeline.get_model_recommendations()

            # Evaluate all models
            evaluation = self.pipeline.evaluate_all_models()

            checks = {
                'has_system_status': 'system_status' in status,
                'has_models_info': 'models' in status,
                'all_models_trained': status['models']['trained'] == status['models']['total'],
                'has_recommendations': len(recommendations) > 0,
                'has_evaluation': len(evaluation) > 0
            }

            all_passed = all(checks.values())

            return {
                'test_name': 'pipeline_integration',
                'passed': all_passed,
                'message': 'Pipeline integration successful' if all_passed else 'Integration issues detected',
                'checks': checks,
                'training_status': status,
                'recommendations': recommendations
            }
        except Exception as e:
            logger.error(f"Pipeline integration test failed: {e}")
            return {
                'test_name': 'pipeline_integration',
                'passed': False,
                'error': str(e)
            }

    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """
        Generate human-readable test report.

        Args:
            results: Test results dictionary

        Returns:
            Formatted test report string
        """
        report = []
        report.append("=" * 80)
        report.append("ML TEST SUITE REPORT")
        report.append("=" * 80)
        report.append(f"Timestamp: {results['timestamp']}")
        report.append(f"Duration: {results['summary']['duration_seconds']:.2f}s")
        report.append("")
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Tests: {results['summary']['total_tests']}")
        report.append(f"Passed: {results['summary']['passed']}")
        report.append(f"Failed: {results['summary']['failed']}")
        report.append(f"Success Rate: {results['summary']['success_rate']:.1f}%")
        report.append("")
        report.append("TEST RESULTS")
        report.append("-" * 80)

        for test_name, test_result in results['tests'].items():
            status = "✓ PASSED" if test_result.get('passed', False) else "✗ FAILED"
            report.append(f"{status} - {test_name}")
            if 'message' in test_result:
                report.append(f"  Message: {test_result['message']}")
            if 'error' in test_result:
                report.append(f"  Error: {test_result['error']}")
            report.append("")

        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Main function for running test suite from command line."""
    import argparse

    parser = argparse.ArgumentParser(description='ML Test Suite')
    parser.add_argument('--vault-path', default='AI_Employee_Vault', help='Path to AI Employee Vault')
    parser.add_argument('--output', type=str, help='Output file for test results')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run tests
    test_suite = MLTestSuite(args.vault_path)
    results = test_suite.run_all_tests()

    # Generate report
    report = test_suite.generate_test_report(results)
    print(report)

    # Save results if output specified
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_path}")

    # Exit with appropriate code
    sys.exit(0 if results['summary']['failed'] == 0 else 1)


if __name__ == '__main__':
    main()

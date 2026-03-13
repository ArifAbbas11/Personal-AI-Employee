"""
ML MCP Server

Model-Context-Protocol server for ML capabilities.
Exposes ML models as tools for Claude Code integration.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ml_engine.training_pipeline import TrainingPipeline
from .ml_engine.model_manager import ModelManager

logger = logging.getLogger(__name__)


class MLMCPServer:
    """MCP Server for ML capabilities."""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        """
        Initialize ML MCP Server.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.vault_path = Path(vault_path)
        self.pipeline = TrainingPipeline(str(vault_path))
        self.manager = self.pipeline.manager

        logger.info("ML MCP Server initialized")

    # Tool 1: Classify Email
    def classify_email(self, email_text: str, email_subject: Optional[str] = None) -> Dict[str, Any]:
        """
        Classify an email into categories.

        Args:
            email_text: Email body text
            email_subject: Email subject (optional)

        Returns:
            Dictionary with classification results
        """
        try:
            # Combine subject and text if subject provided
            full_text = f"{email_subject} {email_text}" if email_subject else email_text

            result = self.pipeline.email_classifier.predict({'text': full_text})

            return {
                'success': True,
                'category': result.get('category', 'informational'),
                'confidence': result.get('confidence', 0.0),
                'top_predictions': result.get('top_predictions', []),
                'model_version': result.get('model_version', 'unknown')
            }
        except Exception as e:
            logger.error(f"Error classifying email: {e}")
            return {
                'success': False,
                'error': str(e),
                'category': 'informational',
                'confidence': 0.0
            }

    # Tool 2: Predict Task Priority
    def predict_task_priority(
        self,
        task_description: str,
        deadline: Optional[str] = None,
        estimated_hours: Optional[float] = None,
        dependencies: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Predict task priority.

        Args:
            task_description: Task description
            deadline: Task deadline (optional)
            estimated_hours: Estimated hours to complete (optional)
            dependencies: List of task dependencies (optional)

        Returns:
            Dictionary with priority prediction
        """
        try:
            task_data = {
                'description': task_description,
                'deadline': deadline,
                'estimated_hours': estimated_hours or 1,
                'dependencies': dependencies or []
            }

            result = self.pipeline.task_predictor.predict(task_data)

            return {
                'success': True,
                'priority': result.get('priority', 'medium'),
                'confidence': result.get('confidence', 0.0),
                'all_predictions': result.get('all_predictions', []),
                'features_used': result.get('features_used', {}),
                'model_version': result.get('model_version', 'unknown')
            }
        except Exception as e:
            logger.error(f"Error predicting task priority: {e}")
            return {
                'success': False,
                'error': str(e),
                'priority': 'medium',
                'confidence': 0.0
            }

    # Tool 3: Categorize Expense
    def categorize_expense(
        self,
        description: str,
        vendor: str,
        amount: float,
        is_recurring: bool = False,
        has_receipt: bool = False
    ) -> Dict[str, Any]:
        """
        Categorize an expense.

        Args:
            description: Expense description
            vendor: Vendor name
            amount: Expense amount
            is_recurring: Whether expense is recurring
            has_receipt: Whether receipt is available

        Returns:
            Dictionary with categorization results
        """
        try:
            expense_data = {
                'description': description,
                'vendor': vendor,
                'amount': amount,
                'is_recurring': is_recurring,
                'has_receipt': has_receipt
            }

            result = self.pipeline.expense_categorizer.predict(expense_data)

            return {
                'success': True,
                'category': result.get('category', 'other'),
                'confidence': result.get('confidence', 0.0),
                'top_predictions': result.get('top_predictions', []),
                'model_version': result.get('model_version', 'unknown')
            }
        except Exception as e:
            logger.error(f"Error categorizing expense: {e}")
            return {
                'success': False,
                'error': str(e),
                'category': 'other',
                'confidence': 0.0
            }

    # Tool 4: Optimize Content
    def optimize_content(
        self,
        content_text: str,
        platform: str = 'facebook',
        has_image: bool = False,
        has_video: bool = False,
        post_hour: int = 12,
        is_weekend: bool = False
    ) -> Dict[str, Any]:
        """
        Optimize social media content for engagement.

        Args:
            content_text: Content text
            platform: Platform name (facebook, twitter, linkedin, instagram)
            has_image: Whether content has image
            has_video: Whether content has video
            post_hour: Hour of day to post (0-23)
            is_weekend: Whether posting on weekend

        Returns:
            Dictionary with optimization results
        """
        try:
            content_data = {
                'text': content_text,
                'platform': platform,
                'has_image': has_image,
                'has_video': has_video,
                'post_hour': post_hour,
                'is_weekend': is_weekend
            }

            result = self.pipeline.content_optimizer.predict(content_data)

            return {
                'success': True,
                'engagement_score': result.get('engagement_score', 0.0),
                'suggestions': result.get('suggestions', []),
                'features_analyzed': result.get('features_analyzed', {}),
                'model_version': result.get('model_version', 'unknown')
            }
        except Exception as e:
            logger.error(f"Error optimizing content: {e}")
            return {
                'success': False,
                'error': str(e),
                'engagement_score': 0.0,
                'suggestions': []
            }

    # Tool 5: Train Models
    def train_models(self, use_sample_data: bool = True) -> Dict[str, Any]:
        """
        Train all ML models.

        Args:
            use_sample_data: Whether to use sample data for training

        Returns:
            Dictionary with training results
        """
        try:
            results = self.pipeline.train_all_models(use_sample_data=use_sample_data)

            return {
                'success': True,
                'training_results': results,
                'message': 'All models trained successfully'
            }
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Training failed'
            }

    # Tool 6: Get ML Status
    def get_ml_status(self) -> Dict[str, Any]:
        """
        Get ML system status.

        Returns:
            Dictionary with system status
        """
        try:
            status = self.pipeline.get_training_status()
            recommendations = self.pipeline.get_model_recommendations()

            return {
                'success': True,
                'status': status,
                'recommendations': recommendations
            }
        except Exception as e:
            logger.error(f"Error getting ML status: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # Tool 7: Evaluate Models
    def evaluate_models(self) -> Dict[str, Any]:
        """
        Evaluate all ML models.

        Returns:
            Dictionary with evaluation results
        """
        try:
            metrics = self.pipeline.evaluate_all_models()

            return {
                'success': True,
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"Error evaluating models: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available ML tools.

        Returns:
            List of tool definitions
        """
        return [
            {
                'name': 'classify_email',
                'description': 'Classify email into categories (urgent, important, spam, promotional, informational)',
                'parameters': ['email_text', 'email_subject (optional)']
            },
            {
                'name': 'predict_task_priority',
                'description': 'Predict task priority (high, medium, low)',
                'parameters': ['task_description', 'deadline (optional)', 'estimated_hours (optional)', 'dependencies (optional)']
            },
            {
                'name': 'categorize_expense',
                'description': 'Categorize expense into accounting categories',
                'parameters': ['description', 'vendor', 'amount', 'is_recurring (optional)', 'has_receipt (optional)']
            },
            {
                'name': 'optimize_content',
                'description': 'Optimize social media content for engagement',
                'parameters': ['content_text', 'platform', 'has_image (optional)', 'has_video (optional)', 'post_hour (optional)', 'is_weekend (optional)']
            },
            {
                'name': 'train_models',
                'description': 'Train all ML models',
                'parameters': ['use_sample_data (optional)']
            },
            {
                'name': 'get_ml_status',
                'description': 'Get ML system status and recommendations',
                'parameters': []
            },
            {
                'name': 'evaluate_models',
                'description': 'Evaluate all ML models and get performance metrics',
                'parameters': []
            }
        ]


def main():
    """Main function for testing MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description='ML MCP Server')
    parser.add_argument('--vault-path', default='AI_Employee_Vault', help='Path to AI Employee Vault')
    parser.add_argument('--test', action='store_true', help='Run test predictions')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize server
    server = MLMCPServer(args.vault_path)

    if args.test:
        print("Testing ML MCP Server...")
        print("\n1. Classifying email...")
        result = server.classify_email("URGENT: Server down, need immediate attention")
        print(json.dumps(result, indent=2))

        print("\n2. Predicting task priority...")
        result = server.predict_task_priority("Fix critical production bug", deadline="2026-03-01")
        print(json.dumps(result, indent=2))

        print("\n3. Categorizing expense...")
        result = server.categorize_expense("Adobe Creative Cloud", "Adobe", 52.99, is_recurring=True)
        print(json.dumps(result, indent=2))

        print("\n4. Optimizing content...")
        result = server.optimize_content("Check out our new product! 🚀", platform="twitter", has_image=True)
        print(json.dumps(result, indent=2))

        print("\n5. Getting ML status...")
        result = server.get_ml_status()
        print(json.dumps(result, indent=2))

    else:
        print("ML MCP Server initialized")
        print("\nAvailable tools:")
        for tool in server.get_available_tools():
            print(f"  - {tool['name']}: {tool['description']}")


if __name__ == '__main__':
    main()

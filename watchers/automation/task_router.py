"""
Intelligent Task Routing System

Automatically routes tasks to appropriate handlers based on ML predictions and rules.
Integrates with Task Priority Prediction model for intelligent routing decisions.
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys

from .base import (
    BaseAutomationSystem,
    AutomationEvent,
    AutomationResponse,
    AutomationRule,
    AutomationAction,
    AutomationPriority
)

# Import ML model for task priority prediction
sys.path.insert(0, str(Path(__file__).parent.parent))
from ml_engine.task_predictor import TaskPredictor

logger = logging.getLogger(__name__)


class TaskRouter(BaseAutomationSystem):
    """Intelligent task routing system."""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        """
        Initialize Task Router.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        super().__init__(vault_path, 'task_routing')

        # Initialize ML model for priority prediction
        self.task_predictor = TaskPredictor(str(vault_path))

        # Define routing destinations
        self.routing_destinations = {
            'high_priority_queue': {'capacity': 10, 'current_load': 0},
            'medium_priority_queue': {'capacity': 20, 'current_load': 0},
            'low_priority_queue': {'capacity': 50, 'current_load': 0},
            'urgent_handler': {'capacity': 5, 'current_load': 0},
            'background_processor': {'capacity': 100, 'current_load': 0}
        }

        # Routing history
        self.routing_history: List[Dict[str, Any]] = []

        # Initialize default routing rules
        self._initialize_default_rules()

    def _initialize_default_rules(self) -> None:
        """Initialize default routing rules."""
        default_rules = [
            AutomationRule(
                rule_id='rule_urgent_tasks',
                name='Route Urgent Tasks',
                condition="priority == 'high' and has_deadline == True",
                action_type=AutomationAction.ROUTE_TASK,
                priority=AutomationPriority.CRITICAL
            ),
            AutomationRule(
                rule_id='rule_background_tasks',
                name='Route Background Tasks',
                condition="priority == 'low' and has_deadline == False",
                action_type=AutomationAction.ROUTE_TASK,
                priority=AutomationPriority.LOW
            ),
            AutomationRule(
                rule_id='rule_medium_tasks',
                name='Route Medium Priority Tasks',
                condition="priority == 'medium'",
                action_type=AutomationAction.ROUTE_TASK,
                priority=AutomationPriority.MEDIUM
            )
        ]

        for rule in default_rules:
            if not any(r.rule_id == rule.rule_id for r in self.rules):
                self.add_rule(rule)

    def route_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a task to appropriate destination.

        Args:
            task_data: Task information

        Returns:
            Dictionary with routing result
        """
        try:
            # Predict task priority using ML if model is trained
            if self.task_predictor.is_trained:
                prediction = self.task_predictor.predict(task_data)
                predicted_priority = prediction.get('priority', 'medium')
                confidence = prediction.get('confidence', 0.5)
            else:
                # Fallback to simple heuristics
                predicted_priority = self._predict_priority_heuristic(task_data)
                confidence = 0.5

            # Determine routing destination
            destination = self._select_destination(predicted_priority, task_data)

            # Check capacity
            if not self._check_capacity(destination):
                # Try alternative destination
                destination = self._find_alternative_destination(predicted_priority)

            # Route task
            routing_result = self._execute_routing(task_data, destination, predicted_priority, confidence)

            # Record routing
            self.routing_history.append(routing_result)
            self._save_routing_history()

            return routing_result

        except Exception as e:
            logger.error(f"Error routing task: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_id': task_data.get('task_id', 'unknown')
            }

    def _predict_priority_heuristic(self, task_data: Dict[str, Any]) -> str:
        """
        Predict priority using simple heuristics.

        Args:
            task_data: Task information

        Returns:
            Priority level (high, medium, low)
        """
        # Check for urgent keywords
        description = task_data.get('description', '').lower()
        urgent_keywords = ['urgent', 'asap', 'critical', 'emergency', 'immediately']

        if any(keyword in description for keyword in urgent_keywords):
            return 'high'

        # Check deadline
        if task_data.get('deadline'):
            return 'high'

        # Check estimated hours
        estimated_hours = task_data.get('estimated_hours', 1)
        if estimated_hours > 20:
            return 'high'

        # Default to medium
        return 'medium'

    def _select_destination(self, priority: str, task_data: Dict[str, Any]) -> str:
        """
        Select routing destination based on priority.

        Args:
            priority: Task priority
            task_data: Task information

        Returns:
            Destination name
        """
        # Check for urgent conditions
        if priority == 'high' and task_data.get('deadline'):
            return 'urgent_handler'

        # Route by priority
        priority_map = {
            'high': 'high_priority_queue',
            'medium': 'medium_priority_queue',
            'low': 'low_priority_queue'
        }

        # Check if task can be backgrounded
        if priority == 'low' and not task_data.get('deadline'):
            return 'background_processor'

        return priority_map.get(priority, 'medium_priority_queue')

    def _check_capacity(self, destination: str) -> bool:
        """
        Check if destination has capacity.

        Args:
            destination: Destination name

        Returns:
            True if has capacity, False otherwise
        """
        if destination not in self.routing_destinations:
            return False

        dest_info = self.routing_destinations[destination]
        return dest_info['current_load'] < dest_info['capacity']

    def _find_alternative_destination(self, priority: str) -> str:
        """
        Find alternative destination when primary is full.

        Args:
            priority: Task priority

        Returns:
            Alternative destination name
        """
        # Try to find any destination with capacity
        for dest_name, dest_info in self.routing_destinations.items():
            if dest_info['current_load'] < dest_info['capacity']:
                logger.info(f"Using alternative destination: {dest_name}")
                return dest_name

        # If all full, use background processor (it has highest capacity)
        logger.warning("All destinations at capacity, using background processor")
        return 'background_processor'

    def _execute_routing(
        self,
        task_data: Dict[str, Any],
        destination: str,
        priority: str,
        confidence: float
    ) -> Dict[str, Any]:
        """
        Execute task routing.

        Args:
            task_data: Task information
            destination: Routing destination
            priority: Predicted priority
            confidence: Prediction confidence

        Returns:
            Routing result
        """
        task_id = task_data.get('task_id', str(uuid.uuid4()))

        # Update destination load
        if destination in self.routing_destinations:
            self.routing_destinations[destination]['current_load'] += 1

        logger.info(f"Routed task {task_id} to {destination} (priority: {priority}, confidence: {confidence:.2f})")

        return {
            'success': True,
            'task_id': task_id,
            'destination': destination,
            'priority': priority,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'task_description': task_data.get('description', '')[:100]  # First 100 chars
        }

    def complete_task(self, task_id: str, destination: str) -> bool:
        """
        Mark task as complete and free up capacity.

        Args:
            task_id: Task ID
            destination: Destination where task was routed

        Returns:
            True if successful, False otherwise
        """
        if destination in self.routing_destinations:
            if self.routing_destinations[destination]['current_load'] > 0:
                self.routing_destinations[destination]['current_load'] -= 1
                logger.info(f"Task {task_id} completed at {destination}")
                return True

        return False

    def process_event(self, event: AutomationEvent) -> Optional[AutomationResponse]:
        """
        Process a task routing event.

        Args:
            event: Event to process

        Returns:
            AutomationResponse if routing performed, None otherwise
        """
        if not self.is_enabled:
            return None

        # Record event
        self.record_event(event)

        # Extract task data from event
        task_data = event.metadata or {}

        # Route task
        routing_result = self.route_task(task_data)

        if routing_result['success']:
            response = AutomationResponse(
                action_id=str(uuid.uuid4()),
                action_type=AutomationAction.ROUTE_TASK,
                timestamp=datetime.now().isoformat(),
                success=True,
                event_id=event.event_id,
                description=f"Routed task to {routing_result['destination']}",
                result=routing_result
            )
            self.record_response(response)
            return response

        return None

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get task routing system status.

        Returns:
            Dictionary with status information
        """
        stats = self.get_statistics()

        # Calculate destination utilization
        destination_status = {}
        for dest_name, dest_info in self.routing_destinations.items():
            utilization = (dest_info['current_load'] / dest_info['capacity'] * 100) if dest_info['capacity'] > 0 else 0
            destination_status[dest_name] = {
                'capacity': dest_info['capacity'],
                'current_load': dest_info['current_load'],
                'utilization': utilization,
                'available': dest_info['capacity'] - dest_info['current_load']
            }

        return {
            'system_name': 'task_routing',
            'enabled': self.is_enabled,
            'ml_model_trained': self.task_predictor.is_trained,
            'statistics': stats,
            'destinations': destination_status,
            'total_routed': len(self.routing_history),
            'recent_routings': self.routing_history[-5:] if self.routing_history else []
        }

    def _save_routing_history(self) -> None:
        """Save routing history to disk."""
        history_path = self.get_file_path('routing_history.json')
        try:
            import json
            with open(history_path, 'w') as f:
                json.dump(self.routing_history[-1000:], f, indent=2)  # Keep last 1000
        except Exception as e:
            logger.error(f"Error saving routing history: {e}")

    def get_routing_analytics(self) -> Dict[str, Any]:
        """
        Get routing analytics.

        Returns:
            Dictionary with analytics
        """
        if not self.routing_history:
            return {'message': 'No routing history available'}

        # Count by destination
        destination_counts = {}
        priority_counts = {}

        for routing in self.routing_history:
            dest = routing.get('destination', 'unknown')
            priority = routing.get('priority', 'unknown')

            destination_counts[dest] = destination_counts.get(dest, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        # Calculate average confidence
        confidences = [r.get('confidence', 0) for r in self.routing_history]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return {
            'total_routings': len(self.routing_history),
            'destination_distribution': destination_counts,
            'priority_distribution': priority_counts,
            'average_confidence': avg_confidence,
            'ml_model_used': self.task_predictor.is_trained
        }


def main():
    """Main function for testing task routing system."""
    import argparse

    parser = argparse.ArgumentParser(description='Intelligent Task Routing System')
    parser.add_argument('--vault-path', default='AI_Employee_Vault', help='Path to AI Employee Vault')
    parser.add_argument('--test', action='store_true', help='Run test scenarios')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize system
    router = TaskRouter(args.vault_path)

    if args.test:
        print("Testing Intelligent Task Routing System...")
        print("=" * 80)

        # Test tasks
        test_tasks = [
            {
                'task_id': 'task_1',
                'description': 'URGENT: Fix critical production bug',
                'deadline': '2026-03-01',
                'estimated_hours': 4
            },
            {
                'task_id': 'task_2',
                'description': 'Update documentation',
                'estimated_hours': 2
            },
            {
                'task_id': 'task_3',
                'description': 'Implement new feature',
                'deadline': '2026-03-15',
                'estimated_hours': 20
            },
            {
                'task_id': 'task_4',
                'description': 'Clean up old files',
                'estimated_hours': 1
            }
        ]

        for task in test_tasks:
            print(f"\nRouting task: {task['description'][:50]}...")
            result = router.route_task(task)

            if result['success']:
                print(f"  ✓ Routed to: {result['destination']}")
                print(f"  Priority: {result['priority']}")
                print(f"  Confidence: {result['confidence']:.2f}")
            else:
                print(f"  ✗ Routing failed: {result.get('error', 'Unknown error')}")

        # Print system status
        print("\n" + "=" * 80)
        print("System Status:")
        status = router.get_system_status()
        print(f"  ML Model Trained: {status['ml_model_trained']}")
        print(f"  Total Routed: {status['total_routed']}")

        print("\nDestination Status:")
        for dest_name, dest_status in status['destinations'].items():
            print(f"  {dest_name}:")
            print(f"    Load: {dest_status['current_load']}/{dest_status['capacity']}")
            print(f"    Utilization: {dest_status['utilization']:.1f}%")

        # Print analytics
        print("\n" + "=" * 80)
        print("Routing Analytics:")
        analytics = router.get_routing_analytics()
        print(f"  Total routings: {analytics['total_routings']}")
        print(f"  Average confidence: {analytics['average_confidence']:.2f}")
        print(f"  Priority distribution: {analytics['priority_distribution']}")

    else:
        print("Intelligent Task Routing System initialized")
        print(f"ML Model Trained: {router.task_predictor.is_trained}")
        print(f"Active rules: {len([r for r in router.rules if r.enabled])}")


if __name__ == '__main__':
    main()

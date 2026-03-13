"""
Proactive Maintenance System

Schedules and executes preventive maintenance tasks before issues occur.
Monitors system health and predicts maintenance needs.
"""

import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json

from .base import (
    BaseAutomationSystem,
    AutomationEvent,
    AutomationResponse,
    AutomationRule,
    AutomationAction,
    AutomationPriority
)

logger = logging.getLogger(__name__)


class MaintenanceTask:
    """Represents a maintenance task."""

    def __init__(
        self,
        task_id: str,
        name: str,
        task_type: str,
        frequency_days: int,
        priority: str = 'medium',
        estimated_duration_minutes: int = 30,
        requires_downtime: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.task_id = task_id
        self.name = name
        self.task_type = task_type
        self.frequency_days = frequency_days
        self.priority = priority
        self.estimated_duration_minutes = estimated_duration_minutes
        self.requires_downtime = requires_downtime
        self.metadata = metadata or {}
        self.last_executed: Optional[str] = None
        self.next_scheduled: Optional[str] = None
        self.execution_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'task_id': self.task_id,
            'name': self.name,
            'task_type': self.task_type,
            'frequency_days': self.frequency_days,
            'priority': self.priority,
            'estimated_duration_minutes': self.estimated_duration_minutes,
            'requires_downtime': self.requires_downtime,
            'metadata': self.metadata,
            'last_executed': self.last_executed,
            'next_scheduled': self.next_scheduled,
            'execution_count': self.execution_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MaintenanceTask':
        """Create from dictionary."""
        task = cls(
            task_id=data['task_id'],
            name=data['name'],
            task_type=data['task_type'],
            frequency_days=data['frequency_days'],
            priority=data.get('priority', 'medium'),
            estimated_duration_minutes=data.get('estimated_duration_minutes', 30),
            requires_downtime=data.get('requires_downtime', False),
            metadata=data.get('metadata', {})
        )
        task.last_executed = data.get('last_executed')
        task.next_scheduled = data.get('next_scheduled')
        task.execution_count = data.get('execution_count', 0)
        return task


class ProactiveMaintenanceSystem(BaseAutomationSystem):
    """Proactive maintenance system for preventive actions."""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        """
        Initialize Proactive Maintenance System.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        super().__init__(vault_path, 'proactive_maintenance')

        # Maintenance tasks
        self.maintenance_tasks: List[MaintenanceTask] = []

        # Health metrics tracking
        self.health_metrics: Dict[str, List[Dict[str, Any]]] = {
            'system': [],
            'database': [],
            'api': [],
            'storage': []
        }

        # Maintenance windows
        self.maintenance_windows = {
            'preferred_hours': [2, 3, 4, 5],  # 2 AM - 5 AM
            'blackout_dates': []  # Dates to avoid maintenance
        }

        # Load existing tasks
        self._load_maintenance_tasks()

        # Initialize default tasks
        self._initialize_default_tasks()

        # Initialize default rules
        self._initialize_default_rules()

    def _initialize_default_rules(self) -> None:
        """Initialize default proactive maintenance rules."""
        default_rules = [
            AutomationRule(
                rule_id='rule_scheduled_maintenance',
                name='Execute Scheduled Maintenance',
                condition="event_type == 'scheduled_maintenance'",
                action_type=AutomationAction.SCHEDULE_MAINTENANCE,
                priority=AutomationPriority.MEDIUM,
                cooldown_seconds=3600
            ),
            AutomationRule(
                rule_id='rule_health_degradation',
                name='Respond to Health Degradation',
                condition="event_type == 'health_degradation' and severity in ['high', 'critical']",
                action_type=AutomationAction.SCHEDULE_MAINTENANCE,
                priority=AutomationPriority.HIGH,
                cooldown_seconds=1800
            ),
            AutomationRule(
                rule_id='rule_predictive_maintenance',
                name='Predictive Maintenance',
                condition="event_type == 'predictive_alert'",
                action_type=AutomationAction.SCHEDULE_MAINTENANCE,
                priority=AutomationPriority.MEDIUM,
                cooldown_seconds=7200
            )
        ]

        for rule in default_rules:
            if not any(r.rule_id == rule.rule_id for r in self.rules):
                self.add_rule(rule)

    def _initialize_default_tasks(self) -> None:
        """Initialize default maintenance tasks."""
        default_tasks = [
            MaintenanceTask(
                task_id='task_database_optimization',
                name='Database Optimization',
                task_type='database',
                frequency_days=7,
                priority='high',
                estimated_duration_minutes=45,
                requires_downtime=False,
                metadata={'operations': ['vacuum', 'reindex', 'analyze']}
            ),
            MaintenanceTask(
                task_id='task_log_rotation',
                name='Log Rotation and Cleanup',
                task_type='system',
                frequency_days=1,
                priority='low',
                estimated_duration_minutes=10,
                requires_downtime=False,
                metadata={'retention_days': 30}
            ),
            MaintenanceTask(
                task_id='task_cache_cleanup',
                name='Cache Cleanup',
                task_type='system',
                frequency_days=3,
                priority='medium',
                estimated_duration_minutes=15,
                requires_downtime=False
            ),
            MaintenanceTask(
                task_id='task_backup_verification',
                name='Backup Verification',
                task_type='storage',
                frequency_days=7,
                priority='high',
                estimated_duration_minutes=30,
                requires_downtime=False
            ),
            MaintenanceTask(
                task_id='task_security_updates',
                name='Security Updates',
                task_type='system',
                frequency_days=7,
                priority='critical',
                estimated_duration_minutes=60,
                requires_downtime=True,
                metadata={'auto_approve': False}
            ),
            MaintenanceTask(
                task_id='task_api_health_check',
                name='API Health Check',
                task_type='api',
                frequency_days=1,
                priority='medium',
                estimated_duration_minutes=5,
                requires_downtime=False
            )
        ]

        for task in default_tasks:
            if not any(t.task_id == task.task_id for t in self.maintenance_tasks):
                self.add_maintenance_task(task)

    def add_maintenance_task(self, task: MaintenanceTask) -> None:
        """
        Add a maintenance task.

        Args:
            task: Maintenance task to add
        """
        self.maintenance_tasks.append(task)
        self._schedule_next_execution(task)
        self._save_maintenance_tasks()
        logger.info(f"Added maintenance task: {task.name}")

    def remove_maintenance_task(self, task_id: str) -> bool:
        """
        Remove a maintenance task.

        Args:
            task_id: ID of task to remove

        Returns:
            True if removed, False if not found
        """
        for i, task in enumerate(self.maintenance_tasks):
            if task.task_id == task_id:
                self.maintenance_tasks.pop(i)
                self._save_maintenance_tasks()
                logger.info(f"Removed maintenance task: {task_id}")
                return True
        return False

    def _schedule_next_execution(self, task: MaintenanceTask) -> None:
        """
        Schedule next execution for a task.

        Args:
            task: Task to schedule
        """
        if task.last_executed:
            last_time = datetime.fromisoformat(task.last_executed)
        else:
            last_time = datetime.now()

        next_time = last_time + timedelta(days=task.frequency_days)

        # Adjust to preferred maintenance window if requires downtime
        if task.requires_downtime:
            next_time = self._adjust_to_maintenance_window(next_time)

        task.next_scheduled = next_time.isoformat()

    def _adjust_to_maintenance_window(self, target_time: datetime) -> datetime:
        """
        Adjust time to preferred maintenance window.

        Args:
            target_time: Target execution time

        Returns:
            Adjusted time in maintenance window
        """
        # Find next preferred hour
        preferred_hours = self.maintenance_windows['preferred_hours']

        if target_time.hour not in preferred_hours:
            # Move to next preferred hour
            next_hour = min(h for h in preferred_hours if h > target_time.hour) if any(h > target_time.hour for h in preferred_hours) else preferred_hours[0]

            if next_hour < target_time.hour:
                # Next day
                target_time = target_time + timedelta(days=1)

            target_time = target_time.replace(hour=next_hour, minute=0, second=0, microsecond=0)

        return target_time

    def get_due_tasks(self) -> List[MaintenanceTask]:
        """
        Get maintenance tasks that are due.

        Returns:
            List of due tasks
        """
        now = datetime.now()
        due_tasks = []

        for task in self.maintenance_tasks:
            if task.next_scheduled:
                scheduled_time = datetime.fromisoformat(task.next_scheduled)
                if scheduled_time <= now:
                    due_tasks.append(task)

        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        due_tasks.sort(key=lambda t: priority_order.get(t.priority, 4))

        return due_tasks

    def execute_maintenance_task(self, task: MaintenanceTask) -> Dict[str, Any]:
        """
        Execute a maintenance task.

        Args:
            task: Task to execute

        Returns:
            Dictionary with execution result
        """
        logger.info(f"Executing maintenance task: {task.name}")

        try:
            # Execute based on task type
            if task.task_type == 'database':
                result = self._execute_database_maintenance(task)
            elif task.task_type == 'system':
                result = self._execute_system_maintenance(task)
            elif task.task_type == 'storage':
                result = self._execute_storage_maintenance(task)
            elif task.task_type == 'api':
                result = self._execute_api_maintenance(task)
            else:
                result = {
                    'success': False,
                    'error': f"Unknown task type: {task.task_type}"
                }

            if result['success']:
                # Update task execution info
                task.last_executed = datetime.now().isoformat()
                task.execution_count += 1
                self._schedule_next_execution(task)
                self._save_maintenance_tasks()

            return result

        except Exception as e:
            logger.error(f"Error executing maintenance task {task.task_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_id': task.task_id
            }

    def _execute_database_maintenance(self, task: MaintenanceTask) -> Dict[str, Any]:
        """Execute database maintenance."""
        operations = task.metadata.get('operations', [])

        # In production, this would execute actual database operations
        # For now, simulate the operations

        return {
            'success': True,
            'message': f"Database maintenance completed: {', '.join(operations)}",
            'task_type': 'database',
            'operations': operations,
            'duration_minutes': task.estimated_duration_minutes
        }

    def _execute_system_maintenance(self, task: MaintenanceTask) -> Dict[str, Any]:
        """Execute system maintenance."""
        # In production, this would execute actual system operations
        # For now, simulate the operations

        if 'Log Rotation' in task.name:
            return {
                'success': True,
                'message': "Log rotation completed",
                'task_type': 'system',
                'logs_rotated': 15,
                'space_freed': '2.3 GB'
            }
        elif 'Cache Cleanup' in task.name:
            return {
                'success': True,
                'message': "Cache cleanup completed",
                'task_type': 'system',
                'cache_cleared': True,
                'space_freed': '500 MB'
            }
        elif 'Security Updates' in task.name:
            return {
                'success': True,
                'message': "Security updates applied",
                'task_type': 'system',
                'updates_applied': 5,
                'restart_required': task.requires_downtime
            }

        return {
            'success': True,
            'message': f"System maintenance completed: {task.name}",
            'task_type': 'system'
        }

    def _execute_storage_maintenance(self, task: MaintenanceTask) -> Dict[str, Any]:
        """Execute storage maintenance."""
        # In production, this would verify actual backups
        # For now, simulate the verification

        return {
            'success': True,
            'message': "Backup verification completed",
            'task_type': 'storage',
            'backups_verified': 7,
            'all_valid': True
        }

    def _execute_api_maintenance(self, task: MaintenanceTask) -> Dict[str, Any]:
        """Execute API maintenance."""
        # In production, this would check actual API health
        # For now, simulate the health check

        return {
            'success': True,
            'message': "API health check completed",
            'task_type': 'api',
            'endpoints_checked': 12,
            'all_healthy': True,
            'avg_response_time_ms': 45
        }

    def record_health_metric(
        self,
        component: str,
        metric_name: str,
        value: float,
        threshold: Optional[float] = None
    ) -> Optional[AutomationEvent]:
        """
        Record a health metric and check for degradation.

        Args:
            component: Component name (system, database, api, storage)
            metric_name: Name of the metric
            value: Metric value
            threshold: Optional threshold for alerting

        Returns:
            AutomationEvent if threshold exceeded, None otherwise
        """
        if component not in self.health_metrics:
            self.health_metrics[component] = []

        metric = {
            'timestamp': datetime.now().isoformat(),
            'metric_name': metric_name,
            'value': value,
            'threshold': threshold
        }

        self.health_metrics[component].append(metric)

        # Keep only last 1000 metrics per component
        if len(self.health_metrics[component]) > 1000:
            self.health_metrics[component] = self.health_metrics[component][-1000:]

        # Check if threshold exceeded
        if threshold and value > threshold:
            severity = 'high' if value > threshold * 1.5 else 'medium'

            event = AutomationEvent(
                event_id=str(uuid.uuid4()),
                event_type='health_degradation',
                timestamp=datetime.now().isoformat(),
                severity=severity,
                source='proactive_maintenance',
                description=f"{component} {metric_name} exceeded threshold: {value} > {threshold}",
                metadata={
                    'component': component,
                    'metric_name': metric_name,
                    'value': value,
                    'threshold': threshold
                }
            )

            return event

        return None

    def predict_maintenance_needs(self) -> List[Dict[str, Any]]:
        """
        Predict upcoming maintenance needs based on trends.

        Returns:
            List of predicted maintenance needs
        """
        predictions = []

        # Analyze health metrics for trends
        for component, metrics in self.health_metrics.items():
            if len(metrics) < 10:
                continue

            # Group by metric name
            metric_groups = {}
            for m in metrics[-100:]:  # Last 100 metrics
                name = m['metric_name']
                if name not in metric_groups:
                    metric_groups[name] = []
                metric_groups[name].append(m)

            # Check for increasing trends
            for metric_name, metric_list in metric_groups.items():
                if len(metric_list) < 5:
                    continue

                values = [m['value'] for m in metric_list[-10:]]

                # Simple trend detection: compare first half to second half
                first_half = sum(values[:len(values)//2]) / (len(values)//2)
                second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)

                if second_half > first_half * 1.2:  # 20% increase
                    predictions.append({
                        'component': component,
                        'metric': metric_name,
                        'trend': 'increasing',
                        'current_value': values[-1],
                        'recommendation': f"Schedule maintenance for {component}",
                        'urgency': 'medium' if second_half > first_half * 1.5 else 'low'
                    })

        return predictions

    def process_event(self, event: AutomationEvent) -> Optional[AutomationResponse]:
        """
        Process a maintenance event.

        Args:
            event: Event to process

        Returns:
            AutomationResponse if action taken, None otherwise
        """
        if not self.is_enabled:
            return None

        # Record event
        self.record_event(event)

        # Find matching rules
        context = {
            'event_type': event.event_type,
            'severity': event.severity,
            'source': event.source
        }

        matching_rules = []
        for rule in self.rules:
            if rule.enabled and self.evaluate_condition(rule.condition, context):
                matching_rules.append(rule)

        if not matching_rules:
            return None

        # Execute first matching rule
        rule = matching_rules[0]

        # Determine action based on event type
        if event.event_type == 'scheduled_maintenance':
            # Execute due maintenance tasks
            due_tasks = self.get_due_tasks()
            results = []

            for task in due_tasks[:3]:  # Execute up to 3 tasks
                result = self.execute_maintenance_task(task)
                results.append(result)

            response = AutomationResponse(
                action_id=str(uuid.uuid4()),
                action_type=rule.action_type,
                timestamp=datetime.now().isoformat(),
                success=all(r['success'] for r in results),
                event_id=event.event_id,
                description=f"Executed {len(results)} maintenance tasks",
                result={'tasks_executed': len(results), 'results': results}
            )

        elif event.event_type == 'health_degradation':
            # Schedule immediate maintenance
            component = event.metadata.get('component') if event.metadata else 'unknown'

            response = AutomationResponse(
                action_id=str(uuid.uuid4()),
                action_type=rule.action_type,
                timestamp=datetime.now().isoformat(),
                success=True,
                event_id=event.event_id,
                description=f"Scheduled maintenance for {component} due to health degradation",
                result={'component': component, 'scheduled': True}
            )

        else:
            response = AutomationResponse(
                action_id=str(uuid.uuid4()),
                action_type=rule.action_type,
                timestamp=datetime.now().isoformat(),
                success=False,
                event_id=event.event_id,
                description="No action taken"
            )

        self.record_response(response)
        return response

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get proactive maintenance system status.

        Returns:
            Dictionary with status information
        """
        stats = self.get_statistics()
        due_tasks = self.get_due_tasks()
        predictions = self.predict_maintenance_needs()

        return {
            'system_name': 'proactive_maintenance',
            'enabled': self.is_enabled,
            'statistics': stats,
            'total_tasks': len(self.maintenance_tasks),
            'due_tasks': len(due_tasks),
            'due_task_details': [
                {
                    'task_id': t.task_id,
                    'name': t.name,
                    'priority': t.priority,
                    'next_scheduled': t.next_scheduled
                }
                for t in due_tasks
            ],
            'maintenance_predictions': predictions,
            'health_metrics_count': sum(len(m) for m in self.health_metrics.values())
        }

    def _save_maintenance_tasks(self) -> None:
        """Save maintenance tasks to disk."""
        tasks_path = self.get_file_path('maintenance_tasks.json')
        try:
            with open(tasks_path, 'w') as f:
                json.dump([t.to_dict() for t in self.maintenance_tasks], f, indent=2)
            logger.debug(f"Saved {len(self.maintenance_tasks)} maintenance tasks")
        except Exception as e:
            logger.error(f"Error saving maintenance tasks: {e}")

    def _load_maintenance_tasks(self) -> None:
        """Load maintenance tasks from disk."""
        tasks_path = self.get_file_path('maintenance_tasks.json')
        if tasks_path.exists():
            try:
                with open(tasks_path, 'r') as f:
                    tasks_data = json.load(f)
                self.maintenance_tasks = [MaintenanceTask.from_dict(t) for t in tasks_data]
                logger.info(f"Loaded {len(self.maintenance_tasks)} maintenance tasks")
            except Exception as e:
                logger.error(f"Error loading maintenance tasks: {e}")
                self.maintenance_tasks = []


def main():
    """Main function for testing proactive maintenance system."""
    import argparse

    parser = argparse.ArgumentParser(description='Proactive Maintenance System')
    parser.add_argument('--vault-path', default='AI_Employee_Vault', help='Path to AI Employee Vault')
    parser.add_argument('--test', action='store_true', help='Run test scenarios')
    parser.add_argument('--status', action='store_true', help='Show system status')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize system
    system = ProactiveMaintenanceSystem(args.vault_path)

    if args.test:
        print("Testing Proactive Maintenance System...")
        print("=" * 80)

        # Show maintenance tasks
        print(f"\nMaintenance Tasks ({len(system.maintenance_tasks)}):")
        for task in system.maintenance_tasks:
            print(f"\n  {task.name}")
            print(f"    Type: {task.task_type}")
            print(f"    Frequency: Every {task.frequency_days} days")
            print(f"    Priority: {task.priority}")
            print(f"    Next scheduled: {task.next_scheduled}")

        # Check for due tasks
        print("\n" + "=" * 80)
        print("Checking for due tasks...")
        due_tasks = system.get_due_tasks()

        if due_tasks:
            print(f"\nFound {len(due_tasks)} due tasks:")
            for task in due_tasks:
                print(f"\n  Executing: {task.name}")
                result = system.execute_maintenance_task(task)

                if result['success']:
                    print(f"    ✓ {result['message']}")
                else:
                    print(f"    ✗ Failed: {result.get('error', 'Unknown error')}")
        else:
            print("\n✓ No tasks due for execution")

        # Test health metric recording
        print("\n" + "=" * 80)
        print("Testing health metric recording...")

        event = system.record_health_metric('database', 'query_time_ms', 250, threshold=200)
        if event:
            print(f"\n  ⚠ Health degradation detected: {event.description}")
        else:
            print("\n  ✓ All metrics within thresholds")

        # Test predictive maintenance
        print("\n" + "=" * 80)
        print("Predictive Maintenance Analysis...")

        predictions = system.predict_maintenance_needs()
        if predictions:
            print(f"\nFound {len(predictions)} predictions:")
            for pred in predictions:
                print(f"\n  Component: {pred['component']}")
                print(f"  Metric: {pred['metric']}")
                print(f"  Trend: {pred['trend']}")
                print(f"  Recommendation: {pred['recommendation']}")
        else:
            print("\n✓ No maintenance predicted needed")

    elif args.status:
        print("Proactive Maintenance System Status")
        print("=" * 80)

        status = system.get_system_status()
        print(f"\nEnabled: {status['enabled']}")
        print(f"Total tasks: {status['total_tasks']}")
        print(f"Due tasks: {status['due_tasks']}")
        print(f"Health metrics tracked: {status['health_metrics_count']}")

        if status['due_task_details']:
            print("\nDue Tasks:")
            for task in status['due_task_details']:
                print(f"  - {task['name']} (Priority: {task['priority']})")

        if status['maintenance_predictions']:
            print("\nMaintenance Predictions:")
            for pred in status['maintenance_predictions']:
                print(f"  - {pred['component']}: {pred['recommendation']}")

    else:
        print("Proactive Maintenance System initialized")
        print(f"Total maintenance tasks: {len(system.maintenance_tasks)}")
        print(f"Active rules: {len([r for r in system.rules if r.enabled])}")


if __name__ == '__main__':
    main()

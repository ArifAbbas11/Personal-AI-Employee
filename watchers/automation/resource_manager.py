"""
Auto-Scaling Resource Management System

Automatically scales resources based on load and predictive analytics.
Monitors system resources and adjusts capacity proactively.
"""

import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import psutil

from .base import (
    BaseAutomationSystem,
    AutomationEvent,
    AutomationResponse,
    AutomationRule,
    AutomationAction,
    AutomationPriority
)

logger = logging.getLogger(__name__)


class ResourceManager(BaseAutomationSystem):
    """Auto-scaling resource management system."""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        """
        Initialize Resource Manager.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        super().__init__(vault_path, 'resource_management')

        # Resource thresholds
        self.thresholds = {
            'cpu': {'scale_up': 80, 'scale_down': 30},
            'memory': {'scale_up': 85, 'scale_down': 40},
            'disk': {'scale_up': 90, 'scale_down': 50}
        }

        # Resource pools
        self.resource_pools = {
            'compute': {'min': 1, 'max': 10, 'current': 2},
            'memory': {'min': 2, 'max': 16, 'current': 4},  # GB
            'workers': {'min': 1, 'max': 20, 'current': 3}
        }

        # Scaling history
        self.scaling_history: List[Dict[str, Any]] = []

        # Initialize default rules
        self._initialize_default_rules()

    def _initialize_default_rules(self) -> None:
        """Initialize default resource management rules."""
        default_rules = [
            AutomationRule(
                rule_id='rule_high_cpu',
                name='Scale Up on High CPU',
                condition="resource_type == 'cpu' and utilization > 80",
                action_type=AutomationAction.SCALE_UP,
                priority=AutomationPriority.HIGH,
                cooldown_seconds=300
            ),
            AutomationRule(
                rule_id='rule_low_cpu',
                name='Scale Down on Low CPU',
                condition="resource_type == 'cpu' and utilization < 30",
                action_type=AutomationAction.SCALE_DOWN,
                priority=AutomationPriority.LOW,
                cooldown_seconds=600
            ),
            AutomationRule(
                rule_id='rule_high_memory',
                name='Scale Up on High Memory',
                condition="resource_type == 'memory' and utilization > 85",
                action_type=AutomationAction.SCALE_UP,
                priority=AutomationPriority.HIGH,
                cooldown_seconds=300
            ),
            AutomationRule(
                rule_id='rule_disk_space',
                name='Alert on Low Disk Space',
                condition="resource_type == 'disk' and utilization > 90",
                action_type=AutomationAction.ALERT_HUMAN,
                priority=AutomationPriority.CRITICAL,
                cooldown_seconds=1800
            )
        ]

        for rule in default_rules:
            if not any(r.rule_id == rule.rule_id for r in self.rules):
                self.add_rule(rule)

    def monitor_resources(self) -> Dict[str, Any]:
        """
        Monitor current resource utilization.

        Returns:
            Dictionary with resource metrics
        """
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'utilization': cpu_percent,
                    'threshold_up': self.thresholds['cpu']['scale_up'],
                    'threshold_down': self.thresholds['cpu']['scale_down']
                },
                'memory': {
                    'utilization': memory.percent,
                    'available_gb': memory.available / (1024**3),
                    'total_gb': memory.total / (1024**3),
                    'threshold_up': self.thresholds['memory']['scale_up'],
                    'threshold_down': self.thresholds['memory']['scale_down']
                },
                'disk': {
                    'utilization': disk.percent,
                    'free_gb': disk.free / (1024**3),
                    'total_gb': disk.total / (1024**3),
                    'threshold_up': self.thresholds['disk']['scale_up'],
                    'threshold_down': self.thresholds['disk']['scale_down']
                }
            }

            return metrics

        except Exception as e:
            logger.error(f"Error monitoring resources: {e}")
            return {'error': str(e)}

    def check_scaling_needed(self) -> List[Dict[str, Any]]:
        """
        Check if scaling is needed based on current metrics.

        Returns:
            List of scaling recommendations
        """
        metrics = self.monitor_resources()
        recommendations = []

        if 'error' in metrics:
            return recommendations

        # Check CPU
        cpu_util = metrics['cpu']['utilization']
        if cpu_util > self.thresholds['cpu']['scale_up']:
            recommendations.append({
                'resource': 'compute',
                'action': 'scale_up',
                'reason': f"CPU utilization {cpu_util:.1f}% exceeds threshold {self.thresholds['cpu']['scale_up']}%",
                'priority': 'high'
            })
        elif cpu_util < self.thresholds['cpu']['scale_down']:
            recommendations.append({
                'resource': 'compute',
                'action': 'scale_down',
                'reason': f"CPU utilization {cpu_util:.1f}% below threshold {self.thresholds['cpu']['scale_down']}%",
                'priority': 'low'
            })

        # Check Memory
        mem_util = metrics['memory']['utilization']
        if mem_util > self.thresholds['memory']['scale_up']:
            recommendations.append({
                'resource': 'memory',
                'action': 'scale_up',
                'reason': f"Memory utilization {mem_util:.1f}% exceeds threshold {self.thresholds['memory']['scale_up']}%",
                'priority': 'high'
            })
        elif mem_util < self.thresholds['memory']['scale_down']:
            recommendations.append({
                'resource': 'memory',
                'action': 'scale_down',
                'reason': f"Memory utilization {mem_util:.1f}% below threshold {self.thresholds['memory']['scale_down']}%",
                'priority': 'low'
            })

        # Check Disk
        disk_util = metrics['disk']['utilization']
        if disk_util > self.thresholds['disk']['scale_up']:
            recommendations.append({
                'resource': 'disk',
                'action': 'alert',
                'reason': f"Disk utilization {disk_util:.1f}% exceeds threshold {self.thresholds['disk']['scale_up']}%",
                'priority': 'critical'
            })

        return recommendations

    def scale_resource(self, resource_name: str, action: str) -> Dict[str, Any]:
        """
        Scale a resource up or down.

        Args:
            resource_name: Name of resource to scale
            action: 'scale_up' or 'scale_down'

        Returns:
            Dictionary with scaling result
        """
        if resource_name not in self.resource_pools:
            return {
                'success': False,
                'error': f"Unknown resource: {resource_name}"
            }

        pool = self.resource_pools[resource_name]
        current = pool['current']

        if action == 'scale_up':
            if current >= pool['max']:
                return {
                    'success': False,
                    'message': f"{resource_name} already at maximum capacity",
                    'current': current,
                    'max': pool['max']
                }

            new_value = min(current + 1, pool['max'])
            pool['current'] = new_value

            result = {
                'success': True,
                'action': 'scale_up',
                'resource': resource_name,
                'previous': current,
                'current': new_value,
                'message': f"Scaled up {resource_name} from {current} to {new_value}"
            }

        elif action == 'scale_down':
            if current <= pool['min']:
                return {
                    'success': False,
                    'message': f"{resource_name} already at minimum capacity",
                    'current': current,
                    'min': pool['min']
                }

            new_value = max(current - 1, pool['min'])
            pool['current'] = new_value

            result = {
                'success': True,
                'action': 'scale_down',
                'resource': resource_name,
                'previous': current,
                'current': new_value,
                'message': f"Scaled down {resource_name} from {current} to {new_value}"
            }

        else:
            return {
                'success': False,
                'error': f"Unknown action: {action}"
            }

        # Record scaling action
        result['timestamp'] = datetime.now().isoformat()
        self.scaling_history.append(result)
        self._save_scaling_history()

        logger.info(result['message'])
        return result

    def auto_scale(self) -> List[Dict[str, Any]]:
        """
        Automatically scale resources based on current metrics.

        Returns:
            List of scaling actions taken
        """
        recommendations = self.check_scaling_needed()
        actions_taken = []

        for rec in recommendations:
            if rec['action'] in ['scale_up', 'scale_down']:
                result = self.scale_resource(rec['resource'], rec['action'])
                if result['success']:
                    actions_taken.append(result)

        return actions_taken

    def process_event(self, event: AutomationEvent) -> Optional[AutomationResponse]:
        """
        Process a resource management event.

        Args:
            event: Event to process

        Returns:
            AutomationResponse if action taken, None otherwise
        """
        if not self.is_enabled:
            return None

        # Record event
        self.record_event(event)

        # Extract resource info from event
        resource_type = event.metadata.get('resource_type') if event.metadata else None
        utilization = event.metadata.get('utilization', 0) if event.metadata else 0

        if not resource_type:
            return None

        # Find matching rules
        context = {
            'resource_type': resource_type,
            'utilization': utilization,
            'severity': event.severity
        }

        matching_rules = []
        for rule in self.rules:
            if rule.enabled and self.evaluate_condition(rule.condition, context):
                matching_rules.append(rule)

        if not matching_rules:
            return None

        # Execute first matching rule
        rule = matching_rules[0]

        # Determine action
        if rule.action_type == AutomationAction.SCALE_UP:
            result = self.scale_resource('compute', 'scale_up')
        elif rule.action_type == AutomationAction.SCALE_DOWN:
            result = self.scale_resource('compute', 'scale_down')
        else:
            result = {'success': False, 'message': 'No action taken'}

        response = AutomationResponse(
            action_id=str(uuid.uuid4()),
            action_type=rule.action_type,
            timestamp=datetime.now().isoformat(),
            success=result.get('success', False),
            event_id=event.event_id,
            description=result.get('message', 'Resource scaling attempted'),
            result=result
        )

        self.record_response(response)
        return response

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get resource management system status.

        Returns:
            Dictionary with status information
        """
        stats = self.get_statistics()
        metrics = self.monitor_resources()
        recommendations = self.check_scaling_needed()

        return {
            'system_name': 'resource_management',
            'enabled': self.is_enabled,
            'statistics': stats,
            'current_metrics': metrics,
            'resource_pools': self.resource_pools,
            'scaling_recommendations': recommendations,
            'recent_scaling': self.scaling_history[-5:] if self.scaling_history else []
        }

    def _save_scaling_history(self) -> None:
        """Save scaling history to disk."""
        history_path = self.get_file_path('scaling_history.json')
        try:
            import json
            with open(history_path, 'w') as f:
                json.dump(self.scaling_history[-1000:], f, indent=2)
        except Exception as e:
            logger.error(f"Error saving scaling history: {e}")

    def get_scaling_analytics(self) -> Dict[str, Any]:
        """
        Get scaling analytics.

        Returns:
            Dictionary with analytics
        """
        if not self.scaling_history:
            return {'message': 'No scaling history available'}

        scale_up_count = sum(1 for s in self.scaling_history if s.get('action') == 'scale_up')
        scale_down_count = sum(1 for s in self.scaling_history if s.get('action') == 'scale_down')

        return {
            'total_scaling_actions': len(self.scaling_history),
            'scale_up_count': scale_up_count,
            'scale_down_count': scale_down_count,
            'resource_pools': self.resource_pools
        }


def main():
    """Main function for testing resource management system."""
    import argparse

    parser = argparse.ArgumentParser(description='Auto-Scaling Resource Management System')
    parser.add_argument('--vault-path', default='AI_Employee_Vault', help='Path to AI Employee Vault')
    parser.add_argument('--monitor', action='store_true', help='Monitor resources')
    parser.add_argument('--auto-scale', action='store_true', help='Run auto-scaling')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize system
    manager = ResourceManager(args.vault_path)

    if args.monitor:
        print("Monitoring System Resources...")
        print("=" * 80)

        metrics = manager.monitor_resources()

        if 'error' not in metrics:
            print(f"\nCPU:")
            print(f"  Utilization: {metrics['cpu']['utilization']:.1f}%")
            print(f"  Scale Up Threshold: {metrics['cpu']['threshold_up']}%")
            print(f"  Scale Down Threshold: {metrics['cpu']['threshold_down']}%")

            print(f"\nMemory:")
            print(f"  Utilization: {metrics['memory']['utilization']:.1f}%")
            print(f"  Available: {metrics['memory']['available_gb']:.2f} GB")
            print(f"  Total: {metrics['memory']['total_gb']:.2f} GB")

            print(f"\nDisk:")
            print(f"  Utilization: {metrics['disk']['utilization']:.1f}%")
            print(f"  Free: {metrics['disk']['free_gb']:.2f} GB")
            print(f"  Total: {metrics['disk']['total_gb']:.2f} GB")

            # Check recommendations
            recommendations = manager.check_scaling_needed()
            if recommendations:
                print(f"\nScaling Recommendations:")
                for rec in recommendations:
                    print(f"  - {rec['action'].upper()} {rec['resource']}: {rec['reason']}")
            else:
                print(f"\n✓ No scaling needed - all resources within thresholds")

    elif args.auto_scale:
        print("Running Auto-Scaling...")
        print("=" * 80)

        actions = manager.auto_scale()

        if actions:
            print(f"\nScaling actions taken:")
            for action in actions:
                print(f"  ✓ {action['message']}")
        else:
            print("\n✓ No scaling actions needed")

    else:
        print("Auto-Scaling Resource Management System initialized")
        print(f"Active rules: {len([r for r in manager.rules if r.enabled])}")
        print("\nResource Pools:")
        for pool_name, pool_info in manager.resource_pools.items():
            print(f"  {pool_name}: {pool_info['current']} (min: {pool_info['min']}, max: {pool_info['max']})")


if __name__ == '__main__':
    main()

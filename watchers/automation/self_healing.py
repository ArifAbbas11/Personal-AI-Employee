"""
Self-Healing System

Automatically detects and recovers from system errors and failures.
Integrates with error detection and implements recovery strategies.
"""

import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import time

from .base import (
    BaseAutomationSystem,
    AutomationEvent,
    AutomationResponse,
    AutomationRule,
    AutomationAction,
    AutomationPriority
)

logger = logging.getLogger(__name__)


class SelfHealingSystem(BaseAutomationSystem):
    """Self-healing system for automatic error recovery."""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        """
        Initialize Self-Healing System.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        super().__init__(vault_path, 'self_healing')

        # Recovery strategies
        self.recovery_strategies: Dict[str, callable] = {
            'restart_service': self._restart_service,
            'clear_cache': self._clear_cache,
            'reset_connection': self._reset_connection,
            'rollback_change': self._rollback_change,
            'increase_resources': self._increase_resources,
            'alert_human': self._alert_human
        }

        # Cooldown tracking
        self.last_action_time: Dict[str, datetime] = {}

        # Initialize default rules
        self._initialize_default_rules()

    def _initialize_default_rules(self) -> None:
        """Initialize default self-healing rules."""
        default_rules = [
            AutomationRule(
                rule_id='rule_connection_error',
                name='Connection Error Recovery',
                condition="event_type == 'connection_error' and severity in ['high', 'critical']",
                action_type=AutomationAction.HEAL_ERROR,
                priority=AutomationPriority.HIGH,
                cooldown_seconds=300
            ),
            AutomationRule(
                rule_id='rule_service_crash',
                name='Service Crash Recovery',
                condition="event_type == 'service_crash'",
                action_type=AutomationAction.RESTART_SERVICE,
                priority=AutomationPriority.CRITICAL,
                cooldown_seconds=60
            ),
            AutomationRule(
                rule_id='rule_memory_leak',
                name='Memory Leak Recovery',
                condition="event_type == 'memory_leak' and severity == 'high'",
                action_type=AutomationAction.RESTART_SERVICE,
                priority=AutomationPriority.HIGH,
                cooldown_seconds=600
            ),
            AutomationRule(
                rule_id='rule_disk_full',
                name='Disk Full Recovery',
                condition="event_type == 'disk_full'",
                action_type=AutomationAction.HEAL_ERROR,
                priority=AutomationPriority.CRITICAL,
                cooldown_seconds=300
            )
        ]

        for rule in default_rules:
            if not any(r.rule_id == rule.rule_id for r in self.rules):
                self.add_rule(rule)

    def process_event(self, event: AutomationEvent) -> Optional[AutomationResponse]:
        """
        Process an error event and attempt recovery.

        Args:
            event: Error event to process

        Returns:
            AutomationResponse if recovery attempted, None otherwise
        """
        if not self.is_enabled:
            return None

        # Record event
        self.record_event(event)

        # Find matching rules
        matching_rules = self._find_matching_rules(event)

        if not matching_rules:
            logger.debug(f"No matching rules for event {event.event_id}")
            return None

        # Sort by priority
        matching_rules.sort(key=lambda r: ['critical', 'high', 'medium', 'low'].index(r.priority.value))

        # Try each rule until one succeeds
        for rule in matching_rules:
            if not rule.enabled:
                continue

            # Check cooldown
            if not self._check_cooldown(rule):
                logger.info(f"Rule {rule.name} is in cooldown period")
                continue

            # Attempt recovery
            response = self._execute_recovery(event, rule)

            if response and response.success:
                self.record_response(response)
                self._update_cooldown(rule)
                return response

        # No successful recovery
        logger.warning(f"Failed to recover from event {event.event_id}")
        return None

    def _find_matching_rules(self, event: AutomationEvent) -> List[AutomationRule]:
        """
        Find rules that match the event.

        Args:
            event: Event to match

        Returns:
            List of matching rules
        """
        matching_rules = []

        context = {
            'event_type': event.event_type,
            'severity': event.severity,
            'source': event.source,
            'metadata': event.metadata or {}
        }

        for rule in self.rules:
            if self.evaluate_condition(rule.condition, context):
                matching_rules.append(rule)

        return matching_rules

    def _check_cooldown(self, rule: AutomationRule) -> bool:
        """
        Check if rule is in cooldown period.

        Args:
            rule: Rule to check

        Returns:
            True if not in cooldown, False otherwise
        """
        if rule.rule_id not in self.last_action_time:
            return True

        last_time = self.last_action_time[rule.rule_id]
        cooldown_end = last_time + timedelta(seconds=rule.cooldown_seconds)

        return datetime.now() >= cooldown_end

    def _update_cooldown(self, rule: AutomationRule) -> None:
        """
        Update cooldown timestamp for rule.

        Args:
            rule: Rule to update
        """
        self.last_action_time[rule.rule_id] = datetime.now()

    def _execute_recovery(self, event: AutomationEvent, rule: AutomationRule) -> AutomationResponse:
        """
        Execute recovery action for event.

        Args:
            event: Event to recover from
            rule: Rule to execute

        Returns:
            AutomationResponse with result
        """
        action_id = str(uuid.uuid4())

        try:
            # Determine recovery strategy
            strategy = self._select_recovery_strategy(event, rule)

            if strategy not in self.recovery_strategies:
                return AutomationResponse(
                    action_id=action_id,
                    action_type=rule.action_type,
                    timestamp=datetime.now().isoformat(),
                    success=False,
                    event_id=event.event_id,
                    description=f"Unknown recovery strategy: {strategy}",
                    error=f"Strategy '{strategy}' not implemented"
                )

            # Execute recovery
            logger.info(f"Executing recovery strategy '{strategy}' for event {event.event_id}")
            result = self.recovery_strategies[strategy](event, rule)

            return AutomationResponse(
                action_id=action_id,
                action_type=rule.action_type,
                timestamp=datetime.now().isoformat(),
                success=result.get('success', False),
                event_id=event.event_id,
                description=f"Executed {strategy}: {result.get('message', 'No message')}",
                result=result
            )

        except Exception as e:
            logger.error(f"Error executing recovery for event {event.event_id}: {e}")
            return AutomationResponse(
                action_id=action_id,
                action_type=rule.action_type,
                timestamp=datetime.now().isoformat(),
                success=False,
                event_id=event.event_id,
                description=f"Recovery failed: {str(e)}",
                error=str(e)
            )

    def _select_recovery_strategy(self, event: AutomationEvent, rule: AutomationRule) -> str:
        """
        Select appropriate recovery strategy.

        Args:
            event: Event to recover from
            rule: Matching rule

        Returns:
            Strategy name
        """
        # Map event types to strategies
        strategy_map = {
            'connection_error': 'reset_connection',
            'service_crash': 'restart_service',
            'memory_leak': 'restart_service',
            'disk_full': 'clear_cache',
            'timeout': 'reset_connection',
            'deadlock': 'restart_service'
        }

        return strategy_map.get(event.event_type, 'alert_human')

    # Recovery Strategy Implementations

    def _restart_service(self, event: AutomationEvent, rule: AutomationRule) -> Dict[str, Any]:
        """Restart a service."""
        service_name = event.metadata.get('service_name', 'unknown') if event.metadata else 'unknown'

        logger.info(f"Restarting service: {service_name}")

        # In production, this would actually restart the service
        # For now, simulate the action
        time.sleep(0.1)  # Simulate restart time

        return {
            'success': True,
            'message': f"Service {service_name} restarted successfully",
            'service_name': service_name,
            'action': 'restart'
        }

    def _clear_cache(self, event: AutomationEvent, rule: AutomationRule) -> Dict[str, Any]:
        """Clear system cache."""
        logger.info("Clearing system cache")

        # In production, this would clear actual caches
        # For now, simulate the action

        return {
            'success': True,
            'message': "System cache cleared successfully",
            'action': 'clear_cache',
            'space_freed': '500MB'  # Simulated
        }

    def _reset_connection(self, event: AutomationEvent, rule: AutomationRule) -> Dict[str, Any]:
        """Reset a connection."""
        connection_type = event.metadata.get('connection_type', 'unknown') if event.metadata else 'unknown'

        logger.info(f"Resetting connection: {connection_type}")

        # In production, this would reset actual connections
        # For now, simulate the action
        time.sleep(0.05)  # Simulate reset time

        return {
            'success': True,
            'message': f"Connection {connection_type} reset successfully",
            'connection_type': connection_type,
            'action': 'reset'
        }

    def _rollback_change(self, event: AutomationEvent, rule: AutomationRule) -> Dict[str, Any]:
        """Rollback a recent change."""
        logger.info("Rolling back recent change")

        # In production, this would rollback actual changes
        # For now, simulate the action

        return {
            'success': True,
            'message': "Change rolled back successfully",
            'action': 'rollback'
        }

    def _increase_resources(self, event: AutomationEvent, rule: AutomationRule) -> Dict[str, Any]:
        """Increase system resources."""
        resource_type = event.metadata.get('resource_type', 'memory') if event.metadata else 'memory'

        logger.info(f"Increasing {resource_type} resources")

        # In production, this would scale resources
        # For now, simulate the action

        return {
            'success': True,
            'message': f"{resource_type.capitalize()} resources increased",
            'resource_type': resource_type,
            'action': 'scale_up'
        }

    def _alert_human(self, event: AutomationEvent, rule: AutomationRule) -> Dict[str, Any]:
        """Alert human operator."""
        logger.warning(f"Alerting human operator for event {event.event_id}")

        # In production, this would send actual alerts
        # For now, log the alert

        return {
            'success': True,
            'message': "Human operator alerted",
            'action': 'alert',
            'event_id': event.event_id
        }

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get self-healing system status.

        Returns:
            Dictionary with status information
        """
        stats = self.get_statistics()

        return {
            'system_name': 'self_healing',
            'enabled': self.is_enabled,
            'statistics': stats,
            'active_rules': [
                {
                    'rule_id': r.rule_id,
                    'name': r.name,
                    'priority': r.priority.value,
                    'enabled': r.enabled
                }
                for r in self.rules if r.enabled
            ],
            'recent_events': [e.to_dict() for e in self.get_recent_events(5)],
            'recent_responses': [r.to_dict() for r in self.get_recent_responses(5)]
        }

    def test_recovery(self, event_type: str, severity: str = 'high') -> Dict[str, Any]:
        """
        Test recovery for a specific event type.

        Args:
            event_type: Type of event to test
            severity: Severity level

        Returns:
            Dictionary with test results
        """
        # Create test event
        test_event = AutomationEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            severity=severity,
            source='test',
            description=f"Test event for {event_type}",
            metadata={'test': True}
        )

        # Process event
        response = self.process_event(test_event)

        return {
            'test_event': test_event.to_dict(),
            'response': response.to_dict() if response else None,
            'success': response.success if response else False
        }


def main():
    """Main function for testing self-healing system."""
    import argparse

    parser = argparse.ArgumentParser(description='Self-Healing System')
    parser.add_argument('--vault-path', default='AI_Employee_Vault', help='Path to AI Employee Vault')
    parser.add_argument('--test', action='store_true', help='Run test scenarios')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize system
    system = SelfHealingSystem(args.vault_path)

    if args.test:
        print("Testing Self-Healing System...")
        print("=" * 80)

        # Test scenarios
        test_scenarios = [
            ('connection_error', 'high'),
            ('service_crash', 'critical'),
            ('memory_leak', 'high'),
            ('disk_full', 'critical')
        ]

        for event_type, severity in test_scenarios:
            print(f"\nTesting {event_type} (severity: {severity})...")
            result = system.test_recovery(event_type, severity)

            if result['success']:
                print(f"  ✓ Recovery successful")
                print(f"  Action: {result['response']['description']}")
            else:
                print(f"  ✗ Recovery failed")

        # Print statistics
        print("\n" + "=" * 80)
        print("System Statistics:")
        stats = system.get_statistics()
        print(f"  Total events: {stats['total_events']}")
        print(f"  Total responses: {stats['total_responses']}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Active rules: {stats['active_rules']}")

    else:
        print("Self-Healing System initialized")
        print(f"Active rules: {len([r for r in system.rules if r.enabled])}")
        print(f"Total rules: {len(system.rules)}")


if __name__ == '__main__':
    main()

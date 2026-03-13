"""
Base classes for Advanced Automation systems.

Provides common functionality for self-healing, task routing, and resource management.
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class AutomationAction(Enum):
    """Types of automation actions."""
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    ROUTE_TASK = "route_task"
    HEAL_ERROR = "heal_error"
    OPTIMIZE_RESOURCE = "optimize_resource"
    SCHEDULE_MAINTENANCE = "schedule_maintenance"
    ALERT_HUMAN = "alert_human"


class AutomationPriority(Enum):
    """Priority levels for automation actions."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AutomationEvent:
    """An event that triggers automation."""
    event_id: str
    event_type: str
    timestamp: str
    severity: str
    source: str
    description: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutomationEvent':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class AutomationResponse:
    """Response from an automation action."""
    action_id: str
    action_type: AutomationAction
    timestamp: str
    success: bool
    event_id: str
    description: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['action_type'] = self.action_type.value
        return data


@dataclass
class AutomationRule:
    """Rule for automated actions."""
    rule_id: str
    name: str
    condition: str  # Python expression to evaluate
    action_type: AutomationAction
    priority: AutomationPriority
    enabled: bool = True
    cooldown_seconds: int = 300  # 5 minutes default
    max_retries: int = 3
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['action_type'] = self.action_type.value
        data['priority'] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutomationRule':
        """Create from dictionary."""
        data['action_type'] = AutomationAction(data['action_type'])
        data['priority'] = AutomationPriority(data['priority'])
        return cls(**data)


class BaseAutomationSystem(ABC):
    """Base class for automation systems."""

    def __init__(self, vault_path: str, system_name: str):
        """
        Initialize base automation system.

        Args:
            vault_path: Path to AI_Employee_Vault
            system_name: Name of the automation system
        """
        self.vault_path = Path(vault_path)
        self.system_name = system_name
        self.system_dir = self.vault_path / "Automation" / system_name
        self.system_dir.mkdir(parents=True, exist_ok=True)

        self.rules: List[AutomationRule] = []
        self.event_history: List[AutomationEvent] = []
        self.response_history: List[AutomationResponse] = []
        self.is_enabled = True

        # Load existing rules and history
        self._load_rules()
        self._load_history()

    @abstractmethod
    def process_event(self, event: AutomationEvent) -> Optional[AutomationResponse]:
        """
        Process an automation event.

        Args:
            event: Event to process

        Returns:
            AutomationResponse if action taken, None otherwise
        """
        pass

    @abstractmethod
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status.

        Returns:
            Dictionary with status information
        """
        pass

    def add_rule(self, rule: AutomationRule) -> None:
        """
        Add an automation rule.

        Args:
            rule: Rule to add
        """
        self.rules.append(rule)
        self._save_rules()
        logger.info(f"Added automation rule: {rule.name}")

    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove an automation rule.

        Args:
            rule_id: ID of rule to remove

        Returns:
            True if removed, False if not found
        """
        for i, rule in enumerate(self.rules):
            if rule.rule_id == rule_id:
                self.rules.pop(i)
                self._save_rules()
                logger.info(f"Removed automation rule: {rule_id}")
                return True
        return False

    def enable_rule(self, rule_id: str) -> bool:
        """
        Enable an automation rule.

        Args:
            rule_id: ID of rule to enable

        Returns:
            True if enabled, False if not found
        """
        for rule in self.rules:
            if rule.rule_id == rule_id:
                rule.enabled = True
                self._save_rules()
                logger.info(f"Enabled automation rule: {rule_id}")
                return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """
        Disable an automation rule.

        Args:
            rule_id: ID of rule to disable

        Returns:
            True if disabled, False if not found
        """
        for rule in self.rules:
            if rule.rule_id == rule_id:
                rule.enabled = False
                self._save_rules()
                logger.info(f"Disabled automation rule: {rule_id}")
                return True
        return False

    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a rule condition.

        Args:
            condition: Python expression to evaluate
            context: Context variables for evaluation

        Returns:
            True if condition met, False otherwise
        """
        try:
            # Safe evaluation with limited context
            return eval(condition, {"__builtins__": {}}, context)
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False

    def record_event(self, event: AutomationEvent) -> None:
        """
        Record an automation event.

        Args:
            event: Event to record
        """
        self.event_history.append(event)
        self._save_history()

    def record_response(self, response: AutomationResponse) -> None:
        """
        Record an automation response.

        Args:
            response: Response to record
        """
        self.response_history.append(response)
        self._save_history()

    def get_recent_events(self, count: int = 10) -> List[AutomationEvent]:
        """
        Get recent automation events.

        Args:
            count: Number of events to return

        Returns:
            List of recent events
        """
        return self.event_history[-count:]

    def get_recent_responses(self, count: int = 10) -> List[AutomationResponse]:
        """
        Get recent automation responses.

        Args:
            count: Number of responses to return

        Returns:
            List of recent responses
        """
        return self.response_history[-count:]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get automation statistics.

        Returns:
            Dictionary with statistics
        """
        total_events = len(self.event_history)
        total_responses = len(self.response_history)
        successful_responses = sum(1 for r in self.response_history if r.success)

        return {
            'total_events': total_events,
            'total_responses': total_responses,
            'successful_responses': successful_responses,
            'success_rate': (successful_responses / total_responses * 100) if total_responses > 0 else 0,
            'active_rules': sum(1 for r in self.rules if r.enabled),
            'total_rules': len(self.rules)
        }

    def _save_rules(self) -> None:
        """Save automation rules to disk."""
        rules_path = self.system_dir / "rules.json"
        try:
            with open(rules_path, 'w') as f:
                json.dump([r.to_dict() for r in self.rules], f, indent=2)
            logger.debug(f"Saved {len(self.rules)} rules for {self.system_name}")
        except Exception as e:
            logger.error(f"Error saving rules: {e}")

    def _load_rules(self) -> None:
        """Load automation rules from disk."""
        rules_path = self.system_dir / "rules.json"
        if rules_path.exists():
            try:
                with open(rules_path, 'r') as f:
                    rules_data = json.load(f)
                self.rules = [AutomationRule.from_dict(r) for r in rules_data]
                logger.info(f"Loaded {len(self.rules)} rules for {self.system_name}")
            except Exception as e:
                logger.error(f"Error loading rules: {e}")
                self.rules = []

    def _save_history(self) -> None:
        """Save event and response history to disk."""
        history_path = self.system_dir / "history.json"
        try:
            history_data = {
                'events': [e.to_dict() for e in self.event_history[-1000:]],  # Keep last 1000
                'responses': [r.to_dict() for r in self.response_history[-1000:]]
            }
            with open(history_path, 'w') as f:
                json.dump(history_data, f, indent=2)
            logger.debug(f"Saved history for {self.system_name}")
        except Exception as e:
            logger.error(f"Error saving history: {e}")

    def _load_history(self) -> None:
        """Load event and response history from disk."""
        history_path = self.system_dir / "history.json"
        if history_path.exists():
            try:
                with open(history_path, 'r') as f:
                    history_data = json.load(f)
                self.event_history = [AutomationEvent.from_dict(e) for e in history_data.get('events', [])]
                self.response_history = [
                    AutomationResponse(
                        action_id=r['action_id'],
                        action_type=AutomationAction(r['action_type']),
                        timestamp=r['timestamp'],
                        success=r['success'],
                        event_id=r['event_id'],
                        description=r['description'],
                        result=r.get('result'),
                        error=r.get('error')
                    )
                    for r in history_data.get('responses', [])
                ]
                logger.info(f"Loaded history for {self.system_name}")
            except Exception as e:
                logger.error(f"Error loading history: {e}")
                self.event_history = []
                self.response_history = []

    def get_file_path(self, filename: str) -> Path:
        """Get full path for system file."""
        return self.system_dir / filename

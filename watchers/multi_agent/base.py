"""
Multi-Agent Coordination System - Base Infrastructure

Provides base classes and coordination mechanisms for specialized AI agents.
Enables agent communication, task delegation, and collaborative problem-solving.
"""

import json
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from enum import Enum

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent role types."""
    FINANCIAL = "financial"
    MARKETING = "marketing"
    OPERATIONS = "operations"
    RESEARCH = "research"
    CUSTOMER_SERVICE = "customer_service"


class AgentStatus(Enum):
    """Agent status types."""
    IDLE = "idle"
    BUSY = "busy"
    WAITING = "waiting"
    ERROR = "error"
    OFFLINE = "offline"


class MessageType(Enum):
    """Inter-agent message types."""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    INFORMATION_REQUEST = "information_request"
    INFORMATION_RESPONSE = "information_response"
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_RESPONSE = "collaboration_response"
    STATUS_UPDATE = "status_update"
    ERROR_NOTIFICATION = "error_notification"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AgentMessage:
    """Message between agents."""
    message_id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    timestamp: str
    content: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    requires_response: bool = False
    in_response_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        data['priority'] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create from dictionary."""
        data['message_type'] = MessageType(data['message_type'])
        data['priority'] = TaskPriority(data['priority'])
        return cls(**data)


@dataclass
class AgentTask:
    """Task assigned to an agent."""
    task_id: str
    task_type: str
    description: str
    priority: TaskPriority
    assigned_to: str
    assigned_by: Optional[str]
    created_at: str
    deadline: Optional[str] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['priority'] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentTask':
        """Create from dictionary."""
        data['priority'] = TaskPriority(data['priority'])
        return cls(**data)


@dataclass
class AgentCapability:
    """Agent capability definition."""
    capability_id: str
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    estimated_duration_seconds: int = 60
    requires_human_approval: bool = False


class AgentCoordinator:
    """Coordinates communication and task delegation between agents."""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        """
        Initialize Agent Coordinator.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.vault_path = Path(vault_path)
        self.coordination_dir = self.vault_path / "Multi_Agent"
        self.coordination_dir.mkdir(parents=True, exist_ok=True)

        # Agent registry
        self.agents: Dict[str, 'BaseAgent'] = {}

        # Message queue
        self.message_queue: List[AgentMessage] = []

        # Task registry
        self.tasks: Dict[str, AgentTask] = {}

        # Load state
        self._load_state()

    def register_agent(self, agent: 'BaseAgent') -> None:
        """
        Register an agent with the coordinator.

        Args:
            agent: Agent to register
        """
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.agent_id} ({agent.role.value})")
        self._save_state()

    def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent.

        Args:
            agent_id: Agent ID to unregister
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")
            self._save_state()

    def send_message(self, message: AgentMessage) -> bool:
        """
        Send a message between agents.

        Args:
            message: Message to send

        Returns:
            True if message sent successfully
        """
        # Validate agents exist
        if message.from_agent not in self.agents:
            logger.error(f"Sender agent not found: {message.from_agent}")
            return False

        if message.to_agent not in self.agents:
            logger.error(f"Recipient agent not found: {message.to_agent}")
            return False

        # Add to queue
        self.message_queue.append(message)

        # Deliver message
        recipient = self.agents[message.to_agent]
        recipient.receive_message(message)

        logger.info(f"Message sent: {message.from_agent} -> {message.to_agent} ({message.message_type.value})")
        self._save_state()
        return True

    def delegate_task(
        self,
        task_type: str,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        assigned_by: Optional[str] = None,
        deadline: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[AgentTask]:
        """
        Delegate a task to the most appropriate agent.

        Args:
            task_type: Type of task
            description: Task description
            priority: Task priority
            assigned_by: Agent ID that assigned the task
            deadline: Optional deadline
            metadata: Optional task metadata

        Returns:
            AgentTask if delegated successfully, None otherwise
        """
        # Find capable agents
        capable_agents = self._find_capable_agents(task_type)

        if not capable_agents:
            logger.warning(f"No capable agents found for task type: {task_type}")
            return None

        # Select best agent (currently simple: first available)
        selected_agent = self._select_best_agent(capable_agents, priority)

        if not selected_agent:
            logger.warning(f"No available agents for task type: {task_type}")
            return None

        # Create task
        task = AgentTask(
            task_id=str(uuid.uuid4()),
            task_type=task_type,
            description=description,
            priority=priority,
            assigned_to=selected_agent.agent_id,
            assigned_by=assigned_by,
            created_at=datetime.now().isoformat(),
            deadline=deadline,
            metadata=metadata or {}
        )

        # Register task
        self.tasks[task.task_id] = task

        # Assign to agent
        selected_agent.assign_task(task)

        logger.info(f"Task delegated: {task.task_id} -> {selected_agent.agent_id}")
        self._save_state()
        return task

    def _find_capable_agents(self, task_type: str) -> List['BaseAgent']:
        """Find agents capable of handling a task type."""
        capable = []
        for agent in self.agents.values():
            if agent.can_handle_task(task_type):
                capable.append(agent)
        return capable

    def _select_best_agent(
        self,
        capable_agents: List['BaseAgent'],
        priority: TaskPriority
    ) -> Optional['BaseAgent']:
        """Select the best agent for a task."""
        # Filter by status
        available = [a for a in capable_agents if a.status == AgentStatus.IDLE]

        if not available:
            # Try busy agents if high priority
            if priority in [TaskPriority.CRITICAL, TaskPriority.HIGH]:
                available = [a for a in capable_agents if a.status == AgentStatus.BUSY]

        if not available:
            return None

        # Select first available (can be enhanced with load balancing)
        return available[0]

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a task."""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        return {
            'task_id': task.task_id,
            'status': task.status,
            'assigned_to': task.assigned_to,
            'result': task.result,
            'error': task.error
        }

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an agent."""
        if agent_id not in self.agents:
            return None

        agent = self.agents[agent_id]
        return {
            'agent_id': agent.agent_id,
            'role': agent.role.value,
            'status': agent.status.value,
            'active_tasks': len(agent.active_tasks),
            'completed_tasks': agent.tasks_completed,
            'capabilities': [c.name for c in agent.capabilities]
        }

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            'total_agents': len(self.agents),
            'active_agents': sum(1 for a in self.agents.values() if a.status != AgentStatus.OFFLINE),
            'total_tasks': len(self.tasks),
            'pending_tasks': sum(1 for t in self.tasks.values() if t.status == 'pending'),
            'active_tasks': sum(1 for t in self.tasks.values() if t.status == 'in_progress'),
            'completed_tasks': sum(1 for t in self.tasks.values() if t.status == 'completed'),
            'message_queue_size': len(self.message_queue),
            'agents': {
                agent_id: {
                    'role': agent.role.value,
                    'status': agent.status.value,
                    'active_tasks': len(agent.active_tasks)
                }
                for agent_id, agent in self.agents.items()
            }
        }

    def _save_state(self) -> None:
        """Save coordinator state to disk."""
        state_path = self.coordination_dir / "coordinator_state.json"
        try:
            state = {
                'agents': {
                    agent_id: {
                        'agent_id': agent.agent_id,
                        'role': agent.role.value,
                        'status': agent.status.value
                    }
                    for agent_id, agent in self.agents.items()
                },
                'tasks': {
                    task_id: task.to_dict()
                    for task_id, task in self.tasks.items()
                },
                'message_queue': [m.to_dict() for m in self.message_queue[-100:]]  # Keep last 100
            }
            with open(state_path, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving coordinator state: {e}")

    def _load_state(self) -> None:
        """Load coordinator state from disk."""
        state_path = self.coordination_dir / "coordinator_state.json"
        if state_path.exists():
            try:
                with open(state_path, 'r') as f:
                    state = json.load(f)

                # Load tasks
                self.tasks = {
                    task_id: AgentTask.from_dict(task_data)
                    for task_id, task_data in state.get('tasks', {}).items()
                }

                # Load message queue
                self.message_queue = [
                    AgentMessage.from_dict(m)
                    for m in state.get('message_queue', [])
                ]

                logger.info(f"Loaded coordinator state: {len(self.tasks)} tasks, {len(self.message_queue)} messages")
            except Exception as e:
                logger.error(f"Error loading coordinator state: {e}")


class BaseAgent(ABC):
    """Base class for all specialized agents."""

    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        vault_path: str = "AI_Employee_Vault",
        coordinator: Optional[AgentCoordinator] = None
    ):
        """
        Initialize base agent.

        Args:
            agent_id: Unique agent identifier
            role: Agent role
            vault_path: Path to AI_Employee_Vault
            coordinator: Optional agent coordinator
        """
        self.agent_id = agent_id
        self.role = role
        self.vault_path = Path(vault_path)
        self.agent_dir = self.vault_path / "Multi_Agent" / agent_id
        self.agent_dir.mkdir(parents=True, exist_ok=True)

        self.coordinator = coordinator
        self.status = AgentStatus.IDLE
        self.capabilities: List[AgentCapability] = []
        self.active_tasks: Dict[str, AgentTask] = {}
        self.inbox: List[AgentMessage] = []
        self.tasks_completed = 0

        # Initialize capabilities
        self._initialize_capabilities()

        # Register with coordinator
        if self.coordinator:
            self.coordinator.register_agent(self)

    @abstractmethod
    def _initialize_capabilities(self) -> None:
        """Initialize agent capabilities."""
        pass

    @abstractmethod
    def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Process an assigned task.

        Args:
            task: Task to process

        Returns:
            Task result dictionary
        """
        pass

    def can_handle_task(self, task_type: str) -> bool:
        """
        Check if agent can handle a task type.

        Args:
            task_type: Task type to check

        Returns:
            True if agent can handle the task
        """
        return any(cap.capability_id == task_type for cap in self.capabilities)

    def assign_task(self, task: AgentTask) -> None:
        """
        Assign a task to this agent.

        Args:
            task: Task to assign
        """
        self.active_tasks[task.task_id] = task
        task.status = "in_progress"
        self.status = AgentStatus.BUSY

        logger.info(f"Task assigned to {self.agent_id}: {task.task_id}")

        # Process task
        try:
            result = self.process_task(task)
            self.complete_task(task.task_id, result)
        except Exception as e:
            self.fail_task(task.task_id, str(e))

    def complete_task(self, task_id: str, result: Dict[str, Any]) -> None:
        """
        Mark a task as completed.

        Args:
            task_id: Task ID
            result: Task result
        """
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = "completed"
            task.result = result
            del self.active_tasks[task_id]
            self.tasks_completed += 1

            # Update status
            if not self.active_tasks:
                self.status = AgentStatus.IDLE

            logger.info(f"Task completed by {self.agent_id}: {task_id}")

    def fail_task(self, task_id: str, error: str) -> None:
        """
        Mark a task as failed.

        Args:
            task_id: Task ID
            error: Error message
        """
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = "failed"
            task.error = error
            del self.active_tasks[task_id]

            # Update status
            if not self.active_tasks:
                self.status = AgentStatus.IDLE

            logger.error(f"Task failed for {self.agent_id}: {task_id} - {error}")

    def receive_message(self, message: AgentMessage) -> None:
        """
        Receive a message from another agent.

        Args:
            message: Message received
        """
        self.inbox.append(message)
        logger.info(f"Message received by {self.agent_id} from {message.from_agent}")

        # Process message
        self._process_message(message)

    def _process_message(self, message: AgentMessage) -> None:
        """Process a received message."""
        # Default implementation - can be overridden
        if message.message_type == MessageType.TASK_REQUEST:
            # Handle task request
            pass
        elif message.message_type == MessageType.INFORMATION_REQUEST:
            # Handle information request
            pass

    def send_message(
        self,
        to_agent: str,
        message_type: MessageType,
        content: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        requires_response: bool = False
    ) -> bool:
        """
        Send a message to another agent.

        Args:
            to_agent: Recipient agent ID
            message_type: Type of message
            content: Message content
            priority: Message priority
            requires_response: Whether response is required

        Returns:
            True if message sent successfully
        """
        if not self.coordinator:
            logger.error(f"Agent {self.agent_id} has no coordinator")
            return False

        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            timestamp=datetime.now().isoformat(),
            content=content,
            priority=priority,
            requires_response=requires_response
        )

        return self.coordinator.send_message(message)

    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            'agent_id': self.agent_id,
            'role': self.role.value,
            'status': self.status.value,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': self.tasks_completed,
            'inbox_size': len(self.inbox),
            'capabilities': [
                {
                    'id': cap.capability_id,
                    'name': cap.name,
                    'description': cap.description
                }
                for cap in self.capabilities
            ]
        }

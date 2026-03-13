"""
Operations Agent

Specialized agent for operations management, task coordination, and resource allocation.
Integrates with Task Router and Resource Manager for intelligent operations.
"""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_agent.base import (
    BaseAgent,
    AgentRole,
    AgentCapability,
    AgentTask,
    AgentCoordinator,
    TaskPriority
)

logger = logging.getLogger(__name__)


class OperationsAgent(BaseAgent):
    """Agent specialized in operations management and task coordination."""

    def __init__(
        self,
        vault_path: str = "AI_Employee_Vault",
        coordinator: Optional[AgentCoordinator] = None
    ):
        """
        Initialize Operations Agent.

        Args:
            vault_path: Path to AI_Employee_Vault
            coordinator: Optional agent coordinator
        """
        super().__init__(
            agent_id="operations_agent",
            role=AgentRole.OPERATIONS,
            vault_path=vault_path,
            coordinator=coordinator
        )

        # Operations data
        self.projects: Dict[str, Dict[str, Any]] = {}
        self.tasks: List[Dict[str, Any]] = []
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.workflows: Dict[str, Dict[str, Any]] = {}

    def _initialize_capabilities(self) -> None:
        """Initialize operations agent capabilities."""
        self.capabilities = [
            AgentCapability(
                capability_id="create_project",
                name="Create Project",
                description="Create and initialize a new project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "deadline": {"type": "string"},
                        "priority": {"type": "string"}
                    },
                    "required": ["name", "description"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                        "created": {"type": "boolean"}
                    }
                },
                estimated_duration_seconds=15
            ),
            AgentCapability(
                capability_id="assign_task",
                name="Assign Task",
                description="Assign a task to a team member or agent",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_description": {"type": "string"},
                        "assignee": {"type": "string"},
                        "priority": {"type": "string"},
                        "deadline": {"type": "string"}
                    },
                    "required": ["task_description", "assignee"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "assigned": {"type": "boolean"}
                    }
                },
                estimated_duration_seconds=10
            ),
            AgentCapability(
                capability_id="track_progress",
                name="Track Progress",
                description="Track project and task progress",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                        "include_tasks": {"type": "boolean"}
                    },
                    "required": ["project_id"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "progress": {"type": "object"}
                    }
                },
                estimated_duration_seconds=15
            ),
            AgentCapability(
                capability_id="allocate_resources",
                name="Allocate Resources",
                description="Allocate resources to projects and tasks",
                input_schema={
                    "type": "object",
                    "properties": {
                        "resource_type": {"type": "string"},
                        "amount": {"type": "number"},
                        "project_id": {"type": "string"}
                    },
                    "required": ["resource_type", "amount", "project_id"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "allocated": {"type": "boolean"}
                    }
                },
                estimated_duration_seconds=10
            ),
            AgentCapability(
                capability_id="identify_bottlenecks",
                name="Identify Bottlenecks",
                description="Identify bottlenecks in projects and workflows",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                        "analysis_depth": {"type": "string"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "bottlenecks": {"type": "array"}
                    }
                },
                estimated_duration_seconds=30
            ),
            AgentCapability(
                capability_id="optimize_workflow",
                name="Optimize Workflow",
                description="Optimize workflows and processes",
                input_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string"},
                        "optimization_goals": {"type": "array"}
                    },
                    "required": ["workflow_id"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "optimizations": {"type": "array"}
                    }
                },
                estimated_duration_seconds=45
            ),
            AgentCapability(
                capability_id="generate_status_report",
                name="Generate Status Report",
                description="Generate comprehensive operations status report",
                input_schema={
                    "type": "object",
                    "properties": {
                        "report_type": {"type": "string"},
                        "include_metrics": {"type": "boolean"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "report": {"type": "object"}
                    }
                },
                estimated_duration_seconds=30
            )
        ]

    def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Process an operations task.

        Args:
            task: Task to process

        Returns:
            Task result dictionary
        """
        task_type = task.task_type
        metadata = task.metadata

        if task_type == "create_project":
            return self._create_project(metadata)
        elif task_type == "assign_task":
            return self._assign_task(metadata)
        elif task_type == "track_progress":
            return self._track_progress(metadata)
        elif task_type == "allocate_resources":
            return self._allocate_resources(metadata)
        elif task_type == "identify_bottlenecks":
            return self._identify_bottlenecks(metadata)
        elif task_type == "optimize_workflow":
            return self._optimize_workflow(metadata)
        elif task_type == "generate_status_report":
            return self._generate_status_report(metadata)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def _create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project."""
        import uuid

        project_id = str(uuid.uuid4())
        project = {
            'project_id': project_id,
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'deadline': data.get('deadline'),
            'priority': data.get('priority', 'medium'),
            'status': 'active',
            'progress': 0,
            'tasks': [],
            'created_at': datetime.now().isoformat()
        }

        self.projects[project_id] = project
        self._save_projects()

        logger.info(f"Project created: {project_id} - {project['name']}")

        return {
            'success': True,
            'project_id': project_id,
            'created': True,
            'project': project
        }

    def _assign_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assign a task to a team member or agent."""
        import uuid

        task_id = str(uuid.uuid4())
        task = {
            'task_id': task_id,
            'description': data.get('task_description', ''),
            'assignee': data.get('assignee', ''),
            'priority': data.get('priority', 'medium'),
            'deadline': data.get('deadline'),
            'status': 'assigned',
            'progress': 0,
            'assigned_at': datetime.now().isoformat()
        }

        self.tasks.append(task)
        self._save_tasks()

        # If assignee is an agent, delegate through coordinator
        if self.coordinator and data.get('assignee', '').endswith('_agent'):
            # This would delegate to another agent
            pass

        logger.info(f"Task assigned: {task_id} to {task['assignee']}")

        return {
            'success': True,
            'task_id': task_id,
            'assigned': True,
            'task': task
        }

    def _track_progress(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Track project and task progress."""
        project_id = data.get('project_id')
        include_tasks = data.get('include_tasks', True)

        if project_id not in self.projects:
            return {
                'success': False,
                'message': f"Project not found: {project_id}"
            }

        project = self.projects[project_id]

        # Get project tasks
        project_tasks = [
            t for t in self.tasks
            if t.get('project_id') == project_id
        ]

        # Calculate progress
        if project_tasks:
            completed_tasks = sum(1 for t in project_tasks if t.get('status') == 'completed')
            progress = (completed_tasks / len(project_tasks) * 100) if project_tasks else 0
        else:
            progress = project.get('progress', 0)

        result = {
            'success': True,
            'project_id': project_id,
            'project_name': project['name'],
            'progress': progress,
            'status': project['status'],
            'total_tasks': len(project_tasks),
            'completed_tasks': sum(1 for t in project_tasks if t.get('status') == 'completed'),
            'in_progress_tasks': sum(1 for t in project_tasks if t.get('status') == 'in_progress'),
            'pending_tasks': sum(1 for t in project_tasks if t.get('status') == 'pending')
        }

        if include_tasks:
            result['tasks'] = [
                {
                    'task_id': t['task_id'],
                    'description': t['description'],
                    'status': t['status'],
                    'assignee': t.get('assignee', 'unassigned')
                }
                for t in project_tasks
            ]

        return result

    def _allocate_resources(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Allocate resources to a project."""
        resource_type = data.get('resource_type', '')
        amount = data.get('amount', 0)
        project_id = data.get('project_id', '')

        if project_id not in self.projects:
            return {
                'success': False,
                'message': f"Project not found: {project_id}"
            }

        # Track resource allocation
        allocation_key = f"{project_id}_{resource_type}"
        if allocation_key not in self.resources:
            self.resources[allocation_key] = {
                'project_id': project_id,
                'resource_type': resource_type,
                'allocated': 0,
                'used': 0
            }

        self.resources[allocation_key]['allocated'] += amount
        self._save_resources()

        logger.info(f"Allocated {amount} {resource_type} to project {project_id}")

        return {
            'success': True,
            'allocated': True,
            'resource_type': resource_type,
            'amount': amount,
            'project_id': project_id,
            'total_allocated': self.resources[allocation_key]['allocated']
        }

    def _identify_bottlenecks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify bottlenecks in a project."""
        project_id = data.get('project_id')

        if project_id and project_id not in self.projects:
            return {
                'success': False,
                'message': f"Project not found: {project_id}"
            }

        bottlenecks = []

        # Analyze tasks
        if project_id:
            project_tasks = [t for t in self.tasks if t.get('project_id') == project_id]
        else:
            project_tasks = self.tasks

        # Check for overdue tasks
        now = datetime.now().isoformat()
        overdue_tasks = [
            t for t in project_tasks
            if t.get('deadline') and t.get('deadline') < now and t.get('status') != 'completed'
        ]

        if overdue_tasks:
            bottlenecks.append({
                'type': 'overdue_tasks',
                'severity': 'high',
                'count': len(overdue_tasks),
                'description': f"{len(overdue_tasks)} tasks are overdue",
                'recommendation': "Review and reprioritize overdue tasks"
            })

        # Check for blocked tasks
        blocked_tasks = [t for t in project_tasks if t.get('status') == 'blocked']
        if blocked_tasks:
            bottlenecks.append({
                'type': 'blocked_tasks',
                'severity': 'high',
                'count': len(blocked_tasks),
                'description': f"{len(blocked_tasks)} tasks are blocked",
                'recommendation': "Resolve blockers to unblock tasks"
            })

        # Check for resource constraints
        if project_id:
            project_resources = {
                k: v for k, v in self.resources.items()
                if v['project_id'] == project_id
            }
            for key, resource in project_resources.items():
                if resource['used'] >= resource['allocated'] * 0.9:
                    bottlenecks.append({
                        'type': 'resource_constraint',
                        'severity': 'medium',
                        'resource_type': resource['resource_type'],
                        'description': f"{resource['resource_type']} at 90% capacity",
                        'recommendation': f"Allocate more {resource['resource_type']}"
                    })

        # Check for unassigned tasks
        unassigned_tasks = [t for t in project_tasks if not t.get('assignee')]
        if unassigned_tasks:
            bottlenecks.append({
                'type': 'unassigned_tasks',
                'severity': 'medium',
                'count': len(unassigned_tasks),
                'description': f"{len(unassigned_tasks)} tasks are unassigned",
                'recommendation': "Assign tasks to team members"
            })

        return {
            'success': True,
            'project_id': project_id,
            'bottlenecks': bottlenecks,
            'bottleneck_count': len(bottlenecks),
            'severity_breakdown': {
                'high': sum(1 for b in bottlenecks if b['severity'] == 'high'),
                'medium': sum(1 for b in bottlenecks if b['severity'] == 'medium'),
                'low': sum(1 for b in bottlenecks if b['severity'] == 'low')
            }
        }

    def _optimize_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize a workflow."""
        workflow_id = data.get('workflow_id')
        optimization_goals = data.get('optimization_goals', ['efficiency', 'quality'])

        if workflow_id not in self.workflows:
            return {
                'success': False,
                'message': f"Workflow not found: {workflow_id}"
            }

        workflow = self.workflows[workflow_id]
        optimizations = []

        # Analyze workflow steps
        steps = workflow.get('steps', [])

        # Identify parallel opportunities
        sequential_steps = [s for s in steps if not s.get('can_parallelize', False)]
        if len(sequential_steps) > 3:
            optimizations.append({
                'type': 'parallelization',
                'impact': 'high',
                'description': "Identify steps that can run in parallel",
                'estimated_improvement': '30-40% time reduction'
            })

        # Identify automation opportunities
        manual_steps = [s for s in steps if s.get('manual', True)]
        if manual_steps:
            optimizations.append({
                'type': 'automation',
                'impact': 'high',
                'description': f"Automate {len(manual_steps)} manual steps",
                'estimated_improvement': '50-60% time reduction'
            })

        # Identify redundant steps
        if len(steps) > 5:
            optimizations.append({
                'type': 'simplification',
                'impact': 'medium',
                'description': "Review workflow for redundant steps",
                'estimated_improvement': '10-20% time reduction'
            })

        return {
            'success': True,
            'workflow_id': workflow_id,
            'optimizations': optimizations,
            'optimization_count': len(optimizations),
            'estimated_total_improvement': '40-60% efficiency gain'
        }

    def _generate_status_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate operations status report."""
        report_type = data.get('report_type', 'summary')
        include_metrics = data.get('include_metrics', True)

        # Gather statistics
        total_projects = len(self.projects)
        active_projects = sum(1 for p in self.projects.values() if p['status'] == 'active')
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks if t.get('status') == 'completed')

        report = {
            'report_type': report_type,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_projects': total_projects,
                'active_projects': active_projects,
                'completed_projects': sum(1 for p in self.projects.values() if p['status'] == 'completed'),
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': sum(1 for t in self.tasks if t.get('status') == 'in_progress'),
                'pending_tasks': sum(1 for t in self.tasks if t.get('status') == 'pending')
            }
        }

        if include_metrics:
            # Calculate completion rate
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            # Calculate average project progress
            avg_progress = sum(p.get('progress', 0) for p in self.projects.values()) / total_projects if total_projects > 0 else 0

            report['metrics'] = {
                'task_completion_rate': completion_rate,
                'average_project_progress': avg_progress,
                'resource_utilization': self._calculate_resource_utilization()
            }

        if report_type == 'detailed':
            report['projects'] = [
                {
                    'project_id': p['project_id'],
                    'name': p['name'],
                    'status': p['status'],
                    'progress': p.get('progress', 0)
                }
                for p in self.projects.values()
            ]

        return {
            'success': True,
            'report': report
        }

    def _calculate_resource_utilization(self) -> Dict[str, float]:
        """Calculate resource utilization."""
        utilization = {}

        for key, resource in self.resources.items():
            resource_type = resource['resource_type']
            if resource['allocated'] > 0:
                util = (resource['used'] / resource['allocated'] * 100)
                if resource_type not in utilization:
                    utilization[resource_type] = []
                utilization[resource_type].append(util)

        # Average utilization per resource type
        return {
            rtype: sum(utils) / len(utils) if utils else 0
            for rtype, utils in utilization.items()
        }

    def _save_projects(self) -> None:
        """Save projects to disk."""
        import json
        projects_path = self.agent_dir / "projects.json"
        try:
            with open(projects_path, 'w') as f:
                json.dump(self.projects, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving projects: {e}")

    def _save_tasks(self) -> None:
        """Save tasks to disk."""
        import json
        tasks_path = self.agent_dir / "tasks.json"
        try:
            with open(tasks_path, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tasks: {e}")

    def _save_resources(self) -> None:
        """Save resources to disk."""
        import json
        resources_path = self.agent_dir / "resources.json"
        try:
            with open(resources_path, 'w') as f:
                json.dump(self.resources, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving resources: {e}")


def main():
    """Main function for testing operations agent."""
    import argparse

    parser = argparse.ArgumentParser(description='Operations Agent')
    parser.add_argument('--vault-path', default='AI_Employee_Vault', help='Path to AI Employee Vault')
    parser.add_argument('--test', action='store_true', help='Run test scenarios')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize agent
    agent = OperationsAgent(args.vault_path)

    if args.test:
        print("Testing Operations Agent...")
        print("=" * 80)

        # Test 1: Create project
        print("\nTest 1: Create Project")
        task = AgentTask(
            task_id="test_1",
            task_type="create_project",
            description="Create new product launch project",
            priority=TaskPriority.HIGH,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'name': 'Product Launch Q2',
                'description': 'Launch new product line in Q2 2026',
                'deadline': '2026-06-30',
                'priority': 'high'
            }
        )
        result = agent.process_task(task)
        print(f"  Project ID: {result['project_id']}")
        print(f"  Created: {result['created']}")

        project_id = result['project_id']

        # Test 2: Assign task
        print("\nTest 2: Assign Task")
        task = AgentTask(
            task_id="test_2",
            task_type="assign_task",
            description="Assign marketing task",
            priority=TaskPriority.MEDIUM,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'task_description': 'Create marketing materials',
                'assignee': 'marketing_agent',
                'priority': 'high',
                'deadline': '2026-03-15'
            }
        )
        result = agent.process_task(task)
        print(f"  Task ID: {result['task_id']}")
        print(f"  Assigned: {result['assigned']}")

        # Test 3: Track progress
        print("\nTest 3: Track Progress")
        task = AgentTask(
            task_id="test_3",
            task_type="track_progress",
            description="Track project progress",
            priority=TaskPriority.MEDIUM,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'project_id': project_id,
                'include_tasks': True
            }
        )
        result = agent.process_task(task)
        print(f"  Progress: {result['progress']:.1f}%")
        print(f"  Total Tasks: {result['total_tasks']}")

        # Test 4: Identify bottlenecks
        print("\nTest 4: Identify Bottlenecks")
        task = AgentTask(
            task_id="test_4",
            task_type="identify_bottlenecks",
            description="Identify project bottlenecks",
            priority=TaskPriority.HIGH,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'project_id': project_id
            }
        )
        result = agent.process_task(task)
        print(f"  Bottlenecks Found: {result['bottleneck_count']}")
        for bottleneck in result['bottlenecks']:
            print(f"    - {bottleneck['type']}: {bottleneck['description']}")

        # Test 5: Generate status report
        print("\nTest 5: Generate Status Report")
        task = AgentTask(
            task_id="test_5",
            task_type="generate_status_report",
            description="Generate operations report",
            priority=TaskPriority.MEDIUM,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'report_type': 'summary',
                'include_metrics': True
            }
        )
        result = agent.process_task(task)
        print(f"  Total Projects: {result['report']['summary']['total_projects']}")
        print(f"  Active Projects: {result['report']['summary']['active_projects']}")
        print(f"  Total Tasks: {result['report']['summary']['total_tasks']}")

        # Test 6: Agent status
        print("\nTest 6: Agent Status")
        status = agent.get_status()
        print(f"  Agent ID: {status['agent_id']}")
        print(f"  Role: {status['role']}")
        print(f"  Capabilities: {len(status['capabilities'])}")

    else:
        print("Operations Agent initialized")
        print(f"Agent ID: {agent.agent_id}")
        print(f"Role: {agent.role.value}")
        print(f"Capabilities: {len(agent.capabilities)}")


if __name__ == '__main__':
    main()

"""
Automation MCP Server

Exposes advanced automation capabilities through MCP tools:
- Self-healing error recovery
- Intelligent task routing
- Auto-scaling resource management
- Proactive maintenance scheduling
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from automation.self_healing import SelfHealingSystem
from automation.task_router import TaskRouter
from automation.resource_manager import ResourceManager
from automation.proactive_maintenance import ProactiveMaintenanceSystem, MaintenanceTask
from automation.base import AutomationEvent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize automation systems
VAULT_PATH = "AI_Employee_Vault"
self_healing = None
task_router = None
resource_manager = None
proactive_maintenance = None


def initialize_systems():
    """Initialize all automation systems."""
    global self_healing, task_router, resource_manager, proactive_maintenance

    try:
        self_healing = SelfHealingSystem(VAULT_PATH)
        task_router = TaskRouter(VAULT_PATH)
        resource_manager = ResourceManager(VAULT_PATH)
        proactive_maintenance = ProactiveMaintenanceSystem(VAULT_PATH)

        logger.info("All automation systems initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing automation systems: {e}")
        return False


# MCP Tool Implementations

async def heal_error(error_type: str, severity: str = "high", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Trigger self-healing for a specific error type.

    Args:
        error_type: Type of error (connection_error, service_crash, memory_leak, disk_full, etc.)
        severity: Error severity (low, medium, high, critical)
        metadata: Optional additional error information

    Returns:
        Dictionary with healing result
    """
    try:
        if not self_healing:
            return {"success": False, "error": "Self-healing system not initialized"}

        # Create automation event
        import uuid
        from datetime import datetime

        event = AutomationEvent(
            event_id=str(uuid.uuid4()),
            event_type=error_type,
            timestamp=datetime.now().isoformat(),
            severity=severity,
            source='mcp_server',
            description=f"Manual healing request for {error_type}",
            metadata=metadata or {}
        )

        # Process event
        response = self_healing.process_event(event)

        if response:
            return {
                "success": response.success,
                "action_id": response.action_id,
                "description": response.description,
                "result": response.result,
                "error": response.error
            }
        else:
            return {
                "success": False,
                "message": "No matching healing rule found for this error type"
            }

    except Exception as e:
        logger.error(f"Error in heal_error: {e}")
        return {"success": False, "error": str(e)}


async def route_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route a task to the appropriate handler using intelligent routing.

    Args:
        task_data: Task information including:
            - task_id: Unique task identifier
            - description: Task description
            - estimated_hours: Estimated hours to complete
            - deadline: Optional deadline (ISO format)
            - priority: Optional priority override

    Returns:
        Dictionary with routing result
    """
    try:
        if not task_router:
            return {"success": False, "error": "Task router not initialized"}

        result = task_router.route_task(task_data)
        return result

    except Exception as e:
        logger.error(f"Error in route_task: {e}")
        return {"success": False, "error": str(e)}


async def complete_task(task_id: str, destination: str) -> Dict[str, Any]:
    """
    Mark a task as complete and free up routing capacity.

    Args:
        task_id: Task identifier
        destination: Destination where task was routed

    Returns:
        Dictionary with completion result
    """
    try:
        if not task_router:
            return {"success": False, "error": "Task router not initialized"}

        success = task_router.complete_task(task_id, destination)

        return {
            "success": success,
            "task_id": task_id,
            "destination": destination,
            "message": "Task completed successfully" if success else "Failed to complete task"
        }

    except Exception as e:
        logger.error(f"Error in complete_task: {e}")
        return {"success": False, "error": str(e)}


async def monitor_resources() -> Dict[str, Any]:
    """
    Monitor current system resource utilization.

    Returns:
        Dictionary with resource metrics (CPU, memory, disk)
    """
    try:
        if not resource_manager:
            return {"success": False, "error": "Resource manager not initialized"}

        metrics = resource_manager.monitor_resources()
        return {"success": True, "metrics": metrics}

    except Exception as e:
        logger.error(f"Error in monitor_resources: {e}")
        return {"success": False, "error": str(e)}


async def check_scaling_needed() -> Dict[str, Any]:
    """
    Check if resource scaling is needed based on current metrics.

    Returns:
        Dictionary with scaling recommendations
    """
    try:
        if not resource_manager:
            return {"success": False, "error": "Resource manager not initialized"}

        recommendations = resource_manager.check_scaling_needed()

        return {
            "success": True,
            "recommendations": recommendations,
            "count": len(recommendations)
        }

    except Exception as e:
        logger.error(f"Error in check_scaling_needed: {e}")
        return {"success": False, "error": str(e)}


async def auto_scale() -> Dict[str, Any]:
    """
    Automatically scale resources based on current metrics.

    Returns:
        Dictionary with scaling actions taken
    """
    try:
        if not resource_manager:
            return {"success": False, "error": "Resource manager not initialized"}

        actions = resource_manager.auto_scale()

        return {
            "success": True,
            "actions_taken": actions,
            "count": len(actions)
        }

    except Exception as e:
        logger.error(f"Error in auto_scale: {e}")
        return {"success": False, "error": str(e)}


async def scale_resource(resource_name: str, action: str) -> Dict[str, Any]:
    """
    Manually scale a specific resource up or down.

    Args:
        resource_name: Resource to scale (compute, memory, workers)
        action: Scaling action (scale_up or scale_down)

    Returns:
        Dictionary with scaling result
    """
    try:
        if not resource_manager:
            return {"success": False, "error": "Resource manager not initialized"}

        result = resource_manager.scale_resource(resource_name, action)
        return result

    except Exception as e:
        logger.error(f"Error in scale_resource: {e}")
        return {"success": False, "error": str(e)}


async def get_maintenance_tasks() -> Dict[str, Any]:
    """
    Get all scheduled maintenance tasks.

    Returns:
        Dictionary with maintenance tasks
    """
    try:
        if not proactive_maintenance:
            return {"success": False, "error": "Proactive maintenance not initialized"}

        tasks = [t.to_dict() for t in proactive_maintenance.maintenance_tasks]

        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks)
        }

    except Exception as e:
        logger.error(f"Error in get_maintenance_tasks: {e}")
        return {"success": False, "error": str(e)}


async def get_due_maintenance() -> Dict[str, Any]:
    """
    Get maintenance tasks that are currently due.

    Returns:
        Dictionary with due maintenance tasks
    """
    try:
        if not proactive_maintenance:
            return {"success": False, "error": "Proactive maintenance not initialized"}

        due_tasks = proactive_maintenance.get_due_tasks()
        tasks_data = [t.to_dict() for t in due_tasks]

        return {
            "success": True,
            "due_tasks": tasks_data,
            "count": len(due_tasks)
        }

    except Exception as e:
        logger.error(f"Error in get_due_maintenance: {e}")
        return {"success": False, "error": str(e)}


async def execute_maintenance(task_id: str) -> Dict[str, Any]:
    """
    Execute a specific maintenance task.

    Args:
        task_id: ID of maintenance task to execute

    Returns:
        Dictionary with execution result
    """
    try:
        if not proactive_maintenance:
            return {"success": False, "error": "Proactive maintenance not initialized"}

        # Find task
        task = None
        for t in proactive_maintenance.maintenance_tasks:
            if t.task_id == task_id:
                task = t
                break

        if not task:
            return {"success": False, "error": f"Task not found: {task_id}"}

        result = proactive_maintenance.execute_maintenance_task(task)
        return result

    except Exception as e:
        logger.error(f"Error in execute_maintenance: {e}")
        return {"success": False, "error": str(e)}


async def predict_maintenance_needs() -> Dict[str, Any]:
    """
    Predict upcoming maintenance needs based on health trends.

    Returns:
        Dictionary with maintenance predictions
    """
    try:
        if not proactive_maintenance:
            return {"success": False, "error": "Proactive maintenance not initialized"}

        predictions = proactive_maintenance.predict_maintenance_needs()

        return {
            "success": True,
            "predictions": predictions,
            "count": len(predictions)
        }

    except Exception as e:
        logger.error(f"Error in predict_maintenance_needs: {e}")
        return {"success": False, "error": str(e)}


async def record_health_metric(
    component: str,
    metric_name: str,
    value: float,
    threshold: Optional[float] = None
) -> Dict[str, Any]:
    """
    Record a health metric for predictive maintenance.

    Args:
        component: Component name (system, database, api, storage)
        metric_name: Name of the metric
        value: Metric value
        threshold: Optional threshold for alerting

    Returns:
        Dictionary with recording result and any alerts
    """
    try:
        if not proactive_maintenance:
            return {"success": False, "error": "Proactive maintenance not initialized"}

        event = proactive_maintenance.record_health_metric(
            component, metric_name, value, threshold
        )

        result = {
            "success": True,
            "component": component,
            "metric_name": metric_name,
            "value": value,
            "threshold": threshold
        }

        if event:
            result["alert"] = {
                "event_id": event.event_id,
                "severity": event.severity,
                "description": event.description
            }

        return result

    except Exception as e:
        logger.error(f"Error in record_health_metric: {e}")
        return {"success": False, "error": str(e)}


async def get_automation_status() -> Dict[str, Any]:
    """
    Get comprehensive status of all automation systems.

    Returns:
        Dictionary with status of all automation systems
    """
    try:
        status = {
            "success": True,
            "systems": {}
        }

        if self_healing:
            status["systems"]["self_healing"] = self_healing.get_system_status()

        if task_router:
            status["systems"]["task_routing"] = task_router.get_system_status()

        if resource_manager:
            status["systems"]["resource_management"] = resource_manager.get_system_status()

        if proactive_maintenance:
            status["systems"]["proactive_maintenance"] = proactive_maintenance.get_system_status()

        return status

    except Exception as e:
        logger.error(f"Error in get_automation_status: {e}")
        return {"success": False, "error": str(e)}


async def get_automation_analytics() -> Dict[str, Any]:
    """
    Get analytics across all automation systems.

    Returns:
        Dictionary with comprehensive automation analytics
    """
    try:
        analytics = {
            "success": True,
            "analytics": {}
        }

        if self_healing:
            analytics["analytics"]["self_healing"] = self_healing.get_statistics()

        if task_router:
            analytics["analytics"]["task_routing"] = task_router.get_routing_analytics()

        if resource_manager:
            analytics["analytics"]["resource_management"] = resource_manager.get_scaling_analytics()

        if proactive_maintenance:
            analytics["analytics"]["proactive_maintenance"] = proactive_maintenance.get_statistics()

        return analytics

    except Exception as e:
        logger.error(f"Error in get_automation_analytics: {e}")
        return {"success": False, "error": str(e)}


# MCP Server Implementation

async def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP tool calls."""

    # Map tool names to functions
    tools = {
        "heal_error": heal_error,
        "route_task": route_task,
        "complete_task": complete_task,
        "monitor_resources": monitor_resources,
        "check_scaling_needed": check_scaling_needed,
        "auto_scale": auto_scale,
        "scale_resource": scale_resource,
        "get_maintenance_tasks": get_maintenance_tasks,
        "get_due_maintenance": get_due_maintenance,
        "execute_maintenance": execute_maintenance,
        "predict_maintenance_needs": predict_maintenance_needs,
        "record_health_metric": record_health_metric,
        "get_automation_status": get_automation_status,
        "get_automation_analytics": get_automation_analytics
    }

    if tool_name not in tools:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    try:
        result = await tools[tool_name](**arguments)
        return result
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return {"success": False, "error": str(e)}


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Get MCP tool definitions."""
    return [
        {
            "name": "heal_error",
            "description": "Trigger self-healing for a specific error type",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "error_type": {
                        "type": "string",
                        "description": "Type of error (connection_error, service_crash, memory_leak, disk_full, etc.)"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "default": "high",
                        "description": "Error severity"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional additional error information"
                    }
                },
                "required": ["error_type"]
            }
        },
        {
            "name": "route_task",
            "description": "Route a task to the appropriate handler using intelligent routing",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_data": {
                        "type": "object",
                        "description": "Task information (task_id, description, estimated_hours, deadline, priority)",
                        "properties": {
                            "task_id": {"type": "string"},
                            "description": {"type": "string"},
                            "estimated_hours": {"type": "number"},
                            "deadline": {"type": "string"},
                            "priority": {"type": "string"}
                        },
                        "required": ["task_id", "description"]
                    }
                },
                "required": ["task_data"]
            }
        },
        {
            "name": "complete_task",
            "description": "Mark a task as complete and free up routing capacity",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task identifier"},
                    "destination": {"type": "string", "description": "Destination where task was routed"}
                },
                "required": ["task_id", "destination"]
            }
        },
        {
            "name": "monitor_resources",
            "description": "Monitor current system resource utilization (CPU, memory, disk)",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "check_scaling_needed",
            "description": "Check if resource scaling is needed based on current metrics",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "auto_scale",
            "description": "Automatically scale resources based on current metrics",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "scale_resource",
            "description": "Manually scale a specific resource up or down",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "resource_name": {
                        "type": "string",
                        "enum": ["compute", "memory", "workers"],
                        "description": "Resource to scale"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["scale_up", "scale_down"],
                        "description": "Scaling action"
                    }
                },
                "required": ["resource_name", "action"]
            }
        },
        {
            "name": "get_maintenance_tasks",
            "description": "Get all scheduled maintenance tasks",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_due_maintenance",
            "description": "Get maintenance tasks that are currently due",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "execute_maintenance",
            "description": "Execute a specific maintenance task",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "ID of maintenance task to execute"}
                },
                "required": ["task_id"]
            }
        },
        {
            "name": "predict_maintenance_needs",
            "description": "Predict upcoming maintenance needs based on health trends",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "record_health_metric",
            "description": "Record a health metric for predictive maintenance",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "component": {
                        "type": "string",
                        "enum": ["system", "database", "api", "storage"],
                        "description": "Component name"
                    },
                    "metric_name": {"type": "string", "description": "Name of the metric"},
                    "value": {"type": "number", "description": "Metric value"},
                    "threshold": {"type": "number", "description": "Optional threshold for alerting"}
                },
                "required": ["component", "metric_name", "value"]
            }
        },
        {
            "name": "get_automation_status",
            "description": "Get comprehensive status of all automation systems",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_automation_analytics",
            "description": "Get analytics across all automation systems",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    ]


async def main():
    """Main function to run the MCP server."""
    print("Initializing Automation MCP Server...")

    if not initialize_systems():
        print("Failed to initialize automation systems")
        return

    print("\nAutomation MCP Server Ready")
    print("=" * 80)
    print(f"\nAvailable Tools: {len(get_tool_definitions())}")
    print("\nAutomation Systems:")
    print("  ✓ Self-Healing System")
    print("  ✓ Intelligent Task Routing")
    print("  ✓ Auto-Scaling Resource Management")
    print("  ✓ Proactive Maintenance")

    # Get initial status
    status = await get_automation_status()
    if status["success"]:
        print("\nSystem Status:")
        for system_name, system_status in status["systems"].items():
            enabled = system_status.get("enabled", False)
            status_icon = "✓" if enabled else "✗"
            print(f"  {status_icon} {system_name}: {'Enabled' if enabled else 'Disabled'}")

    print("\n" + "=" * 80)
    print("Server is running. Press Ctrl+C to stop.")

    # Keep server running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Automation MCP Server...")


if __name__ == "__main__":
    asyncio.run(main())

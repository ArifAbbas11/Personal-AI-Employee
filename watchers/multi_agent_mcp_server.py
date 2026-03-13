"""
Multi-Agent MCP Server

Exposes multi-agent coordination and specialized agent capabilities through MCP tools.
Provides unified interface for Financial, Marketing, Operations, Research, and Customer Service agents.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from multi_agent.base import AgentCoordinator, AgentTask, TaskPriority
from multi_agent.financial_agent import FinancialAgent
from multi_agent.marketing_agent import MarketingAgent
from multi_agent.operations_agent import OperationsAgent
from multi_agent.research_agent import ResearchAgent
from multi_agent.customer_service_agent import CustomerServiceAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize multi-agent system
VAULT_PATH = "AI_Employee_Vault"
coordinator = None
financial_agent = None
marketing_agent = None
operations_agent = None
research_agent = None
customer_service_agent = None


def initialize_multi_agent_system():
    """Initialize all agents and coordinator."""
    global coordinator, financial_agent, marketing_agent, operations_agent, research_agent, customer_service_agent

    try:
        # Initialize coordinator
        coordinator = AgentCoordinator(VAULT_PATH)

        # Initialize all agents
        financial_agent = FinancialAgent(VAULT_PATH, coordinator)
        marketing_agent = MarketingAgent(VAULT_PATH, coordinator)
        operations_agent = OperationsAgent(VAULT_PATH, coordinator)
        research_agent = ResearchAgent(VAULT_PATH, coordinator)
        customer_service_agent = CustomerServiceAgent(VAULT_PATH, coordinator)

        logger.info("Multi-agent system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing multi-agent system: {e}")
        return False


# MCP Tool Implementations

# Coordination Tools

async def delegate_task(
    task_type: str,
    description: str,
    priority: str = "medium",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Delegate a task to the most appropriate agent.

    Args:
        task_type: Type of task (e.g., "categorize_expense", "optimize_content")
        description: Task description
        priority: Task priority (critical, high, medium, low)
        metadata: Optional task metadata

    Returns:
        Dictionary with delegation result
    """
    try:
        if not coordinator:
            return {"success": False, "error": "Coordinator not initialized"}

        # Map priority string to enum
        priority_map = {
            "critical": TaskPriority.CRITICAL,
            "high": TaskPriority.HIGH,
            "medium": TaskPriority.MEDIUM,
            "low": TaskPriority.LOW
        }
        task_priority = priority_map.get(priority.lower(), TaskPriority.MEDIUM)

        # Delegate task
        task = coordinator.delegate_task(
            task_type=task_type,
            description=description,
            priority=task_priority,
            metadata=metadata or {}
        )

        if task:
            return {
                "success": True,
                "task_id": task.task_id,
                "assigned_to": task.assigned_to,
                "status": task.status
            }
        else:
            return {
                "success": False,
                "error": "No capable agent found for this task type"
            }

    except Exception as e:
        logger.error(f"Error in delegate_task: {e}")
        return {"success": False, "error": str(e)}


async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a delegated task.

    Args:
        task_id: Task identifier

    Returns:
        Dictionary with task status
    """
    try:
        if not coordinator:
            return {"success": False, "error": "Coordinator not initialized"}

        status = coordinator.get_task_status(task_id)

        if status:
            return {"success": True, **status}
        else:
            return {"success": False, "error": f"Task not found: {task_id}"}

    except Exception as e:
        logger.error(f"Error in get_task_status: {e}")
        return {"success": False, "error": str(e)}


async def get_agent_status(agent_id: str) -> Dict[str, Any]:
    """
    Get the status of a specific agent.

    Args:
        agent_id: Agent identifier

    Returns:
        Dictionary with agent status
    """
    try:
        if not coordinator:
            return {"success": False, "error": "Coordinator not initialized"}

        status = coordinator.get_agent_status(agent_id)

        if status:
            return {"success": True, **status}
        else:
            return {"success": False, "error": f"Agent not found: {agent_id}"}

    except Exception as e:
        logger.error(f"Error in get_agent_status: {e}")
        return {"success": False, "error": str(e)}


async def get_system_status() -> Dict[str, Any]:
    """
    Get comprehensive multi-agent system status.

    Returns:
        Dictionary with system status
    """
    try:
        if not coordinator:
            return {"success": False, "error": "Coordinator not initialized"}

        status = coordinator.get_system_status()
        return {"success": True, **status}

    except Exception as e:
        logger.error(f"Error in get_system_status: {e}")
        return {"success": False, "error": str(e)}


# Financial Agent Tools

async def categorize_expense(
    description: str,
    amount: float,
    vendor: str = ""
) -> Dict[str, Any]:
    """
    Categorize an expense using ML.

    Args:
        description: Expense description
        amount: Expense amount
        vendor: Vendor name

    Returns:
        Dictionary with categorization result
    """
    try:
        if not financial_agent:
            return {"success": False, "error": "Financial agent not initialized"}

        result = financial_agent._categorize_expense({
            'description': description,
            'amount': amount,
            'vendor': vendor
        })
        return result

    except Exception as e:
        logger.error(f"Error in categorize_expense: {e}")
        return {"success": False, "error": str(e)}


async def generate_financial_report(
    report_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a financial report.

    Args:
        report_type: Type of report (profit_loss, balance_sheet, cash_flow, summary)
        start_date: Optional start date (ISO format)
        end_date: Optional end date (ISO format)

    Returns:
        Dictionary with report
    """
    try:
        if not financial_agent:
            return {"success": False, "error": "Financial agent not initialized"}

        result = financial_agent._generate_financial_report({
            'report_type': report_type,
            'start_date': start_date,
            'end_date': end_date
        })
        return result

    except Exception as e:
        logger.error(f"Error in generate_financial_report: {e}")
        return {"success": False, "error": str(e)}


# Marketing Agent Tools

async def optimize_content(
    content: str,
    platform: str,
    post_time: Optional[str] = None
) -> Dict[str, Any]:
    """
    Optimize social media content for engagement.

    Args:
        content: Content text
        platform: Platform (twitter, linkedin, facebook, instagram)
        post_time: Optional posting time (ISO format)

    Returns:
        Dictionary with optimization results
    """
    try:
        if not marketing_agent:
            return {"success": False, "error": "Marketing agent not initialized"}

        result = marketing_agent._optimize_content({
            'content': content,
            'platform': platform,
            'post_time': post_time
        })
        return result

    except Exception as e:
        logger.error(f"Error in optimize_content: {e}")
        return {"success": False, "error": str(e)}


async def generate_content_ideas(
    topic: str,
    platform: str = "twitter",
    count: int = 5
) -> Dict[str, Any]:
    """
    Generate content ideas for a topic.

    Args:
        topic: Content topic
        platform: Target platform
        count: Number of ideas to generate

    Returns:
        Dictionary with content ideas
    """
    try:
        if not marketing_agent:
            return {"success": False, "error": "Marketing agent not initialized"}

        result = marketing_agent._generate_content_ideas({
            'topic': topic,
            'platform': platform,
            'count': count
        })
        return result

    except Exception as e:
        logger.error(f"Error in generate_content_ideas: {e}")
        return {"success": False, "error": str(e)}


# Operations Agent Tools

async def create_project(
    name: str,
    description: str,
    deadline: Optional[str] = None,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Create a new project.

    Args:
        name: Project name
        description: Project description
        deadline: Optional deadline (ISO format)
        priority: Project priority

    Returns:
        Dictionary with project creation result
    """
    try:
        if not operations_agent:
            return {"success": False, "error": "Operations agent not initialized"}

        result = operations_agent._create_project({
            'name': name,
            'description': description,
            'deadline': deadline,
            'priority': priority
        })
        return result

    except Exception as e:
        logger.error(f"Error in create_project: {e}")
        return {"success": False, "error": str(e)}


async def identify_bottlenecks(
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Identify bottlenecks in projects.

    Args:
        project_id: Optional specific project ID

    Returns:
        Dictionary with bottleneck analysis
    """
    try:
        if not operations_agent:
            return {"success": False, "error": "Operations agent not initialized"}

        result = operations_agent._identify_bottlenecks({
            'project_id': project_id
        })
        return result

    except Exception as e:
        logger.error(f"Error in identify_bottlenecks: {e}")
        return {"success": False, "error": str(e)}


# Research Agent Tools

async def conduct_market_research(
    market: str,
    focus_areas: Optional[List[str]] = None,
    depth: str = "standard"
) -> Dict[str, Any]:
    """
    Conduct market research.

    Args:
        market: Market to research
        focus_areas: Optional focus areas
        depth: Research depth (quick, standard, deep)

    Returns:
        Dictionary with research findings
    """
    try:
        if not research_agent:
            return {"success": False, "error": "Research agent not initialized"}

        result = research_agent._conduct_market_research({
            'market': market,
            'focus_areas': focus_areas or ['size', 'growth', 'opportunities'],
            'depth': depth
        })
        return result

    except Exception as e:
        logger.error(f"Error in conduct_market_research: {e}")
        return {"success": False, "error": str(e)}


async def analyze_competitor(
    competitor_name: str,
    analysis_areas: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Analyze a competitor.

    Args:
        competitor_name: Competitor name
        analysis_areas: Optional analysis areas

    Returns:
        Dictionary with competitor analysis
    """
    try:
        if not research_agent:
            return {"success": False, "error": "Research agent not initialized"}

        result = research_agent._analyze_competitor({
            'competitor_name': competitor_name,
            'analysis_areas': analysis_areas or ['products', 'pricing', 'marketing']
        })
        return result

    except Exception as e:
        logger.error(f"Error in analyze_competitor: {e}")
        return {"success": False, "error": str(e)}


# Customer Service Agent Tools

async def classify_ticket(
    subject: str,
    body: str,
    sender: str = ""
) -> Dict[str, Any]:
    """
    Classify a support ticket.

    Args:
        subject: Ticket subject
        body: Ticket body
        sender: Sender email

    Returns:
        Dictionary with classification result
    """
    try:
        if not customer_service_agent:
            return {"success": False, "error": "Customer service agent not initialized"}

        result = customer_service_agent._classify_ticket({
            'subject': subject,
            'body': body,
            'sender': sender
        })
        return result

    except Exception as e:
        logger.error(f"Error in classify_ticket: {e}")
        return {"success": False, "error": str(e)}


async def create_support_ticket(
    customer_id: str,
    subject: str,
    description: str,
    priority: str = "medium",
    category: str = "general"
) -> Dict[str, Any]:
    """
    Create a support ticket.

    Args:
        customer_id: Customer identifier
        subject: Ticket subject
        description: Ticket description
        priority: Ticket priority
        category: Ticket category

    Returns:
        Dictionary with ticket creation result
    """
    try:
        if not customer_service_agent:
            return {"success": False, "error": "Customer service agent not initialized"}

        result = customer_service_agent._create_ticket({
            'customer_id': customer_id,
            'subject': subject,
            'description': description,
            'priority': priority,
            'category': category
        })
        return result

    except Exception as e:
        logger.error(f"Error in create_support_ticket: {e}")
        return {"success": False, "error": str(e)}


async def track_customer_satisfaction(
    period_days: int = 30,
    segment: str = "all"
) -> Dict[str, Any]:
    """
    Track customer satisfaction metrics.

    Args:
        period_days: Period in days
        segment: Customer segment

    Returns:
        Dictionary with satisfaction metrics
    """
    try:
        if not customer_service_agent:
            return {"success": False, "error": "Customer service agent not initialized"}

        result = customer_service_agent._track_satisfaction({
            'period_days': period_days,
            'segment': segment
        })
        return result

    except Exception as e:
        logger.error(f"Error in track_customer_satisfaction: {e}")
        return {"success": False, "error": str(e)}


# MCP Server Implementation

async def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP tool calls."""

    # Map tool names to functions
    tools = {
        # Coordination tools
        "delegate_task": delegate_task,
        "get_task_status": get_task_status,
        "get_agent_status": get_agent_status,
        "get_system_status": get_system_status,

        # Financial agent tools
        "categorize_expense": categorize_expense,
        "generate_financial_report": generate_financial_report,

        # Marketing agent tools
        "optimize_content": optimize_content,
        "generate_content_ideas": generate_content_ideas,

        # Operations agent tools
        "create_project": create_project,
        "identify_bottlenecks": identify_bottlenecks,

        # Research agent tools
        "conduct_market_research": conduct_market_research,
        "analyze_competitor": analyze_competitor,

        # Customer service agent tools
        "classify_ticket": classify_ticket,
        "create_support_ticket": create_support_ticket,
        "track_customer_satisfaction": track_customer_satisfaction
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
        # Coordination tools
        {
            "name": "delegate_task",
            "description": "Delegate a task to the most appropriate agent",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_type": {"type": "string", "description": "Type of task"},
                    "description": {"type": "string", "description": "Task description"},
                    "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"], "default": "medium"},
                    "metadata": {"type": "object", "description": "Optional task metadata"}
                },
                "required": ["task_type", "description"]
            }
        },
        {
            "name": "get_task_status",
            "description": "Get the status of a delegated task",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task identifier"}
                },
                "required": ["task_id"]
            }
        },
        {
            "name": "get_agent_status",
            "description": "Get the status of a specific agent",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Agent identifier"}
                },
                "required": ["agent_id"]
            }
        },
        {
            "name": "get_system_status",
            "description": "Get comprehensive multi-agent system status",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },

        # Financial agent tools
        {
            "name": "categorize_expense",
            "description": "Categorize an expense using ML",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "amount": {"type": "number"},
                    "vendor": {"type": "string", "default": ""}
                },
                "required": ["description", "amount"]
            }
        },
        {
            "name": "generate_financial_report",
            "description": "Generate a financial report",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "report_type": {"type": "string", "enum": ["profit_loss", "balance_sheet", "cash_flow", "summary"]},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"}
                },
                "required": ["report_type"]
            }
        },

        # Marketing agent tools
        {
            "name": "optimize_content",
            "description": "Optimize social media content for engagement",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "platform": {"type": "string", "enum": ["twitter", "linkedin", "facebook", "instagram"]},
                    "post_time": {"type": "string"}
                },
                "required": ["content", "platform"]
            }
        },
        {
            "name": "generate_content_ideas",
            "description": "Generate content ideas for a topic",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "platform": {"type": "string", "default": "twitter"},
                    "count": {"type": "integer", "default": 5}
                },
                "required": ["topic"]
            }
        },

        # Operations agent tools
        {
            "name": "create_project",
            "description": "Create a new project",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "deadline": {"type": "string"},
                    "priority": {"type": "string", "default": "medium"}
                },
                "required": ["name", "description"]
            }
        },
        {
            "name": "identify_bottlenecks",
            "description": "Identify bottlenecks in projects",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"}
                }
            }
        },

        # Research agent tools
        {
            "name": "conduct_market_research",
            "description": "Conduct market research",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "market": {"type": "string"},
                    "focus_areas": {"type": "array"},
                    "depth": {"type": "string", "enum": ["quick", "standard", "deep"], "default": "standard"}
                },
                "required": ["market"]
            }
        },
        {
            "name": "analyze_competitor",
            "description": "Analyze a competitor",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "competitor_name": {"type": "string"},
                    "analysis_areas": {"type": "array"}
                },
                "required": ["competitor_name"]
            }
        },

        # Customer service agent tools
        {
            "name": "classify_ticket",
            "description": "Classify a support ticket",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                    "sender": {"type": "string", "default": ""}
                },
                "required": ["subject", "body"]
            }
        },
        {
            "name": "create_support_ticket",
            "description": "Create a support ticket",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "subject": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "default": "medium"},
                    "category": {"type": "string", "default": "general"}
                },
                "required": ["customer_id", "subject", "description"]
            }
        },
        {
            "name": "track_customer_satisfaction",
            "description": "Track customer satisfaction metrics",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "period_days": {"type": "integer", "default": 30},
                    "segment": {"type": "string", "default": "all"}
                }
            }
        }
    ]


async def main():
    """Main function to run the MCP server."""
    print("Initializing Multi-Agent MCP Server...")

    if not initialize_multi_agent_system():
        print("Failed to initialize multi-agent system")
        return

    print("\nMulti-Agent MCP Server Ready")
    print("=" * 80)
    print(f"\nAvailable Tools: {len(get_tool_definitions())}")
    print("\nSpecialized Agents:")
    print("  ✓ Financial Agent (6 capabilities)")
    print("  ✓ Marketing Agent (6 capabilities)")
    print("  ✓ Operations Agent (7 capabilities)")
    print("  ✓ Research Agent (6 capabilities)")
    print("  ✓ Customer Service Agent (7 capabilities)")

    # Get system status
    status = await get_system_status()
    if status["success"]:
        print("\nSystem Status:")
        print(f"  Total Agents: {status['total_agents']}")
        print(f"  Active Agents: {status['active_agents']}")
        print(f"  Total Tasks: {status['total_tasks']}")

    print("\n" + "=" * 80)
    print("Server is running. Press Ctrl+C to stop.")

    # Keep server running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Multi-Agent MCP Server...")


if __name__ == "__main__":
    asyncio.run(main())

"""
Customer Service Agent

Specialized agent for customer support, ticket management, and satisfaction tracking.
Integrates with Email Classifier ML model for intelligent ticket routing.
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

# Import ML model for email classification
from ml_engine.email_classifier import EmailClassifier

logger = logging.getLogger(__name__)


class CustomerServiceAgent(BaseAgent):
    """Agent specialized in customer service and support."""

    def __init__(
        self,
        vault_path: str = "AI_Employee_Vault",
        coordinator: Optional[AgentCoordinator] = None
    ):
        """
        Initialize Customer Service Agent.

        Args:
            vault_path: Path to AI_Employee_Vault
            coordinator: Optional agent coordinator
        """
        super().__init__(
            agent_id="customer_service_agent",
            role=AgentRole.CUSTOMER_SERVICE,
            vault_path=vault_path,
            coordinator=coordinator
        )

        # Initialize ML model for email classification
        try:
            self.email_classifier = EmailClassifier(vault_path)
            logger.info("Email classifier loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load email classifier: {e}")
            self.email_classifier = None

        # Customer service data
        self.tickets: Dict[str, Dict[str, Any]] = {}
        self.customers: Dict[str, Dict[str, Any]] = {}
        self.responses: List[Dict[str, Any]] = []
        self.satisfaction_scores: List[Dict[str, Any]] = []

    def _initialize_capabilities(self) -> None:
        """Initialize customer service agent capabilities."""
        self.capabilities = [
            AgentCapability(
                capability_id="classify_ticket",
                name="Classify Support Ticket",
                description="Classify support tickets by urgency and category using ML",
                input_schema={
                    "type": "object",
                    "properties": {
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                        "sender": {"type": "string"}
                    },
                    "required": ["subject", "body"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "priority": {"type": "string"},
                        "confidence": {"type": "number"}
                    }
                },
                estimated_duration_seconds=5
            ),
            AgentCapability(
                capability_id="create_ticket",
                name="Create Support Ticket",
                description="Create and track a customer support ticket",
                input_schema={
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string"},
                        "subject": {"type": "string"},
                        "description": {"type": "string"},
                        "priority": {"type": "string"},
                        "category": {"type": "string"}
                    },
                    "required": ["customer_id", "subject", "description"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "string"},
                        "created": {"type": "boolean"}
                    }
                },
                estimated_duration_seconds=10
            ),
            AgentCapability(
                capability_id="respond_to_ticket",
                name="Respond to Ticket",
                description="Generate and send response to customer ticket",
                input_schema={
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "string"},
                        "response_type": {"type": "string"},
                        "custom_message": {"type": "string"}
                    },
                    "required": ["ticket_id"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "response_id": {"type": "string"},
                        "sent": {"type": "boolean"}
                    }
                },
                estimated_duration_seconds=15
            ),
            AgentCapability(
                capability_id="track_satisfaction",
                name="Track Customer Satisfaction",
                description="Track and analyze customer satisfaction metrics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "period_days": {"type": "integer"},
                        "segment": {"type": "string"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "metrics": {"type": "object"}
                    }
                },
                estimated_duration_seconds=20
            ),
            AgentCapability(
                capability_id="escalate_ticket",
                name="Escalate Ticket",
                description="Escalate ticket to human agent or specialist",
                input_schema={
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "string"},
                        "escalation_reason": {"type": "string"},
                        "escalate_to": {"type": "string"}
                    },
                    "required": ["ticket_id", "escalation_reason"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "escalated": {"type": "boolean"}
                    }
                },
                estimated_duration_seconds=10,
                requires_human_approval=True
            ),
            AgentCapability(
                capability_id="generate_csat_report",
                name="Generate CSAT Report",
                description="Generate customer satisfaction (CSAT) report",
                input_schema={
                    "type": "object",
                    "properties": {
                        "report_period": {"type": "string"},
                        "include_trends": {"type": "boolean"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "report": {"type": "object"}
                    }
                },
                estimated_duration_seconds=30
            ),
            AgentCapability(
                capability_id="identify_common_issues",
                name="Identify Common Issues",
                description="Identify and analyze common customer issues",
                input_schema={
                    "type": "object",
                    "properties": {
                        "period_days": {"type": "integer"},
                        "min_occurrences": {"type": "integer"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "issues": {"type": "array"}
                    }
                },
                estimated_duration_seconds=25
            )
        ]

    def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Process a customer service task.

        Args:
            task: Task to process

        Returns:
            Task result dictionary
        """
        task_type = task.task_type
        metadata = task.metadata

        if task_type == "classify_ticket":
            return self._classify_ticket(metadata)
        elif task_type == "create_ticket":
            return self._create_ticket(metadata)
        elif task_type == "respond_to_ticket":
            return self._respond_to_ticket(metadata)
        elif task_type == "track_satisfaction":
            return self._track_satisfaction(metadata)
        elif task_type == "escalate_ticket":
            return self._escalate_ticket(metadata)
        elif task_type == "generate_csat_report":
            return self._generate_csat_report(metadata)
        elif task_type == "identify_common_issues":
            return self._identify_common_issues(metadata)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def _classify_ticket(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify a support ticket using ML."""
        subject = data.get('subject', '')
        body = data.get('body', '')
        sender = data.get('sender', '')

        if self.email_classifier and self.email_classifier.is_trained:
            # Use ML model
            result = self.email_classifier.predict({
                'subject': subject,
                'body': body,
                'sender': sender
            })
            category = result['category']
            confidence = result['confidence']
        else:
            # Fallback to heuristic classification
            category = self._heuristic_classify(subject, body)
            confidence = 0.5

        # Map category to priority
        priority_map = {
            'urgent': 'high',
            'important': 'high',
            'normal': 'medium',
            'spam': 'low',
            'newsletter': 'low'
        }
        priority = priority_map.get(category, 'medium')

        return {
            'success': True,
            'category': category,
            'priority': priority,
            'confidence': confidence,
            'subject': subject
        }

    def _heuristic_classify(self, subject: str, body: str) -> str:
        """Fallback heuristic classification."""
        text = (subject + ' ' + body).lower()

        # Check for urgent keywords
        urgent_keywords = ['urgent', 'asap', 'critical', 'emergency', 'down', 'broken']
        if any(keyword in text for keyword in urgent_keywords):
            return 'urgent'

        # Check for important keywords
        important_keywords = ['important', 'issue', 'problem', 'error', 'bug']
        if any(keyword in text for keyword in important_keywords):
            return 'important'

        # Check for spam indicators
        spam_keywords = ['unsubscribe', 'click here', 'free', 'winner']
        if any(keyword in text for keyword in spam_keywords):
            return 'spam'

        return 'normal'

    def _create_ticket(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a support ticket."""
        import uuid

        ticket_id = str(uuid.uuid4())
        ticket = {
            'ticket_id': ticket_id,
            'customer_id': data.get('customer_id', ''),
            'subject': data.get('subject', ''),
            'description': data.get('description', ''),
            'priority': data.get('priority', 'medium'),
            'category': data.get('category', 'general'),
            'status': 'open',
            'assigned_to': None,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'responses': []
        }

        self.tickets[ticket_id] = ticket
        self._save_tickets()

        logger.info(f"Ticket created: {ticket_id} - {ticket['subject']}")

        return {
            'success': True,
            'ticket_id': ticket_id,
            'created': True,
            'ticket': ticket
        }

    def _respond_to_ticket(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Respond to a support ticket."""
        import uuid

        ticket_id = data.get('ticket_id', '')
        response_type = data.get('response_type', 'standard')
        custom_message = data.get('custom_message', '')

        if ticket_id not in self.tickets:
            return {
                'success': False,
                'message': f"Ticket not found: {ticket_id}"
            }

        ticket = self.tickets[ticket_id]

        # Generate response based on type
        if custom_message:
            response_text = custom_message
        else:
            response_text = self._generate_response(ticket, response_type)

        response_id = str(uuid.uuid4())
        response = {
            'response_id': response_id,
            'ticket_id': ticket_id,
            'response_text': response_text,
            'response_type': response_type,
            'sent_at': datetime.now().isoformat(),
            'sent_by': self.agent_id
        }

        # Add response to ticket
        ticket['responses'].append(response)
        ticket['updated_at'] = datetime.now().isoformat()

        # Store response
        self.responses.append(response)
        self._save_tickets()
        self._save_responses()

        logger.info(f"Response sent for ticket: {ticket_id}")

        return {
            'success': True,
            'response_id': response_id,
            'sent': True,
            'response': response
        }

    def _generate_response(self, ticket: Dict[str, Any], response_type: str) -> str:
        """Generate automated response."""
        if response_type == 'acknowledgment':
            return f"Thank you for contacting us. We have received your request regarding '{ticket['subject']}' and will respond within 24 hours."
        elif response_type == 'resolution':
            return f"We have resolved the issue described in your ticket. Please let us know if you need any further assistance."
        elif response_type == 'follow_up':
            return f"We wanted to follow up on your recent ticket regarding '{ticket['subject']}'. Is everything working as expected?"
        else:
            return f"Thank you for your message. We are reviewing your request and will get back to you soon."

    def _track_satisfaction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Track customer satisfaction metrics."""
        period_days = data.get('period_days', 30)
        segment = data.get('segment', 'all')

        cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()

        # Filter tickets by date
        recent_tickets = [
            t for t in self.tickets.values()
            if t.get('created_at', '') >= cutoff_date
        ]

        # Calculate metrics
        total_tickets = len(recent_tickets)
        resolved_tickets = sum(1 for t in recent_tickets if t.get('status') == 'resolved')
        avg_response_time = 4.5  # hours (simulated)
        avg_resolution_time = 24.0  # hours (simulated)

        # Simulated satisfaction scores
        csat_score = 4.2  # out of 5
        nps_score = 45

        # Calculate resolution rate
        resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0

        metrics = {
            'period_days': period_days,
            'total_tickets': total_tickets,
            'resolved_tickets': resolved_tickets,
            'resolution_rate': resolution_rate,
            'avg_response_time_hours': avg_response_time,
            'avg_resolution_time_hours': avg_resolution_time,
            'csat_score': csat_score,
            'nps_score': nps_score,
            'ticket_breakdown': {
                'open': sum(1 for t in recent_tickets if t.get('status') == 'open'),
                'in_progress': sum(1 for t in recent_tickets if t.get('status') == 'in_progress'),
                'resolved': resolved_tickets,
                'closed': sum(1 for t in recent_tickets if t.get('status') == 'closed')
            }
        }

        return {
            'success': True,
            'metrics': metrics
        }

    def _escalate_ticket(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate a ticket to human agent."""
        ticket_id = data.get('ticket_id', '')
        escalation_reason = data.get('escalation_reason', '')
        escalate_to = data.get('escalate_to', 'senior_support')

        if ticket_id not in self.tickets:
            return {
                'success': False,
                'message': f"Ticket not found: {ticket_id}"
            }

        ticket = self.tickets[ticket_id]
        ticket['status'] = 'escalated'
        ticket['escalated_to'] = escalate_to
        ticket['escalation_reason'] = escalation_reason
        ticket['escalated_at'] = datetime.now().isoformat()
        ticket['updated_at'] = datetime.now().isoformat()

        self._save_tickets()

        logger.info(f"Ticket escalated: {ticket_id} to {escalate_to}")

        return {
            'success': True,
            'escalated': True,
            'ticket_id': ticket_id,
            'escalated_to': escalate_to,
            'reason': escalation_reason
        }

    def _generate_csat_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate customer satisfaction report."""
        report_period = data.get('report_period', 'monthly')
        include_trends = data.get('include_trends', True)

        # Calculate period
        if report_period == 'weekly':
            period_days = 7
        elif report_period == 'monthly':
            period_days = 30
        else:
            period_days = 90

        # Get satisfaction metrics
        metrics_result = self._track_satisfaction({'period_days': period_days})
        metrics = metrics_result['metrics']

        report = {
            'report_period': report_period,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'csat_score': metrics['csat_score'],
                'nps_score': metrics['nps_score'],
                'resolution_rate': metrics['resolution_rate'],
                'total_tickets': metrics['total_tickets']
            },
            'performance_indicators': {
                'avg_response_time': f"{metrics['avg_response_time_hours']:.1f} hours",
                'avg_resolution_time': f"{metrics['avg_resolution_time_hours']:.1f} hours",
                'first_contact_resolution': '68%'  # Simulated
            },
            'ticket_volume': metrics['ticket_breakdown'],
            'top_categories': [
                {'category': 'Technical Issues', 'count': 45, 'percentage': 35},
                {'category': 'Billing Questions', 'count': 32, 'percentage': 25},
                {'category': 'Feature Requests', 'count': 28, 'percentage': 22},
                {'category': 'General Inquiries', 'count': 23, 'percentage': 18}
            ]
        }

        if include_trends:
            report['trends'] = {
                'csat_trend': 'improving',
                'ticket_volume_trend': 'stable',
                'resolution_time_trend': 'improving'
            }

        return {
            'success': True,
            'report': report
        }

    def _identify_common_issues(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify common customer issues."""
        period_days = data.get('period_days', 30)
        min_occurrences = data.get('min_occurrences', 3)

        cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()

        # Filter recent tickets
        recent_tickets = [
            t for t in self.tickets.values()
            if t.get('created_at', '') >= cutoff_date
        ]

        # Simulated common issues analysis
        issues = [
            {
                'issue_id': 'issue_1',
                'title': 'Login problems',
                'occurrences': 15,
                'severity': 'high',
                'avg_resolution_time': '2.5 hours',
                'status': 'recurring',
                'recommended_action': 'Improve authentication system'
            },
            {
                'issue_id': 'issue_2',
                'title': 'Slow performance',
                'occurrences': 12,
                'severity': 'medium',
                'avg_resolution_time': '4 hours',
                'status': 'recurring',
                'recommended_action': 'Optimize database queries'
            },
            {
                'issue_id': 'issue_3',
                'title': 'Missing features',
                'occurrences': 8,
                'severity': 'low',
                'avg_resolution_time': '24 hours',
                'status': 'ongoing',
                'recommended_action': 'Add to product roadmap'
            }
        ]

        # Filter by min occurrences
        filtered_issues = [i for i in issues if i['occurrences'] >= min_occurrences]

        return {
            'success': True,
            'period_days': period_days,
            'issues': filtered_issues,
            'issue_count': len(filtered_issues),
            'total_occurrences': sum(i['occurrences'] for i in filtered_issues)
        }

    def _save_tickets(self) -> None:
        """Save tickets to disk."""
        import json
        tickets_path = self.agent_dir / "tickets.json"
        try:
            with open(tickets_path, 'w') as f:
                json.dump(self.tickets, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tickets: {e}")

    def _save_responses(self) -> None:
        """Save responses to disk."""
        import json
        responses_path = self.agent_dir / "responses.json"
        try:
            with open(responses_path, 'w') as f:
                json.dump(self.responses, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving responses: {e}")


def main():
    """Main function for testing customer service agent."""
    import argparse

    parser = argparse.ArgumentParser(description='Customer Service Agent')
    parser.add_argument('--vault-path', default='AI_Employee_Vault', help='Path to AI Employee Vault')
    parser.add_argument('--test', action='store_true', help='Run test scenarios')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize agent
    agent = CustomerServiceAgent(args.vault_path)

    if args.test:
        print("Testing Customer Service Agent...")
        print("=" * 80)

        # Test 1: Classify ticket
        print("\nTest 1: Classify Ticket")
        task = AgentTask(
            task_id="test_1",
            task_type="classify_ticket",
            description="Classify support email",
            priority=TaskPriority.HIGH,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'subject': 'URGENT: System is down',
                'body': 'Our production system is not responding. Please help immediately!',
                'sender': 'customer@company.com'
            }
        )
        result = agent.process_task(task)
        print(f"  Category: {result['category']}")
        print(f"  Priority: {result['priority']}")
        print(f"  Confidence: {result['confidence']:.2f}")

        # Test 2: Create ticket
        print("\nTest 2: Create Ticket")
        task = AgentTask(
            task_id="test_2",
            task_type="create_ticket",
            description="Create support ticket",
            priority=TaskPriority.HIGH,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'customer_id': 'cust_123',
                'subject': 'Login issue',
                'description': 'Cannot log in to my account',
                'priority': 'high',
                'category': 'technical'
            }
        )
        result = agent.process_task(task)
        print(f"  Ticket ID: {result['ticket_id']}")
        print(f"  Created: {result['created']}")

        ticket_id = result['ticket_id']

        # Test 3: Respond to ticket
        print("\nTest 3: Respond to Ticket")
        task = AgentTask(
            task_id="test_3",
            task_type="respond_to_ticket",
            description="Send acknowledgment",
            priority=TaskPriority.MEDIUM,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'ticket_id': ticket_id,
                'response_type': 'acknowledgment'
            }
        )
        result = agent.process_task(task)
        print(f"  Response ID: {result['response_id']}")
        print(f"  Sent: {result['sent']}")

        # Test 4: Track satisfaction
        print("\nTest 4: Track Satisfaction")
        task = AgentTask(
            task_id="test_4",
            task_type="track_satisfaction",
            description="Track CSAT metrics",
            priority=TaskPriority.MEDIUM,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'period_days': 30,
                'segment': 'all'
            }
        )
        result = agent.process_task(task)
        print(f"  CSAT Score: {result['metrics']['csat_score']:.1f}/5")
        print(f"  NPS Score: {result['metrics']['nps_score']}")
        print(f"  Resolution Rate: {result['metrics']['resolution_rate']:.1f}%")

        # Test 5: Identify common issues
        print("\nTest 5: Identify Common Issues")
        task = AgentTask(
            task_id="test_5",
            task_type="identify_common_issues",
            description="Find recurring issues",
            priority=TaskPriority.MEDIUM,
            assigned_to=agent.agent_id,
            assigned_by=None,
            created_at=datetime.now().isoformat(),
            metadata={
                'period_days': 30,
                'min_occurrences': 3
            }
        )
        result = agent.process_task(task)
        print(f"  Issues Found: {result['issue_count']}")
        for issue in result['issues']:
            print(f"    - {issue['title']}: {issue['occurrences']} occurrences ({issue['severity']})")

        # Test 6: Agent status
        print("\nTest 6: Agent Status")
        status = agent.get_status()
        print(f"  Agent ID: {status['agent_id']}")
        print(f"  Role: {status['role']}")
        print(f"  Capabilities: {len(status['capabilities'])}")

    else:
        print("Customer Service Agent initialized")
        print(f"Agent ID: {agent.agent_id}")
        print(f"Role: {agent.role.value}")
        print(f"Capabilities: {len(agent.capabilities)}")


if __name__ == '__main__':
    main()

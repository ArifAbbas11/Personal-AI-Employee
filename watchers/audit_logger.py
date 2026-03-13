#!/usr/bin/env python3
"""
Comprehensive Audit Logging System
Tracks all operations, user actions, and system events for compliance and security.
"""

import json
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    AUTHENTICATE = "authenticate"
    AUTHORIZE = "authorize"
    APPROVE = "approve"
    REJECT = "reject"
    SEND = "send"
    RECEIVE = "receive"
    SCHEDULE = "schedule"
    CANCEL = "cancel"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class AuditCategory(Enum):
    """Categories of audit events."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_OPERATION = "system_operation"
    USER_ACTION = "user_action"
    API_CALL = "api_call"
    FILE_OPERATION = "file_operation"
    EMAIL_OPERATION = "email_operation"
    SOCIAL_MEDIA = "social_media"
    FINANCIAL = "financial"
    APPROVAL = "approval"
    ERROR_EVENT = "error_event"


@dataclass
class AuditEvent:
    """Represents an audit event."""
    timestamp: str
    event_id: str
    event_type: AuditEventType
    category: AuditCategory
    actor: str  # Who performed the action
    action: str  # What action was performed
    resource: str  # What resource was affected
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    result: str = "success"  # success, failure, partial
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    parent_event_id: Optional[str] = None  # For related events


class AuditLogger:
    """Comprehensive audit logging system."""

    def __init__(self, vault_path: str):
        """Initialize audit logger."""
        self.vault = Path(vault_path)
        self.audit_log_path = self.vault / 'Logs' / 'audit'
        self.audit_log_path.mkdir(exist_ok=True)

        # Create separate log files by category
        self.log_files = {
            category: self.audit_log_path / f"{category.value}.log"
            for category in AuditCategory
        }

        # Master audit log (all events)
        self.master_log = self.audit_log_path / 'master_audit.log'

    def log_event(self, event: AuditEvent) -> str:
        """Log an audit event."""
        # Generate event ID if not provided
        if not event.event_id:
            event.event_id = self._generate_event_id(event)

        # Convert to dict
        event_dict = asdict(event)
        event_dict['event_type'] = event.event_type.value
        event_dict['category'] = event.category.value

        # Write to category-specific log
        category_log = self.log_files[event.category]
        with open(category_log, 'a') as f:
            f.write(json.dumps(event_dict) + '\n')

        # Write to master log
        with open(self.master_log, 'a') as f:
            f.write(json.dumps(event_dict) + '\n')

        return event.event_id

    def _generate_event_id(self, event: AuditEvent) -> str:
        """Generate unique event ID."""
        data = f"{event.timestamp}{event.actor}{event.action}{event.resource}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    # Convenience methods for common operations

    def log_authentication(self, actor: str, result: str, details: Optional[Dict] = None):
        """Log authentication event."""
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_id="",
            event_type=AuditEventType.AUTHENTICATE,
            category=AuditCategory.AUTHENTICATION,
            actor=actor,
            action="authenticate",
            resource="system",
            result=result,
            details=details
        )
        return self.log_event(event)

    def log_file_operation(self, actor: str, operation: str, file_path: str,
                          result: str = "success", details: Optional[Dict] = None):
        """Log file operation."""
        event_type_map = {
            'create': AuditEventType.CREATE,
            'read': AuditEventType.READ,
            'update': AuditEventType.UPDATE,
            'delete': AuditEventType.DELETE
        }

        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_id="",
            event_type=event_type_map.get(operation, AuditEventType.EXECUTE),
            category=AuditCategory.FILE_OPERATION,
            actor=actor,
            action=f"file_{operation}",
            resource=file_path,
            result=result,
            details=details
        )
        return self.log_event(event)

    def log_api_call(self, actor: str, api: str, endpoint: str, method: str,
                    result: str = "success", details: Optional[Dict] = None):
        """Log API call."""
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_id="",
            event_type=AuditEventType.EXECUTE,
            category=AuditCategory.API_CALL,
            actor=actor,
            action=f"{method} {endpoint}",
            resource=api,
            result=result,
            details=details
        )
        return self.log_event(event)

    def log_email_operation(self, actor: str, operation: str, recipient: str,
                           subject: str, result: str = "success", details: Optional[Dict] = None):
        """Log email operation."""
        event_type_map = {
            'send': AuditEventType.SEND,
            'receive': AuditEventType.RECEIVE
        }

        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_id="",
            event_type=event_type_map.get(operation, AuditEventType.EXECUTE),
            category=AuditCategory.EMAIL_OPERATION,
            actor=actor,
            action=f"email_{operation}",
            resource=recipient,
            details={'subject': subject, **(details or {})}
        )
        return self.log_event(event)

    def log_social_media_post(self, actor: str, platform: str, post_id: str,
                             result: str = "success", details: Optional[Dict] = None):
        """Log social media post."""
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_id="",
            event_type=AuditEventType.CREATE,
            category=AuditCategory.SOCIAL_MEDIA,
            actor=actor,
            action=f"post_to_{platform}",
            resource=platform,
            resource_id=post_id,
            result=result,
            details=details
        )
        return self.log_event(event)

    def log_financial_operation(self, actor: str, operation: str, amount: float,
                                currency: str, result: str = "success", details: Optional[Dict] = None):
        """Log financial operation."""
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_id="",
            event_type=AuditEventType.EXECUTE,
            category=AuditCategory.FINANCIAL,
            actor=actor,
            action=operation,
            resource="financial_system",
            result=result,
            details={'amount': amount, 'currency': currency, **(details or {})}
        )
        return self.log_event(event)

    def log_approval(self, actor: str, action: str, resource: str, decision: str,
                    details: Optional[Dict] = None):
        """Log approval decision."""
        event_type = AuditEventType.APPROVE if decision == "approved" else AuditEventType.REJECT

        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_id="",
            event_type=event_type,
            category=AuditCategory.APPROVAL,
            actor=actor,
            action=action,
            resource=resource,
            result="success",
            details={'decision': decision, **(details or {})}
        )
        return self.log_event(event)

    def log_error(self, actor: str, error_type: str, message: str, details: Optional[Dict] = None):
        """Log error event."""
        event = AuditEvent(
            timestamp=datetime.now().isoformat(),
            event_id="",
            event_type=AuditEventType.ERROR,
            category=AuditCategory.ERROR_EVENT,
            actor=actor,
            action=error_type,
            resource="system",
            result="failure",
            details={'message': message, **(details or {})}
        )
        return self.log_event(event)

    # Query methods

    def query_events(self, category: Optional[AuditCategory] = None,
                    actor: Optional[str] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None,
                    limit: int = 100) -> List[Dict[str, Any]]:
        """Query audit events."""
        events = []

        # Determine which log file to read
        if category:
            log_file = self.log_files[category]
        else:
            log_file = self.master_log

        if not log_file.exists():
            return events

        # Read and filter events
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())

                    # Apply filters
                    if actor and event.get('actor') != actor:
                        continue

                    if start_time or end_time:
                        event_time = datetime.fromisoformat(event['timestamp'])
                        if start_time and event_time < start_time:
                            continue
                        if end_time and event_time > end_time:
                            continue

                    events.append(event)

                    if len(events) >= limit:
                        break

                except json.JSONDecodeError:
                    continue

        return events

    def generate_audit_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate audit report for a time period."""
        events = self.query_events(start_time=start_date, end_time=end_date, limit=10000)

        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary': {
                'total_events': len(events),
                'by_category': {},
                'by_actor': {},
                'by_result': {'success': 0, 'failure': 0, 'partial': 0}
            },
            'top_actors': [],
            'top_actions': [],
            'errors': []
        }

        # Analyze events
        category_counts = {}
        actor_counts = {}
        action_counts = {}

        for event in events:
            # Count by category
            category = event.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1

            # Count by actor
            actor = event.get('actor', 'unknown')
            actor_counts[actor] = actor_counts.get(actor, 0) + 1

            # Count by action
            action = event.get('action', 'unknown')
            action_counts[action] = action_counts.get(action, 0) + 1

            # Count by result
            result = event.get('result', 'success')
            report['summary']['by_result'][result] = report['summary']['by_result'].get(result, 0) + 1

            # Collect errors
            if event.get('event_type') == 'error':
                report['errors'].append({
                    'timestamp': event['timestamp'],
                    'actor': event['actor'],
                    'action': event['action'],
                    'details': event.get('details', {})
                })

        report['summary']['by_category'] = category_counts
        report['summary']['by_actor'] = actor_counts

        # Top actors
        report['top_actors'] = sorted(actor_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # Top actions
        report['top_actions'] = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return report

    def export_audit_log(self, output_path: str, category: Optional[AuditCategory] = None,
                        start_time: Optional[datetime] = None, end_time: Optional[datetime] = None):
        """Export audit log to file."""
        events = self.query_events(category, start_time=start_time, end_time=end_time, limit=100000)

        output = Path(output_path)
        with open(output, 'w') as f:
            json.dump(events, f, indent=2)

        logger.info(f"Exported {len(events)} events to {output_path}")
        return len(events)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Comprehensive Audit Logging System')
    parser.add_argument(
        '--vault',
        default='/mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--query',
        action='store_true',
        help='Query audit events'
    )
    parser.add_argument(
        '--category',
        choices=[c.value for c in AuditCategory],
        help='Filter by category'
    )
    parser.add_argument(
        '--actor',
        help='Filter by actor'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to query'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate audit report'
    )
    parser.add_argument(
        '--export',
        help='Export audit log to file'
    )

    args = parser.parse_args()

    audit_logger = AuditLogger(args.vault)

    if args.query:
        # Query events
        end_time = datetime.now()
        start_time = end_time - timedelta(days=args.days)

        category = AuditCategory(args.category) if args.category else None

        events = audit_logger.query_events(
            category=category,
            actor=args.actor,
            start_time=start_time,
            end_time=end_time,
            limit=50
        )

        print(f"\n📋 Found {len(events)} audit event(s)\n")
        for event in events:
            print(f"[{event['timestamp']}] {event['actor']}: {event['action']}")
            print(f"  Resource: {event['resource']}")
            print(f"  Result: {event['result']}")
            print()

    elif args.report:
        # Generate report
        end_time = datetime.now()
        start_time = end_time - timedelta(days=args.days)

        report = audit_logger.generate_audit_report(start_time, end_time)

        print(f"\n📊 Audit Report ({args.days} days)\n")
        print(f"Period: {report['period']['start']} to {report['period']['end']}")
        print(f"\nTotal Events: {report['summary']['total_events']}")
        print(f"\nBy Result:")
        for result, count in report['summary']['by_result'].items():
            print(f"  {result}: {count}")
        print(f"\nTop Actors:")
        for actor, count in report['top_actors'][:5]:
            print(f"  {actor}: {count} events")
        print(f"\nTop Actions:")
        for action, count in report['top_actions'][:5]:
            print(f"  {action}: {count} times")
        print(f"\nErrors: {len(report['errors'])}")
        print()

    elif args.export:
        # Export audit log
        end_time = datetime.now()
        start_time = end_time - timedelta(days=args.days)

        category = AuditCategory(args.category) if args.category else None

        count = audit_logger.export_audit_log(
            args.export,
            category=category,
            start_time=start_time,
            end_time=end_time
        )

        print(f"\n✅ Exported {count} events to {args.export}\n")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()

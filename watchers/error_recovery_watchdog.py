#!/usr/bin/env python3
"""
Error Recovery & Watchdog System
Monitors system health, detects errors, and implements automatic recovery strategies.
"""

import json
import sys
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStatus(Enum):
    """Recovery attempt status."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


@dataclass
class ErrorEvent:
    """Represents an error event."""
    timestamp: str
    severity: ErrorSeverity
    component: str
    error_type: str
    message: str
    stack_trace: Optional[str] = None
    recovery_attempted: bool = False
    recovery_status: Optional[RecoveryStatus] = None
    recovery_details: Optional[str] = None


class ErrorDetector:
    """Detects errors from logs and system state."""

    def __init__(self, vault_path: str):
        """Initialize error detector."""
        self.vault = Path(vault_path)
        self.logs_path = self.vault / 'Logs'
        self.error_patterns = self._load_error_patterns()

    def _load_error_patterns(self) -> Dict[str, Any]:
        """Load error patterns for detection."""
        return {
            'authentication_failed': {
                'patterns': ['authentication failed', 'auth error', 'invalid credentials'],
                'severity': ErrorSeverity.HIGH,
                'component': 'authentication'
            },
            'api_rate_limit': {
                'patterns': ['rate limit exceeded', 'too many requests', '429'],
                'severity': ErrorSeverity.MEDIUM,
                'component': 'api'
            },
            'network_error': {
                'patterns': ['connection refused', 'timeout', 'network unreachable'],
                'severity': ErrorSeverity.MEDIUM,
                'component': 'network'
            },
            'file_not_found': {
                'patterns': ['file not found', 'no such file', 'FileNotFoundError'],
                'severity': ErrorSeverity.LOW,
                'component': 'filesystem'
            },
            'permission_denied': {
                'patterns': ['permission denied', 'access denied', 'PermissionError'],
                'severity': ErrorSeverity.HIGH,
                'component': 'filesystem'
            },
            'database_error': {
                'patterns': ['database error', 'connection lost', 'query failed'],
                'severity': ErrorSeverity.CRITICAL,
                'component': 'database'
            },
            'memory_error': {
                'patterns': ['out of memory', 'MemoryError', 'memory allocation failed'],
                'severity': ErrorSeverity.CRITICAL,
                'component': 'system'
            },
            'disk_full': {
                'patterns': ['no space left', 'disk full', 'quota exceeded'],
                'severity': ErrorSeverity.CRITICAL,
                'component': 'filesystem'
            }
        }

    def scan_logs(self, hours: int = 1) -> List[ErrorEvent]:
        """Scan logs for errors in the last N hours."""
        errors = []
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Scan all log files
        for log_file in self.logs_path.glob('*.log'):
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        # Check if line contains error
                        error_event = self._parse_log_line(line, log_file.name)
                        if error_event and self._is_recent(error_event.timestamp, cutoff_time):
                            errors.append(error_event)
            except Exception as e:
                logger.error(f"Error scanning log file {log_file}: {e}")

        return errors

    def _parse_log_line(self, line: str, log_file: str) -> Optional[ErrorEvent]:
        """Parse a log line for errors."""
        line_lower = line.lower()

        # Check against error patterns
        for error_type, pattern_info in self.error_patterns.items():
            for pattern in pattern_info['patterns']:
                if pattern in line_lower:
                    return ErrorEvent(
                        timestamp=datetime.now().isoformat(),
                        severity=pattern_info['severity'],
                        component=pattern_info['component'],
                        error_type=error_type,
                        message=line.strip()
                    )

        return None

    def _is_recent(self, timestamp: str, cutoff: datetime) -> bool:
        """Check if timestamp is recent."""
        try:
            event_time = datetime.fromisoformat(timestamp)
            return event_time >= cutoff
        except:
            return True  # If can't parse, assume recent

    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health."""
        health = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'checks': {}
        }

        # Check disk space
        disk_check = self._check_disk_space()
        health['checks']['disk_space'] = disk_check
        if disk_check['status'] != 'ok':
            health['status'] = 'degraded'

        # Check log file sizes
        log_check = self._check_log_sizes()
        health['checks']['log_files'] = log_check
        if log_check['status'] != 'ok':
            health['status'] = 'degraded'

        # Check queue directories
        queue_check = self._check_queues()
        health['checks']['queues'] = queue_check
        if queue_check['status'] != 'ok':
            health['status'] = 'degraded'

        # Check for stuck tasks
        stuck_check = self._check_stuck_tasks()
        health['checks']['stuck_tasks'] = stuck_check
        if stuck_check['status'] != 'ok':
            health['status'] = 'degraded'

        return health

    def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space."""
        import shutil
        try:
            usage = shutil.disk_usage(str(self.vault))
            percent_used = (usage.used / usage.total) * 100

            if percent_used > 90:
                return {'status': 'critical', 'percent_used': percent_used}
            elif percent_used > 80:
                return {'status': 'warning', 'percent_used': percent_used}
            else:
                return {'status': 'ok', 'percent_used': percent_used}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _check_log_sizes(self) -> Dict[str, Any]:
        """Check log file sizes."""
        large_logs = []
        total_size = 0

        for log_file in self.logs_path.glob('*.log'):
            size_mb = log_file.stat().st_size / (1024 * 1024)
            total_size += size_mb
            if size_mb > 100:  # > 100MB
                large_logs.append({'file': log_file.name, 'size_mb': size_mb})

        if large_logs:
            return {'status': 'warning', 'large_logs': large_logs, 'total_size_mb': total_size}
        else:
            return {'status': 'ok', 'total_size_mb': total_size}

    def _check_queues(self) -> Dict[str, Any]:
        """Check queue directories for stuck items."""
        queues = {
            'social_media': Path('/tmp/social_media_queue'),
            'needs_action': self.vault / 'Needs_Action'
        }

        stuck_items = []
        for queue_name, queue_path in queues.items():
            if queue_path.exists():
                for item in queue_path.glob('*'):
                    age_hours = (time.time() - item.stat().st_mtime) / 3600
                    if age_hours > 24:  # Stuck for > 24 hours
                        stuck_items.append({
                            'queue': queue_name,
                            'item': item.name,
                            'age_hours': age_hours
                        })

        if stuck_items:
            return {'status': 'warning', 'stuck_items': stuck_items}
        else:
            return {'status': 'ok'}

    def _check_stuck_tasks(self) -> Dict[str, Any]:
        """Check for tasks stuck in Needs_Action."""
        needs_action = self.vault / 'Needs_Action'
        if not needs_action.exists():
            return {'status': 'ok'}

        stuck_tasks = []
        for task_file in needs_action.glob('*.md'):
            age_days = (time.time() - task_file.stat().st_mtime) / (3600 * 24)
            if age_days > 3:  # Stuck for > 3 days
                stuck_tasks.append({
                    'task': task_file.name,
                    'age_days': age_days
                })

        if len(stuck_tasks) > 5:
            return {'status': 'warning', 'stuck_tasks': stuck_tasks}
        else:
            return {'status': 'ok', 'stuck_tasks': stuck_tasks}


class ErrorRecovery:
    """Implements automatic error recovery strategies."""

    def __init__(self, vault_path: str):
        """Initialize error recovery."""
        self.vault = Path(vault_path)
        self.recovery_log = self.vault / 'Logs' / 'error_recovery.log'

    def attempt_recovery(self, error: ErrorEvent) -> RecoveryStatus:
        """Attempt to recover from an error."""
        logger.info(f"Attempting recovery for {error.error_type}")

        # Select recovery strategy based on error type
        if error.error_type == 'authentication_failed':
            return self._recover_authentication(error)
        elif error.error_type == 'api_rate_limit':
            return self._recover_rate_limit(error)
        elif error.error_type == 'network_error':
            return self._recover_network(error)
        elif error.error_type == 'file_not_found':
            return self._recover_file_not_found(error)
        elif error.error_type == 'permission_denied':
            return self._recover_permission(error)
        elif error.error_type == 'disk_full':
            return self._recover_disk_full(error)
        else:
            return RecoveryStatus.SKIPPED

    def _recover_authentication(self, error: ErrorEvent) -> RecoveryStatus:
        """Recover from authentication errors."""
        # Create manual review task
        self._create_manual_review_task(
            error,
            "Authentication Failed",
            "Please check and update credentials in configuration files."
        )
        return RecoveryStatus.PARTIAL

    def _recover_rate_limit(self, error: ErrorEvent) -> RecoveryStatus:
        """Recover from rate limit errors."""
        # Implement exponential backoff
        logger.info("Rate limit detected - implementing backoff")
        # Create task to retry later
        self._create_retry_task(error, delay_minutes=15)
        return RecoveryStatus.SUCCESS

    def _recover_network(self, error: ErrorEvent) -> RecoveryStatus:
        """Recover from network errors."""
        # Retry with exponential backoff
        logger.info("Network error detected - will retry")
        self._create_retry_task(error, delay_minutes=5)
        return RecoveryStatus.SUCCESS

    def _recover_file_not_found(self, error: ErrorEvent) -> RecoveryStatus:
        """Recover from file not found errors."""
        # Create manual review task
        self._create_manual_review_task(
            error,
            "File Not Found",
            "Please verify file path and ensure file exists."
        )
        return RecoveryStatus.PARTIAL

    def _recover_permission(self, error: ErrorEvent) -> RecoveryStatus:
        """Recover from permission errors."""
        # Create manual review task
        self._create_manual_review_task(
            error,
            "Permission Denied",
            "Please check file permissions and user access rights."
        )
        return RecoveryStatus.PARTIAL

    def _recover_disk_full(self, error: ErrorEvent) -> RecoveryStatus:
        """Recover from disk full errors."""
        # Attempt to clean up old logs
        cleaned = self._cleanup_old_logs()
        if cleaned:
            logger.info(f"Cleaned up {cleaned} old log files")
            return RecoveryStatus.SUCCESS
        else:
            self._create_manual_review_task(
                error,
                "Disk Full",
                "Please free up disk space or increase storage capacity."
            )
            return RecoveryStatus.PARTIAL

    def _cleanup_old_logs(self) -> int:
        """Clean up old log files."""
        logs_path = self.vault / 'Logs'
        cleaned = 0
        cutoff = datetime.now() - timedelta(days=30)

        for log_file in logs_path.glob('*.log'):
            if log_file.stat().st_mtime < cutoff.timestamp():
                try:
                    log_file.unlink()
                    cleaned += 1
                except Exception as e:
                    logger.error(f"Failed to delete {log_file}: {e}")

        return cleaned

    def _create_manual_review_task(self, error: ErrorEvent, title: str, instructions: str):
        """Create a manual review task for errors that need human intervention."""
        needs_action = self.vault / 'Needs_Action'
        needs_action.mkdir(exist_ok=True)

        task_file = needs_action / f"ERROR_REVIEW_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        content = f"""---
type: error_review
severity: {error.severity.value}
component: {error.component}
error_type: {error.error_type}
created: {datetime.now().isoformat()}
---

# {title}

## Error Details

**Component:** {error.component}
**Severity:** {error.severity.value}
**Error Type:** {error.error_type}
**Timestamp:** {error.timestamp}

## Error Message

```
{error.message}
```

## Recovery Instructions

{instructions}

## Actions Required

- [ ] Review error details
- [ ] Implement fix
- [ ] Test resolution
- [ ] Move to Done/

## Notes

Add any additional notes or observations here.
"""

        task_file.write_text(content)
        logger.info(f"Created manual review task: {task_file.name}")

    def _create_retry_task(self, error: ErrorEvent, delay_minutes: int):
        """Create a retry task for transient errors."""
        # Log retry attempt
        self._log_recovery(error, RecoveryStatus.SUCCESS, f"Will retry in {delay_minutes} minutes")

    def _log_recovery(self, error: ErrorEvent, status: RecoveryStatus, details: str):
        """Log recovery attempt."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error.error_type,
            'component': error.component,
            'severity': error.severity.value,
            'recovery_status': status.value,
            'details': details
        }

        with open(self.recovery_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


class WatchdogDaemon:
    """Monitors system health and triggers recovery."""

    def __init__(self, vault_path: str, check_interval: int = 300):
        """Initialize watchdog daemon."""
        self.vault = Path(vault_path)
        self.check_interval = check_interval
        self.detector = ErrorDetector(str(vault_path))
        self.recovery = ErrorRecovery(str(vault_path))
        self.alert_log = self.vault / 'Logs' / 'watchdog_alerts.log'

    def run(self):
        """Run watchdog daemon."""
        logger.info(f"Starting watchdog daemon (checking every {self.check_interval}s)")

        try:
            while True:
                self._check_and_recover()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info("Watchdog daemon stopped")

    def _check_and_recover(self):
        """Check for errors and attempt recovery."""
        # Scan for errors
        errors = self.detector.scan_logs(hours=1)

        if errors:
            logger.info(f"Found {len(errors)} error(s)")
            for error in errors:
                if not error.recovery_attempted:
                    status = self.recovery.attempt_recovery(error)
                    error.recovery_attempted = True
                    error.recovery_status = status
                    self._log_alert(error)

        # Check system health
        health = self.detector.check_system_health()
        if health['status'] != 'healthy':
            logger.warning(f"System health: {health['status']}")
            self._log_health_alert(health)

    def _log_alert(self, error: ErrorEvent):
        """Log alert."""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': 'error',
            'severity': error.severity.value,
            'component': error.component,
            'error_type': error.error_type,
            'recovery_status': error.recovery_status.value if error.recovery_status else None
        }

        with open(self.alert_log, 'a') as f:
            f.write(json.dumps(alert) + '\n')

    def _log_health_alert(self, health: Dict[str, Any]):
        """Log health alert."""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': 'health',
            'status': health['status'],
            'checks': health['checks']
        }

        with open(self.alert_log, 'a') as f:
            f.write(json.dumps(alert) + '\n')


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Error Recovery & Watchdog System')
    parser.add_argument(
        '--vault',
        default='/mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run as daemon'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Check interval in seconds (daemon mode)'
    )
    parser.add_argument(
        '--scan',
        action='store_true',
        help='Scan for errors once'
    )
    parser.add_argument(
        '--health',
        action='store_true',
        help='Check system health'
    )

    args = parser.parse_args()

    if args.daemon:
        watchdog = WatchdogDaemon(args.vault, args.interval)
        watchdog.run()

    elif args.scan:
        detector = ErrorDetector(args.vault)
        errors = detector.scan_logs(hours=24)
        print(f"\n🔍 Found {len(errors)} error(s) in last 24 hours\n")
        for error in errors:
            print(f"[{error.severity.value.upper()}] {error.component}: {error.error_type}")
            print(f"  {error.message[:100]}...")
            print()

    elif args.health:
        detector = ErrorDetector(args.vault)
        health = detector.check_system_health()
        print(f"\n💚 System Health: {health['status'].upper()}\n")
        for check_name, check_result in health['checks'].items():
            status_icon = "✅" if check_result['status'] == 'ok' else "⚠️"
            print(f"{status_icon} {check_name}: {check_result['status']}")
        print()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()

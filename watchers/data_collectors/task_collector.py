#!/usr/bin/env python3
"""
Task Data Collector for CEO Briefing System
Collects task completion data from vault folders
"""

from pathlib import Path
from datetime import datetime, timedelta
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskDataCollector:
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.done = self.vault / 'Done'
        self.needs_action = self.vault / 'Needs_Action'
        self.plans = self.vault / 'Plans'

    def collect_weekly_data(self, start_date: datetime, end_date: datetime):
        """Collect task data for the specified week"""
        logger.info(f"Collecting task data from {start_date.date()} to {end_date.date()}")

        completed_tasks = self._get_completed_tasks(start_date, end_date)
        pending_tasks = self._get_pending_tasks()
        bottlenecks = self._detect_bottlenecks(pending_tasks)

        return {
            'completed': {
                'count': len(completed_tasks),
                'tasks': completed_tasks
            },
            'pending': {
                'count': len(pending_tasks),
                'tasks': pending_tasks
            },
            'bottlenecks': {
                'count': len(bottlenecks),
                'tasks': bottlenecks
            }
        }

    def _get_completed_tasks(self, start_date: datetime, end_date: datetime):
        """Get tasks completed during the specified period"""
        completed = []

        if not self.done.exists():
            logger.warning(f"Done folder not found: {self.done}")
            return completed

        for task_file in self.done.glob('*.md'):
            try:
                # Get file modification time
                stat = task_file.stat()
                modified_time = datetime.fromtimestamp(stat.st_mtime)

                # Check if completed in date range
                if start_date <= modified_time <= end_date:
                    task_info = self._parse_task_file(task_file)
                    task_info['completed_date'] = modified_time.isoformat()
                    completed.append(task_info)

            except Exception as e:
                logger.error(f"Error processing {task_file}: {e}")
                continue

        logger.info(f"Found {len(completed)} completed tasks")
        return completed

    def _get_pending_tasks(self):
        """Get currently pending tasks"""
        pending = []

        if not self.needs_action.exists():
            logger.warning(f"Needs_Action folder not found: {self.needs_action}")
            return pending

        for task_file in self.needs_action.glob('*.md'):
            try:
                task_info = self._parse_task_file(task_file)

                # Calculate age
                stat = task_file.stat()
                created_time = datetime.fromtimestamp(stat.st_ctime)
                age_days = (datetime.now() - created_time).days
                task_info['age_days'] = age_days

                pending.append(task_info)

            except Exception as e:
                logger.error(f"Error processing {task_file}: {e}")
                continue

        logger.info(f"Found {len(pending)} pending tasks")
        return pending

    def _detect_bottlenecks(self, pending_tasks):
        """Identify tasks that are stuck (pending > 3 days)"""
        bottlenecks = []

        for task in pending_tasks:
            if task.get('age_days', 0) > 3:
                bottleneck = {
                    'name': task['name'],
                    'age_days': task['age_days'],
                    'priority': task.get('priority', 'unknown'),
                    'type': task.get('type', 'unknown'),
                    'severity': 'high' if task['age_days'] > 7 else 'medium'
                }

                # Infer likely cause
                name_lower = task['name'].lower()
                if 'email' in name_lower:
                    bottleneck['likely_cause'] = 'Waiting on client response'
                elif 'approval' in name_lower:
                    bottleneck['likely_cause'] = 'Pending human approval'
                elif 'payment' in name_lower or 'invoice' in name_lower:
                    bottleneck['likely_cause'] = 'Financial action required'
                else:
                    bottleneck['likely_cause'] = 'Unknown - requires investigation'

                bottlenecks.append(bottleneck)

        logger.info(f"Detected {len(bottlenecks)} bottlenecks")
        return bottlenecks

    def _parse_task_file(self, task_file: Path):
        """Parse task file to extract metadata"""
        task_info = {
            'name': task_file.stem,
            'type': 'unknown',
            'priority': 'medium'
        }

        try:
            content = task_file.read_text()

            # Parse frontmatter if present
            if content.startswith('---'):
                lines = content.split('\n')
                in_frontmatter = False
                for line in lines[1:]:
                    if line.strip() == '---':
                        break
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if key == 'type':
                            task_info['type'] = value
                        elif key == 'priority':
                            task_info['priority'] = value

        except Exception as e:
            logger.error(f"Error parsing {task_file}: {e}")

        return task_info


if __name__ == '__main__':
    # Test the collector
    import sys

    vault_path = sys.argv[1] if len(sys.argv) > 1 else '/mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault'

    collector = TaskDataCollector(vault_path)

    # Get last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    data = collector.collect_weekly_data(start_date, end_date)

    print(json.dumps(data, indent=2))

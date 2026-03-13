#!/usr/bin/env python3
"""
Communication Data Collector for CEO Briefing System
Collects communication metrics from logs
"""

from pathlib import Path
from datetime import datetime, timedelta
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommunicationDataCollector:
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.logs = self.vault / 'Logs'

    def collect_weekly_data(self, start_date: datetime, end_date: datetime):
        """Collect communication data for the specified week"""
        logger.info(f"Collecting communication data from {start_date.date()} to {end_date.date()}")

        emails_sent = 0
        emails_received = 0
        emails_processed = 0
        social_posts = 0
        approvals_requested = 0
        approvals_granted = 0

        if not self.logs.exists():
            logger.warning(f"Logs folder not found: {self.logs}")
            return self._empty_data()

        # Process JSON log files
        for log_file in self.logs.glob('*.json'):
            try:
                log_date_str = log_file.stem

                # Try to parse date from filename
                try:
                    log_date = datetime.strptime(log_date_str, '%Y-%m-%d')
                except ValueError:
                    # Skip files that don't match date pattern
                    continue

                # Check if in date range
                if not (start_date.date() <= log_date.date() <= end_date.date()):
                    continue

                # Read and parse log entries
                with open(log_file, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        continue

                    # Handle both single JSON object and newline-delimited JSON
                    if content.startswith('['):
                        # JSON array
                        logs = json.loads(content)
                    else:
                        # Newline-delimited JSON
                        logs = [json.loads(line) for line in content.split('\n') if line.strip()]

                    for log in logs:
                        action_type = log.get('action_type', '')

                        if action_type == 'email_send':
                            emails_sent += 1
                        elif action_type == 'email_receive':
                            emails_received += 1
                        elif action_type == 'email_process':
                            emails_processed += 1
                        elif action_type in ['linkedin_post', 'facebook_post', 'twitter_post']:
                            social_posts += 1
                        elif action_type == 'approval_request':
                            approvals_requested += 1
                        elif action_type == 'approval_granted':
                            approvals_granted += 1

            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON in {log_file}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error processing {log_file}: {e}")
                continue

        # Also check text log files for activity
        for log_file in self.logs.glob('*.log'):
            try:
                log_date_str = log_file.stem.split('_')[0] if '_' in log_file.stem else log_file.stem

                try:
                    log_date = datetime.strptime(log_date_str, '%Y-%m-%d')
                except ValueError:
                    continue

                if not (start_date.date() <= log_date.date() <= end_date.date()):
                    continue

                # Simple keyword counting in text logs
                content = log_file.read_text().lower()

                if 'email' in content and 'sent' in content:
                    emails_sent += content.count('email sent')
                if 'email' in content and 'received' in content:
                    emails_received += content.count('email received')

            except Exception as e:
                logger.error(f"Error processing {log_file}: {e}")
                continue

        logger.info(f"Communication metrics: {emails_sent} sent, {emails_received} received, {social_posts} posts")

        return {
            'emails': {
                'sent': emails_sent,
                'received': emails_received,
                'processed': emails_processed,
                'response_rate': self._calculate_response_rate(emails_received, emails_sent)
            },
            'social_media': {
                'posts': social_posts
            },
            'approvals': {
                'requested': approvals_requested,
                'granted': approvals_granted,
                'approval_rate': self._calculate_approval_rate(approvals_requested, approvals_granted)
            }
        }

    def _calculate_response_rate(self, received, sent):
        """Calculate email response rate"""
        if received == 0:
            return 0
        return round((sent / received) * 100, 1)

    def _calculate_approval_rate(self, requested, granted):
        """Calculate approval rate"""
        if requested == 0:
            return 0
        return round((granted / requested) * 100, 1)

    def _empty_data(self):
        """Return empty data structure"""
        return {
            'emails': {
                'sent': 0,
                'received': 0,
                'processed': 0,
                'response_rate': 0
            },
            'social_media': {
                'posts': 0
            },
            'approvals': {
                'requested': 0,
                'granted': 0,
                'approval_rate': 0
            }
        }


if __name__ == '__main__':
    # Test the collector
    import sys

    vault_path = sys.argv[1] if len(sys.argv) > 1 else '/mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault'

    collector = CommunicationDataCollector(vault_path)

    # Get last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    data = collector.collect_weekly_data(start_date, end_date)

    print(json.dumps(data, indent=2))

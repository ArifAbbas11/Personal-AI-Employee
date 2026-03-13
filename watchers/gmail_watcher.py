"""Gmail Watcher - Monitors Gmail inbox for important emails."""
import base64
import time
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher
from gmail_auth import GmailAuthenticator
import logging


class GmailWatcher(BaseWatcher):
    """Watcher for monitoring Gmail inbox."""

    def __init__(self, vault_path: str, credentials_path: str, check_interval: int = 120):
        """
        Initialize Gmail watcher.

        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to Gmail credentials.json
            check_interval: Seconds between checks (default: 120 = 2 minutes)
        """
        super().__init__(vault_path, check_interval)

        # Authenticate with Gmail
        self.authenticator = GmailAuthenticator(credentials_path)
        self.service = self.authenticator.get_gmail_service()

        # Track processed message IDs
        self.processed_ids = set()

        # Keywords that trigger high priority
        self.urgent_keywords = [
            'urgent', 'asap', 'important', 'critical',
            'invoice', 'payment', 'overdue', 'deadline',
            'meeting', 'call', 'emergency'
        ]

        # Senders that are always important
        self.important_senders = []  # Add important email addresses here

        self.logger.info("Gmail watcher initialized")

    def check_for_updates(self) -> list:
        """
        Check Gmail for new important emails.

        Returns:
            List of new message objects
        """
        try:
            # Query for unread important emails
            query = 'is:unread (is:important OR is:starred)'

            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()

            messages = results.get('messages', [])

            # Filter out already processed messages
            new_messages = [
                msg for msg in messages
                if msg['id'] not in self.processed_ids
            ]

            return new_messages

        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            return []

    def get_message_details(self, message_id: str) -> dict:
        """
        Get full details of a message.

        Args:
            message_id: Gmail message ID

        Returns:
            Dictionary with message details
        """
        try:
            msg = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract headers
            headers = {
                h['name']: h['value']
                for h in msg['payload'].get('headers', [])
            }

            # Extract body
            body = self._get_message_body(msg['payload'])

            # Extract snippet
            snippet = msg.get('snippet', '')

            return {
                'id': message_id,
                'thread_id': msg.get('threadId'),
                'from': headers.get('From', 'Unknown'),
                'to': headers.get('To', ''),
                'subject': headers.get('Subject', 'No Subject'),
                'date': headers.get('Date', ''),
                'body': body,
                'snippet': snippet,
                'labels': msg.get('labelIds', [])
            }

        except Exception as e:
            self.logger.error(f"Error getting message details: {e}")
            return None

    def _get_message_body(self, payload: dict) -> str:
        """
        Extract message body from payload.

        Args:
            payload: Message payload

        Returns:
            Message body text
        """
        body = ""

        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
        else:
            # Simple message
            if 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8')

        return body

    def determine_priority(self, message: dict) -> str:
        """
        Determine priority level of a message.

        Args:
            message: Message details dictionary

        Returns:
            Priority level: 'high', 'medium', or 'low'
        """
        subject = message.get('subject', '').lower()
        body = message.get('snippet', '').lower()
        sender = message.get('from', '').lower()

        # Check for urgent keywords
        text = f"{subject} {body}"
        if any(keyword in text for keyword in self.urgent_keywords):
            return 'high'

        # Check for important senders
        if any(important in sender for important in self.important_senders):
            return 'high'

        # Check labels
        labels = message.get('labels', [])
        if 'IMPORTANT' in labels or 'STARRED' in labels:
            return 'high'

        return 'medium'

    def create_action_file(self, message_id: str) -> Path:
        """
        Create action file for an email.

        Args:
            message_id: Gmail message ID

        Returns:
            Path to created action file
        """
        # Get message details
        message = self.get_message_details(message_id)

        if not message:
            self.logger.error(f"Could not get details for message {message_id}")
            return None

        # Determine priority
        priority = self.determine_priority(message)

        # Create action file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'EMAIL_{timestamp}_{message_id[:8]}.md'
        filepath = self.needs_action / filename

        # Truncate body for preview
        body_preview = message['body'][:500] if message['body'] else message['snippet']

        content = f'''---
type: email
message_id: {message['id']}
thread_id: {message['thread_id']}
from: {message['from']}
to: {message['to']}
subject: {message['subject']}
date: {message['date']}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
---

## Email Details

**From:** {message['from']}
**Subject:** {message['subject']}
**Date:** {message['date']}
**Priority:** {priority.upper()}

## Message Preview

```
{body_preview}
```

## Suggested Actions

- [ ] Read full email content
- [ ] Determine required response
- [ ] Draft reply (if needed)
- [ ] Forward to relevant party (if needed)
- [ ] Mark as processed when complete

## Notes

Add any relevant notes or context about this email here.

## Response Draft

(Claude will draft a response here if needed)
'''

        filepath.write_text(content)
        self.processed_ids.add(message_id)

        return filepath

    def run(self):
        """Main loop - continuously check for new emails."""
        self.logger.info(f'Starting Gmail Watcher')
        self.logger.info(f'Monitoring Gmail inbox every {self.check_interval} seconds')
        self.logger.info(f'Creating action items in: {self.needs_action}')

        # Test connection
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            self.logger.info(f'Connected to Gmail: {profile.get("emailAddress")}')
        except Exception as e:
            self.logger.error(f'Failed to connect to Gmail: {e}')
            return

        while True:
            try:
                messages = self.check_for_updates()

                if messages:
                    self.logger.info(f'Found {len(messages)} new email(s)')
                    for message in messages:
                        filepath = self.create_action_file(message['id'])
                        if filepath:
                            self.logger.info(f'Created action file: {filepath.name}')
                else:
                    self.logger.debug('No new emails')

            except KeyboardInterrupt:
                self.logger.info('Gmail watcher stopped by user')
                break
            except Exception as e:
                self.logger.error(f'Error in main loop: {e}', exc_info=True)

            time.sleep(self.check_interval)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("Usage: python gmail_watcher.py <vault_path> <credentials_path>")
        print("Example: python gmail_watcher.py ../AI_Employee_Vault ./credentials.json")
        sys.exit(1)

    vault_path = sys.argv[1]
    credentials_path = sys.argv[2]

    watcher = GmailWatcher(vault_path, credentials_path)
    watcher.run()

"""Approval Processor - Handles human-in-the-loop approval workflow."""
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging


class ApprovalHandler(FileSystemEventHandler):
    """Handler for approval workflow events."""

    def __init__(self, vault_path: str):
        """
        Initialize approval handler.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'

        # Ensure directories exist
        for directory in [self.pending_approval, self.approved, self.rejected, self.logs]:
            directory.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for approval processor."""
        logger = logging.getLogger('ApprovalProcessor')
        logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        log_file = self.logs / 'ApprovalProcessor.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    def on_created(self, event):
        """
        Handle new files in Approved or Rejected folders.

        Args:
            event: File system event
        """
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if file is in Approved folder
        if self.approved in file_path.parents:
            self.process_approval(file_path)

        # Check if file is in Rejected folder
        elif self.rejected in file_path.parents:
            self.process_rejection(file_path)

    def process_approval(self, file_path: Path):
        """
        Process an approved action.

        Args:
            file_path: Path to approved file
        """
        self.logger.info(f"Processing approval: {file_path.name}")

        try:
            # Read the approval file
            content = file_path.read_text()

            # Extract metadata
            metadata = self._extract_metadata(content)

            # Log the approval
            self._log_action('approved', file_path.name, metadata)

            # Execute the approved action
            self._execute_action(metadata)

            self.logger.info(f"✅ Approved action executed: {file_path.name}")

        except Exception as e:
            self.logger.error(f"Error processing approval: {e}", exc_info=True)

    def process_rejection(self, file_path: Path):
        """
        Process a rejected action.

        Args:
            file_path: Path to rejected file
        """
        self.logger.info(f"Processing rejection: {file_path.name}")

        try:
            # Read the rejection file
            content = file_path.read_text()

            # Extract metadata
            metadata = self._extract_metadata(content)

            # Log the rejection
            self._log_action('rejected', file_path.name, metadata)

            self.logger.info(f"❌ Action rejected: {file_path.name}")

        except Exception as e:
            self.logger.error(f"Error processing rejection: {e}", exc_info=True)

    def _extract_metadata(self, content: str) -> dict:
        """
        Extract YAML frontmatter metadata from file.

        Args:
            content: File content

        Returns:
            Dictionary of metadata
        """
        metadata = {}

        if content.startswith('---'):
            # Extract YAML frontmatter
            parts = content.split('---', 2)
            if len(parts) >= 2:
                yaml_content = parts[1].strip()
                for line in yaml_content.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()

        return metadata

    def _execute_action(self, metadata: dict):
        """
        Execute an approved action based on metadata.

        Args:
            metadata: Action metadata
        """
        action_type = metadata.get('action', metadata.get('type', 'unknown'))

        self.logger.info(f"Executing action type: {action_type}")

        # Route to appropriate handler
        if action_type == 'send_email':
            self._execute_email_send(metadata)
        elif action_type == 'whatsapp_send':
            self._execute_whatsapp_send(metadata)
        elif action_type == 'linkedin_post':
            self._execute_linkedin_post(metadata)
        elif action_type == 'payment':
            self._execute_payment(metadata)
        else:
            self.logger.warning(f"Unknown action type: {action_type}")

    def _execute_email_send(self, metadata: dict):
        """Execute email sending action."""
        self.logger.info("Email send action - requires MCP server integration")
        # This will be implemented when MCP server is ready
        pass

    def _execute_whatsapp_send(self, metadata: dict):
        """Execute WhatsApp sending action."""
        self.logger.info("WhatsApp send action - requires MCP server integration")
        # This will be implemented when MCP server is ready
        pass

    def _execute_linkedin_post(self, metadata: dict):
        """Execute LinkedIn posting action."""
        self.logger.info("LinkedIn post action - requires MCP server integration")
        # This will be implemented when MCP server is ready
        pass

    def _execute_payment(self, metadata: dict):
        """Execute payment action."""
        self.logger.info("Payment action - requires MCP server integration")
        # This will be implemented when MCP server is ready
        pass

    def _log_action(self, status: str, filename: str, metadata: dict):
        """
        Log approval/rejection action.

        Args:
            status: 'approved' or 'rejected'
            filename: Name of the file
            metadata: Action metadata
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': 'approval_decision',
            'status': status,
            'filename': filename,
            'metadata': metadata,
            'actor': 'human'
        }

        # Append to today's log file
        log_file = self.logs / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        # Read existing logs
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except:
                logs = []

        # Append new log
        logs.append(log_entry)

        # Write back
        log_file.write_text(json.dumps(logs, indent=2))

    def check_expired_approvals(self):
        """Check for expired approval requests and move to rejected."""
        self.logger.debug("Checking for expired approvals...")

        for file_path in self.pending_approval.glob('*.md'):
            try:
                content = file_path.read_text()
                metadata = self._extract_metadata(content)

                # Check expiration
                expires = metadata.get('expires', '')
                if expires:
                    expiry_time = datetime.fromisoformat(expires)
                    if datetime.now() > expiry_time:
                        # Move to rejected
                        dest = self.rejected / file_path.name
                        file_path.rename(dest)
                        self.logger.warning(f"Approval expired: {file_path.name}")

            except Exception as e:
                self.logger.error(f"Error checking expiration: {e}")


class ApprovalProcessor:
    """Main approval processor that watches for approval decisions."""

    def __init__(self, vault_path: str):
        """
        Initialize approval processor.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.observer = Observer()
        self.handler = ApprovalHandler(vault_path)
        self.logger = logging.getLogger('ApprovalProcessor')

    def run(self):
        """Start the approval processor."""
        print(f"Starting Approval Processor")
        print(f"Monitoring: {self.vault_path}")
        print(f"Watching for approvals/rejections...")
        print(f"Press Ctrl+C to stop\n")

        # Schedule observers for Approved and Rejected folders
        self.observer.schedule(
            self.handler,
            str(self.handler.approved),
            recursive=False
        )
        self.observer.schedule(
            self.handler,
            str(self.handler.rejected),
            recursive=False
        )

        self.observer.start()
        self.logger.info('Approval processor started')

        try:
            while True:
                # Check for expired approvals every 5 minutes
                self.handler.check_expired_approvals()
                time.sleep(300)

        except KeyboardInterrupt:
            print("\nStopping Approval Processor...")
            self.observer.stop()

        self.observer.join()
        print("Approval Processor stopped")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python approval_processor.py <vault_path>")
        print("Example: python approval_processor.py ../AI_Employee_Vault")
        sys.exit(1)

    vault_path = sys.argv[1]
    processor = ApprovalProcessor(vault_path)
    processor.run()

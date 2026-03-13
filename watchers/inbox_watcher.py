"""Inbox Watcher - Monitors the Inbox folder for new files."""
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import logging


class InboxHandler(FileSystemEventHandler):
    """Handler for files dropped in the Inbox folder."""

    def __init__(self, vault_path: str):
        """
        Initialize the inbox handler.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.processed_files = set()

        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for this watcher."""
        logger = logging.getLogger('InboxWatcher')
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # File handler
        log_dir = self.vault_path / 'Logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'InboxWatcher.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Formatter
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
        Handle file creation events in Inbox.

        Args:
            event: File system event
        """
        if event.is_directory:
            return

        source = Path(event.src_path)

        # Ignore hidden files, temporary files, and action files
        if (source.name.startswith('.') or
            source.name.endswith('~') or
            source.name.startswith('FILE_')):
            return

        # Avoid processing the same file multiple times
        if source.name in self.processed_files:
            return

        self.logger.info(f"New file detected in Inbox: {source.name}")

        # Wait a moment to ensure file is fully written
        time.sleep(0.5)

        try:
            # Create metadata file in Needs_Action
            self.create_action_file(source)
            self.processed_files.add(source.name)
        except Exception as e:
            self.logger.error(f"Error processing file {source.name}: {e}")

    def on_modified(self, event):
        """
        Handle file modification events.

        Args:
            event: File system event
        """
        if event.is_directory:
            return

        source = Path(event.src_path)

        # Only process if not already processed
        if source.name not in self.processed_files:
            self.on_created(event)

    def create_action_file(self, source: Path):
        """
        Create an action file for the inbox file.

        Args:
            source: Path to the file in Inbox
        """
        # Get file stats
        try:
            stats = source.stat()
            file_size = stats.st_size
        except Exception:
            file_size = 0

        file_type = source.suffix[1:] if source.suffix else 'unknown'

        # Read file content preview (first 500 chars)
        content_preview = ""
        try:
            if file_type in ['md', 'txt', 'text']:
                content_preview = source.read_text(encoding='utf-8')[:500]
        except Exception:
            content_preview = "[Unable to read file content]"

        # Create action file name (sanitize)
        action_name = source.stem.replace(' ', '_')
        meta_path = self.needs_action / f'FILE_{action_name}.md'

        # If file already exists, add timestamp
        if meta_path.exists():
            timestamp = datetime.now().strftime('%H%M%S')
            meta_path = self.needs_action / f'FILE_{action_name}_{timestamp}.md'

        content = f'''---
type: file_drop
original_name: {source.name}
file_type: {file_type}
size_bytes: {file_size}
inbox_location: Inbox/{source.name}
created: {datetime.now().isoformat()}
status: pending
priority: medium
---

## New File Dropped for Processing

**File:** {source.name}
**Type:** {file_type}
**Size:** {file_size:,} bytes ({file_size / 1024:.2f} KB)
**Location:** `Inbox/{source.name}`

## Content Preview

```
{content_preview}
```

## Suggested Actions

- [ ] Review file contents
- [ ] Determine appropriate action
- [ ] Process or categorize
- [ ] Move to appropriate folder when complete

## Notes

Add any relevant notes or context about this file here.
'''

        meta_path.write_text(content)
        self.logger.info(f"Created action file: {meta_path.name}")


class InboxWatcher:
    """Watcher for monitoring the Inbox folder."""

    def __init__(self, vault_path: str):
        """
        Initialize the inbox watcher.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / 'Inbox'
        self.inbox.mkdir(parents=True, exist_ok=True)

        self.observer = Observer()
        self.event_handler = InboxHandler(vault_path)
        self.logger = logging.getLogger('InboxWatcher')

    def scan_existing_files(self):
        """Scan for existing files in Inbox and create action items."""
        self.logger.info("Scanning for existing files in Inbox...")

        for file_path in self.inbox.glob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                self.logger.info(f"Found existing file: {file_path.name}")
                self.event_handler.create_action_file(file_path)
                self.event_handler.processed_files.add(file_path.name)

    def run(self):
        """Start the inbox observer."""
        print(f"Starting Inbox Watcher")
        print(f"Monitoring: {self.inbox}")
        print(f"Vault: {self.vault_path}")
        print(f"Drop files into Inbox/ to create tasks automatically")
        print(f"Press Ctrl+C to stop\n")

        # Scan for existing files first
        self.scan_existing_files()

        # Schedule the observer
        self.observer.schedule(
            self.event_handler,
            str(self.inbox),
            recursive=False
        )

        self.observer.start()
        self.logger.info('Inbox observer started')

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping Inbox Watcher...")
            self.observer.stop()

        self.observer.join()
        print("Inbox Watcher stopped")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python inbox_watcher.py <vault_path>")
        print("Example: python inbox_watcher.py ../AI_Employee_Vault")
        sys.exit(1)

    vault_path = sys.argv[1]
    watcher = InboxWatcher(vault_path)
    watcher.run()

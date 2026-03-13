"""WhatsApp Watcher - Monitors WhatsApp Web for important messages."""
import time
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import logging


class WhatsAppWatcher(BaseWatcher):
    """Watcher for monitoring WhatsApp Web messages."""

    def __init__(self, vault_path: str, session_path: str, check_interval: int = 30):
        """
        Initialize WhatsApp watcher.

        Args:
            vault_path: Path to the Obsidian vault
            session_path: Path to store browser session data
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)

        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Keywords that trigger action items
        self.urgent_keywords = [
            'urgent', 'asap', 'emergency', 'help',
            'invoice', 'payment', 'due', 'overdue',
            'meeting', 'call', 'important', 'critical',
            'quote', 'proposal', 'contract', 'deadline'
        ]

        # Track processed messages
        self.processed_messages = set()

        self.logger.info("WhatsApp watcher initialized")

    def check_for_updates(self) -> list:
        """
        Check WhatsApp Web for new messages with urgent keywords.

        Returns:
            List of message dictionaries
        """
        messages = []

        try:
            with sync_playwright() as p:
                # Launch browser with persistent context (saves login)
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Set to True for production
                    args=['--no-sandbox']
                )

                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://web.whatsapp.com', timeout=90000)

                # Wait for WhatsApp to load
                try:
                    # Wait for chat list or QR code (increased timeout)
                    self.logger.info("Waiting for WhatsApp Web to load...")
                    page.wait_for_selector('[data-testid="chat-list"], canvas, [data-testid="default-user"]', timeout=90000)

                    # Check if QR code is present (not logged in)
                    qr_code = page.query_selector('canvas')
                    if qr_code:
                        self.logger.warning("WhatsApp not logged in - scan QR code to authenticate")
                        self.logger.info("Waiting 120 seconds for QR code scan...")
                        time.sleep(120)

                        # After scan, wait for WhatsApp to fully load with multiple possible selectors
                        self.logger.info("Waiting for WhatsApp to load after authentication...")

                        # Try multiple selectors that indicate WhatsApp is loaded
                        loaded = False
                        for attempt in range(3):
                            try:
                                self.logger.info(f"Load attempt {attempt + 1}/3...")
                                page.wait_for_selector(
                                    '[data-testid="chat-list"], [data-testid="default-user"], #pane-side',
                                    timeout=60000
                                )
                                self.logger.info("WhatsApp loaded successfully!")
                                loaded = True
                                break
                            except PlaywrightTimeout:
                                if attempt < 2:
                                    self.logger.warning(f"Attempt {attempt + 1} timed out, retrying...")
                                    time.sleep(10)
                                else:
                                    self.logger.error("WhatsApp did not load after QR scan - will retry next cycle")

                        browser.close()
                        return []

                    # Wait for chat list to be ready with multiple possible selectors
                    self.logger.info("Checking for chat list...")
                    page.wait_for_selector(
                        '[data-testid="chat-list"], [data-testid="default-user"], #pane-side',
                        timeout=90000
                    )
                    self.logger.info("WhatsApp Web loaded successfully")

                    # Find unread chats
                    unread_chats = page.query_selector_all('[data-testid="cell-frame-container"]')

                    for chat in unread_chats[:10]:  # Limit to 10 most recent
                        try:
                            # Check if chat has unread indicator
                            unread_badge = chat.query_selector('[data-testid="icon-unread-count"]')
                            if not unread_badge:
                                continue

                            # Get chat name
                            name_element = chat.query_selector('[data-testid="cell-frame-title"]')
                            chat_name = name_element.inner_text() if name_element else "Unknown"

                            # Get last message
                            message_element = chat.query_selector('[data-testid="last-msg-text"]')
                            if not message_element:
                                continue

                            message_text = message_element.inner_text()

                            # Check for urgent keywords
                            if any(keyword in message_text.lower() for keyword in self.urgent_keywords):
                                # Create unique ID for this message
                                message_id = f"{chat_name}_{message_text[:20]}"

                                if message_id not in self.processed_messages:
                                    messages.append({
                                        'chat_name': chat_name,
                                        'message': message_text,
                                        'timestamp': datetime.now().isoformat(),
                                        'id': message_id
                                    })
                                    self.processed_messages.add(message_id)

                        except Exception as e:
                            self.logger.debug(f"Error processing chat: {e}")
                            continue

                except PlaywrightTimeout:
                    self.logger.error("Timeout waiting for WhatsApp to load")

                browser.close()

        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}", exc_info=True)

        return messages

    def create_action_file(self, message: dict) -> Path:
        """
        Create action file for a WhatsApp message.

        Args:
            message: Message dictionary

        Returns:
            Path to created action file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        chat_name_safe = message['chat_name'].replace(' ', '_').replace('/', '_')
        filename = f'WHATSAPP_{timestamp}_{chat_name_safe}.md'
        filepath = self.needs_action / filename

        content = f'''---
type: whatsapp_message
chat_name: {message['chat_name']}
received: {message['timestamp']}
priority: high
status: pending
---

## WhatsApp Message

**From:** {message['chat_name']}
**Received:** {message['timestamp']}
**Priority:** HIGH (contains urgent keyword)

## Message Content

```
{message['message']}
```

## Suggested Actions

- [ ] Read full conversation context
- [ ] Determine required response
- [ ] Draft reply (requires approval)
- [ ] Escalate if needed
- [ ] Mark as processed when complete

## Notes

This message was flagged as urgent based on keywords. Review the full conversation in WhatsApp Web for context.

## Response Draft

(Claude will draft a response here if needed - requires human approval before sending)

---

**⚠️ IMPORTANT:** All WhatsApp responses require human approval before sending.
'''

        filepath.write_text(content)
        return filepath


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("Usage: python whatsapp_watcher.py <vault_path> <session_path>")
        print("Example: python whatsapp_watcher.py ../AI_Employee_Vault ./whatsapp_session")
        print()
        print("First run: Browser will open for QR code scan")
        print("Subsequent runs: Will use saved session")
        sys.exit(1)

    vault_path = sys.argv[1]
    session_path = sys.argv[2]

    watcher = WhatsAppWatcher(vault_path, session_path)
    watcher.run()

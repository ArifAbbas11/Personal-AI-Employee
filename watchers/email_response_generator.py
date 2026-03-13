#!/usr/bin/env python3
"""
Email Response Generator
Monitors Needs_Action folder and generates draft responses
"""

import os
import re
import time
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailResponseGenerator:
    """Generate draft email responses from action items"""

    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize Email Response Generator.

        Args:
            vault_path: Path to the vault
            check_interval: Seconds between checks (default: 30)
        """
        self.vault_path = Path(vault_path)
        self.needs_action_dir = self.vault_path / 'Needs_Action'
        self.pending_approval_dir = self.vault_path / 'Pending_Approval' / 'emails'
        self.check_interval = check_interval

        # Create directories if they don't exist
        self.pending_approval_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Email Response Generator initialized")

    def parse_email_action(self, file_path: Path) -> dict:
        """Parse email action file"""
        try:
            content = file_path.read_text()

            # Extract metadata
            metadata = {}
            lines = content.split('\n')

            in_metadata = False
            for line in lines:
                if line.strip() == '---':
                    in_metadata = not in_metadata
                    continue

                if in_metadata and ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

            # Extract message preview
            message_preview = ""
            if '```' in content:
                parts = content.split('```')
                if len(parts) >= 2:
                    message_preview = parts[1].strip()

            return {
                'message_id': metadata.get('message_id', ''),
                'thread_id': metadata.get('thread_id', ''),
                'from': metadata.get('from', ''),
                'to': metadata.get('to', ''),
                'subject': metadata.get('subject', ''),
                'date': metadata.get('date', ''),
                'priority': metadata.get('priority', 'medium'),
                'message': message_preview
            }

        except Exception as e:
            logger.error(f"Error parsing {file_path.name}: {e}")
            return None

    def generate_response(self, email_data: dict) -> str:
        """Generate draft response based on email content"""

        subject = email_data.get('subject', '').lower()
        message = email_data.get('message', '').lower()
        from_email = email_data.get('from', '')

        # Extract sender name
        sender_name = "there"
        if '<' in from_email:
            sender_name = from_email.split('<')[0].strip()

        # Generate contextual response based on keywords
        if any(word in message or word in subject for word in ['pricing', 'price', 'cost', 'quote']):
            response = self._generate_pricing_response(sender_name)
        elif any(word in message or word in subject for word in ['meeting', 'call', 'schedule', 'appointment']):
            response = self._generate_meeting_response(sender_name)
        elif any(word in message or word in subject for word in ['question', 'inquiry', 'ask', 'information']):
            response = self._generate_inquiry_response(sender_name)
        elif any(word in message or word in subject for word in ['demo', 'demonstration', 'trial']):
            response = self._generate_demo_response(sender_name)
        else:
            response = self._generate_general_response(sender_name)

        return response

    def _generate_pricing_response(self, sender_name: str) -> str:
        """Generate pricing inquiry response"""
        return f"""Hi {sender_name},

Thank you for your interest in our AI automation services!

I'd be happy to provide information about our pricing. Our services are customized based on your specific needs and requirements.

Our AI Employee system can help automate:
- Email management and auto-responses
- Social media posting (LinkedIn, Twitter)
- Business process automation
- Task routing and management
- Daily activity summaries and reporting

To provide you with accurate pricing, I'd like to understand:
- What processes you're looking to automate
- Your current workflow challenges
- Expected volume of automation tasks
- Timeline for implementation

Could you please share more details about your specific needs? I'd be happy to schedule a call to discuss how our AI Employee can help your business.

Best regards,
Azfia Ghufran
AI Automation Services
azfiaghufran.cis@gmail.com"""

    def _generate_meeting_response(self, sender_name: str) -> str:
        """Generate meeting request response"""
        return f"""Hi {sender_name},

Thank you for reaching out!

I'd be happy to schedule a meeting to discuss your needs. I'm available for a call or video meeting at your convenience.

Please let me know:
- Your preferred date and time
- Duration needed (30 min, 1 hour, etc.)
- Meeting format preference (phone, Zoom, Google Meet, etc.)
- Any specific topics you'd like to cover

Looking forward to connecting with you!

Best regards,
Azfia Ghufran
AI Automation Services
azfiaghufran.cis@gmail.com"""

    def _generate_inquiry_response(self, sender_name: str) -> str:
        """Generate general inquiry response"""
        return f"""Hi {sender_name},

Thank you for your inquiry!

I'd be happy to help answer your questions about our AI automation services. Our AI Employee system is designed to streamline business operations through intelligent automation.

Key capabilities include:
- Automated email management and responses
- Social media content creation and posting
- Business process automation
- Intelligent task routing
- Analytics and reporting

Could you please provide more details about what you're looking to achieve? This will help me give you the most relevant information.

I'm here to help!

Best regards,
Azfia Ghufran
AI Automation Services
azfiaghufran.cis@gmail.com"""

    def _generate_demo_response(self, sender_name: str) -> str:
        """Generate demo request response"""
        return f"""Hi {sender_name},

Thank you for your interest in seeing our AI Employee system in action!

I'd be delighted to provide you with a personalized demonstration. During the demo, I can show you:
- Real-time email automation
- Social media integration
- Task management capabilities
- Custom workflow automation
- Analytics and reporting features

To schedule your demo, please let me know:
- Your preferred date and time
- Specific features you're most interested in
- Any particular use cases you'd like to explore

I'll prepare a customized demo based on your needs.

Looking forward to showing you what our AI Employee can do!

Best regards,
Azfia Ghufran
AI Automation Services
azfiaghufran.cis@gmail.com"""

    def _generate_general_response(self, sender_name: str) -> str:
        """Generate general response"""
        return f"""Hi {sender_name},

Thank you for reaching out!

I appreciate your message and would be happy to assist you. To provide you with the most helpful response, could you please provide a bit more detail about what you're looking for?

I'm here to help with:
- AI automation solutions
- Business process optimization
- Email and social media management
- Custom workflow automation
- And more

Please feel free to share more about your needs, and I'll get back to you with detailed information.

Best regards,
Azfia Ghufran
AI Automation Services
azfiaghufran.cis@gmail.com"""

    def create_response_file(self, email_data: dict, response_text: str):
        """Create response file in Pending_Approval folder"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            message_id_short = email_data['message_id'][:8] if email_data['message_id'] else 'unknown'
            filename = f"EMAIL_RESPONSE_{timestamp}_{message_id_short}.md"
            filepath = self.pending_approval_dir / filename

            content = f"""# Email Response Draft

**Status:** Pending Approval
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Original Email

**Message ID:** {email_data['message_id']}
**From:** {email_data['from']}
**To:** {email_data['to']}
**Subject:** {email_data['subject']}
**Date:** {email_data['date']}

**Body:**
{email_data['message']}

---

## Proposed Response

{response_text}

---

## Instructions

1. **Review** the proposed response above
2. **Edit** if needed (modify the text under "Proposed Response")
3. **When satisfied**, move this file to: `AI_Employee_Vault/Approved/emails/`
4. The system will automatically send the response within 60 seconds

**To approve:**
```bash
mv AI_Employee_Vault/Pending_Approval/emails/{filename} \\
   AI_Employee_Vault/Approved/emails/
```

**To reject:** Delete this file or move to a "Rejected" folder
"""

            filepath.write_text(content)
            logger.info(f"Created response draft: {filename}")
            return filepath

        except Exception as e:
            logger.error(f"Error creating response file: {e}")
            return None

    def process_email_actions(self):
        """Process all email action files"""
        try:
            email_files = list(self.needs_action_dir.glob('EMAIL_*.md'))

            if not email_files:
                logger.debug("No email action files to process")
                return

            logger.info(f"Processing {len(email_files)} email action file(s)")

            for file in email_files:
                try:
                    # Parse email data
                    email_data = self.parse_email_action(file)
                    if not email_data or not email_data.get('message_id'):
                        logger.warning(f"Could not parse {file.name}")
                        continue

                    # Check if response already exists
                    message_id_short = email_data['message_id'][:8]
                    existing = list(self.pending_approval_dir.glob(f'EMAIL_RESPONSE_*_{message_id_short}.md'))
                    if existing:
                        logger.info(f"Response already exists for {file.name}")
                        # Delete the original email action file
                        file.unlink()
                        continue

                    # Generate response
                    response_text = self.generate_response(email_data)

                    # Create response file
                    response_file = self.create_response_file(email_data, response_text)

                    if response_file:
                        # Delete the original email action file
                        file.unlink()
                        logger.info(f"Processed {file.name} → {response_file.name}")

                except Exception as e:
                    logger.error(f"Error processing {file.name}: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Error in process_email_actions: {e}", exc_info=True)

    def run(self):
        """Main loop - continuously process email actions"""
        logger.info(f"Starting Email Response Generator")
        logger.info(f"Monitoring: {self.needs_action_dir}")
        logger.info(f"Output to: {self.pending_approval_dir}")
        logger.info(f"Check interval: {self.check_interval} seconds")

        while True:
            try:
                self.process_email_actions()
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info("Email Response Generator stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(self.check_interval)


if __name__ == '__main__':
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    if len(sys.argv) < 2:
        print("Usage: python email_response_generator.py <vault_path>")
        print("Example: python email_response_generator.py ../AI_Employee_Vault")
        sys.exit(1)

    vault_path = sys.argv[1]

    generator = EmailResponseGenerator(vault_path)
    generator.run()

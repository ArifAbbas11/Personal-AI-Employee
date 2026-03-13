#!/usr/bin/env python3
"""
Gmail Auto-Responder
Monitors approved emails and sends automatic responses
"""

import pickle
import os
from pathlib import Path
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import time
from datetime import datetime

class GmailAutoResponder:
    """Handle Gmail auto-responses"""
    
    def __init__(self):
        self.creds = self.load_credentials()
        self.service = build('gmail', 'v1', credentials=self.creds)

        # Use Docker vault path if available, otherwise local path
        vault_path = os.getenv('VAULT_PATH', str(Path(__file__).parent.parent / 'AI_Employee_Vault'))
        self.approved_dir = Path(vault_path) / 'Approved' / 'emails'
        self.done_dir = Path(vault_path) / 'Done' / 'emails'
        
    def load_credentials(self):
        """Load Gmail credentials"""
        # Try Docker path first, then local path
        token_paths = [
            Path('/secrets/token.pickle'),  # Docker mount
            Path(__file__).parent.parent / 'secrets' / 'token.pickle'  # Local
        ]

        token_path = None
        for path in token_paths:
            if path.exists():
                token_path = path
                break

        if not token_path:
            raise FileNotFoundError("Gmail token not found. Run Gmail authentication first.")

        with open(token_path, 'rb') as token:
            return pickle.load(token)
    
    def get_email_details(self, message_id):
        """Get email details from Gmail"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
            
            return {
                'id': message_id,
                'subject': subject,
                'from': from_email,
                'thread_id': message.get('threadId')
            }
        except Exception as e:
            print(f"❌ Error getting email details: {e}")
            return None
    
    def send_auto_response(self, to_email, original_subject, response_text):
        """Send automatic response email"""
        try:
            # Create reply message
            message = MIMEText(response_text)
            message['to'] = to_email
            message['subject'] = f"Re: {original_subject}"
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send email
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"✅ Auto-response sent to: {to_email}")
            return send_message
            
        except Exception as e:
            print(f"❌ Error sending auto-response: {e}")
            return None
    
    def check_approved_emails(self):
        """Check for approved email responses in Approved folder"""
        if not self.approved_dir.exists():
            return
        
        # Look for email response files
        email_files = list(self.approved_dir.glob('EMAIL_RESPONSE_*.md'))
        
        for file in email_files:
            try:
                content = file.read_text()
                
                # Parse email response file
                lines = content.split('\n')
                message_id = None
                response_text = []
                in_response = False
                in_proposed_response = False

                for line in lines:
                    # Handle both formats: "Message ID:" and "**Message ID:**"
                    if 'Message ID:' in line or '**Message ID:**' in line:
                        # Extract message ID from line
                        if '**Message ID:**' in line:
                            message_id = line.split('**Message ID:**')[1].strip()
                        elif 'Message ID:' in line:
                            message_id = line.split('Message ID:')[1].strip()
                    elif line.strip() == '## Proposed Response':
                        in_proposed_response = True
                        continue
                    elif in_proposed_response and line.strip() == '---':
                        # End of proposed response section
                        break
                    elif in_proposed_response and line.strip():
                        response_text.append(line)
                
                if not message_id:
                    print(f"⚠️ No message ID found in {file.name}")
                    continue
                
                # Get original email details
                email_details = self.get_email_details(message_id)
                if not email_details:
                    continue
                
                # Extract sender email
                from_email = email_details['from']
                if '<' in from_email:
                    from_email = from_email.split('<')[1].split('>')[0]
                
                # Send auto-response
                response = '\n'.join(response_text).strip()
                self.send_auto_response(
                    from_email,
                    email_details['subject'],
                    response
                )

                # Update status in file content
                updated_content = content.replace(
                    '**Status:** Pending Approval',
                    f'**Status:** Sent\n**Sent At:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                )

                # Move to Done with updated status
                done_file = self.done_dir / file.name
                done_file.write_text(updated_content)
                file.unlink()
                print(f"✅ Moved {file.name} to Done")
                
            except Exception as e:
                print(f"❌ Error processing {file.name}: {e}")
    
    def run_monitor(self, interval=60):
        """Run continuous monitoring"""
        print("🔄 Gmail Auto-Responder started")
        print(f"📁 Monitoring: {self.approved_dir}")
        print(f"⏱️  Check interval: {interval} seconds")
        print()
        
        while True:
            try:
                self.check_approved_emails()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n⏹️  Auto-responder stopped")
                break
            except Exception as e:
                print(f"❌ Error in monitor loop: {e}")
                time.sleep(interval)

def test_auto_responder():
    """Test auto-responder"""
    try:
        responder = GmailAutoResponder()
        print("✅ Gmail Auto-Responder initialized")
        
        # Check once
        responder.check_approved_emails()
        print("✅ Check complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Run monitor
    responder = GmailAutoResponder()
    responder.run_monitor(interval=60)

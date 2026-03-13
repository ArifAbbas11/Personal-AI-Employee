"""Gmail OAuth2 Authentication Helper."""
import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]


class GmailAuthenticator:
    """Handle Gmail OAuth2 authentication."""

    def __init__(self, credentials_path: str, token_path: str = None):
        """
        Initialize Gmail authenticator.

        Args:
            credentials_path: Path to credentials.json from Google Cloud
            token_path: Path to store token.pickle (default: same dir as credentials)
        """
        self.credentials_path = Path(credentials_path)

        if token_path:
            self.token_path = Path(token_path)
        else:
            self.token_path = self.credentials_path.parent / 'token.pickle'

        self.creds = None

    def authenticate(self):
        """
        Authenticate with Gmail API using OAuth2.

        Returns:
            Credentials object for Gmail API
        """
        # Load existing token if available
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)

        # If no valid credentials, authenticate
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # Refresh expired token
                print("Refreshing expired token...")
                self.creds.refresh(Request())
            else:
                # Run OAuth flow
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        "Please download credentials.json from Google Cloud Console"
                    )

                print("Starting OAuth2 authentication flow...")
                print("A browser window will open for authentication.")

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # Save credentials for future use
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)
            print(f"Credentials saved to {self.token_path}")

        return self.creds

    def get_gmail_service(self):
        """
        Get authenticated Gmail API service.

        Returns:
            Gmail API service object
        """
        if not self.creds:
            self.authenticate()

        return build('gmail', 'v1', credentials=self.creds)

    def test_connection(self):
        """
        Test Gmail API connection.

        Returns:
            bool: True if connection successful
        """
        try:
            service = self.get_gmail_service()
            # Try to get user profile
            profile = service.users().getProfile(userId='me').execute()
            print(f"✅ Successfully connected to Gmail")
            print(f"   Email: {profile.get('emailAddress')}")
            print(f"   Total messages: {profile.get('messagesTotal')}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Gmail: {e}")
            return False


def setup_gmail_auth(credentials_path: str = None):
    """
    Interactive setup for Gmail authentication.

    Args:
        credentials_path: Path to credentials.json (optional)
    """
    print("=" * 60)
    print("Gmail Authentication Setup")
    print("=" * 60)
    print()

    # Find credentials file
    if not credentials_path:
        # Look in common locations
        possible_paths = [
            Path('credentials.json'),
            Path('../credentials.json'),
            Path('watchers/credentials.json'),
            Path.home() / '.credentials' / 'gmail_credentials.json'
        ]

        for path in possible_paths:
            if path.exists():
                credentials_path = str(path)
                print(f"Found credentials at: {credentials_path}")
                break

    if not credentials_path or not Path(credentials_path).exists():
        print("❌ credentials.json not found!")
        print()
        print("To set up Gmail API access:")
        print("1. Go to https://console.cloud.google.com")
        print("2. Create a new project (or select existing)")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download credentials.json")
        print("6. Place it in the watchers/ directory")
        print()
        return False

    # Authenticate
    try:
        authenticator = GmailAuthenticator(credentials_path)
        authenticator.authenticate()

        # Test connection
        if authenticator.test_connection():
            print()
            print("✅ Gmail authentication successful!")
            print(f"   Token saved to: {authenticator.token_path}")
            print()
            print("You can now run the Gmail watcher:")
            print("   python gmail_watcher.py ../AI_Employee_Vault")
            return True
        else:
            return False

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        credentials_path = sys.argv[1]
    else:
        credentials_path = None

    setup_gmail_auth(credentials_path)

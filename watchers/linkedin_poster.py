"""
LinkedIn Auto-Posting Module
"""

import json
import requests
from pathlib import Path
from datetime import datetime
from linkedin_config import (
    LINKEDIN_SHARE_URL,
    TOKEN_FILE
)

class LinkedInPoster:
    """Handle LinkedIn posting"""

    def __init__(self):
        self.access_token = self.load_token()
        self.person_urn = None

    def load_token(self):
        """Load access token from file"""
        if not TOKEN_FILE.exists():
            raise FileNotFoundError(
                f"LinkedIn token not found at {TOKEN_FILE}. "
                "Run linkedin_auth.py first."
            )

        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)

        return token_data.get('access_token')

    def get_user_info(self):
        """Get authenticated user's profile info using userinfo endpoint"""
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        response = requests.get(
            'https://api.linkedin.com/v2/userinfo',
            headers=headers
        )
        response.raise_for_status()

        user_data = response.json()
        # The 'sub' field contains the member ID
        member_id = user_data.get('sub')
        self.person_urn = f"urn:li:person:{member_id}"
        return user_data

    def post_text(self, text):
        """Post text update to LinkedIn"""
        if not self.person_urn:
            self.get_user_info()

        post_data = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        response = requests.post(
            LINKEDIN_SHARE_URL,
            headers=headers,
            json=post_data
        )

        if not response.ok:
            print(f"❌ LinkedIn API Error: {response.status_code}")
            print(f"Response: {response.text}")

        response.raise_for_status()

        return response.json()

def test_posting():
    """Test LinkedIn posting"""
    try:
        poster = LinkedInPoster()
        print("✅ LinkedIn token loaded successfully")

        # Get user info
        user_info = poster.get_user_info()
        print(f"✅ Authenticated as: {user_info.get('name')}")
        print(f"✅ Member URN: {poster.person_urn}")

        # Test post
        test_text = f"🤖 Testing AI Employee auto-posting! Posted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        print(f"\n📝 Posting to LinkedIn: {test_text}")
        result = poster.post_text(test_text)

        print(f"✅ Posted successfully!")
        print(f"Post ID: {result.get('id')}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_posting()

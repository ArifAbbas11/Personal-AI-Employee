"""
LinkedIn API Configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# LinkedIn App Credentials (from Developer Portal)
# Get these from: https://www.linkedin.com/developers/apps
LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID', 'YOUR_CLIENT_ID_HERE')
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET', 'YOUR_CLIENT_SECRET_HERE')

# OAuth URLs
LINKEDIN_AUTHORIZATION_URL = 'https://www.linkedin.com/oauth/v2/authorization'
LINKEDIN_TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
LINKEDIN_REDIRECT_URI = 'http://localhost:8080/callback'

# API URLs
LINKEDIN_API_BASE = 'https://api.linkedin.com/v2'
LINKEDIN_SHARE_URL = f'{LINKEDIN_API_BASE}/ugcPosts'

# Scopes needed
LINKEDIN_SCOPES = ['openid', 'profile', 'w_member_social']

# Token storage
# Check if running in Docker (secrets mounted at /secrets)
if Path('/secrets').exists():
    TOKEN_FILE = Path('/secrets/linkedin_token.json')
else:
    TOKEN_FILE = Path(__file__).parent.parent / 'secrets' / 'linkedin_token.json'

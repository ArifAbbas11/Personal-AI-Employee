"""
Twitter (X) API Configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Twitter API Credentials (from Developer Portal)
# Get these from: https://developer.twitter.com/en/portal/dashboard
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', 'YOUR_API_KEY_HERE')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', 'YOUR_API_SECRET_HERE')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN_HERE')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', 'YOUR_ACCESS_TOKEN_SECRET_HERE')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', 'YOUR_BEARER_TOKEN_HERE')

# API URLs
TWITTER_API_V2_BASE = 'https://api.twitter.com/2'
TWITTER_TWEET_URL = f'{TWITTER_API_V2_BASE}/tweets'

# Token storage
TOKEN_FILE = Path(__file__).parent.parent / 'secrets' / 'twitter_credentials.json'

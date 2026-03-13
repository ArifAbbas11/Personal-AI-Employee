#!/usr/bin/env python3
"""
Twitter (X) Auto-Posting Module
"""

import json
import requests
from pathlib import Path
from datetime import datetime
from requests_oauthlib import OAuth1
from twitter_config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_TWEET_URL
)

class TwitterPoster:
    """Handle Twitter posting"""
    
    def __init__(self):
        self.auth = OAuth1(
            TWITTER_API_KEY,
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_TOKEN_SECRET
        )
    
    def post_tweet(self, text):
        """Post tweet to Twitter"""
        if len(text) > 280:
            print(f"⚠️ Warning: Tweet is {len(text)} characters (max 280)")
            text = text[:277] + "..."
        
        payload = {
            "text": text
        }
        
        try:
            response = requests.post(
                TWITTER_TWEET_URL,
                auth=self.auth,
                json=payload
            )
            
            if not response.ok:
                print(f"❌ Twitter API Error: {response.status_code}")
                print(f"Response: {response.text}")
            
            response.raise_for_status()
            
            result = response.json()
            return result
            
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
            raise
    
    def post_thread(self, tweets):
        """Post a thread of tweets"""
        tweet_ids = []
        previous_tweet_id = None
        
        for i, text in enumerate(tweets):
            print(f"📝 Posting tweet {i+1}/{len(tweets)}")
            
            payload = {"text": text}
            
            # Reply to previous tweet if this is part of a thread
            if previous_tweet_id:
                payload["reply"] = {
                    "in_reply_to_tweet_id": previous_tweet_id
                }
            
            try:
                response = requests.post(
                    TWITTER_TWEET_URL,
                    auth=self.auth,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                tweet_id = result['data']['id']
                tweet_ids.append(tweet_id)
                previous_tweet_id = tweet_id
                
                print(f"✅ Tweet {i+1} posted: {tweet_id}")
                
            except Exception as e:
                print(f"❌ Error posting tweet {i+1}: {e}")
                break
        
        return tweet_ids

def test_posting():
    """Test Twitter posting"""
    try:
        poster = TwitterPoster()
        print("✅ Twitter poster initialized")
        
        # Test tweet
        test_text = f"🤖 Testing AI Employee auto-posting to Twitter! Posted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        print(f"\n📝 Posting to Twitter: {test_text}")
        result = poster.post_tweet(test_text)
        
        print(f"✅ Posted successfully!")
        print(f"Tweet ID: {result['data']['id']}")
        print(f"Tweet text: {result['data']['text']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_posting()

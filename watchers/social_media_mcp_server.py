#!/usr/bin/env python3
"""
Social Media MCP Server - Multi-Platform Content Management
Provides social media posting and management tools for the Personal AI Employee system.
"""

import json
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SocialMediaPost:
    """Represents a social media post."""
    platform: str
    content: str
    media_urls: List[str]
    scheduled_time: Optional[str]
    status: str  # draft, scheduled, posted, failed
    post_id: Optional[str] = None
    error: Optional[str] = None


class SocialMediaMCPServer:
    """MCP Server for social media integration."""

    def __init__(self, config_path: str):
        """Initialize social media connections."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.platforms = {}

        # Initialize platform connectors
        if self.config.get('facebook', {}).get('enabled'):
            self.platforms['facebook'] = FacebookConnector(self.config['facebook'])
        if self.config.get('instagram', {}).get('enabled'):
            self.platforms['instagram'] = InstagramConnector(self.config['instagram'])
        if self.config.get('twitter', {}).get('enabled'):
            self.platforms['twitter'] = TwitterConnector(self.config['twitter'])
        if self.config.get('linkedin', {}).get('enabled'):
            self.platforms['linkedin'] = LinkedInConnector(self.config['linkedin'])

    def _load_config(self) -> Dict[str, Any]:
        """Load social media configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path) as f:
            return json.load(f)

    # Tool 1: Post to Social Media
    def post_to_platform(self, platform: str, content: str,
                        media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Post content to a social media platform.

        Args:
            platform: Platform name (facebook, instagram, twitter, linkedin)
            content: Post content/text
            media_urls: Optional list of media URLs to attach

        Returns:
            Post result with post_id and status
        """
        try:
            if platform not in self.platforms:
                return {
                    'status': 'error',
                    'error': f'Platform {platform} not configured or not enabled'
                }

            connector = self.platforms[platform]
            result = connector.post(content, media_urls or [])

            return {
                'status': 'success',
                'platform': platform,
                'post_id': result.get('id'),
                'url': result.get('url'),
                'posted_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error posting to {platform}: {e}")
            return {
                'status': 'error',
                'platform': platform,
                'error': str(e)
            }

    # Tool 2: Schedule Post
    def schedule_post(self, platform: str, content: str,
                     scheduled_time: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Schedule a post for future publication.

        Args:
            platform: Platform name
            content: Post content
            scheduled_time: ISO format datetime (e.g., "2026-02-28T10:00:00")
            media_urls: Optional media URLs

        Returns:
            Scheduled post details
        """
        try:
            # Validate scheduled time
            scheduled_dt = datetime.fromisoformat(scheduled_time)
            if scheduled_dt <= datetime.now():
                return {
                    'status': 'error',
                    'error': 'Scheduled time must be in the future'
                }

            # Create scheduled post record
            post = SocialMediaPost(
                platform=platform,
                content=content,
                media_urls=media_urls or [],
                scheduled_time=scheduled_time,
                status='scheduled'
            )

            # Save to queue
            queue_path = Path(self.config.get('queue_path', '/tmp/social_media_queue'))
            queue_path.mkdir(exist_ok=True)

            post_file = queue_path / f"{platform}_{scheduled_dt.strftime('%Y%m%d_%H%M%S')}.json"
            with open(post_file, 'w') as f:
                json.dump({
                    'platform': post.platform,
                    'content': post.content,
                    'media_urls': post.media_urls,
                    'scheduled_time': post.scheduled_time,
                    'status': post.status
                }, f, indent=2)

            return {
                'status': 'scheduled',
                'platform': platform,
                'scheduled_time': scheduled_time,
                'queue_file': str(post_file)
            }

        except Exception as e:
            logger.error(f"Error scheduling post: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    # Tool 3: Get Platform Stats
    def get_platform_stats(self, platform: str, days: int = 7) -> Dict[str, Any]:
        """
        Get statistics for a platform.

        Args:
            platform: Platform name
            days: Number of days to look back

        Returns:
            Platform statistics
        """
        try:
            if platform not in self.platforms:
                return {
                    'status': 'error',
                    'error': f'Platform {platform} not configured'
                }

            connector = self.platforms[platform]
            stats = connector.get_stats(days)

            return {
                'status': 'success',
                'platform': platform,
                'period_days': days,
                'stats': stats
            }

        except Exception as e:
            logger.error(f"Error getting stats for {platform}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    # Tool 4: Get Recent Posts
    def get_recent_posts(self, platform: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent posts from a platform.

        Args:
            platform: Platform name
            limit: Maximum number of posts to retrieve

        Returns:
            List of recent posts
        """
        try:
            if platform not in self.platforms:
                return {
                    'status': 'error',
                    'error': f'Platform {platform} not configured'
                }

            connector = self.platforms[platform]
            posts = connector.get_recent_posts(limit)

            return {
                'status': 'success',
                'platform': platform,
                'posts': posts,
                'count': len(posts)
            }

        except Exception as e:
            logger.error(f"Error getting recent posts from {platform}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    # Tool 5: Delete Post
    def delete_post(self, platform: str, post_id: str) -> Dict[str, Any]:
        """
        Delete a post from a platform.

        Args:
            platform: Platform name
            post_id: Post ID to delete

        Returns:
            Deletion result
        """
        try:
            if platform not in self.platforms:
                return {
                    'status': 'error',
                    'error': f'Platform {platform} not configured'
                }

            connector = self.platforms[platform]
            result = connector.delete_post(post_id)

            return {
                'status': 'success',
                'platform': platform,
                'post_id': post_id,
                'deleted': result
            }

        except Exception as e:
            logger.error(f"Error deleting post from {platform}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }


# Platform Connectors

class FacebookConnector:
    """Facebook API connector."""

    def __init__(self, config: Dict[str, Any]):
        self.access_token = config.get('access_token')
        self.page_id = config.get('page_id')
        self.api_version = config.get('api_version', 'v18.0')
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def post(self, content: str, media_urls: List[str]) -> Dict[str, Any]:
        """Post to Facebook."""
        url = f"{self.base_url}/{self.page_id}/feed"

        data = {
            'message': content,
            'access_token': self.access_token
        }

        if media_urls:
            # For simplicity, attach first image
            data['link'] = media_urls[0]

        response = requests.post(url, data=data)
        response.raise_for_status()

        result = response.json()
        return {
            'id': result.get('id'),
            'url': f"https://facebook.com/{result.get('id')}"
        }

    def get_stats(self, days: int) -> Dict[str, Any]:
        """Get Facebook page stats."""
        url = f"{self.base_url}/{self.page_id}/insights"

        params = {
            'metric': 'page_impressions,page_engaged_users,page_post_engagements',
            'period': 'day',
            'access_token': self.access_token
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return {
            'impressions': sum(d.get('values', [{}])[0].get('value', 0) for d in data.get('data', [])),
            'engaged_users': 0,  # Parse from response
            'engagements': 0  # Parse from response
        }

    def get_recent_posts(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent Facebook posts."""
        url = f"{self.base_url}/{self.page_id}/posts"

        params = {
            'limit': limit,
            'fields': 'id,message,created_time,permalink_url',
            'access_token': self.access_token
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return data.get('data', [])

    def delete_post(self, post_id: str) -> bool:
        """Delete a Facebook post."""
        url = f"{self.base_url}/{post_id}"

        params = {'access_token': self.access_token}

        response = requests.delete(url, params=params)
        response.raise_for_status()

        return True


class InstagramConnector:
    """Instagram API connector."""

    def __init__(self, config: Dict[str, Any]):
        self.access_token = config.get('access_token')
        self.account_id = config.get('account_id')
        self.api_version = config.get('api_version', 'v18.0')
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def post(self, content: str, media_urls: List[str]) -> Dict[str, Any]:
        """Post to Instagram."""
        if not media_urls:
            return {'error': 'Instagram requires at least one image'}

        # Create media container
        container_url = f"{self.base_url}/{self.account_id}/media"

        container_data = {
            'image_url': media_urls[0],
            'caption': content,
            'access_token': self.access_token
        }

        container_response = requests.post(container_url, data=container_data)
        container_response.raise_for_status()

        container_id = container_response.json().get('id')

        # Publish media
        publish_url = f"{self.base_url}/{self.account_id}/media_publish"

        publish_data = {
            'creation_id': container_id,
            'access_token': self.access_token
        }

        publish_response = requests.post(publish_url, data=publish_data)
        publish_response.raise_for_status()

        result = publish_response.json()
        return {
            'id': result.get('id'),
            'url': f"https://instagram.com/p/{result.get('id')}"
        }

    def get_stats(self, days: int) -> Dict[str, Any]:
        """Get Instagram stats."""
        url = f"{self.base_url}/{self.account_id}/insights"

        params = {
            'metric': 'impressions,reach,profile_views',
            'period': 'day',
            'access_token': self.access_token
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return {
            'impressions': 0,  # Parse from response
            'reach': 0,
            'profile_views': 0
        }

    def get_recent_posts(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent Instagram posts."""
        url = f"{self.base_url}/{self.account_id}/media"

        params = {
            'limit': limit,
            'fields': 'id,caption,media_type,media_url,permalink,timestamp',
            'access_token': self.access_token
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return data.get('data', [])

    def delete_post(self, post_id: str) -> bool:
        """Delete an Instagram post."""
        url = f"{self.base_url}/{post_id}"

        params = {'access_token': self.access_token}

        response = requests.delete(url, params=params)
        response.raise_for_status()

        return True


class TwitterConnector:
    """Twitter/X API connector."""

    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get('api_key')
        self.api_secret = config.get('api_secret')
        self.access_token = config.get('access_token')
        self.access_secret = config.get('access_secret')
        self.bearer_token = config.get('bearer_token')
        self.base_url = "https://api.twitter.com/2"

    def post(self, content: str, media_urls: List[str]) -> Dict[str, Any]:
        """Post to Twitter."""
        url = f"{self.base_url}/tweets"

        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }

        data = {'text': content}

        # Note: Media upload requires separate endpoint
        # Simplified for now

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        tweet_id = result.get('data', {}).get('id')

        return {
            'id': tweet_id,
            'url': f"https://twitter.com/i/web/status/{tweet_id}"
        }

    def get_stats(self, days: int) -> Dict[str, Any]:
        """Get Twitter stats."""
        # Simplified - would need Twitter API v2 metrics
        return {
            'tweets': 0,
            'impressions': 0,
            'engagements': 0
        }

    def get_recent_posts(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent tweets."""
        # Would need user ID and proper endpoint
        return []

    def delete_post(self, post_id: str) -> bool:
        """Delete a tweet."""
        url = f"{self.base_url}/tweets/{post_id}"

        headers = {
            'Authorization': f'Bearer {self.bearer_token}'
        }

        response = requests.delete(url, headers=headers)
        response.raise_for_status()

        return True


class LinkedInConnector:
    """LinkedIn API connector."""

    def __init__(self, config: Dict[str, Any]):
        self.access_token = config.get('access_token')
        self.person_urn = config.get('person_urn')
        self.base_url = "https://api.linkedin.com/v2"

    def post(self, content: str, media_urls: List[str]) -> Dict[str, Any]:
        """Post to LinkedIn."""
        url = f"{self.base_url}/ugcPosts"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        data = {
            'author': self.person_urn,
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': content
                    },
                    'shareMediaCategory': 'NONE'
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        return {
            'id': result.get('id'),
            'url': f"https://linkedin.com/feed/update/{result.get('id')}"
        }

    def get_stats(self, days: int) -> Dict[str, Any]:
        """Get LinkedIn stats."""
        # Simplified - would need proper analytics endpoint
        return {
            'posts': 0,
            'impressions': 0,
            'engagements': 0
        }

    def get_recent_posts(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent LinkedIn posts."""
        # Would need proper endpoint
        return []

    def delete_post(self, post_id: str) -> bool:
        """Delete a LinkedIn post."""
        url = f"{self.base_url}/ugcPosts/{post_id}"

        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        response = requests.delete(url, headers=headers)
        response.raise_for_status()

        return True


def handle_mcp_request(server: SocialMediaMCPServer, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP tool request."""
    tool = request.get('tool')
    params = request.get('params', {})

    if tool == 'post_to_platform':
        return server.post_to_platform(
            params['platform'],
            params['content'],
            params.get('media_urls')
        )

    elif tool == 'schedule_post':
        return server.schedule_post(
            params['platform'],
            params['content'],
            params['scheduled_time'],
            params.get('media_urls')
        )

    elif tool == 'get_platform_stats':
        return server.get_platform_stats(
            params['platform'],
            params.get('days', 7)
        )

    elif tool == 'get_recent_posts':
        return server.get_recent_posts(
            params['platform'],
            params.get('limit', 10)
        )

    elif tool == 'delete_post':
        return server.delete_post(
            params['platform'],
            params['post_id']
        )

    else:
        return {'error': f'Unknown tool: {tool}'}


def main():
    """Main MCP server loop."""
    config_path = Path(__file__).parent.parent / 'AI_Employee_Vault' / 'Config' / 'social_media_config.json'

    if not config_path.exists():
        print(json.dumps({
            'error': 'Social media configuration not found',
            'message': 'Create AI_Employee_Vault/Config/social_media_config.json with platform credentials'
        }))
        sys.exit(1)

    try:
        server = SocialMediaMCPServer(str(config_path))
    except Exception as e:
        print(json.dumps({'error': f'Failed to initialize social media server: {e}'}))
        sys.exit(1)

    logger.info("Social Media MCP Server started")

    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = handle_mcp_request(server, request)
            print(json.dumps(response))
            sys.stdout.flush()
        except json.JSONDecodeError:
            print(json.dumps({'error': 'Invalid JSON request'}))
        except Exception as e:
            print(json.dumps({'error': str(e)}))


if __name__ == '__main__':
    main()

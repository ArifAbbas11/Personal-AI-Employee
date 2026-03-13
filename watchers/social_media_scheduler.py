#!/usr/bin/env python3
"""
Social Media Content Scheduler
Processes scheduled posts from the queue and publishes them at the right time.
"""

import json
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SocialMediaScheduler:
    """Manages scheduled social media posts."""

    def __init__(self, vault_path: str, config_path: str):
        """Initialize scheduler."""
        self.vault = Path(vault_path)
        self.config_path = Path(config_path)
        self.queue_path = self._get_queue_path()
        self.queue_path.mkdir(exist_ok=True)

    def _get_queue_path(self) -> Path:
        """Get queue path from config."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                config = json.load(f)
                return Path(config.get('queue_path', '/tmp/social_media_queue'))
        return Path('/tmp/social_media_queue')

    def get_pending_posts(self) -> List[Dict[str, Any]]:
        """Get all pending scheduled posts."""
        pending = []

        for post_file in self.queue_path.glob('*.json'):
            try:
                with open(post_file) as f:
                    post_data = json.load(f)

                if post_data.get('status') == 'scheduled':
                    post_data['file'] = str(post_file)
                    pending.append(post_data)

            except Exception as e:
                logger.error(f"Error reading post file {post_file}: {e}")

        # Sort by scheduled time
        pending.sort(key=lambda x: x.get('scheduled_time', ''))
        return pending

    def get_due_posts(self) -> List[Dict[str, Any]]:
        """Get posts that are due to be published."""
        now = datetime.now()
        pending = self.get_pending_posts()
        due = []

        for post in pending:
            scheduled_time = datetime.fromisoformat(post['scheduled_time'])
            if scheduled_time <= now:
                due.append(post)

        return due

    def publish_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Publish a scheduled post."""
        try:
            # Import MCP server
            sys.path.insert(0, str(Path(__file__).parent))
            from social_media_mcp_server import SocialMediaMCPServer

            # Initialize MCP server
            server = SocialMediaMCPServer(str(self.config_path))

            # Post to platform
            result = server.post_to_platform(
                post['platform'],
                post['content'],
                post.get('media_urls')
            )

            if result.get('status') == 'success':
                # Update post status
                post['status'] = 'posted'
                post['posted_at'] = datetime.now().isoformat()
                post['post_id'] = result.get('post_id')
                post['url'] = result.get('url')

                # Save updated post
                self._save_post(post)

                # Log success
                logger.info(f"✅ Published post to {post['platform']}: {result.get('url')}")

                return {
                    'status': 'success',
                    'platform': post['platform'],
                    'post_id': result.get('post_id'),
                    'url': result.get('url')
                }
            else:
                # Mark as failed
                post['status'] = 'failed'
                post['error'] = result.get('error')
                self._save_post(post)

                logger.error(f"❌ Failed to publish post to {post['platform']}: {result.get('error')}")

                return {
                    'status': 'failed',
                    'error': result.get('error')
                }

        except Exception as e:
            logger.error(f"Error publishing post: {e}")
            post['status'] = 'failed'
            post['error'] = str(e)
            self._save_post(post)

            return {
                'status': 'failed',
                'error': str(e)
            }

    def _save_post(self, post: Dict[str, Any]):
        """Save post data to file."""
        post_file = Path(post['file'])
        post_data = {k: v for k, v in post.items() if k != 'file'}

        with open(post_file, 'w') as f:
            json.dump(post_data, f, indent=2)

    def process_queue(self, dry_run: bool = False) -> Dict[str, Any]:
        """Process all due posts in the queue."""
        due_posts = self.get_due_posts()

        if not due_posts:
            logger.info("No posts due for publication")
            return {
                'processed': 0,
                'successful': 0,
                'failed': 0
            }

        logger.info(f"Found {len(due_posts)} post(s) due for publication")

        successful = 0
        failed = 0

        for post in due_posts:
            if dry_run:
                logger.info(f"[DRY RUN] Would publish to {post['platform']}: {post['content'][:50]}...")
                successful += 1
            else:
                result = self.publish_post(post)
                if result.get('status') == 'success':
                    successful += 1
                else:
                    failed += 1

        return {
            'processed': len(due_posts),
            'successful': successful,
            'failed': failed
        }

    def run_daemon(self, interval_seconds: int = 60):
        """Run scheduler as a daemon."""
        logger.info(f"Starting scheduler daemon (checking every {interval_seconds}s)")

        try:
            while True:
                result = self.process_queue()

                if result['processed'] > 0:
                    logger.info(f"Processed {result['processed']} post(s): "
                              f"{result['successful']} successful, {result['failed']} failed")

                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            logger.info("Scheduler daemon stopped")

    def list_queue(self) -> List[Dict[str, Any]]:
        """List all posts in queue."""
        return self.get_pending_posts()

    def clear_completed(self):
        """Remove completed posts from queue."""
        removed = 0

        for post_file in self.queue_path.glob('*.json'):
            try:
                with open(post_file) as f:
                    post_data = json.load(f)

                if post_data.get('status') in ['posted', 'failed']:
                    # Move to archive
                    archive_path = self.vault / 'Logs' / 'social_media_archive'
                    archive_path.mkdir(exist_ok=True)

                    archive_file = archive_path / post_file.name
                    post_file.rename(archive_file)
                    removed += 1

            except Exception as e:
                logger.error(f"Error archiving post file {post_file}: {e}")

        logger.info(f"Archived {removed} completed post(s)")
        return removed


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Social Media Content Scheduler')
    parser.add_argument(
        '--vault',
        default='/mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--config',
        default='/mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault/Config/social_media_config.json',
        help='Path to social media config'
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run as daemon'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds (daemon mode)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List pending posts'
    )
    parser.add_argument(
        '--process',
        action='store_true',
        help='Process due posts once'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run (don\'t actually post)'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear completed posts'
    )

    args = parser.parse_args()

    scheduler = SocialMediaScheduler(args.vault, args.config)

    if args.list:
        posts = scheduler.list_queue()
        print(f"\n📋 Pending Posts: {len(posts)}\n")
        for i, post in enumerate(posts, 1):
            print(f"{i}. [{post['platform']}] {post['content'][:50]}...")
            print(f"   Scheduled: {post['scheduled_time']}")
            print(f"   Status: {post['status']}")
            print()

    elif args.clear:
        removed = scheduler.clear_completed()
        print(f"✅ Archived {removed} completed post(s)")

    elif args.daemon:
        scheduler.run_daemon(args.interval)

    elif args.process:
        result = scheduler.process_queue(args.dry_run)
        print(f"\n✅ Processed {result['processed']} post(s)")
        print(f"   Successful: {result['successful']}")
        print(f"   Failed: {result['failed']}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()

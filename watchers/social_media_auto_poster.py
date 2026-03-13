#!/usr/bin/env python3
"""
Social Media Auto-Poster
Monitors Approved folders and posts to LinkedIn/Twitter automatically
"""

import os
import re
import time
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SocialMediaAutoPoster:
    """Automatically post approved social media content"""

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize Social Media Auto-Poster.

        Args:
            vault_path: Path to the vault
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.approved_linkedin_dir = self.vault_path / 'Approved' / 'linkedin'
        self.approved_twitter_dir = self.vault_path / 'Approved' / 'twitter'
        self.done_linkedin_dir = self.vault_path / 'Done' / 'linkedin'
        self.done_twitter_dir = self.vault_path / 'Done' / 'twitter'
        self.check_interval = check_interval

        # Create directories if they don't exist
        self.approved_linkedin_dir.mkdir(parents=True, exist_ok=True)
        self.approved_twitter_dir.mkdir(parents=True, exist_ok=True)
        self.done_linkedin_dir.mkdir(parents=True, exist_ok=True)
        self.done_twitter_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Social Media Auto-Poster initialized")

    def parse_post_file(self, file_path: Path) -> dict:
        """Parse post file and extract content"""
        try:
            content = file_path.read_text()

            # Extract post content between ## Post Content and ---
            post_content = ""
            lines = content.split('\n')
            in_post_content = False

            for line in lines:
                if line.strip() == '## Post Content':
                    in_post_content = True
                    continue
                elif in_post_content and line.strip() == '---':
                    break
                elif in_post_content and line.strip():
                    post_content += line + '\n'

            return {
                'content': post_content.strip(),
                'original_file': content
            }

        except Exception as e:
            logger.error(f"Error parsing {file_path.name}: {e}")
            return None

    def post_to_linkedin(self, content: str) -> dict:
        """Post content to LinkedIn"""
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent))
            from linkedin_poster import LinkedInPoster

            poster = LinkedInPoster()
            result = poster.post_text(content)

            return {
                'success': True,
                'post_id': result.get('id', 'unknown'),
                'platform': 'LinkedIn'
            }

        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'platform': 'LinkedIn'
            }

    def post_to_twitter(self, content: str) -> dict:
        """Post content to Twitter"""
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent))
            from twitter_poster import TwitterPoster

            poster = TwitterPoster()
            result = poster.post_tweet(content)

            return {
                'success': True,
                'post_id': result.get('id', 'unknown'),
                'platform': 'Twitter'
            }

        except Exception as e:
            logger.error(f"Error posting to Twitter: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'platform': 'Twitter'
            }

    def update_post_status(self, original_content: str, post_result: dict) -> str:
        """Update post file with sent status"""
        # Replace status line
        updated_content = original_content.replace(
            '**Status:** Pending Approval',
            f'**Status:** Posted to {post_result["platform"]}'
        )

        # Add posted timestamp
        posted_line = f'\n**Posted:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'

        # Insert after Status line
        lines = updated_content.split('\n')
        for i, line in enumerate(lines):
            if '**Status:**' in line:
                lines.insert(i + 1, posted_line.strip())
                break

        return '\n'.join(lines)

    def process_approved_posts(self):
        """Process all approved posts"""
        try:
            # Process LinkedIn posts
            linkedin_files = list(self.approved_linkedin_dir.glob('*.md'))
            for file in linkedin_files:
                try:
                    logger.info(f"Processing LinkedIn post: {file.name}")

                    # Parse post content
                    post_data = self.parse_post_file(file)
                    if not post_data or not post_data.get('content'):
                        logger.warning(f"Could not parse {file.name}")
                        continue

                    # Post to LinkedIn
                    result = self.post_to_linkedin(post_data['content'])

                    if result['success']:
                        # Update status
                        updated_content = self.update_post_status(
                            post_data['original_file'],
                            result
                        )

                        # Move to Done folder
                        done_file = self.done_linkedin_dir / file.name
                        done_file.write_text(updated_content)
                        file.unlink()

                        logger.info(f"✅ Posted to LinkedIn: {file.name}")
                        print(f"✅ Posted to LinkedIn successfully!")
                    else:
                        logger.error(f"❌ Failed to post {file.name}: {result.get('error')}")
                        print(f"❌ Failed to post to LinkedIn: {result.get('error')}")

                except Exception as e:
                    logger.error(f"Error processing LinkedIn post {file.name}: {e}", exc_info=True)

            # Process Twitter posts
            twitter_files = list(self.approved_twitter_dir.glob('*.md'))
            for file in twitter_files:
                try:
                    logger.info(f"Processing Twitter post: {file.name}")

                    # Parse post content
                    post_data = self.parse_post_file(file)
                    if not post_data or not post_data.get('content'):
                        logger.warning(f"Could not parse {file.name}")
                        continue

                    # Post to Twitter
                    result = self.post_to_twitter(post_data['content'])

                    if result['success']:
                        # Update status
                        updated_content = self.update_post_status(
                            post_data['original_file'],
                            result
                        )

                        # Move to Done folder
                        done_file = self.done_twitter_dir / file.name
                        done_file.write_text(updated_content)
                        file.unlink()

                        logger.info(f"✅ Posted to Twitter: {file.name}")
                        print(f"✅ Posted to Twitter successfully!")
                    else:
                        logger.error(f"❌ Failed to post {file.name}: {result.get('error')}")
                        print(f"❌ Failed to post to Twitter: {result.get('error')}")

                except Exception as e:
                    logger.error(f"Error processing Twitter post {file.name}: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Error in process_approved_posts: {e}", exc_info=True)

    def run(self):
        """Main loop - continuously process approved posts"""
        logger.info(f"Starting Social Media Auto-Poster")
        logger.info(f"Monitoring: Approved/linkedin/ and Approved/twitter/")
        logger.info(f"Check interval: {self.check_interval} seconds")

        while True:
            try:
                self.process_approved_posts()
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info("Social Media Auto-Poster stopped by user")
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
        print("Usage: python social_media_auto_poster.py <vault_path>")
        print("Example: python social_media_auto_poster.py ../AI_Employee_Vault")
        sys.exit(1)

    vault_path = sys.argv[1]

    poster = SocialMediaAutoPoster(vault_path)
    poster.run()

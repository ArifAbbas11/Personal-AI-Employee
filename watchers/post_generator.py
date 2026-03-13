#!/usr/bin/env python3
"""
Social Media Post Generator
Monitors Post_Ideas folder and generates draft posts
"""

import os
import re
import time
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PostGenerator:
    """Generate social media posts from topic ideas"""

    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize Post Generator.

        Args:
            vault_path: Path to the vault
            check_interval: Seconds between checks (default: 30)
        """
        self.vault_path = Path(vault_path)
        self.post_ideas_dir = self.vault_path / 'Post_Ideas'
        self.pending_linkedin_dir = self.vault_path / 'Pending_Approval' / 'linkedin'
        self.pending_twitter_dir = self.vault_path / 'Pending_Approval' / 'twitter'
        self.check_interval = check_interval

        # Create directories if they don't exist
        self.post_ideas_dir.mkdir(parents=True, exist_ok=True)
        self.pending_linkedin_dir.mkdir(parents=True, exist_ok=True)
        self.pending_twitter_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Post Generator initialized")

    def parse_topic_file(self, file_path: Path) -> dict:
        """Parse topic file"""
        try:
            content = file_path.read_text()

            # Extract metadata
            platform = 'linkedin'  # default
            topic = ''
            details = []

            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '**Platform:**' in line:
                    platform = line.split('**Platform:**')[1].strip().lower()
                elif '**Topic:**' in line:
                    topic = line.split('**Topic:**')[1].strip()
                elif line.strip().startswith('-'):
                    details.append(line.strip()[1:].strip())

            return {
                'platform': platform,
                'topic': topic,
                'details': details
            }

        except Exception as e:
            logger.error(f"Error parsing {file_path.name}: {e}")
            return None

    def generate_linkedin_post(self, topic: str, details: list) -> str:
        """Generate LinkedIn post content"""

        # Create engaging LinkedIn post
        post_parts = []

        # Opening hook
        if 'automation' in topic.lower():
            post_parts.append("🤖 The future of work is here, and it's automated.")
        elif 'ai' in topic.lower():
            post_parts.append("🚀 AI is transforming how we work.")
        elif 'productivity' in topic.lower():
            post_parts.append("⚡ Want to 10x your productivity?")
        else:
            post_parts.append(f"💡 Let's talk about {topic}.")

        post_parts.append("")

        # Main content based on topic
        if 'small business' in topic.lower() or 'business' in topic.lower():
            post_parts.append("Small businesses are discovering that AI automation isn't just for enterprise companies anymore.")
            post_parts.append("")
            post_parts.append("Here's what's possible today:")
            post_parts.append("• Automated email responses that sound human")
            post_parts.append("• Social media posts scheduled and published automatically")
            post_parts.append("• Task routing and management without manual intervention")
            post_parts.append("• Daily summaries and analytics delivered to your inbox")
            post_parts.append("")
            post_parts.append("The best part? You stay in control. Review and approve everything before it goes out.")
        elif 'email' in topic.lower():
            post_parts.append("Imagine never missing an important email again.")
            post_parts.append("")
            post_parts.append("AI-powered email automation can:")
            post_parts.append("• Detect and prioritize urgent messages")
            post_parts.append("• Generate contextual draft responses")
            post_parts.append("• Send approved replies automatically")
            post_parts.append("• Archive and organize everything")
            post_parts.append("")
            post_parts.append("You review and approve. The AI handles the rest.")
        elif 'social media' in topic.lower():
            post_parts.append("Consistent social media presence without the daily grind.")
            post_parts.append("")
            post_parts.append("AI can help you:")
            post_parts.append("• Generate engaging post ideas")
            post_parts.append("• Write platform-optimized content")
            post_parts.append("• Schedule posts at optimal times")
            post_parts.append("• Maintain your authentic voice")
            post_parts.append("")
            post_parts.append("You approve the content. AI handles the posting.")
        else:
            # Generic post about the topic
            post_parts.append(f"Here's what I've learned about {topic}:")
            post_parts.append("")
            for detail in details[:3]:  # Use up to 3 details
                post_parts.append(f"• {detail}")
            post_parts.append("")
            post_parts.append("The key is finding the right balance between automation and human oversight.")

        post_parts.append("")

        # Call to action
        post_parts.append("What's your experience with AI automation? Drop a comment below! 👇")

        # Hashtags
        hashtags = []
        if 'ai' in topic.lower():
            hashtags.extend(['#AI', '#ArtificialIntelligence'])
        if 'automation' in topic.lower():
            hashtags.extend(['#Automation', '#WorkflowAutomation'])
        if 'business' in topic.lower():
            hashtags.extend(['#SmallBusiness', '#Entrepreneurship'])
        if 'productivity' in topic.lower():
            hashtags.extend(['#Productivity', '#Efficiency'])

        # Add default hashtags if none found
        if not hashtags:
            hashtags = ['#Technology', '#Innovation', '#FutureOfWork']

        post_parts.append("")
        post_parts.append(' '.join(hashtags[:5]))  # Max 5 hashtags

        return '\n'.join(post_parts)

    def generate_twitter_post(self, topic: str, details: list) -> str:
        """Generate Twitter post content (max 280 characters)"""

        # Create concise tweet
        if 'automation' in topic.lower():
            tweet = "🤖 AI automation isn't just for big companies anymore. Small businesses can now automate emails, social media, and task management. You stay in control, AI handles the repetitive work. #AI #Automation"
        elif 'email' in topic.lower():
            tweet = "📧 Never miss an important email again. AI detects priorities, drafts responses, and sends approved replies automatically. You review, AI executes. #EmailAutomation #Productivity"
        elif 'social media' in topic.lower():
            tweet = "📱 Consistent social media without the daily grind. AI generates posts, you approve them, system publishes automatically. Maintain your voice, save your time. #SocialMedia #AI"
        elif 'productivity' in topic.lower():
            tweet = "⚡ 10x your productivity with AI automation. Automate the repetitive, focus on what matters. Human oversight + AI execution = perfect balance. #Productivity #AI"
        else:
            # Generic tweet
            tweet = f"💡 {topic}: The future is automated, but human-guided. AI handles execution, you maintain control. #AI #Automation #FutureOfWork"

        # Ensure it's under 280 characters
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."

        return tweet

    def create_post_file(self, topic_data: dict, post_content: str):
        """Create post file in Pending_Approval folder"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            platform = topic_data['platform']

            if platform == 'linkedin':
                filename = f"LINKEDIN_POST_{timestamp}.md"
                filepath = self.pending_linkedin_dir / filename
            elif platform == 'twitter':
                filename = f"TWITTER_POST_{timestamp}.md"
                filepath = self.pending_twitter_dir / filename
            else:
                logger.warning(f"Unknown platform: {platform}")
                return None

            content = f"""# {platform.title()} Post

**Status:** Pending Approval
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Topic:** {topic_data['topic']}

---

## Post Content

{post_content}

---

## Instructions

1. **Review** the post content above
2. **Edit** if needed (modify the text under "Post Content")
3. **When satisfied**, move this file to: `AI_Employee_Vault/Approved/{platform}/`
4. The system will automatically post it

**To approve:**
```bash
mv AI_Employee_Vault/Pending_Approval/{platform}/{filename} \\
   AI_Employee_Vault/Approved/{platform}/
```

**To reject:** Delete this file
"""

            filepath.write_text(content)
            logger.info(f"Created post draft: {filename}")
            return filepath

        except Exception as e:
            logger.error(f"Error creating post file: {e}")
            return None

    def process_topic_files(self):
        """Process all topic files"""
        try:
            topic_files = list(self.post_ideas_dir.glob('*.md'))

            # Filter out example file
            topic_files = [f for f in topic_files if 'EXAMPLE' not in f.name.upper()]

            if not topic_files:
                logger.debug("No topic files to process")
                return

            logger.info(f"Processing {len(topic_files)} topic file(s)")

            for file in topic_files:
                try:
                    # Parse topic data
                    topic_data = self.parse_topic_file(file)
                    if not topic_data or not topic_data.get('topic'):
                        logger.warning(f"Could not parse {file.name}")
                        continue

                    # Generate post content based on platform
                    if topic_data['platform'] == 'linkedin':
                        post_content = self.generate_linkedin_post(
                            topic_data['topic'],
                            topic_data['details']
                        )
                    elif topic_data['platform'] == 'twitter':
                        post_content = self.generate_twitter_post(
                            topic_data['topic'],
                            topic_data['details']
                        )
                    else:
                        logger.warning(f"Unknown platform: {topic_data['platform']}")
                        continue

                    # Create post file
                    post_file = self.create_post_file(topic_data, post_content)

                    if post_file:
                        # Delete the original topic file
                        file.unlink()
                        logger.info(f"Processed {file.name} → {post_file.name}")

                except Exception as e:
                    logger.error(f"Error processing {file.name}: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Error in process_topic_files: {e}", exc_info=True)

    def run(self):
        """Main loop - continuously process topic files"""
        logger.info(f"Starting Post Generator")
        logger.info(f"Monitoring: {self.post_ideas_dir}")
        logger.info(f"Output to: Pending_Approval/linkedin/ and Pending_Approval/twitter/")
        logger.info(f"Check interval: {self.check_interval} seconds")

        while True:
            try:
                self.process_topic_files()
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info("Post Generator stopped by user")
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
        print("Usage: python post_generator.py <vault_path>")
        print("Example: python post_generator.py ../AI_Employee_Vault")
        sys.exit(1)

    vault_path = sys.argv[1]

    generator = PostGenerator(vault_path)
    generator.run()

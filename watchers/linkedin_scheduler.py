"""
LinkedIn Auto-Posting Scheduler
Posts to LinkedIn on schedule with approval workflow
"""

import time
import schedule
from datetime import datetime
from pathlib import Path
import sys
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from watchers.linkedin_poster import LinkedInPoster
from workflows.linkedin_content_generator import LinkedInContentGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LinkedInScheduler:
    """Schedule LinkedIn posts with approval workflow"""

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.poster = None  # Initialize on first use
        self.generator = LinkedInContentGenerator(vault_path)

        # Directories
        self.pending_approval_dir = self.vault_path / 'Pending_Approval' / 'linkedin'
        self.approved_dir = self.vault_path / 'Approved'
        self.done_dir = self.vault_path / 'Done'
        self.rejected_dir = self.vault_path / 'Rejected'

        # Create directories
        for directory in [self.pending_approval_dir, self.approved_dir,
                         self.done_dir, self.rejected_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def initialize_poster(self):
        """Initialize LinkedIn poster (lazy loading)"""
        if self.poster is None:
            try:
                self.poster = LinkedInPoster()
                logger.info("✅ LinkedIn poster initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize LinkedIn poster: {e}")
                logger.error("Run 'python watchers/linkedin_auth.py' first")
                return False
        return True

    def create_draft_post(self):
        """Create draft post for approval"""
        try:
            content = self.generator.generate_business_update()

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'LINKEDIN_POST_{timestamp}.md'
            filepath = self.pending_approval_dir / filename

            draft_content = f"""---
type: linkedin_post
created: {datetime.now().isoformat()}
status: pending_approval
---

# LinkedIn Post Draft

{content}

---

## Instructions

**To approve and post:**
1. Review the content above
2. Edit if needed (keep it under 3000 characters)
3. Move this file to `/Approved/` folder

**To reject:**
1. Move this file to `/Rejected/` folder

**Note:** The scheduler checks for approved posts every 5 minutes.
"""

            filepath.write_text(draft_content)
            logger.info(f"✅ Draft created: {filepath.name}")
            return filepath

        except Exception as e:
            logger.error(f"❌ Error creating draft: {e}")
            return None

    def check_approved_posts(self):
        """Check for approved posts and publish them"""
        approved_posts = list(self.approved_dir.glob('LINKEDIN_POST_*.md'))

        if not approved_posts:
            return

        logger.info(f"📋 Found {len(approved_posts)} approved post(s)")

        for file in approved_posts:
            try:
                content = file.read_text()

                # Extract post content
                lines = content.split('\n')
                post_lines = []
                in_post = False

                for line in lines:
                    if line.strip() == '# LinkedIn Post Draft':
                        in_post = True
                        continue
                    if line.strip() == '---' and in_post:
                        break
                    if in_post and line.strip():
                        post_lines.append(line)

                post_text = '\n'.join(post_lines).strip()

                if not post_text:
                    logger.warning(f"⚠️ Empty post content in {file.name}")
                    continue

                # Initialize poster if needed
                if not self.initialize_poster():
                    logger.error("❌ Cannot post without LinkedIn authentication")
                    return

                # Post to LinkedIn
                logger.info(f"📤 Posting to LinkedIn: {post_text[:50]}...")
                result = self.poster.post_text(post_text)

                post_id = result.get('id', 'unknown')
                logger.info(f"✅ Posted successfully! Post ID: {post_id}")

                # Move to Done with metadata
                done_file = self.done_dir / file.name
                done_content = f"""---
type: linkedin_post
created: {datetime.now().isoformat()}
status: posted
post_id: {post_id}
---

# Posted to LinkedIn

{post_text}

---

Posted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Post ID: {post_id}
"""
                done_file.write_text(done_content)
                file.unlink()  # Delete from Approved

                logger.info(f"✅ Moved to Done: {done_file.name}")

            except Exception as e:
                logger.error(f"❌ Error posting {file.name}: {e}")
                # Move to Rejected on error
                rejected_file = self.rejected_dir / file.name
                file.rename(rejected_file)
                logger.info(f"⚠️ Moved to Rejected: {rejected_file.name}")

    def run_scheduler(self):
        """Run the scheduler"""
        logger.info("🚀 LinkedIn Scheduler Started")
        logger.info(f"📁 Vault: {self.vault_path}")
        logger.info(f"📝 Drafts: {self.pending_approval_dir}")
        logger.info(f"✅ Approved: {self.approved_dir}")
        logger.info("")

        # Schedule draft creation (daily at 9 AM)
        schedule.every().day.at("09:00").do(self.create_draft_post)

        # Check for approved posts every 5 minutes
        schedule.every(5).minutes.do(self.check_approved_posts)

        logger.info("📅 Schedule:")
        logger.info("  - Create draft: Daily at 9:00 AM")
        logger.info("  - Check approved: Every 5 minutes")
        logger.info("")

        # Create initial draft for testing
        logger.info("🧪 Creating initial test draft...")
        self.create_draft_post()
        logger.info("")
        logger.info("✅ Scheduler running. Press Ctrl+C to stop.")
        logger.info("")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("\n🛑 Scheduler stopped")

if __name__ == '__main__':
    import sys

    vault_path = sys.argv[1] if len(sys.argv) > 1 else '../AI_Employee_Vault'
    scheduler = LinkedInScheduler(vault_path)
    scheduler.run_scheduler()

"""Scheduler - Automated task scheduling for AI Employee."""
import schedule
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime


class AIEmployeeScheduler:
    """Scheduler for automated AI Employee tasks."""

    def __init__(self, vault_path: str):
        """
        Initialize scheduler.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for scheduler."""
        logger = logging.getLogger('AIEmployeeScheduler')
        logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        log_dir = self.vault_path / 'Logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'Scheduler.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    def weekly_ceo_briefing(self):
        """Generate weekly CEO briefing."""
        self.logger.info("Running weekly CEO briefing task...")
        try:
            result = subprocess.run(
                ['python', 'watchers/simple_ceo_briefing.py', '--vault', str(self.vault_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                self.logger.info("✅ Weekly CEO briefing generated successfully")
            else:
                self.logger.error(f"❌ CEO briefing failed: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Error generating CEO briefing: {e}")

    def daily_briefing(self):
        """Generate daily morning briefing."""
        self.logger.info("Running daily briefing task...")

        try:
            # Create briefing request file
            briefing_file = self.vault_path / 'Needs_Action' / f'BRIEFING_{datetime.now().strftime("%Y%m%d")}.md'

            content = f'''---
type: scheduled_task
task: daily_briefing
created: {datetime.now().isoformat()}
priority: high
status: pending
---

## Daily Morning Briefing

Generate a comprehensive morning briefing covering:

### Pending Actions
- Review all files in Needs_Action/
- Summarize urgent items
- List items awaiting approval

### Yesterday's Activity
- Review completed tasks from Done/
- Summarize key accomplishments
- Note any issues or delays

### Today's Priorities
- Based on Business_Goals.md
- Upcoming deadlines
- Scheduled meetings or calls

### Financial Overview
- Current expenses vs budget
- Outstanding invoices
- Recent transactions

### Communications
- Unread emails (if Gmail watcher running)
- Pending WhatsApp messages
- LinkedIn engagement

## Output

Create a briefing document in Plans/ folder with today's date.
'''

            briefing_file.write_text(content)
            self.logger.info(f"Created daily briefing request: {briefing_file.name}")

        except Exception as e:
            self.logger.error(f"Error creating daily briefing: {e}")

    def weekly_review(self):
        """Generate weekly business review."""
        self.logger.info("Running weekly review task...")

        try:
            # Create weekly review request file
            review_file = self.vault_path / 'Needs_Action' / f'WEEKLY_REVIEW_{datetime.now().strftime("%Y%m%d")}.md'

            content = f'''---
type: scheduled_task
task: weekly_review
created: {datetime.now().isoformat()}
priority: high
status: pending
---

## Weekly Business Review

Generate a comprehensive weekly review covering:

### Revenue & Expenses
- Compare against Business_Goals.md targets
- Analyze spending patterns
- Identify cost optimization opportunities

### Task Completion
- Tasks completed this week
- Task completion rate
- Bottlenecks identified

### Communications
- Emails processed
- WhatsApp messages handled
- LinkedIn posts published

### Client Activity
- New inquiries
- Active projects
- Client satisfaction

### Goals Progress
- Progress toward Q1 objectives
- Milestones achieved
- Adjustments needed

### Next Week Planning
- Priorities for upcoming week
- Scheduled activities
- Proactive actions

## Output

Create a comprehensive weekly review document in Plans/ folder.
'''

            review_file.write_text(content)
            self.logger.info(f"Created weekly review request: {review_file.name}")

        except Exception as e:
            self.logger.error(f"Error creating weekly review: {e}")

    def linkedin_post_generation(self):
        """Generate LinkedIn post ideas for the week."""
        self.logger.info("Running LinkedIn post generation task...")

        try:
            # Create LinkedIn post request file
            post_file = self.vault_path / 'Needs_Action' / f'LINKEDIN_POSTS_{datetime.now().strftime("%Y%m%d")}.md'

            content = f'''---
type: scheduled_task
task: linkedin_posts
created: {datetime.now().isoformat()}
priority: medium
status: pending
---

## Weekly LinkedIn Post Generation

Generate 3-5 LinkedIn post drafts for this week based on:

### Content Sources
- Business_Goals.md objectives
- Recent accomplishments from Done/
- Industry trends and insights
- Tips and best practices

### Post Requirements
- Professional yet personable tone
- Value-driven content
- Engaging and discussion-worthy
- 150-300 words each
- 3-5 relevant hashtags

### Post Types to Include
1. Business update or milestone
2. Industry insight or trend
3. Tips or best practices
4. Thought leadership piece
5. Engagement question

## Output

Create post drafts in Plans/LinkedIn_Posts/ folder with approval requests.
'''

            post_file.write_text(content)
            self.logger.info(f"Created LinkedIn post generation request: {post_file.name}")

        except Exception as e:
            self.logger.error(f"Error creating LinkedIn post request: {e}")

    def subscription_audit(self):
        """Monthly subscription audit."""
        self.logger.info("Running monthly subscription audit...")

        try:
            # Create audit request file
            audit_file = self.vault_path / 'Needs_Action' / f'SUBSCRIPTION_AUDIT_{datetime.now().strftime("%Y%m%d")}.md'

            content = f'''---
type: scheduled_task
task: subscription_audit
created: {datetime.now().isoformat()}
priority: medium
status: pending
---

## Monthly Subscription Audit

Review all subscriptions and recurring expenses:

### Audit Criteria (from Business_Goals.md)
- No login in 30 days → Flag for cancellation
- Cost increased > 20% → Review necessity
- Duplicate functionality → Consolidate
- Total monthly subscriptions > $300 → Reduce

### Review Process
1. List all current subscriptions
2. Check last usage date
3. Evaluate ROI and necessity
4. Identify duplicates
5. Calculate total monthly cost

### Recommendations
- Subscriptions to cancel
- Subscriptions to downgrade
- Subscriptions to keep
- Potential savings

## Output

Create subscription audit report in Plans/ folder with recommendations.
'''

            audit_file.write_text(content)
            self.logger.info(f"Created subscription audit request: {audit_file.name}")

        except Exception as e:
            self.logger.error(f"Error creating subscription audit: {e}")

    def log_cleanup(self):
        """Clean up old log files."""
        self.logger.info("Running log cleanup task...")

        try:
            log_dir = self.vault_path / 'Logs'
            if not log_dir.exists():
                return

            # Keep logs for 90 days
            cutoff_date = datetime.now().timestamp() - (90 * 24 * 60 * 60)

            for log_file in log_dir.glob('*.log'):
                if log_file.stat().st_mtime < cutoff_date:
                    log_file.unlink()
                    self.logger.info(f"Deleted old log file: {log_file.name}")

        except Exception as e:
            self.logger.error(f"Error cleaning up logs: {e}")

    def setup_schedule(self):
        """Set up all scheduled tasks."""
        # Daily briefing at 8:00 AM
        schedule.every().day.at("08:00").do(self.daily_briefing)

        # Weekly review every Monday at 8:00 AM
        schedule.every().monday.at("08:00").do(self.weekly_review)

        # LinkedIn posts every Monday at 9:00 AM
        schedule.every().monday.at("09:00").do(self.linkedin_post_generation)

        # Monthly subscription audit on 1st of month at 9:00 AM
        schedule.every().day.at("09:00").do(self._check_monthly_audit)

        # Log cleanup every Sunday at 2:00 AM
        schedule.every().sunday.at("02:00").do(self.log_cleanup)

        self.logger.info("Scheduled tasks configured:")
        self.logger.info("  - Daily briefing: 8:00 AM")
        self.logger.info("  - Weekly review: Monday 8:00 AM")
        self.logger.info("  - LinkedIn posts: Monday 9:00 AM")
        self.logger.info("  - Subscription audit: 1st of month 9:00 AM")
        self.logger.info("  - Log cleanup: Sunday 2:00 AM")

    def _check_monthly_audit(self):
        """Check if today is 1st of month for subscription audit."""
        if datetime.now().day == 1:
            self.subscription_audit()

    def run(self):
        """Run the scheduler."""
        print("=" * 60)
        print("AI Employee Scheduler")
        print("=" * 60)
        print()
        print("Scheduled Tasks:")
        print("  - Daily briefing: 8:00 AM")
        print("  - Weekly review: Monday 8:00 AM")
        print("  - LinkedIn posts: Monday 9:00 AM")
        print("  - Subscription audit: 1st of month 9:00 AM")
        print("  - Log cleanup: Sunday 2:00 AM")
        print()
        print("Press Ctrl+C to stop")
        print()

        self.setup_schedule()

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            print("\nScheduler stopped")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scheduler.py <vault_path>")
        print("Example: python scheduler.py ../AI_Employee_Vault")
        sys.exit(1)

    vault_path = sys.argv[1]
    scheduler = AIEmployeeScheduler(vault_path)
    scheduler.run()

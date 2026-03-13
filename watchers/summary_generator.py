#!/usr/bin/env python3
"""
Automatic Summary Generator
Generates daily/weekly summaries of AI Employee activities
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import pickle

class SummaryGenerator:
    """Generate activity summaries"""
    
    def __init__(self):
        self.vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
        self.logs_path = Path(__file__).parent.parent / 'logs'
        self.summaries_path = self.vault_path / 'Summaries'
        self.summaries_path.mkdir(parents=True, exist_ok=True)
    
    def count_files_in_folder(self, folder_path):
        """Count files in a folder"""
        if not folder_path.exists():
            return 0
        return len([f for f in folder_path.iterdir() if f.is_file()])
    
    def get_activity_stats(self):
        """Get statistics from vault folders"""
        stats = {
            'pending_approval': {},
            'approved': {},
            'done': {},
            'total_processed': 0
        }
        
        # Count pending items
        pending_dir = self.vault_path / 'Pending_Approval'
        if pending_dir.exists():
            for subdir in pending_dir.iterdir():
                if subdir.is_dir():
                    count = self.count_files_in_folder(subdir)
                    if count > 0:
                        stats['pending_approval'][subdir.name] = count
        
        # Count approved items
        approved_dir = self.vault_path / 'Approved'
        if approved_dir.exists():
            for subdir in approved_dir.iterdir():
                if subdir.is_dir():
                    count = self.count_files_in_folder(subdir)
                    if count > 0:
                        stats['approved'][subdir.name] = count
        
        # Count done items
        done_dir = self.vault_path / 'Done'
        if done_dir.exists():
            for subdir in done_dir.iterdir():
                if subdir.is_dir():
                    count = self.count_files_in_folder(subdir)
                    if count > 0:
                        stats['done'][subdir.name] = count
                        stats['total_processed'] += count
        
        return stats
    
    def get_social_media_stats(self):
        """Get social media posting statistics"""
        stats = {
            'linkedin': {'posts': 0, 'last_post': None},
            'twitter': {'posts': 0, 'last_post': None}
        }
        
        done_dir = self.vault_path / 'Done'
        
        # LinkedIn stats
        linkedin_dir = done_dir / 'linkedin'
        if linkedin_dir.exists():
            posts = list(linkedin_dir.glob('LINKEDIN_POST_*.md'))
            stats['linkedin']['posts'] = len(posts)
            if posts:
                latest = max(posts, key=lambda p: p.stat().st_mtime)
                stats['linkedin']['last_post'] = datetime.fromtimestamp(latest.stat().st_mtime)
        
        # Twitter stats
        twitter_dir = done_dir / 'twitter'
        if twitter_dir.exists():
            posts = list(twitter_dir.glob('TWITTER_POST_*.md'))
            stats['twitter']['posts'] = len(posts)
            if posts:
                latest = max(posts, key=lambda p: p.stat().st_mtime)
                stats['twitter']['last_post'] = datetime.fromtimestamp(latest.stat().st_mtime)
        
        return stats
    
    def get_email_stats(self):
        """Get email processing statistics"""
        stats = {
            'emails_processed': 0,
            'responses_sent': 0,
            'pending_responses': 0
        }
        
        done_dir = self.vault_path / 'Done'
        email_dir = done_dir / 'emails'
        if email_dir.exists():
            stats['emails_processed'] = self.count_files_in_folder(email_dir)
        
        approved_dir = self.vault_path / 'Approved'
        email_approved = approved_dir / 'emails'
        if email_approved.exists():
            stats['responses_sent'] = self.count_files_in_folder(email_approved)
        
        pending_dir = self.vault_path / 'Pending_Approval'
        email_pending = pending_dir / 'emails'
        if email_pending.exists():
            stats['pending_responses'] = self.count_files_in_folder(email_pending)
        
        return stats
    
    def generate_daily_summary(self):
        """Generate daily summary"""
        today = datetime.now()
        
        # Get all statistics
        activity_stats = self.get_activity_stats()
        social_stats = self.get_social_media_stats()
        email_stats = self.get_email_stats()
        
        # Generate summary text
        summary = f"""# AI Employee Daily Summary
**Date:** {today.strftime('%Y-%m-%d')}
**Generated:** {today.strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Activity Overview

### Total Items Processed: {activity_stats['total_processed']}

### Pending Approval
"""
        
        if activity_stats['pending_approval']:
            for category, count in activity_stats['pending_approval'].items():
                summary += f"- **{category.title()}:** {count} items\n"
        else:
            summary += "- No items pending approval\n"
        
        summary += "\n### Approved & Ready\n"
        if activity_stats['approved']:
            for category, count in activity_stats['approved'].items():
                summary += f"- **{category.title()}:** {count} items\n"
        else:
            summary += "- No items approved\n"
        
        summary += "\n### Completed Today\n"
        if activity_stats['done']:
            for category, count in activity_stats['done'].items():
                summary += f"- **{category.title()}:** {count} items\n"
        else:
            summary += "- No items completed\n"
        
        # Social Media Stats
        summary += "\n---\n\n## 📱 Social Media Activity\n\n"
        
        summary += f"### LinkedIn\n"
        summary += f"- **Posts:** {social_stats['linkedin']['posts']}\n"
        if social_stats['linkedin']['last_post']:
            summary += f"- **Last Post:** {social_stats['linkedin']['last_post'].strftime('%Y-%m-%d %H:%M')}\n"
        else:
            summary += "- **Last Post:** No posts yet\n"
        
        summary += f"\n### Twitter (X)\n"
        summary += f"- **Tweets:** {social_stats['twitter']['posts']}\n"
        if social_stats['twitter']['last_post']:
            summary += f"- **Last Tweet:** {social_stats['twitter']['last_post'].strftime('%Y-%m-%d %H:%M')}\n"
        else:
            summary += "- **Last Tweet:** No tweets yet\n"
        
        # Email Stats
        summary += "\n---\n\n## 📧 Email Activity\n\n"
        summary += f"- **Emails Processed:** {email_stats['emails_processed']}\n"
        summary += f"- **Responses Sent:** {email_stats['responses_sent']}\n"
        summary += f"- **Pending Responses:** {email_stats['pending_responses']}\n"
        
        # System Health
        summary += "\n---\n\n## 🔧 System Status\n\n"
        summary += "- **Status:** ✅ Operational\n"
        summary += f"- **Uptime:** Running since system start\n"
        summary += f"- **Last Check:** {today.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # Action Items
        summary += "\n---\n\n## ⚡ Action Items\n\n"
        
        action_items = []
        
        if activity_stats['pending_approval']:
            total_pending = sum(activity_stats['pending_approval'].values())
            action_items.append(f"Review {total_pending} items pending approval")
        
        if activity_stats['approved']:
            total_approved = sum(activity_stats['approved'].values())
            action_items.append(f"Process {total_approved} approved items")
        
        if email_stats['pending_responses'] > 0:
            action_items.append(f"Review {email_stats['pending_responses']} pending email responses")
        
        if action_items:
            for item in action_items:
                summary += f"- {item}\n"
        else:
            summary += "- No action items at this time\n"
        
        summary += "\n---\n\n## 📝 Notes\n\n"
        summary += "This summary was automatically generated by your AI Employee.\n"
        summary += "For detailed logs, check the `logs/` directory.\n"
        
        return summary
    
    def save_summary(self, summary_text, summary_type='daily'):
        """Save summary to file"""
        today = datetime.now()
        filename = f"{summary_type}_summary_{today.strftime('%Y-%m-%d')}.md"
        filepath = self.summaries_path / filename
        
        filepath.write_text(summary_text)
        print(f"✅ Summary saved to: {filepath}")
        
        return filepath
    
    def generate_and_save(self):
        """Generate and save daily summary"""
        print("📊 Generating daily summary...")
        summary = self.generate_daily_summary()
        filepath = self.save_summary(summary)
        print(f"✅ Daily summary complete: {filepath}")
        return summary

def test_summary():
    """Test summary generation"""
    try:
        generator = SummaryGenerator()
        summary = generator.generate_and_save()
        print("\n" + "="*50)
        print(summary)
        print("="*50)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_summary()

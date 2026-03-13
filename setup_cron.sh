#!/bin/bash
# Cron Automation Setup for Personal AI Employee
# Sets up automated tasks for Bronze, Silver, and Gold tier features

set -e

PROJECT_DIR="/mnt/d/AI/Personal-AI-Employee"
VAULT_DIR="$PROJECT_DIR/AI_Employee_Vault"
WATCHERS_DIR="$PROJECT_DIR/watchers"
WORKFLOWS_DIR="$PROJECT_DIR/workflows"
LOGS_DIR="$PROJECT_DIR/logs"

echo "=========================================="
echo "Personal AI Employee - Cron Setup"
echo "=========================================="
echo ""

# Check if running as correct user
if [ "$EUID" -eq 0 ]; then
    echo "❌ Don't run this script as root"
    echo "Run as your regular user: ./setup_cron.sh"
    exit 1
fi

# Create logs directory
mkdir -p "$LOGS_DIR"

# Backup existing crontab
echo "📋 Backing up existing crontab..."
crontab -l > "$PROJECT_DIR/crontab_backup_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null || echo "No existing crontab"

# Create temporary crontab file
TEMP_CRON=$(mktemp)

# Add existing crontab entries (if any)
crontab -l 2>/dev/null > "$TEMP_CRON" || true

# Add header
cat >> "$TEMP_CRON" << 'EOF'

# ==========================================
# Personal AI Employee - Automated Tasks
# ==========================================

# Environment variables
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

EOF

echo ""
echo "Select automation level:"
echo "1) Bronze Tier - Basic automation (CEO briefing, filesystem watcher)"
echo "2) Silver Tier - Enhanced automation (+ Gmail, LinkedIn, daily reports)"
echo "3) Gold Tier - Full automation (+ Odoo, social media, health monitoring)"
echo ""
read -p "Enter choice (1-3): " TIER_CHOICE

case $TIER_CHOICE in
    1)
        echo "Setting up Bronze Tier automation..."
        TIER="bronze"
        ;;
    2)
        echo "Setting up Silver Tier automation..."
        TIER="silver"
        ;;
    3)
        echo "Setting up Gold Tier automation..."
        TIER="gold"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Bronze Tier Tasks (All tiers include these)
cat >> "$TEMP_CRON" << EOF

# ==========================================
# BRONZE TIER - Core Automation
# ==========================================

# CEO Briefing - Every Monday at 8:00 AM
0 8 * * 1 cd $WORKFLOWS_DIR && python3 ceo_briefing_generator.py >> $LOGS_DIR/ceo_briefing_cron.log 2>&1

# Filesystem Watcher - Every 5 minutes
*/5 * * * * cd $WATCHERS_DIR && python3 filesystem_watcher.py $VAULT_DIR >> $LOGS_DIR/filesystem_watcher_cron.log 2>&1

# Dashboard Update - Every hour
0 * * * * cd $WORKFLOWS_DIR && python3 update_dashboard.py >> $LOGS_DIR/dashboard_update_cron.log 2>&1

EOF

# Silver Tier Tasks
if [ "$TIER" = "silver" ] || [ "$TIER" = "gold" ]; then
    cat >> "$TEMP_CRON" << EOF

# ==========================================
# SILVER TIER - Enhanced Automation
# ==========================================

# Gmail Watcher - Every 10 minutes (if configured)
*/10 * * * * cd $WATCHERS_DIR && [ -f ../credentials.json ] && python3 gmail_watcher.py $VAULT_DIR ../credentials.json >> $LOGS_DIR/gmail_watcher_cron.log 2>&1

# LinkedIn Content Generation - Every Monday at 9:00 AM
0 9 * * 1 cd $WORKFLOWS_DIR && python3 generate_linkedin_posts.py >> $LOGS_DIR/linkedin_generation_cron.log 2>&1

# Daily Business Report - Every day at 6:00 PM
0 18 * * * cd $WORKFLOWS_DIR && python3 automated_daily_report.py >> $LOGS_DIR/daily_report_cron.log 2>&1

# Weekly Summary - Every Sunday at 8:00 PM
0 20 * * 0 cd $WORKFLOWS_DIR && python3 generate_weekly_summary.py >> $LOGS_DIR/weekly_summary_cron.log 2>&1

EOF
fi

# Gold Tier Tasks
if [ "$TIER" = "gold" ]; then
    cat >> "$TEMP_CRON" << EOF

# ==========================================
# GOLD TIER - Full Automation
# ==========================================

# Health Monitor - Every 15 minutes
*/15 * * * * cd $WATCHERS_DIR && python3 health_monitor.py >> $LOGS_DIR/health_monitor_cron.log 2>&1

# Odoo Sync - Every hour (if configured)
0 * * * * cd $WORKFLOWS_DIR && [ -f ../odoo_config.json ] && python3 sync_odoo.py >> $LOGS_DIR/odoo_sync_cron.log 2>&1

# Social Media Queue Processing - Every 30 minutes
*/30 * * * * cd $WORKFLOWS_DIR && python3 process_social_media_queue.py >> $LOGS_DIR/social_media_cron.log 2>&1

# System Cleanup - Daily at 2:00 AM
0 2 * * * cd $PROJECT_DIR && python3 cleanup_old_logs.py >> $LOGS_DIR/cleanup_cron.log 2>&1

# Backup Vault - Daily at 3:00 AM
0 3 * * * cd $PROJECT_DIR && tar -czf backups/vault_backup_\$(date +\%Y\%m\%d).tar.gz AI_Employee_Vault/ >> $LOGS_DIR/backup_cron.log 2>&1

EOF
fi

# Add footer
cat >> "$TEMP_CRON" << 'EOF'

# ==========================================
# End of Personal AI Employee Tasks
# ==========================================

EOF

# Install new crontab
echo ""
echo "📋 Installing crontab..."
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo ""
echo "✅ Cron automation setup complete!"
echo ""
echo "=========================================="
echo "Scheduled Tasks Summary"
echo "=========================================="
echo ""

case $TIER in
    bronze)
        echo "Bronze Tier Tasks:"
        echo "  • CEO Briefing: Mondays at 8:00 AM"
        echo "  • Filesystem Watcher: Every 5 minutes"
        echo "  • Dashboard Update: Every hour"
        ;;
    silver)
        echo "Silver Tier Tasks:"
        echo "  • CEO Briefing: Mondays at 8:00 AM"
        echo "  • Filesystem Watcher: Every 5 minutes"
        echo "  • Dashboard Update: Every hour"
        echo "  • Gmail Watcher: Every 10 minutes"
        echo "  • LinkedIn Content: Mondays at 9:00 AM"
        echo "  • Daily Report: Daily at 6:00 PM"
        echo "  • Weekly Summary: Sundays at 8:00 PM"
        ;;
    gold)
        echo "Gold Tier Tasks:"
        echo "  • CEO Briefing: Mondays at 8:00 AM"
        echo "  • Filesystem Watcher: Every 5 minutes"
        echo "  • Dashboard Update: Every hour"
        echo "  • Gmail Watcher: Every 10 minutes"
        echo "  • LinkedIn Content: Mondays at 9:00 AM"
        echo "  • Daily Report: Daily at 6:00 PM"
        echo "  • Weekly Summary: Sundays at 8:00 PM"
        echo "  • Health Monitor: Every 15 minutes"
        echo "  • Odoo Sync: Every hour"
        echo "  • Social Media Queue: Every 30 minutes"
        echo "  • System Cleanup: Daily at 2:00 AM"
        echo "  • Vault Backup: Daily at 3:00 AM"
        ;;
esac

echo ""
echo "=========================================="
echo "Management Commands"
echo "=========================================="
echo ""
echo "View scheduled tasks:"
echo "  crontab -l"
echo ""
echo "View cron logs:"
echo "  tail -f $LOGS_DIR/*_cron.log"
echo ""
echo "Edit crontab manually:"
echo "  crontab -e"
echo ""
echo "Remove all cron tasks:"
echo "  crontab -r"
echo ""
echo "Restore from backup:"
echo "  crontab $PROJECT_DIR/crontab_backup_*.txt"
echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. Verify cron service is running:"
echo "   sudo systemctl status cron"
echo ""
echo "2. Test a task manually:"
echo "   cd $WORKFLOWS_DIR && python3 ceo_briefing_generator.py"
echo ""
echo "3. Monitor logs for errors:"
echo "   tail -f $LOGS_DIR/*.log"
echo ""
echo "4. Adjust schedules if needed:"
echo "   crontab -e"
echo ""
echo "✅ Your AI Employee is now automated!"
echo ""

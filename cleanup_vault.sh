#!/bin/bash
# Vault Cleanup Script - Remove old and Platinum tier folders

set -e

echo "=========================================="
echo "Vault Cleanup - Removing Old Folders"
echo "=========================================="
echo ""

VAULT_DIR="AI_Employee_Vault"
BACKUP_DIR="./vault_cleanup_backup_$(date +%Y%m%d_%H%M%S)"

# Create backup
mkdir -p "$BACKUP_DIR"
echo "✅ Created backup directory: $BACKUP_DIR"
echo ""

# Function to backup and remove directory
backup_and_remove() {
    local dir="$1"
    if [ -d "$dir" ]; then
        echo "  📦 Backing up: $dir"
        cp -r "$dir" "$BACKUP_DIR/"
        rm -rf "$dir"
        echo "  ✓ Deleted: $dir"
    fi
}

echo "🗑️  Removing old processed_tasks folder..."
# Move any unique files first
if [ -d "$VAULT_DIR/Done/processed_tasks" ]; then
    for file in "$VAULT_DIR/Done/processed_tasks"/*.md; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            if [ ! -f "$VAULT_DIR/Done/general/$filename" ]; then
                echo "  → Moving unique file: $filename"
                mv "$file" "$VAULT_DIR/Done/general/"
            fi
        fi
    done
    backup_and_remove "$VAULT_DIR/Done/processed_tasks"
fi
echo ""

echo "🗑️  Removing old Approvals folder (using Approved now)..."
backup_and_remove "$VAULT_DIR/Approvals"
echo ""

echo "🗑️  Removing Platinum Tier folders (not implemented for hackathon)..."
backup_and_remove "$VAULT_DIR/ML_Models"
backup_and_remove "$VAULT_DIR/Multi_Agent"
backup_and_remove "$VAULT_DIR/Predictive_Analytics"
backup_and_remove "$VAULT_DIR/learning"
backup_and_remove "$VAULT_DIR/Automation"
echo ""

echo "🗑️  Cleaning up old JSON reports in Done/..."
if [ -f "$VAULT_DIR/Done/daily_report_20260303.json" ]; then
    mv "$VAULT_DIR/Done/daily_report_20260303.json" "$BACKUP_DIR/"
    rm "$VAULT_DIR/Done/daily_report_20260303.json"
    echo "  ✓ Deleted: daily_report_20260303.json"
fi
if [ -f "$VAULT_DIR/Done/expense_report_20260303_143411.json" ]; then
    mv "$VAULT_DIR/Done/expense_report_20260303_143411.json" "$BACKUP_DIR/"
    rm "$VAULT_DIR/Done/expense_report_20260303_143411.json"
    echo "  ✓ Deleted: expense_report_20260303_143411.json"
fi
echo ""

echo "=========================================="
echo "✅ Vault Cleanup Complete!"
echo "=========================================="
echo ""
echo "Files backed up to: $BACKUP_DIR"
echo ""
echo "📋 Remaining Vault Structure:"
echo ""
ls -d "$VAULT_DIR"/*/ 2>/dev/null | sed 's|AI_Employee_Vault/||' | sed 's|/$||' | while read dir; do
    echo "  ✓ $dir/"
done
echo ""
echo "Essential folders kept:"
echo "  ✓ Needs_Action/ - Incoming tasks"
echo "  ✓ Pending_Approval/ - Awaiting approval"
echo "  ✓ Approved/ - Ready for execution"
echo "  ✓ Done/ - Completed tasks"
echo "  ✓ Plans/ - Task plans"
echo "  ✓ Briefings/ - CEO briefings"
echo "  ✓ Logs/ - Audit logs"
echo "  ✓ Config/ - Configuration"
echo "  ✓ Inbox/ - Drop folder"
echo "  ✓ Post_Ideas/ - Social media ideas"
echo "  ✓ Summaries/ - Generated summaries"
echo "  ✓ Rejected/ - Rejected tasks"
echo ""
echo "To restore: cp -r $BACKUP_DIR/* $VAULT_DIR/"
echo ""

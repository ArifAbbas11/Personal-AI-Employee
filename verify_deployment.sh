#!/bin/bash
# Comprehensive Deployment Verification Script
# Verifies all Gold Tier features are properly deployed and operational

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Gold Tier Deployment Verification${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

PASSED=0
FAILED=0
WARNINGS=0

# Function to check and report
check_status() {
    local description=$1
    local status=$2

    if [ "$status" = "pass" ]; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    elif [ "$status" = "fail" ]; then
        echo -e "${RED}✗${NC} $description"
        ((FAILED++))
    else
        echo -e "${YELLOW}⚠${NC} $description"
        ((WARNINGS++))
    fi
}

# Feature 1: Ralph Wiggum
echo -e "${BLUE}Feature 1: Ralph Wiggum (Autonomous Loops)${NC}"
echo "-----------------------------------"

if [ -x "ralph_wiggum_setup.sh" ]; then
    check_status "Helper script executable" "pass"
else
    check_status "Helper script executable" "fail"
fi

if [ -x ".claude/hooks/stop.sh" ]; then
    check_status "Stop hook executable" "pass"
else
    check_status "Stop hook executable" "fail"
fi

if [ -f ".claude/skills/ralph-loop-executor.md" ]; then
    check_status "Ralph skill exists" "pass"
else
    check_status "Ralph skill exists" "fail"
fi

if [ -f "RALPH_WIGGUM_REFINED_GUIDE.md" ]; then
    check_status "User guide exists" "pass"
else
    check_status "User guide exists" "fail"
fi

if [ -d "AI_Employee_Vault/Needs_Action" ] && [ -d "AI_Employee_Vault/Done" ]; then
    check_status "Required directories exist" "pass"
else
    check_status "Required directories exist" "fail"
fi

# Check if test files exist
if ls AI_Employee_Vault/Needs_Action/RALPH_*.md >/dev/null 2>&1; then
    check_status "Test files available" "pass"
else
    check_status "Test files available" "warn"
fi

echo ""

# Feature 2: CEO Briefing
echo -e "${BLUE}Feature 2: CEO Briefing (Business Intelligence)${NC}"
echo "-----------------------------------"

if [ -f "watchers/simple_ceo_briefing.py" ]; then
    check_status "CEO Briefing script exists" "pass"
else
    check_status "CEO Briefing script exists" "fail"
fi

if [ -f "watchers/data_collectors/task_collector.py" ]; then
    check_status "Task collector exists" "pass"
else
    check_status "Task collector exists" "fail"
fi

if [ -f "watchers/data_collectors/communication_collector.py" ]; then
    check_status "Communication collector exists" "pass"
else
    check_status "Communication collector exists" "fail"
fi

# Test CEO Briefing generation
if python3 watchers/simple_ceo_briefing.py >/dev/null 2>&1; then
    check_status "CEO Briefing generates successfully" "pass"

    # Check if briefing file was created
    if ls AI_Employee_Vault/Briefings/*.md >/dev/null 2>&1; then
        check_status "Briefing file created" "pass"
    else
        check_status "Briefing file created" "fail"
    fi
else
    check_status "CEO Briefing generates successfully" "fail"
fi

echo ""

# Feature 3: Odoo Accounting
echo -e "${BLUE}Feature 3: Odoo Accounting Integration${NC}"
echo "-----------------------------------"

if [ -f "watchers/odoo_mcp_server.py" ]; then
    check_status "Odoo MCP server exists" "pass"
else
    check_status "Odoo MCP server exists" "fail"
fi

if [ -f "watchers/data_collectors/financial_collector.py" ]; then
    check_status "Financial collector exists" "pass"
else
    check_status "Financial collector exists" "fail"
fi

# Check if Odoo is configured
if [ -f "AI_Employee_Vault/Config/odoo_config.json" ]; then
    check_status "Odoo configured" "pass"

    # Test Odoo connection
    if python3 watchers/odoo_mcp_server.py --test >/dev/null 2>&1; then
        check_status "Odoo connection successful" "pass"
    else
        check_status "Odoo connection successful" "fail"
    fi
else
    check_status "Odoo configured" "warn"
    check_status "Odoo connection successful" "warn"
fi

# Check if Odoo is running (Docker)
if docker ps | grep -q "odoo"; then
    check_status "Odoo container running" "pass"
else
    check_status "Odoo container running" "warn"
fi

echo ""

# Feature 4: Social Media Integration
echo -e "${BLUE}Feature 4: Social Media Integration${NC}"
echo "-----------------------------------"

if [ -f "watchers/social_media_mcp_server.py" ]; then
    check_status "Social Media MCP server exists" "pass"
else
    check_status "Social Media MCP server exists" "fail"
fi

if [ -f "watchers/social_media_scheduler.py" ]; then
    check_status "Content scheduler exists" "pass"
else
    check_status "Content scheduler exists" "fail"
fi

# Check if Social Media is configured
if [ -f "AI_Employee_Vault/Config/social_media_config.json" ]; then
    check_status "Social Media configured" "pass"

    # Test platform connections
    for platform in facebook instagram twitter linkedin; do
        if python3 watchers/social_media_mcp_server.py --test "$platform" >/dev/null 2>&1; then
            check_status "$platform connection successful" "pass"
        else
            check_status "$platform connection successful" "warn"
        fi
    done
else
    check_status "Social Media configured" "warn"
fi

# Check if scheduler is running
if pgrep -f "social_media_scheduler.py" >/dev/null; then
    check_status "Scheduler daemon running" "pass"
else
    check_status "Scheduler daemon running" "warn"
fi

echo ""

# Feature 5: Error Recovery & Watchdog
echo -e "${BLUE}Feature 5: Error Recovery & Watchdog${NC}"
echo "-----------------------------------"

if [ -f "watchers/error_recovery_watchdog.py" ]; then
    check_status "Error Recovery system exists" "pass"
else
    check_status "Error Recovery system exists" "fail"
fi

# Test error detection
if python3 watchers/error_recovery_watchdog.py --scan >/dev/null 2>&1; then
    check_status "Error detection working" "pass"
else
    check_status "Error detection working" "fail"
fi

# Test system health check
if python3 watchers/error_recovery_watchdog.py --health >/dev/null 2>&1; then
    check_status "System health check working" "pass"
else
    check_status "System health check working" "fail"
fi

# Check if watchdog is running
if pgrep -f "error_recovery_watchdog.py" >/dev/null; then
    check_status "Watchdog daemon running" "pass"
else
    check_status "Watchdog daemon running" "warn"
fi

echo ""

# Feature 6: Comprehensive Audit Logging
echo -e "${BLUE}Feature 6: Comprehensive Audit Logging${NC}"
echo "-----------------------------------"

if [ -f "watchers/audit_logger.py" ]; then
    check_status "Audit Logger exists" "pass"
else
    check_status "Audit Logger exists" "fail"
fi

# Test audit logger import
if python3 -c "from watchers.audit_logger import AuditLogger" 2>/dev/null; then
    check_status "Audit Logger module loads" "pass"
else
    check_status "Audit Logger module loads" "fail"
fi

# Check audit logs directory
if [ -d "AI_Employee_Vault/Logs/audit" ]; then
    check_status "Audit logs directory exists" "pass"
else
    check_status "Audit logs directory exists" "warn"
fi

echo ""

# Deployment Scripts
echo -e "${BLUE}Deployment Scripts${NC}"
echo "-----------------------------------"

if [ -x "deploy_odoo.sh" ]; then
    check_status "Odoo deployment script executable" "pass"
else
    check_status "Odoo deployment script executable" "warn"
fi

if [ -x "deploy_social_media.sh" ]; then
    check_status "Social Media deployment script executable" "pass"
else
    check_status "Social Media deployment script executable" "warn"
fi

if [ -x "verify_gold_tier_deployment.sh" ]; then
    check_status "Verification script executable" "pass"
else
    check_status "Verification script executable" "warn"
fi

echo ""

# Documentation
echo -e "${BLUE}Documentation${NC}"
echo "-----------------------------------"

if [ -f "GOLD_TIER_DEPLOYMENT_GUIDE.md" ]; then
    check_status "Deployment guide exists" "pass"
else
    check_status "Deployment guide exists" "fail"
fi

if [ -f "GOLD_TIER_PRODUCTION_READINESS_CHECKLIST.md" ]; then
    check_status "Production checklist exists" "pass"
else
    check_status "Production checklist exists" "fail"
fi

if [ -f "AUTOMATED_DEPLOYMENT_GUIDE.md" ]; then
    check_status "Automated deployment guide exists" "pass"
else
    check_status "Automated deployment guide exists" "warn"
fi

echo ""

# System Health
echo -e "${BLUE}System Health${NC}"
echo "-----------------------------------"

# Check disk space
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 90 ]; then
    check_status "Disk space available ($DISK_USAGE% used)" "pass"
else
    check_status "Disk space available ($DISK_USAGE% used)" "warn"
fi

# Check if logs directory is writable
if [ -w "AI_Employee_Vault/Logs" ]; then
    check_status "Logs directory writable" "pass"
else
    check_status "Logs directory writable" "fail"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
check_status "Python version: $PYTHON_VERSION" "pass"

echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Verification Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo -e "${RED}Failed:${NC} $FAILED"
echo ""

# Calculate deployment percentage
TOTAL=$((PASSED + WARNINGS + FAILED))
if [ $TOTAL -gt 0 ]; then
    DEPLOYMENT_PCT=$((PASSED * 100 / TOTAL))
    echo "Deployment Status: $DEPLOYMENT_PCT% operational"
    echo ""
fi

# Recommendations
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}⚠ Critical issues detected${NC}"
    echo "Please review the failures above and fix them before proceeding."
    echo ""
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ Warnings detected${NC}"
    echo "Some optional features are not configured:"
    echo ""

    if [ ! -f "AI_Employee_Vault/Config/odoo_config.json" ]; then
        echo "  • Odoo not configured - Run: ./deploy_odoo.sh"
    fi

    if [ ! -f "AI_Employee_Vault/Config/social_media_config.json" ]; then
        echo "  • Social Media not configured - Run: ./deploy_social_media.sh"
    fi

    if ! pgrep -f "error_recovery_watchdog.py" >/dev/null; then
        echo "  • Watchdog not running - Run: python3 watchers/error_recovery_watchdog.py --daemon &"
    fi

    if ! pgrep -f "social_media_scheduler.py" >/dev/null; then
        echo "  • Scheduler not running - Run: python3 watchers/social_media_scheduler.py --daemon &"
    fi

    echo ""
fi

# Next steps
echo -e "${BLUE}Next Steps${NC}"
echo "-----------------------------------"

if [ ! -f "AI_Employee_Vault/Config/odoo_config.json" ]; then
    echo "1. Deploy Odoo: ./deploy_odoo.sh"
fi

if [ ! -f "AI_Employee_Vault/Config/social_media_config.json" ]; then
    echo "2. Deploy Social Media: ./deploy_social_media.sh"
fi

if [ -f "AI_Employee_Vault/Needs_Action/RALPH_TEST_LOOP.md" ]; then
    echo "3. Test Ralph Wiggum: See RALPH_QUICK_TEST_REFERENCE.md"
fi

echo "4. Generate CEO Briefing: python3 watchers/simple_ceo_briefing.py"
echo "5. Review deployment guide: cat GOLD_TIER_DEPLOYMENT_GUIDE.md"

echo ""

# Exit code
if [ $FAILED -gt 0 ]; then
    exit 1
else
    exit 0
fi

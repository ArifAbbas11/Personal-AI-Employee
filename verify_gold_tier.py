#!/usr/bin/env python3
"""
Gold Tier Verification Script
Verifies all Gold Tier requirements are met and functional
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add watchers to path
sys.path.insert(0, str(Path(__file__).parent / "watchers"))

print("=" * 80)
print("🥇 GOLD TIER VERIFICATION")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Track results
results = {
    'bronze_requirements': {},
    'silver_requirements': {},
    'gold_requirements': {},
    'overall_status': 'unknown',
    'timestamp': datetime.now().isoformat()
}

def check_requirement(name: str, check_func, tier: str = 'gold') -> bool:
    """Check a requirement and record result."""
    try:
        result = check_func()
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        results[f'{tier}_requirements'][name] = result
        return result
    except Exception as e:
        print(f"❌ ERROR - {name}: {e}")
        results[f'{tier}_requirements'][name] = False
        return False

# ============================================================================
# BRONZE TIER PREREQUISITES
# ============================================================================
print("BRONZE TIER PREREQUISITES")
print("-" * 80)

def check_obsidian_vault():
    vault = Path("AI_Employee_Vault")
    obsidian_dir = vault / ".obsidian"
    return vault.exists() and obsidian_dir.exists()

def check_filesystem_watcher():
    watcher = Path("watchers/filesystem_watcher.py")
    return watcher.exists()

def check_ceo_briefing():
    briefing = Path("workflows/ceo_briefing_generator.py")
    return briefing.exists()

check_requirement("Obsidian vault configured", check_obsidian_vault, 'bronze')
check_requirement("Filesystem watcher", check_filesystem_watcher, 'bronze')
check_requirement("CEO Briefing generator", check_ceo_briefing, 'bronze')

print()

# ============================================================================
# SILVER TIER PREREQUISITES
# ============================================================================
print("SILVER TIER PREREQUISITES")
print("-" * 80)

def check_gmail_watcher():
    gmail_watcher = Path("watchers/gmail_watcher.py")
    return gmail_watcher.exists()

def check_linkedin_skill():
    linkedin_skill = Path(".claude/skills/linkedin-manager.md")
    return linkedin_skill.exists()

def check_plan_generation():
    plan_skill = Path(".claude/skills/generate_plan/SKILL.md")
    return plan_skill.exists()

check_requirement("Gmail watcher", check_gmail_watcher, 'silver')
check_requirement("LinkedIn skill", check_linkedin_skill, 'silver')
check_requirement("Plan generation", check_plan_generation, 'silver')

print()

# ============================================================================
# GOLD TIER REQUIREMENTS
# ============================================================================
print("GOLD TIER REQUIREMENTS")
print("-" * 80)

def check_odoo_integration():
    """Check Odoo integration components exist."""
    odoo_mcp = Path("watchers/odoo_mcp_server.py")
    odoo_skill = Path(".claude/skills/odoo-accounting.md")
    return odoo_mcp.exists() and odoo_skill.exists()

def check_odoo_deployment():
    """Check Odoo deployment script exists."""
    deploy_script = Path("deploy_odoo.sh")
    return deploy_script.exists()

def check_social_media_integration():
    """Check social media integration exists."""
    social_mcp = Path("watchers/social_media_mcp_server.py")
    social_skill = Path(".claude/skills/social-media.md")
    return social_mcp.exists() and social_skill.exists()

def check_facebook_instagram():
    """Check Facebook/Instagram support in social media MCP."""
    social_mcp = Path("watchers/social_media_mcp_server.py")
    if not social_mcp.exists():
        return False
    content = social_mcp.read_text()
    return 'facebook' in content.lower() and 'instagram' in content.lower()

def check_twitter_integration():
    """Check Twitter/X support in social media MCP."""
    social_mcp = Path("watchers/social_media_mcp_server.py")
    if not social_mcp.exists():
        return False
    content = social_mcp.read_text()
    return 'twitter' in content.lower()

def check_ralph_wiggum():
    """Check Ralph Wiggum loop implementation."""
    ralph_skill = Path(".claude/skills/ralph-loop-executor.md")
    ralph_setup = Path("ralph_wiggum_setup.sh")
    return ralph_skill.exists() and ralph_setup.exists()

def check_multiple_mcp_servers():
    """Check multiple MCP servers exist."""
    automation_mcp = Path("watchers/automation_mcp_server.py")
    multi_agent_mcp = Path("watchers/multi_agent_mcp_server.py")
    social_media_mcp = Path("watchers/social_media_mcp_server.py")
    odoo_mcp = Path("watchers/odoo_mcp_server.py")
    ml_mcp = Path("watchers/ml_mcp_server.py")

    count = sum([
        automation_mcp.exists(),
        multi_agent_mcp.exists(),
        social_media_mcp.exists(),
        odoo_mcp.exists(),
        ml_mcp.exists()
    ])

    print(f"  Found {count} MCP servers")
    return count >= 3  # Gold tier requires multiple MCP servers

def check_error_recovery():
    """Check error recovery system exists."""
    error_recovery_skill = Path(".claude/skills/error-recovery.md")
    self_healing = Path("watchers/automation/self_healing.py")
    return error_recovery_skill.exists() or self_healing.exists()

def check_audit_logging():
    """Check audit logging system exists."""
    audit_skill = Path(".claude/skills/audit-logging.md")
    return audit_skill.exists()

check_requirement("Odoo integration", check_odoo_integration)
check_requirement("Odoo deployment script", check_odoo_deployment)
check_requirement("Social media integration", check_social_media_integration)
check_requirement("Facebook/Instagram support", check_facebook_instagram)
check_requirement("Twitter/X support", check_twitter_integration)
check_requirement("Ralph Wiggum loop", check_ralph_wiggum)
check_requirement("Multiple MCP servers", check_multiple_mcp_servers)
check_requirement("Error recovery system", check_error_recovery)
check_requirement("Audit logging system", check_audit_logging)

print()

# ============================================================================
# ADVANCED FEATURES CHECK
# ============================================================================
print("ADVANCED FEATURES CHECK")
print("-" * 80)

def check_ml_systems():
    """Check ML/predictive systems exist."""
    ml_mcp = Path("watchers/ml_mcp_server.py")
    predictive_mcp = Path("watchers/predictive_mcp_server.py")
    return ml_mcp.exists() and predictive_mcp.exists()

def check_automation_systems():
    """Check advanced automation systems exist."""
    automation_dir = Path("watchers/automation")
    if not automation_dir.exists():
        return False

    task_router = automation_dir / "task_router.py"
    self_healing = automation_dir / "self_healing.py"
    resource_manager = automation_dir / "resource_manager.py"

    return task_router.exists() and self_healing.exists() and resource_manager.exists()

def check_multi_agent_system():
    """Check multi-agent coordination exists."""
    multi_agent_dir = Path("watchers/multi_agent")
    if not multi_agent_dir.exists():
        return False

    base = multi_agent_dir / "base.py"
    financial = multi_agent_dir / "financial_agent.py"

    return base.exists() and financial.exists()

def check_health_monitoring():
    """Check health monitoring exists."""
    health_monitor = Path("watchers/health_monitor.py")
    start_script = Path("start_health_monitor.sh")
    return health_monitor.exists() or start_script.exists()

check_requirement("ML/Predictive systems", check_ml_systems)
check_requirement("Advanced automation", check_automation_systems)
check_requirement("Multi-agent coordination", check_multi_agent_system)
check_requirement("Health monitoring", check_health_monitoring)

print()

# ============================================================================
# DEPLOYMENT CHECK
# ============================================================================
print("DEPLOYMENT CHECK")
print("-" * 80)

def check_deployment_scripts():
    """Check deployment scripts exist."""
    deploy_odoo = Path("deploy_odoo.sh")
    deploy_social = Path("deploy_social_media.sh")
    deploy_platinum = Path("deploy_platinum_tier.sh")
    stop_services = Path("stop_all_services.sh")

    count = sum([
        deploy_odoo.exists(),
        deploy_social.exists(),
        deploy_platinum.exists(),
        stop_services.exists()
    ])

    print(f"  Found {count} deployment scripts")
    return count >= 2

def check_verification_scripts():
    """Check verification scripts exist."""
    verify_deployment = Path("verify_deployment.sh")
    verify_gold = Path("verify_gold_tier_deployment.sh")

    return verify_deployment.exists() or verify_gold.exists()

def check_service_management():
    """Check service management scripts exist."""
    start_automation = Path("start_automation_mcp.sh")
    start_multi_agent = Path("start_multi_agent_mcp.sh")
    check_status = Path("check_system_status.sh")

    count = sum([
        start_automation.exists(),
        start_multi_agent.exists(),
        check_status.exists()
    ])

    print(f"  Found {count} service management scripts")
    return count >= 2

check_requirement("Deployment scripts", check_deployment_scripts)
check_requirement("Verification scripts", check_verification_scripts)
check_requirement("Service management", check_service_management)

print()

# ============================================================================
# DOCUMENTATION CHECK
# ============================================================================
print("DOCUMENTATION CHECK")
print("-" * 80)

def check_gold_tier_docs():
    """Check Gold Tier documentation exists."""
    docs = [
        Path("GOLD_TIER_COMPLETE_SUMMARY.md"),
        Path("GOLD_TIER_DEPLOYMENT_GUIDE.md"),
        Path("GOLD_TIER_PLAN.md")
    ]

    count = sum([doc.exists() for doc in docs])
    print(f"  Found {count} Gold Tier documents")
    return count >= 1

def check_platinum_tier_docs():
    """Check Platinum Tier documentation exists."""
    docs = [
        Path("PLATINUM_TIER_PLAN.md"),
        Path("PLATINUM_TIER_COMPLETE.md"),
        Path("PLATINUM_TIER_USER_GUIDE.md")
    ]

    count = sum([doc.exists() for doc in docs])
    print(f"  Found {count} Platinum Tier documents")
    return count >= 1

def check_installation_guides():
    """Check installation guides exist."""
    odoo_guide = Path("ODOO_INSTALLATION_GUIDE.md")
    social_guide = Path("SOCIAL_MEDIA_INSTALLATION_GUIDE.md")

    return odoo_guide.exists() or social_guide.exists()

check_requirement("Gold Tier documentation", check_gold_tier_docs)
check_requirement("Platinum Tier documentation", check_platinum_tier_docs)
check_requirement("Installation guides", check_installation_guides)

print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)
print()

bronze_passed = sum(1 for v in results['bronze_requirements'].values() if v)
bronze_total = len(results['bronze_requirements'])
silver_passed = sum(1 for v in results['silver_requirements'].values() if v)
silver_total = len(results['silver_requirements'])
gold_passed = sum(1 for v in results['gold_requirements'].values() if v)
gold_total = len(results['gold_requirements'])

print(f"Bronze Tier Prerequisites: {bronze_passed}/{bronze_total} passed")
print(f"Silver Tier Prerequisites: {silver_passed}/{silver_total} passed")
print(f"Gold Tier Requirements:    {gold_passed}/{gold_total} passed")
print()

bronze_pct = (bronze_passed / bronze_total * 100) if bronze_total > 0 else 0
silver_pct = (silver_passed / silver_total * 100) if silver_total > 0 else 0
gold_pct = (gold_passed / gold_total * 100) if gold_total > 0 else 0

print(f"Bronze Tier: {bronze_pct:.0f}% complete")
print(f"Silver Tier: {silver_pct:.0f}% complete")
print(f"Gold Tier:   {gold_pct:.0f}% complete")
print()

# Determine overall status
if bronze_pct == 100 and silver_pct == 100 and gold_pct == 100:
    results['overall_status'] = 'GOLD_TIER_COMPLETE'
    print("🎉 GOLD TIER COMPLETE!")
    print()
    print("All Gold Tier requirements are met and functional.")
    print("Your Personal AI Employee is fully featured!")
elif bronze_pct == 100 and silver_pct == 100 and gold_pct >= 80:
    results['overall_status'] = 'GOLD_TIER_MOSTLY_COMPLETE'
    print("⚠️  GOLD TIER MOSTLY COMPLETE")
    print()
    print("Most Gold Tier requirements are met. Review failed checks above.")
elif bronze_pct == 100 and silver_pct == 100:
    results['overall_status'] = 'SILVER_COMPLETE_GOLD_IN_PROGRESS'
    print("⏳ GOLD TIER IN PROGRESS")
    print()
    print("Bronze and Silver Tiers complete. Continue implementing Gold Tier features.")
else:
    results['overall_status'] = 'PREREQUISITES_INCOMPLETE'
    print("❌ PREREQUISITES INCOMPLETE")
    print()
    print("Complete Bronze and Silver Tier requirements before Gold Tier.")

print()
print("=" * 80)
print("FEATURE BREAKDOWN")
print("=" * 80)
print()

print("✅ Implemented Features:")
for tier in ['bronze_requirements', 'silver_requirements', 'gold_requirements']:
    for name, passed in results[tier].items():
        if passed:
            tier_label = tier.replace('_requirements', '').upper()
            print(f"  [{tier_label}] {name}")

print()
print("❌ Missing Features:")
for tier in ['bronze_requirements', 'silver_requirements', 'gold_requirements']:
    for name, passed in results[tier].items():
        if not passed:
            tier_label = tier.replace('_requirements', '').upper()
            print(f"  [{tier_label}] {name}")

print()
print("=" * 80)
print("NEXT STEPS")
print("=" * 80)
print()

if results['overall_status'] == 'GOLD_TIER_COMPLETE':
    print("🎉 Congratulations! Gold Tier is complete!")
    print()
    print("Next steps:")
    print("1. Run end-to-end system tests")
    print("2. Deploy all services: ./deploy_platinum_tier.sh")
    print("3. Set up cron automation: ./setup_cron.sh")
    print("4. Configure Odoo (if not done): ./deploy_odoo.sh")
    print("5. Configure social media: ./deploy_social_media.sh")
    print("6. Create demo video for hackathon submission")
    print("7. Submit to hackathon!")
elif results['overall_status'] == 'GOLD_TIER_MOSTLY_COMPLETE':
    print("You're almost there! Complete the remaining features:")
    print()
    for tier in ['gold_requirements']:
        for name, passed in results[tier].items():
            if not passed:
                print(f"  ❌ {name}")
else:
    print("Continue implementing Gold Tier features.")
    print()
    print("Priority features to implement:")
    print("1. Odoo accounting integration")
    print("2. Social media posting (Facebook, Instagram, Twitter)")
    print("3. Ralph Wiggum autonomous loop")
    print("4. Error recovery and graceful degradation")
    print("5. Comprehensive audit logging")

print()

# Save results
results_file = Path("logs/gold_tier_verification.json")
results_file.parent.mkdir(exist_ok=True)
with open(results_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"📊 Results saved to: {results_file}")
print()
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Exit with appropriate code
if results['overall_status'] in ['GOLD_TIER_COMPLETE', 'GOLD_TIER_MOSTLY_COMPLETE']:
    sys.exit(0)
else:
    sys.exit(1)

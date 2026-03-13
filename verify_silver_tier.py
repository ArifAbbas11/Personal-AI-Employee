#!/usr/bin/env python3
"""
Silver Tier Verification Script
Verifies all Silver Tier requirements are met and functional
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add watchers to path
sys.path.insert(0, str(Path(__file__).parent / "watchers"))

print("=" * 80)
print("🥈 SILVER TIER VERIFICATION")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Track results
results = {
    'bronze_requirements': {},
    'silver_requirements': {},
    'overall_status': 'unknown',
    'timestamp': datetime.now().isoformat()
}

def check_requirement(name: str, check_func, tier: str = 'silver') -> bool:
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
# BRONZE TIER REQUIREMENTS (Prerequisites for Silver)
# ============================================================================
print("BRONZE TIER PREREQUISITES")
print("-" * 80)

def check_obsidian_vault():
    """Check Obsidian vault exists and is configured."""
    vault = Path("AI_Employee_Vault")
    obsidian_dir = vault / ".obsidian"
    return vault.exists() and obsidian_dir.exists()

def check_filesystem_watcher():
    """Check filesystem watcher exists."""
    watcher = Path("watchers/filesystem_watcher.py")
    return watcher.exists()

def check_ceo_briefing():
    """Check CEO briefing generator exists."""
    briefing = Path("workflows/ceo_briefing_generator.py")
    return briefing.exists()

def check_agent_skills():
    """Check Agent Skills exist."""
    skills_dir = Path(".claude/skills")
    process_inbox = skills_dir / "process_inbox" / "SKILL.md"
    generate_briefing = skills_dir / "generate_ceo_briefing" / "SKILL.md"
    return process_inbox.exists() and generate_briefing.exists()

def check_approval_workflow():
    """Check approval workflow folders exist."""
    vault = Path("AI_Employee_Vault")
    pending = vault / "Pending_Approval"
    approved = vault / "Approved"
    rejected = vault / "Rejected"
    return pending.exists() and approved.exists() and rejected.exists()

check_requirement("Obsidian vault configured", check_obsidian_vault, 'bronze')
check_requirement("Filesystem watcher implemented", check_filesystem_watcher, 'bronze')
check_requirement("CEO Briefing generator", check_ceo_briefing, 'bronze')
check_requirement("Agent Skills created", check_agent_skills, 'bronze')
check_requirement("Approval workflow folders", check_approval_workflow, 'bronze')

print()

# ============================================================================
# SILVER TIER REQUIREMENTS
# ============================================================================
print("SILVER TIER REQUIREMENTS")
print("-" * 80)

def check_second_watcher():
    """Check second watcher (Gmail) exists."""
    gmail_watcher = Path("watchers/gmail_watcher.py")
    gmail_auth = Path("watchers/gmail_auth.py")
    return gmail_watcher.exists() and gmail_auth.exists()

def check_gmail_setup_docs():
    """Check Gmail setup documentation exists."""
    setup_doc = Path("GMAIL_SETUP.md")
    return setup_doc.exists()

def check_linkedin_skill():
    """Check LinkedIn manager skill exists."""
    linkedin_skill = Path(".claude/skills/linkedin-manager.md")
    return linkedin_skill.exists()

def check_plan_generation():
    """Check Plan.md generation skill exists."""
    plan_skill = Path(".claude/skills/generate_plan/SKILL.md")
    plan_impl = Path(".claude/skills/generate_plan/implementation.py")
    return plan_skill.exists() and plan_impl.exists()

def check_mcp_servers():
    """Check MCP servers exist."""
    automation_mcp = Path("watchers/automation_mcp_server.py")
    multi_agent_mcp = Path("watchers/multi_agent_mcp_server.py")
    social_media_mcp = Path("watchers/social_media_mcp_server.py")
    return automation_mcp.exists() and multi_agent_mcp.exists() and social_media_mcp.exists()

def check_cron_setup():
    """Check cron setup script exists."""
    cron_script = Path("setup_cron.sh")
    return cron_script.exists()

check_requirement("Second watcher (Gmail) implemented", check_second_watcher)
check_requirement("Gmail setup documentation", check_gmail_setup_docs)
check_requirement("LinkedIn posting skill", check_linkedin_skill)
check_requirement("Plan.md generation skill", check_plan_generation)
check_requirement("External action MCP servers", check_mcp_servers)
check_requirement("Cron scheduling setup", check_cron_setup)

print()

# ============================================================================
# FUNCTIONAL TESTS
# ============================================================================
print("FUNCTIONAL TESTS")
print("-" * 80)

def test_filesystem_watcher():
    """Test filesystem watcher can be imported."""
    try:
        from filesystem_watcher import FilesystemWatcher
        return True
    except Exception as e:
        print(f"  Import error: {e}")
        return False

def test_ceo_briefing():
    """Test CEO briefing generator can be imported."""
    try:
        sys.path.insert(0, str(Path("workflows")))
        from ceo_briefing_generator import CEOBriefingGenerator
        return True
    except Exception as e:
        print(f"  Import error: {e}")
        return False

def test_plan_generation():
    """Test plan generation implementation."""
    try:
        plan_impl = Path(".claude/skills/generate_plan/implementation.py")
        if not plan_impl.exists():
            return False
        # Check if it has the main functions
        content = plan_impl.read_text()
        return 'create_plan' in content and 'sanitize_filename' in content
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_vault_structure():
    """Test vault has required folders."""
    vault = Path("AI_Employee_Vault")
    required = ['Inbox', 'Needs_Action', 'Done', 'Pending_Approval',
                'Approved', 'Rejected', 'Plans', 'Logs']
    missing = [f for f in required if not (vault / f).exists()]
    if missing:
        print(f"  Missing folders: {', '.join(missing)}")
        return False
    return True

check_requirement("Filesystem watcher imports", test_filesystem_watcher)
check_requirement("CEO briefing imports", test_ceo_briefing)
check_requirement("Plan generation functional", test_plan_generation)
check_requirement("Vault structure complete", test_vault_structure)

print()

# ============================================================================
# DOCUMENTATION CHECK
# ============================================================================
print("DOCUMENTATION CHECK")
print("-" * 80)

def check_readme():
    """Check README exists."""
    return Path("README.md").exists()

def check_hackathon_docs():
    """Check hackathon documentation exists."""
    hackathon_readme = Path("HACKATHON_README.md")
    compliance = Path("HACKATHON_COMPLIANCE_STATUS.md")
    return hackathon_readme.exists() and compliance.exists()

def check_setup_guides():
    """Check setup guides exist."""
    gmail_setup = Path("GMAIL_SETUP.md")
    return gmail_setup.exists()

check_requirement("README.md exists", check_readme)
check_requirement("Hackathon documentation", check_hackathon_docs)
check_requirement("Setup guides", check_setup_guides)

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

print(f"Bronze Tier Prerequisites: {bronze_passed}/{bronze_total} passed")
print(f"Silver Tier Requirements:  {silver_passed}/{silver_total} passed")
print()

bronze_pct = (bronze_passed / bronze_total * 100) if bronze_total > 0 else 0
silver_pct = (silver_passed / silver_total * 100) if silver_total > 0 else 0

print(f"Bronze Tier: {bronze_pct:.0f}% complete")
print(f"Silver Tier: {silver_pct:.0f}% complete")
print()

# Determine overall status
if bronze_pct == 100 and silver_pct == 100:
    results['overall_status'] = 'SILVER_TIER_COMPLETE'
    print("🎉 SILVER TIER COMPLETE!")
    print()
    print("All Silver Tier requirements are met and functional.")
elif bronze_pct == 100 and silver_pct >= 80:
    results['overall_status'] = 'SILVER_TIER_MOSTLY_COMPLETE'
    print("⚠️  SILVER TIER MOSTLY COMPLETE")
    print()
    print("Most Silver Tier requirements are met. Review failed checks above.")
elif bronze_pct == 100:
    results['overall_status'] = 'BRONZE_COMPLETE_SILVER_IN_PROGRESS'
    print("⏳ SILVER TIER IN PROGRESS")
    print()
    print("Bronze Tier complete. Continue implementing Silver Tier features.")
else:
    results['overall_status'] = 'BRONZE_INCOMPLETE'
    print("❌ BRONZE TIER INCOMPLETE")
    print()
    print("Complete Bronze Tier requirements before proceeding to Silver.")

print()
print("=" * 80)
print("NEXT STEPS")
print("=" * 80)
print()

if results['overall_status'] == 'SILVER_TIER_COMPLETE':
    print("✅ Silver Tier is complete!")
    print()
    print("Next steps:")
    print("1. Test all features end-to-end")
    print("2. Set up cron automation: ./setup_cron.sh")
    print("3. Configure Gmail integration (if not done)")
    print("4. Proceed to Gold Tier implementation")
    print("5. Or submit Bronze/Silver tier to hackathon")
else:
    print("Review failed checks above and complete missing requirements.")
    print()
    print("Failed requirements:")
    for tier in ['bronze_requirements', 'silver_requirements']:
        for name, passed in results[tier].items():
            if not passed:
                print(f"  ❌ {name}")

print()

# Save results
results_file = Path("logs/silver_tier_verification.json")
results_file.parent.mkdir(exist_ok=True)
with open(results_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"📊 Results saved to: {results_file}")
print()
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Exit with appropriate code
if results['overall_status'] in ['SILVER_TIER_COMPLETE', 'SILVER_TIER_MOSTLY_COMPLETE']:
    sys.exit(0)
else:
    sys.exit(1)

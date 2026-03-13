#!/usr/bin/env python3
"""
Generate Plan Skill - Implementation
Creates structured Plan.md files for complex tasks
"""

import sys
from pathlib import Path
from datetime import datetime
import re

# Add watchers to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "watchers"))


def sanitize_filename(text: str, max_length: int = 50) -> str:
    """Convert text to safe filename."""
    # Remove special characters
    safe = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with underscores
    safe = re.sub(r'[-\s]+', '_', safe)
    # Truncate
    return safe[:max_length].strip('_')


def create_plan(task_description: str, vault_path: str = None) -> Path:
    """
    Create a structured plan for a task.

    Args:
        task_description: Description of the task to plan
        vault_path: Path to Obsidian vault (optional)

    Returns:
        Path to created plan file
    """
    if vault_path is None:
        vault_path = Path(__file__).parent.parent.parent / "AI_Employee_Vault"
    else:
        vault_path = Path(vault_path)

    plans_dir = vault_path / "Plans"
    plans_dir.mkdir(exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_task = sanitize_filename(task_description)
    filename = f"PLAN_{timestamp}_{safe_task}.md"
    plan_file = plans_dir / filename

    # Create plan template
    now = datetime.now().isoformat()

    content = f"""---
type: plan
task: {task_description}
created: {now}
status: in_progress
priority: medium
estimated_time: TBD
---

# Plan: {task_description}

## Objective
[Clear statement of what needs to be accomplished]

## Context
[Background information, constraints, requirements]

## Prerequisites
- [ ] Prerequisite 1
- [ ] Prerequisite 2

## Implementation Steps

### Phase 1: [Phase Name]
- [ ] Step 1.1: [Description]
- [ ] Step 1.2: [Description]
- [ ] Step 1.3: [Description]

### Phase 2: [Phase Name]
- [ ] Step 2.1: [Description]
- [ ] Step 2.2: [Description]

### Phase 3: [Phase Name]
- [ ] Step 3.1: [Description]
- [ ] Step 3.2: [Description]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Testing Plan
- [ ] Test 1
- [ ] Test 2

## Risks and Mitigation
- **Risk 1:** [Description]
  - Mitigation: [Strategy]
- **Risk 2:** [Description]
  - Mitigation: [Strategy]

## Notes
[Any additional context, decisions, or considerations]

---
**Plan Status:** In Progress
**Last Updated:** {now}
"""

    # Write plan file
    with open(plan_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return plan_file


def main():
    """Main entry point for generate_plan skill."""
    if len(sys.argv) < 2:
        print("Usage: python implementation.py <task_description> [vault_path]")
        print("Example: python implementation.py 'Implement Gmail integration'")
        sys.exit(1)

    task_description = sys.argv[1]
    vault_path = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"📋 Creating plan for: {task_description}")
    print()

    try:
        plan_file = create_plan(task_description, vault_path)

        print(f"✅ Plan created successfully!")
        print(f"📄 File: {plan_file}")
        print()
        print("📝 Next steps:")
        print("1. Open the plan file in Obsidian")
        print("2. Fill in the sections with specific details")
        print("3. Break down phases into actionable steps")
        print("4. Identify prerequisites and risks")
        print("5. Define clear success criteria")
        print()
        print("💡 Tip: Use Claude to help fill in the plan details:")
        print(f'   claude "Fill in the plan at {plan_file} with detailed steps"')

    except Exception as e:
        print(f"❌ Error creating plan: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

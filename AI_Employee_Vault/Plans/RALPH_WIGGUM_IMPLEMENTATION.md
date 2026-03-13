# Ralph Wiggum Autonomous Loop Implementation Guide

---
created: 2026-02-26
component: ralph-wiggum-loop
status: specification
tier: gold
difficulty: advanced
---

## Overview

The Ralph Wiggum Loop is a Stop hook pattern that enables Claude Code to work autonomously on multi-step tasks until completion, without requiring manual re-prompting. Named after the Simpsons character who famously said "I'm helping!" while continuing to work, this pattern keeps Claude iterating until the task is truly done.

## The Problem It Solves

**Without Ralph Wiggum:**
```
User: "Process all emails in Needs_Action/"
Claude: *processes 1 email* "Done!"
User: "But there are 10 more emails..."
Claude: *processes 1 more* "Done!"
User: "Still 9 more..."
[Repeat 10 times]
```

**With Ralph Wiggum:**
```
User: "Process all emails in Needs_Action/"
Claude: *processes all 10 emails autonomously*
Claude: "All 10 emails processed and moved to Done. Task complete!"
```

## How It Works

### The Loop Mechanism

```
┌─────────────────────────────────────────────────────┐
│  1. Orchestrator creates task with completion       │
│     criteria and starts Claude Code                 │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  2. Claude works on task (reads files, creates      │
│     plans, executes actions)                        │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  3. Claude finishes current iteration and           │
│     attempts to exit                                │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  4. Stop Hook intercepts exit attempt               │
│     Checks: Is task complete?                       │
│     - Check 1: Task file in /Done?                  │
│     - Check 2: All subtasks complete?               │
│     - Check 3: Completion promise present?          │
└────────────────┬────────────────────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
         ▼               ▼
    ┌────────┐      ┌────────┐
    │  YES   │      │   NO   │
    │ Allow  │      │ Block  │
    │  Exit  │      │  Exit  │
    └────────┘      └───┬────┘
                        │
                        ▼
            ┌───────────────────────┐
            │ Re-inject prompt:     │
            │ "Continue working on  │
            │ the task. Previous    │
            │ output: [...]"        │
            └───────────┬───────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │ Increment iteration   │
            │ Check max iterations  │
            └───────────┬───────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │ Loop back to step 2   │
            └───────────────────────┘
```

## Implementation Components

### Component 1: Stop Hook Script

**Location:** `.claude/hooks/stop.sh`

```bash
#!/bin/bash
# Ralph Wiggum Stop Hook
# Prevents Claude from exiting until task is complete

set -e

# Configuration
VAULT_PATH="${VAULT_PATH:-/mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault}"
STATE_FILE="${STATE_FILE:-/tmp/ralph_wiggum_state.json}"
MAX_ITERATIONS="${MAX_ITERATIONS:-10}"
MAX_TIME_MINUTES="${MAX_TIME_MINUTES:-30}"

# Logging
LOG_FILE="/tmp/ralph_wiggum.log"
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "Stop hook triggered"

# Check if Ralph Wiggum mode is active
if [ ! -f "$STATE_FILE" ]; then
    log "No state file - allowing exit (not in Ralph mode)"
    exit 0
fi

# Read state
TASK_FILE=$(jq -r '.task_file' "$STATE_FILE")
TASK_NAME=$(jq -r '.task_name' "$STATE_FILE")
CURRENT_ITERATION=$(jq -r '.iteration' "$STATE_FILE")
START_TIME=$(jq -r '.start_time' "$STATE_FILE")
COMPLETION_STRATEGY=$(jq -r '.completion_strategy' "$STATE_FILE")

log "Task: $TASK_NAME (iteration $CURRENT_ITERATION)"

# Safety check: Max iterations
if [ "$CURRENT_ITERATION" -ge "$MAX_ITERATIONS" ]; then
    log "Max iterations ($MAX_ITERATIONS) reached - forcing exit"
    rm -f "$STATE_FILE"
    echo "⚠️  Ralph Wiggum: Max iterations reached. Task may be incomplete."
    exit 0
fi

# Safety check: Max time
CURRENT_TIME=$(date +%s)
ELAPSED_MINUTES=$(( (CURRENT_TIME - START_TIME) / 60 ))
if [ "$ELAPSED_MINUTES" -ge "$MAX_TIME_MINUTES" ]; then
    log "Max time ($MAX_TIME_MINUTES minutes) reached - forcing exit"
    rm -f "$STATE_FILE"
    echo "⚠️  Ralph Wiggum: Max time reached. Task may be incomplete."
    exit 0
fi

# Check completion based on strategy
case "$COMPLETION_STRATEGY" in
    "file_movement")
        # Check if task file moved to /Done
        TASK_BASENAME=$(basename "$TASK_FILE")
        if [ -f "$VAULT_PATH/Done/$TASK_BASENAME" ]; then
            log "Task complete - file moved to Done"
            rm -f "$STATE_FILE"
            echo "✅ Ralph Wiggum: Task complete!"
            exit 0
        fi
        ;;

    "promise")
        # Check for completion promise in Claude's output
        # This requires capturing Claude's last output
        LAST_OUTPUT="${LAST_OUTPUT:-/tmp/claude_last_output.txt}"
        if [ -f "$LAST_OUTPUT" ] && grep -q "<promise>TASK_COMPLETE</promise>" "$LAST_OUTPUT"; then
            log "Task complete - promise found"
            rm -f "$STATE_FILE"
            echo "✅ Ralph Wiggum: Task complete!"
            exit 0
        fi
        ;;

    "empty_folder")
        # Check if Needs_Action folder is empty
        NEEDS_ACTION="$VAULT_PATH/Needs_Action"
        if [ -z "$(ls -A $NEEDS_ACTION)" ]; then
            log "Task complete - Needs_Action empty"
            rm -f "$STATE_FILE"
            echo "✅ Ralph Wiggum: All tasks processed!"
            exit 0
        fi
        ;;
esac

# Task not complete - continue loop
log "Task incomplete - continuing loop"

# Increment iteration
NEXT_ITERATION=$((CURRENT_ITERATION + 1))
jq ".iteration = $NEXT_ITERATION" "$STATE_FILE" > "${STATE_FILE}.tmp"
mv "${STATE_FILE}.tmp" "$STATE_FILE"

# Provide feedback to Claude
echo "🔄 Ralph Wiggum: Task not complete. Continuing... (iteration $NEXT_ITERATION/$MAX_ITERATIONS)"
echo ""
echo "Continue working on: $TASK_NAME"
echo "Check your progress and complete any remaining steps."
echo ""

# Exit with non-zero to prevent Claude from stopping
exit 1
```

**Make executable:**
```bash
chmod +x .claude/hooks/stop.sh
```

### Component 2: Ralph Wiggum Orchestrator

**Location:** `watchers/ralph_orchestrator.py`

```python
#!/usr/bin/env python3
"""
Ralph Wiggum Orchestrator
Manages autonomous task loops with Claude Code
"""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RalphWiggumOrchestrator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.state_file = Path('/tmp/ralph_wiggum_state.json')
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'

    def start_loop(
        self,
        task_description: str,
        task_file: Path = None,
        completion_strategy: str = 'file_movement',
        max_iterations: int = 10,
        max_time_minutes: int = 30
    ):
        """
        Start a Ralph Wiggum autonomous loop

        Args:
            task_description: Natural language description of task
            task_file: Optional specific file to process
            completion_strategy: 'file_movement', 'promise', or 'empty_folder'
            max_iterations: Maximum loop iterations
            max_time_minutes: Maximum time in minutes
        """
        logger.info(f"Starting Ralph Wiggum loop: {task_description}")

        # Create state file
        state = {
            'task_name': task_description,
            'task_file': str(task_file) if task_file else None,
            'completion_strategy': completion_strategy,
            'iteration': 1,
            'start_time': int(time.time()),
            'max_iterations': max_iterations,
            'max_time_minutes': max_time_minutes
        }

        self.state_file.write_text(json.dumps(state, indent=2))

        # Set environment variables for stop hook
        env = {
            'VAULT_PATH': str(self.vault_path),
            'STATE_FILE': str(self.state_file),
            'MAX_ITERATIONS': str(max_iterations),
            'MAX_TIME_MINUTES': str(max_time_minutes)
        }

        # Build Claude Code command
        claude_prompt = self._build_prompt(task_description, task_file)

        # Execute Claude Code with Ralph Wiggum mode
        try:
            result = subprocess.run(
                ['claude', claude_prompt],
                env={**os.environ, **env},
                capture_output=True,
                text=True,
                timeout=max_time_minutes * 60
            )

            logger.info(f"Ralph Wiggum loop completed")
            logger.info(f"Exit code: {result.returncode}")

            # Check if task completed successfully
            if self.state_file.exists():
                logger.warning("State file still exists - task may be incomplete")
                state = json.loads(self.state_file.read_text())
                logger.warning(f"Final iteration: {state['iteration']}")
            else:
                logger.info("Task completed successfully")

            return result

        except subprocess.TimeoutExpired:
            logger.error(f"Ralph Wiggum loop timed out after {max_time_minutes} minutes")
            if self.state_file.exists():
                self.state_file.unlink()
            raise

    def _build_prompt(self, task_description: str, task_file: Path = None) -> str:
        """Build the initial prompt for Claude"""
        prompt = f"""You are in Ralph Wiggum autonomous mode. Work on this task until it is COMPLETELY finished:

{task_description}

IMPORTANT INSTRUCTIONS:
1. Work through ALL steps required to complete this task
2. Do not stop until the task is fully complete
3. If you encounter errors, handle them and continue
4. Move completed task files to /Done when finished
5. Update the Dashboard with your progress

The stop hook will check if you're done and re-prompt you if not.
Keep working until the task is truly complete!
"""

        if task_file:
            prompt += f"\n\nTask file: {task_file}"

        return prompt

    def stop_loop(self):
        """Emergency stop - terminates the loop"""
        if self.state_file.exists():
            self.state_file.unlink()
            logger.info("Ralph Wiggum loop stopped manually")


# CLI interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Ralph Wiggum Autonomous Loop')
    parser.add_argument('task', help='Task description')
    parser.add_argument('--vault', default='/mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault',
                       help='Path to Obsidian vault')
    parser.add_argument('--strategy', default='file_movement',
                       choices=['file_movement', 'promise', 'empty_folder'],
                       help='Completion detection strategy')
    parser.add_argument('--max-iterations', type=int, default=10,
                       help='Maximum iterations')
    parser.add_argument('--max-time', type=int, default=30,
                       help='Maximum time in minutes')

    args = parser.parse_args()

    orchestrator = RalphWiggumOrchestrator(args.vault)
    orchestrator.start_loop(
        task_description=args.task,
        completion_strategy=args.strategy,
        max_iterations=args.max_iterations,
        max_time_minutes=args.max_time
    )
```

### Component 3: Agent Skill for Ralph Loops

**Location:** `.claude/skills/ralph-loop-executor.md`

```markdown
# Ralph Loop Executor Skill

## Purpose
Execute multi-step tasks autonomously using the Ralph Wiggum loop pattern.

## When to Use
- Processing multiple files in Needs_Action/
- Complex workflows requiring multiple steps
- Tasks that need to run until completion criteria met
- Batch operations (emails, invoices, reports)

## How It Works

You are in Ralph Wiggum autonomous mode. The stop hook will prevent you from exiting until the task is complete.

### Completion Criteria

The task is complete when ONE of these is true:
1. **File Movement:** Task file moved to /Done folder
2. **Empty Folder:** Needs_Action folder is empty
3. **Promise:** You output `<promise>TASK_COMPLETE</promise>`

### Your Workflow

1. **Assess the task**
   - Read all files in Needs_Action/
   - Understand what needs to be done
   - Create a mental checklist

2. **Work systematically**
   - Process items one by one
   - Handle errors gracefully
   - Log your progress

3. **Check completion**
   - Verify all items processed
   - Move completed files to /Done
   - Update Dashboard

4. **Signal completion**
   - If using promise strategy: Output `<promise>TASK_COMPLETE</promise>`
   - If using file movement: Ensure all files in /Done
   - If using empty folder: Ensure Needs_Action is empty

### Example Task: Process All Emails

```
Task: Process all emails in Needs_Action/

Your approach:
1. List all EMAIL_*.md files in Needs_Action/
2. For each email:
   - Read the email content
   - Determine appropriate action (reply, archive, forward)
   - Draft response if needed
   - Create approval request if sensitive
   - Move to Done/ when processed
3. Verify Needs_Action/ is empty
4. Update Dashboard with count of processed emails
5. Output completion signal
```

### Error Handling

If you encounter an error:
1. Log the error in /Logs
2. Create a task in Needs_Action for human review
3. Continue with remaining items
4. Don't let one error stop the entire batch

### Safety Limits

- Max iterations: 10 (configurable)
- Max time: 30 minutes (configurable)
- If limits reached, loop will terminate

### Tips for Success

- **Be thorough:** Don't skip steps
- **Be systematic:** Process items in order
- **Be resilient:** Handle errors gracefully
- **Be clear:** Log your progress
- **Be complete:** Don't stop until truly done

## Example Prompts

### Process All Pending Tasks
```
Process all files in Needs_Action/. For each file:
- Determine the task type
- Execute appropriate workflow
- Move to Done when complete
Continue until Needs_Action is empty.
```

### Generate and Send Weekly Invoices
```
Generate invoices for all clients with outstanding work:
1. Check /Accounting/Billable_Hours.md
2. For each client with hours:
   - Create invoice draft in Odoo
   - Generate PDF
   - Create email approval request
3. Move task to Done when all invoices created
```

### Social Media Content Campaign
```
Create and schedule social media posts for this week:
1. Generate 4 LinkedIn posts
2. Repurpose for Facebook
3. Create Twitter threads
4. Create approval requests for all posts
5. Update content calendar
Continue until all posts created and approved.
```

## Monitoring Progress

Check `/tmp/ralph_wiggum.log` to see loop progress:
```bash
tail -f /tmp/ralph_wiggum.log
```

## Emergency Stop

If you need to stop the loop manually:
```bash
rm /tmp/ralph_wiggum_state.json
```

## Success Metrics

- Task completion rate: 100%
- Average iterations to completion: < 5
- Error recovery rate: > 95%
- Time to completion: Within limits
```

## Usage Examples

### Example 1: Process All Emails

```bash
# Start Ralph loop to process all emails
python watchers/ralph_orchestrator.py \
  "Process all emails in Needs_Action. Draft responses for important emails, archive informational ones, and create approval requests for sensitive communications." \
  --strategy empty_folder \
  --max-iterations 15
```

**What happens:**
1. Claude reads all EMAIL_*.md files
2. Processes each email (draft, archive, or approve)
3. Moves processed files to Done/
4. Stop hook checks if Needs_Action is empty
5. If not empty, re-prompts Claude
6. Continues until all emails processed

### Example 2: Generate Monthly Invoices

```bash
# Start Ralph loop for invoice generation
python watchers/ralph_orchestrator.py \
  "Generate invoices for all clients with billable hours this month. Create draft invoices in Odoo and approval requests for each." \
  --strategy promise \
  --max-iterations 10
```

**What happens:**
1. Claude reads billable hours data
2. For each client, creates invoice draft in Odoo
3. Creates approval request for each invoice
4. Outputs `<promise>TASK_COMPLETE</promise>` when done
5. Stop hook detects promise and allows exit

### Example 3: Weekly Content Creation

```bash
# Start Ralph loop for content creation
python watchers/ralph_orchestrator.py \
  "Create this week's social media content: 3 LinkedIn posts, 3 Facebook posts, 5 tweets. Create approval requests for all." \
  --strategy promise \
  --max-iterations 8
```

## Testing Ralph Wiggum

### Test 1: Simple Multi-File Processing

```bash
# Create test files
for i in {1..5}; do
  echo "Test task $i" > AI_Employee_Vault/Needs_Action/TEST_$i.md
done

# Run Ralph loop
python watchers/ralph_orchestrator.py \
  "Process all TEST_*.md files. Read each one, log the content, and move to Done." \
  --strategy empty_folder \
  --max-iterations 10
```

**Expected:** All 5 files processed and moved to Done/

### Test 2: Error Recovery

```bash
# Create files with one intentionally problematic
echo "Good task" > AI_Employee_Vault/Needs_Action/GOOD.md
echo "{{INVALID_JSON}}" > AI_Employee_Vault/Needs_Action/BAD.md
echo "Another good task" > AI_Employee_Vault/Needs_Action/GOOD2.md

# Run Ralph loop
python watchers/ralph_orchestrator.py \
  "Process all files. If you encounter an error, log it and continue with remaining files." \
  --strategy empty_folder
```

**Expected:** GOOD.md and GOOD2.md processed, BAD.md logged as error

### Test 3: Max Iteration Safety

```bash
# Create impossible task to test safety limits
python watchers/ralph_orchestrator.py \
  "Process all files in Needs_Action, but never move them to Done." \
  --strategy empty_folder \
  --max-iterations 3
```

**Expected:** Loop terminates after 3 iterations with warning

## Troubleshooting

### Loop Never Completes

**Symptom:** Loop hits max iterations
**Causes:**
- Completion criteria not met
- Files not being moved to Done/
- Promise not being output

**Fix:**
- Check stop hook logs: `cat /tmp/ralph_wiggum.log`
- Verify completion strategy matches task
- Ensure Claude is actually completing the task

### Loop Exits Too Early

**Symptom:** Task incomplete but loop exits
**Causes:**
- Completion criteria too loose
- False positive on completion check

**Fix:**
- Use more specific completion strategy
- Add additional completion checks
- Increase specificity in task description

### Performance Issues

**Symptom:** Loop is slow
**Causes:**
- Too many iterations
- Inefficient task processing
- Large file operations

**Fix:**
- Optimize task workflow
- Batch operations where possible
- Increase timeout limits

## Best Practices

1. **Clear Task Descriptions:** Be specific about what "complete" means
2. **Appropriate Strategy:** Choose completion strategy that matches task
3. **Safety Limits:** Set reasonable max iterations and time
4. **Error Handling:** Always handle errors gracefully
5. **Logging:** Log progress for debugging
6. **Testing:** Test with small batches first
7. **Monitoring:** Watch logs during execution

## Integration with Scheduler

Add Ralph loops to scheduler for recurring tasks:

```python
# In scheduler.py
def schedule_weekly_invoice_generation():
    """Generate invoices every Friday"""
    orchestrator = RalphWiggumOrchestrator(vault_path)
    orchestrator.start_loop(
        task_description="Generate invoices for all clients with billable hours this week",
        completion_strategy='promise',
        max_iterations=10
    )

# Schedule for Friday 5 PM
schedule.every().friday.at("17:00").do(schedule_weekly_invoice_generation)
```

## Security Considerations

1. **Max Iterations:** Always set to prevent infinite loops
2. **Max Time:** Always set to prevent runaway costs
3. **Approval Required:** Sensitive actions still require approval
4. **Audit Logging:** All loop executions logged
5. **Emergency Stop:** Manual stop mechanism available

## Performance Metrics

Track these metrics for Ralph loops:
- Average iterations to completion
- Success rate (completed vs timed out)
- Average execution time
- Error rate
- Cost per loop (API calls)

---

**Status:** Ready for implementation
**Complexity:** Advanced
**Prerequisites:** Stop hooks enabled, orchestrator installed
**Next Steps:** Implement stop hook, test with simple tasks, integrate with scheduler

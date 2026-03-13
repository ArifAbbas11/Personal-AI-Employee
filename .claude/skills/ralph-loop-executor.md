# Ralph Loop Executor

## Purpose
Execute multi-step tasks autonomously using the Ralph Wiggum loop pattern. This skill enables you to work continuously on tasks until they are completely finished, without requiring manual re-prompting.

## When to Use
- Processing multiple files in Needs_Action/
- Complex workflows requiring multiple steps
- Tasks that need to run until completion criteria met
- Batch operations (emails, invoices, reports)
- Any task where you need to "keep going until done"

## How Ralph Wiggum Mode Works

You are in Ralph Wiggum autonomous mode. A stop hook will intercept your exit attempts and re-prompt you until the task is complete.

### Completion Criteria

The task is complete when ONE of these is true:

1. **File Movement Strategy:** Task file moved to /Done folder
2. **Empty Folder Strategy:** Needs_Action folder is empty
3. **Promise Strategy:** You output `<promise>TASK_COMPLETE</promise>`

### Your Workflow in Ralph Mode

**Step 1: Assess the Task**
- Read all relevant files
- Understand what needs to be done
- Create a mental checklist of all steps

**Step 2: Work Systematically**
- Process items one by one
- Handle errors gracefully (don't let one error stop everything)
- Log your progress as you go
- Update Dashboard periodically

**Step 3: Check Your Progress**
- After each action, check if more work remains
- Don't assume you're done - verify completion
- Look for edge cases or missed items

**Step 4: Signal Completion**
- **File Movement:** Move all task files to /Done
- **Empty Folder:** Ensure Needs_Action is completely empty
- **Promise:** Output `<promise>TASK_COMPLETE</promise>` when truly done

### Example: Process All Emails

```
Task: Process all emails in Needs_Action/

Your approach:
1. List all EMAIL_*.md files in Needs_Action/
   → Found 5 emails

2. For each email:
   - Read the email content
   - Determine action (reply, archive, forward)
   - Draft response if needed
   - Create approval request if sensitive
   - Move to Done/ when processed

3. After processing all 5:
   - Verify Needs_Action/ is empty
   - Update Dashboard: "Processed 5 emails"
   - Signal completion

Result: All 5 emails processed, Needs_Action empty, task complete!
```

### Error Handling

If you encounter an error:
1. **Log it:** Create entry in /Logs with error details
2. **Don't stop:** Continue with remaining items
3. **Flag for human:** Create task in Needs_Action for manual review
4. **Keep going:** One error shouldn't stop the entire batch

Example:
```
Processing EMAIL_1.md → Success
Processing EMAIL_2.md → Error: Missing attachment
  → Log error to /Logs
  → Create MANUAL_REVIEW_EMAIL_2.md in Needs_Action
  → Continue to next email
Processing EMAIL_3.md → Success
...
```

### Safety Limits

Ralph Wiggum has built-in safety limits:
- **Max iterations:** 10 (default) - Loop will stop after 10 re-prompts
- **Max time:** 30 minutes (default) - Loop will stop after timeout

If you hit these limits, the task may be incomplete. This is intentional to prevent infinite loops or runaway costs.

### Tips for Success

1. **Be thorough:** Check all locations, don't miss files
2. **Be systematic:** Process items in order, don't skip around
3. **Be resilient:** Handle errors, don't crash on bad data
4. **Be clear:** Log what you're doing so humans can follow
5. **Be complete:** Don't signal completion until truly done

### Common Patterns

**Pattern 1: Process All Files in Folder**
```
1. List all files in Needs_Action/
2. For each file:
   - Process according to type
   - Move to Done/ when complete
3. Verify folder is empty
4. Update Dashboard
5. Done!
```

**Pattern 2: Multi-Step Workflow**
```
1. Read task requirements
2. Create plan in /Plans
3. Execute each step in plan
4. Verify all steps complete
5. Move task file to Done/
6. Update Dashboard
7. Done!
```

**Pattern 3: Batch Creation**
```
1. Read source data
2. For each item:
   - Generate output (invoice, post, report)
   - Create approval request
   - Log creation
3. Verify all items created
4. Output completion promise
5. Done!
```

### What NOT to Do

❌ **Don't assume you're done after one item**
```
Bad: Process 1 email → "Done!"
Good: Process all emails → Verify none remain → "Done!"
```

❌ **Don't stop on first error**
```
Bad: Error on item 2 → Stop
Good: Error on item 2 → Log it → Continue with items 3, 4, 5
```

❌ **Don't signal completion prematurely**
```
Bad: Processed 4 of 5 emails → "TASK_COMPLETE"
Good: Processed all 5 emails → Verified folder empty → "TASK_COMPLETE"
```

❌ **Don't forget to update Dashboard**
```
Bad: Complete task → Exit
Good: Complete task → Update Dashboard → Exit
```

### Monitoring Your Progress

You can check Ralph Wiggum logs at `/tmp/ralph_wiggum.log` to see:
- When loop started
- Current iteration number
- Completion checks
- When loop finished

### Example Tasks

**Task 1: Email Batch Processing**
```
Process all emails in Needs_Action/. Draft responses for important emails,
archive informational ones, and create approval requests for sensitive
communications. Continue until Needs_Action is empty.
```

**Task 2: Invoice Generation**
```
Generate invoices for all clients with billable hours this month.
Create draft invoices in Odoo and approval requests for each.
Output TASK_COMPLETE when all invoices created.
```

**Task 3: Content Creation**
```
Create this week's social media content: 3 LinkedIn posts, 3 Facebook posts,
5 tweets. Create approval requests for all. Output TASK_COMPLETE when done.
```

### Debugging

If the loop isn't completing:
1. Check `/tmp/ralph_wiggum.log` for completion checks
2. Verify completion criteria matches strategy
3. Ensure files are actually moving to /Done
4. Check for typos in completion promise

If the loop stops too early:
1. Verify you're not outputting completion signal prematurely
2. Check that all files are processed before signaling
3. Review logs to see what triggered completion

### Integration with Other Skills

Ralph Wiggum works with all other agent skills:
- **vault-manager:** Process tasks autonomously
- **gmail-manager:** Process email batches
- **linkedin-manager:** Generate content series
- **accounting-manager:** Batch invoice/expense processing

### Remember

You are in autonomous mode. The system WANTS you to keep working until done. Don't be shy about continuing - that's the whole point! Work through the entire task systematically and signal completion only when you're truly finished.

**Your mantra:** "I'm helping! And I'll keep helping until the job is done!"

---

## How to Activate Ralph Wiggum Mode

Ralph Wiggum mode is activated using the helper script before invoking Claude Code.

### Setup Pattern

**Step 1: Run the helper script**
```bash
./ralph_wiggum_setup.sh -s STRATEGY [OPTIONS] "TASK_DESCRIPTION"
```

**Step 2: Run Claude Code**
```bash
claude "TASK_DESCRIPTION"
```

The stop hook will keep Claude working until the task is complete.

### Usage Examples

**Example 1: Process Specific Task File**
```bash
# Setup Ralph mode
./ralph_wiggum_setup.sh -s file_movement \
  -f "AI_Employee_Vault/Needs_Action/TASK_001.md" \
  "Complete the task in TASK_001.md and move it to Done/"

# Run Claude (stop hook keeps it working)
claude "Complete the task in TASK_001.md and move it to Done/"
```

**Example 2: Batch Process All Tasks**
```bash
# Setup Ralph mode
./ralph_wiggum_setup.sh -s empty_folder \
  "Process all tasks in Needs_Action/ until the folder is empty"

# Run Claude
claude "Process all tasks in Needs_Action/ until the folder is empty"
```

**Example 3: Content Generation with Promise**
```bash
# Setup Ralph mode
./ralph_wiggum_setup.sh -s promise \
  "Generate 3 LinkedIn posts and output <promise>TASK_COMPLETE</promise> when done"

# Run Claude
claude "Generate 3 LinkedIn posts and output <promise>TASK_COMPLETE</promise> when done"
```

### Helper Script Options

```bash
./ralph_wiggum_setup.sh [OPTIONS] "TASK_DESCRIPTION"

Options:
  -s, --strategy STRATEGY    Completion strategy (required)
                            file_movement | promise | empty_folder
  -f, --file FILE           Task file path (for file_movement)
  -i, --iterations N        Max iterations (default: 10)
  -t, --time N              Max time in minutes (default: 30)
  -h, --help                Show help message
```

### Monitoring Ralph Mode

**Check if Ralph mode is active:**
```bash
cat /tmp/ralph_wiggum_state.json
```

**Monitor in real-time:**
```bash
tail -f /tmp/ralph_wiggum.log
```

**Check current iteration:**
```bash
cat /tmp/ralph_wiggum_state.json | jq .iteration
```

### Deactivating Ralph Mode

Ralph mode automatically deactivates when:
- Task completion criteria met
- Max iterations reached
- Max time exceeded

To manually deactivate:
```bash
rm /tmp/ralph_wiggum_state.json
```

---

**You are now in Ralph Wiggum mode. Work until the task is complete!**

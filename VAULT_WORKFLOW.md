# Vault Workflow Structure

## Folder Organization

### Task Flow

```
Needs_Action/
    ↓
Pending_Approval/
    ↓ (after approval)
Approved/general/
    ↓ (after completion)
Done/general/
```

### Folder Purposes

#### Needs_Action/
Tasks that need to be processed by the AI agent or require action.

#### Pending_Approval/
Tasks that have been processed and are waiting for human approval.

#### Approved/general/
Tasks that have been approved by a human and are ready to be executed or published.

#### Done/general/
Completed general tasks that have been fully executed.

#### Done/ (other subfolders)
- `emails/` - Completed email-related tasks
- `linkedin/` - Completed LinkedIn posts
- `twitter/` - Completed tweets
- Other category-specific folders as needed

## Workflow Examples

### Example 1: General Task

1. **Create task**: `Needs_Action/TASK_001.md`
2. **AI processes**: Reads requirements, creates draft
3. **Moves to approval**: `Pending_Approval/TASK_001_DRAFT.md`
4. **Human approves**: Moves to `Approved/general/TASK_001_DRAFT.md`
5. **AI executes**: Completes the approved task
6. **Final location**: `Done/general/TASK_001.md`

### Example 2: Content Creation

1. **Create task**: `Needs_Action/CREATE_LINKEDIN_POST.md`
2. **AI generates**: Creates post draft
3. **Moves to approval**: `Pending_Approval/LINKEDIN_POST_DRAFT.md`
4. **Human approves**: Moves to `Approved/general/LINKEDIN_POST_DRAFT.md`
5. **AI publishes**: Posts to LinkedIn
6. **Final location**: `Done/linkedin/POST_20260312.md`

### Example 3: Email Response

1. **Email arrives**: `Needs_Action/EMAIL_CLIENT_INQUIRY.md`
2. **AI drafts response**: Creates reply
3. **Moves to approval**: `Pending_Approval/EMAIL_RESPONSE_DRAFT.md`
4. **Human approves**: Moves to `Approved/general/EMAIL_RESPONSE_DRAFT.md`
5. **AI sends**: Sends approved email
6. **Final location**: `Done/emails/EMAIL_CLIENT_INQUIRY.md`

## Folder Structure

```
AI_Employee_Vault/
├── Needs_Action/          # Tasks waiting to be processed
├── Pending_Approval/      # Tasks waiting for human approval
├── Approved/
│   └── general/          # Approved general tasks ready for execution
├── Done/
│   ├── general/          # Completed general tasks
│   ├── emails/           # Completed email tasks
│   ├── linkedin/         # Completed LinkedIn posts
│   └── twitter/          # Completed tweets
├── Rejected/             # Tasks that were rejected
├── Logs/                 # System logs
├── Plans/                # Planning documents
└── Summaries/            # Summary reports
```

## Task Categories

### General Tasks
- System maintenance
- Data processing
- Report generation
- Analysis tasks
- Administrative work

**Flow**: Needs_Action → Pending_Approval → Approved/general → Done/general

### Content Tasks
- Social media posts
- Blog articles
- Marketing materials

**Flow**: Needs_Action → Pending_Approval → Approved/general → Done/[platform]/

### Communication Tasks
- Email responses
- Client communications
- Internal messages

**Flow**: Needs_Action → Pending_Approval → Approved/general → Done/emails/

## Approval Process

### Manual Approval

1. Review task in `Pending_Approval/`
2. If approved: Move to `Approved/general/`
3. If rejected: Move to `Rejected/` with feedback
4. If needs revision: Move back to `Needs_Action/` with notes

### Approval Commands

```bash
# Approve a task
mv AI_Employee_Vault/Pending_Approval/TASK.md AI_Employee_Vault/Approved/general/

# Reject a task
mv AI_Employee_Vault/Pending_Approval/TASK.md AI_Employee_Vault/Rejected/

# Request revision
mv AI_Employee_Vault/Pending_Approval/TASK.md AI_Employee_Vault/Needs_Action/
```

## Ralph Groq Integration

### Process Approved Tasks

```bash
# Process all approved general tasks
./ralph_groq_setup.sh -s empty_folder \
  "Process all tasks in Approved/general/. Execute each task and move to Done/general/ when complete."
```

### Automated Workflow

```bash
# 1. Process new tasks
./ralph_groq_setup.sh -s empty_folder \
  "Process all tasks in Needs_Action/. Create drafts and move to Pending_Approval/."

# 2. Human reviews and approves (manual step)

# 3. Execute approved tasks
./ralph_groq_setup.sh -s empty_folder \
  "Process all tasks in Approved/general/. Execute and move to Done/general/."
```

## Best Practices

### Task Naming

- Use descriptive names: `EMAIL_CLIENT_UPDATE.md` not `TASK1.md`
- Include date for time-sensitive tasks: `REPORT_20260312.md`
- Use category prefixes: `EMAIL_`, `LINKEDIN_`, `DATA_`, `SYSTEM_`

### Task Metadata

Always include frontmatter:

```markdown
---
type: general|email|content|data|system
priority: high|medium|low
created: YYYY-MM-DD
category: general
approved_by: [name]
approved_date: YYYY-MM-DD
---
```

### Folder Maintenance

- Clean up old tasks monthly
- Archive completed tasks older than 90 days
- Review rejected tasks for patterns
- Monitor Pending_Approval for bottlenecks

## Automation Opportunities

### Scheduled Processing

```bash
# Cron job: Process new tasks every hour
0 * * * * cd /path/to/project && ./ralph_groq_setup.sh -s empty_folder "Process Needs_Action/"

# Cron job: Execute approved tasks every 30 minutes
*/30 * * * * cd /path/to/project && ./ralph_groq_setup.sh -s empty_folder "Process Approved/general/"
```

### Webhook Integration

Set up webhooks to trigger processing when:
- New file added to Needs_Action/
- File moved to Approved/general/
- Approval deadline approaching

## Monitoring

### Check Workflow Status

```bash
# Count tasks in each stage
echo "Needs Action: $(ls AI_Employee_Vault/Needs_Action/*.md 2>/dev/null | wc -l)"
echo "Pending Approval: $(ls AI_Employee_Vault/Pending_Approval/*.md 2>/dev/null | wc -l)"
echo "Approved: $(ls AI_Employee_Vault/Approved/general/*.md 2>/dev/null | wc -l)"
echo "Done: $(ls AI_Employee_Vault/Done/general/*.md 2>/dev/null | wc -l)"
```

### Dashboard Integration

Update Dashboard.md with workflow metrics:
- Tasks processed today
- Tasks pending approval
- Average approval time
- Completion rate

## Summary

The new workflow provides:
- ✅ Clear task progression
- ✅ Human approval checkpoint
- ✅ Organized completion tracking
- ✅ Category-based organization
- ✅ Easy automation integration

**Key Change**: `Done/processed_tasks/` → `Done/general/` for better organization and clarity.

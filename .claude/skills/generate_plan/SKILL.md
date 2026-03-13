# Generate Plan Skill

## Purpose
Break down complex tasks into structured, actionable plans with checkbox-based tracking. This skill enables systematic task decomposition and progress monitoring.

## When to Use
- Complex multi-step tasks requiring planning
- Projects with unclear implementation path
- Tasks that need to be broken into subtasks
- When you need to think through an approach before executing
- Any task where a structured plan would be helpful

## How It Works

This skill uses Claude's reasoning capabilities to:
1. Analyze the task requirements
2. Break down the task into logical steps
3. Identify dependencies and prerequisites
4. Create a structured Plan.md file with checkboxes
5. Save the plan in `AI_Employee_Vault/Plans/`

## Plan.md Format

Plans are created in a standardized format:

```markdown
---
type: plan
task: [Task description]
created: [ISO timestamp]
status: in_progress
priority: [high|medium|low]
estimated_time: [hours]
---

# Plan: [Task Name]

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
**Last Updated:** [Timestamp]
```

## Your Workflow

### Step 1: Understand the Task
- Read the task description carefully
- Identify the goal and success criteria
- Note any constraints or requirements
- Ask clarifying questions if needed

### Step 2: Analyze and Decompose
- Break the task into logical phases
- Identify dependencies between steps
- Consider prerequisites and setup requirements
- Think about potential risks and challenges

### Step 3: Create Structured Plan
- Organize steps into phases
- Make each step actionable and specific
- Add checkboxes for tracking
- Include success criteria
- Document risks and mitigation strategies

### Step 4: Save and Track
- Save plan to `AI_Employee_Vault/Plans/`
- Create corresponding task in `Needs_Action/` if needed
- Update Dashboard with plan creation
- Reference plan in related tasks

## Example: Plan for Email Integration

**Task:** "Integrate Gmail with the AI Employee system"

**Generated Plan:**

```markdown
---
type: plan
task: Integrate Gmail with AI Employee system
created: 2026-03-03T16:00:00Z
status: in_progress
priority: high
estimated_time: 4-6 hours
---

# Plan: Gmail Integration

## Objective
Enable the AI Employee to monitor Gmail inbox, create action items for important emails, and integrate with the approval workflow.

## Context
- Need read-only access to Gmail
- Must respect privacy (local-first)
- Should filter for important/urgent emails only
- Integration must be secure and revocable

## Prerequisites
- [ ] Google Cloud account created
- [ ] Gmail API enabled
- [ ] OAuth credentials downloaded
- [ ] Python Gmail libraries installed

## Implementation Steps

### Phase 1: Authentication Setup
- [ ] Create Google Cloud project
- [ ] Enable Gmail API
- [ ] Configure OAuth consent screen
- [ ] Download credentials.json
- [ ] Implement OAuth flow in gmail_auth.py
- [ ] Test authentication and token storage

### Phase 2: Watcher Implementation
- [ ] Create GmailWatcher class extending BaseWatcher
- [ ] Implement check_for_updates() method
- [ ] Add email filtering logic (important/starred)
- [ ] Implement priority detection
- [ ] Create action file generation
- [ ] Add error handling and logging

### Phase 3: Testing and Validation
- [ ] Test with sample emails
- [ ] Verify action items created correctly
- [ ] Test priority detection
- [ ] Validate error handling
- [ ] Check token refresh logic

### Phase 4: Documentation and Deployment
- [ ] Create GMAIL_SETUP.md guide
- [ ] Document configuration options
- [ ] Add troubleshooting section
- [ ] Create systemd service file
- [ ] Update Dashboard with Gmail status

## Success Criteria
- [ ] Gmail watcher successfully authenticates
- [ ] Important emails create action items
- [ ] Priority detection works correctly
- [ ] Watcher runs continuously without errors
- [ ] Documentation is complete and clear

## Testing Plan
- [ ] Send test email marked as important
- [ ] Verify action item created in Needs_Action/
- [ ] Test with multiple emails
- [ ] Verify priority levels assigned correctly
- [ ] Test error recovery (network issues)

## Risks and Mitigation
- **Risk 1:** OAuth token expiration
  - Mitigation: Implement automatic token refresh
- **Risk 2:** API rate limits
  - Mitigation: Implement exponential backoff
- **Risk 3:** Privacy concerns
  - Mitigation: Use read-only scope, store locally only

## Notes
- Gmail API has quota limits (1 billion quota units/day)
- Each message.list() call costs 5 quota units
- Token refresh is automatic with google-auth library
- Consider adding webhook support for real-time updates in future

---
**Plan Status:** In Progress
**Last Updated:** 2026-03-03T16:00:00Z
```

## Plan Types

### 1. Implementation Plan
For building new features or systems.
- Focus on technical steps
- Include testing and validation
- Document architecture decisions

### 2. Investigation Plan
For researching or troubleshooting.
- Define questions to answer
- List information sources
- Plan experiments or tests

### 3. Process Plan
For establishing workflows or procedures.
- Define process steps
- Identify stakeholders
- Document decision points

### 4. Migration Plan
For moving or upgrading systems.
- Plan backward compatibility
- Define rollback strategy
- Schedule downtime if needed

## Best Practices

### Make Steps Actionable
❌ Bad: "Set up authentication"
✅ Good: "Create OAuth credentials in Google Cloud Console"

### Be Specific
❌ Bad: "Test the system"
✅ Good: "Send 3 test emails and verify action items created"

### Include Context
❌ Bad: "Install dependencies"
✅ Good: "Install google-auth libraries: pip install google-auth google-auth-oauthlib"

### Think About Risks
Always include a "Risks and Mitigation" section to anticipate problems.

### Define Success
Clear success criteria help you know when you're done.

## Integration with Other Skills

Plans work with other agent skills:
- **ralph-loop-executor:** Execute plans step-by-step autonomously
- **vault-manager:** Track plan progress in Dashboard
- **process-inbox:** Plans can be created from complex inbox items

## Updating Plans

As you work through a plan:
1. Check off completed items: `- [x] Completed step`
2. Add new steps if discovered: `- [ ] New step`
3. Update status in frontmatter
4. Add notes about decisions or changes
5. Update "Last Updated" timestamp

## Usage Examples

**Example 1: Create plan for new feature**
```bash
claude "Create a plan for implementing WhatsApp integration"
```

**Example 2: Plan complex task**
```bash
claude "I need to migrate our database. Create a detailed plan."
```

**Example 3: Plan from inbox item**
```bash
claude "Process the task in Needs_Action/TASK_001.md and create a plan"
```

## Output

After creating a plan, you should:
1. Confirm plan was saved to `/Plans` folder
2. Summarize the key phases
3. Highlight any risks or prerequisites
4. Ask if user wants to proceed with execution

Example output:
```
✅ Plan created: AI_Employee_Vault/Plans/PLAN_Gmail_Integration.md

📋 Summary:
- 4 phases: Authentication, Implementation, Testing, Documentation
- Estimated time: 4-6 hours
- 3 prerequisites required before starting
- 2 key risks identified with mitigation strategies

⚠️ Prerequisites needed:
1. Google Cloud account
2. Gmail API enabled
3. OAuth credentials

Ready to proceed? I can execute this plan step-by-step, or you can review it first.
```

## Tips for Success

1. **Start with Why:** Always include context and objectives
2. **Think Dependencies:** Order steps logically
3. **Be Realistic:** Don't underestimate complexity
4. **Plan for Failure:** Include error handling and rollback
5. **Document Decisions:** Capture the "why" behind choices
6. **Keep It Updated:** Plans are living documents

## Remember

A good plan:
- Is clear and actionable
- Considers risks and dependencies
- Defines success criteria
- Can be executed by someone else
- Serves as documentation

**Your goal:** Create plans that make complex tasks manageable and trackable.

---

## Invocation

This skill is automatically invoked when:
- User asks to "create a plan"
- User asks to "break down" a complex task
- User requests "planning" for a project
- A task in Needs_Action requires planning

Manual invocation:
```bash
claude "Use the generate-plan skill to plan [task description]"
```

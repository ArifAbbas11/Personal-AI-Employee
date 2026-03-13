# Completed General Tasks

This folder contains general tasks that have been fully completed.

## What Goes Here

- System maintenance tasks
- Data processing tasks
- Report generation
- Analysis tasks
- Administrative work
- Any general task that doesn't fit specific categories

## Task Lifecycle

```
Needs_Action → Pending_Approval → Approved/general → Done/general
```

## Organization

Tasks are stored here after completion. For better organization:
- Keep tasks for 90 days
- Archive older tasks monthly
- Use descriptive filenames
- Include completion date in metadata

## Other Done Folders

- `Done/emails/` - Completed email tasks
- `Done/linkedin/` - Published LinkedIn posts
- `Done/twitter/` - Published tweets

## Viewing Completed Tasks

```bash
# List recent completions
ls -lt AI_Employee_Vault/Done/general/ | head -20

# Count completed tasks
ls AI_Employee_Vault/Done/general/*.md | wc -l

# Search for specific task
grep -r "keyword" AI_Employee_Vault/Done/general/
```

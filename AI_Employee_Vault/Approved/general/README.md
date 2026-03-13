# Approved General Tasks

This folder contains tasks that have been approved by a human and are ready to be executed.

## Workflow

1. Tasks are processed in `Needs_Action/`
2. Drafts/results are created in `Pending_Approval/`
3. Human reviews and approves → moves here
4. AI executes the approved task
5. Completed task moves to `Done/general/`

## Task Format

Each task should include:
- Clear instructions
- Approval metadata (who approved, when)
- Expected outcome
- Completion criteria

## Processing

To process all approved tasks:

```bash
./ralph_groq_setup.sh -s empty_folder \
  "Process all tasks in Approved/general/. Execute each task and move to Done/general/ when complete."
```

## Notes

- Only approved tasks should be in this folder
- Tasks should be ready for immediate execution
- No further human review needed before execution

---
type: system_task
priority: high
created: 2026-03-12
---

# System Health Check

Perform system health check and create report.

## Checks Required

1. Verify all vault folders exist
2. Count files in each folder
3. Check for old files (>30 days) in Needs_Action
4. Verify log directory is accessible

## Output

Create health report in Logs/ with:
- Folder structure status
- File counts
- Any issues found
- Recommendations

## Success Criteria

Report created in Logs/system_health_*.md

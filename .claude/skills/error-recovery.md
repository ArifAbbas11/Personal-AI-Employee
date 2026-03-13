---
name: error-recovery
description: Automatic error detection, recovery, and system health monitoring
version: 1.0.0
---

# Error Recovery & Watchdog

This skill provides automatic error detection, recovery strategies, and continuous system health monitoring for the Personal AI Employee system.

## Features

- **Error Detection** - Scans logs for errors and issues
- **Automatic Recovery** - Implements recovery strategies for common errors
- **System Health Monitoring** - Checks disk space, queues, stuck tasks
- **Watchdog Daemon** - Continuous monitoring and alerting
- **Manual Review Tasks** - Creates tasks for errors requiring human intervention

## Available Operations

### 1. Scan for Errors

Scan logs for errors in the last N hours:

```
Scan for errors in the last 24 hours
```

```
Check for recent errors
```

### 2. Check System Health

Check overall system health:

```
Check system health
```

```
Show me system status
```

### 3. Start Watchdog Daemon

Start continuous monitoring:

```bash
python3 watchers/error_recovery_watchdog.py --daemon --interval 300
```

### 4. Review Error Recovery Log

Check recovery attempts:

```
Show me the error recovery log
```

```
cat AI_Employee_Vault/Logs/error_recovery.log
```

## Error Types Detected

### Authentication Errors
- **Severity:** High
- **Recovery:** Creates manual review task
- **Action:** Update credentials in configuration files

### API Rate Limits
- **Severity:** Medium
- **Recovery:** Implements exponential backoff
- **Action:** Automatic retry after delay

### Network Errors
- **Severity:** Medium
- **Recovery:** Automatic retry with backoff
- **Action:** Retries connection after delay

### File Not Found
- **Severity:** Low
- **Recovery:** Creates manual review task
- **Action:** Verify file path and existence

### Permission Denied
- **Severity:** High
- **Recovery:** Creates manual review task
- **Action:** Check file permissions and user access

### Database Errors
- **Severity:** Critical
- **Recovery:** Creates manual review task
- **Action:** Check database connection and status

### Disk Full
- **Severity:** Critical
- **Recovery:** Attempts to clean up old logs
- **Action:** Free up disk space or increase capacity

### Memory Errors
- **Severity:** Critical
- **Recovery:** Creates manual review task
- **Action:** Restart services or increase memory

## System Health Checks

### Disk Space
- **Warning:** > 80% used
- **Critical:** > 90% used
- **Action:** Clean up old files or increase storage

### Log File Sizes
- **Warning:** Individual log > 100MB
- **Action:** Rotate or archive large logs

### Queue Status
- **Warning:** Items stuck > 24 hours
- **Action:** Review and process stuck items

### Stuck Tasks
- **Warning:** > 5 tasks in Needs_Action > 3 days
- **Action:** Review and complete stuck tasks

## Recovery Strategies

### Automatic Recovery

**Rate Limit Errors:**
- Implement exponential backoff
- Retry after 15 minutes
- Log retry attempt

**Network Errors:**
- Retry with exponential backoff
- Retry after 5 minutes
- Log retry attempt

**Disk Full:**
- Clean up logs older than 30 days
- Archive large log files
- Create manual review if cleanup insufficient

### Manual Review Required

**Authentication Errors:**
- Creates task in Needs_Action/
- Provides instructions for credential update
- Requires human intervention

**Permission Errors:**
- Creates task in Needs_Action/
- Provides instructions for permission fix
- Requires human intervention

**Database Errors:**
- Creates task in Needs_Action/
- Provides troubleshooting steps
- Requires human intervention

## Watchdog Daemon

### Starting the Daemon

```bash
# Start with default 5-minute interval
python3 watchers/error_recovery_watchdog.py --daemon

# Start with custom interval (seconds)
python3 watchers/error_recovery_watchdog.py --daemon --interval 60

# Run in background
nohup python3 watchers/error_recovery_watchdog.py --daemon > /tmp/watchdog.log 2>&1 &
```

### Stopping the Daemon

```bash
# Find process
ps aux | grep error_recovery_watchdog

# Kill process
kill <PID>
```

### Monitoring the Daemon

```bash
# View logs
tail -f /tmp/watchdog.log

# View alerts
tail -f AI_Employee_Vault/Logs/watchdog_alerts.log

# View recovery log
tail -f AI_Employee_Vault/Logs/error_recovery.log
```

## Integration with Other Systems

### CEO Briefing Integration

Error and recovery metrics included in weekly briefings:
- Errors detected this week
- Recovery success rate
- System health status
- Manual reviews required

### Email Integration

Automatically process error notifications:
- Parse error emails
- Create recovery tasks
- Track resolution status

### Dashboard Integration

Real-time error and health metrics:
- Current system health
- Recent errors
- Recovery attempts
- Alerts pending

## Error Recovery Workflow

### Automatic Recovery Flow

```
1. Error detected in logs
2. Classify error type and severity
3. Select recovery strategy
4. Attempt automatic recovery
5. Log recovery attempt
6. If successful: Continue monitoring
7. If failed: Create manual review task
```

### Manual Review Flow

```
1. Error requires human intervention
2. Create task in Needs_Action/
3. Include error details and instructions
4. User reviews and implements fix
5. User tests resolution
6. User moves task to Done/
7. System continues monitoring
```

## Alerting

### Alert Levels

**Info:** Normal operation, no action required
**Warning:** Degraded performance, review recommended
**Critical:** System issue, immediate action required

### Alert Channels

- **Log Files:** All alerts logged to watchdog_alerts.log
- **Manual Review Tasks:** Critical errors create tasks
- **Dashboard:** Real-time health status display

## Best Practices

1. **Run Watchdog Daemon** - Enable continuous monitoring
2. **Review Alerts Daily** - Check watchdog_alerts.log regularly
3. **Address Manual Reviews** - Process error review tasks promptly
4. **Monitor Disk Space** - Keep disk usage below 80%
5. **Rotate Logs** - Archive or delete old logs regularly
6. **Test Recovery** - Verify recovery strategies work
7. **Update Patterns** - Add new error patterns as discovered

## Troubleshooting

### Watchdog Not Detecting Errors

1. Check log file locations
2. Verify error patterns in code
3. Review log file permissions
4. Check watchdog daemon is running

### Recovery Not Working

1. Review error_recovery.log
2. Check recovery strategy implementation
3. Verify file permissions
4. Test recovery manually

### High False Positive Rate

1. Refine error patterns
2. Adjust severity levels
3. Filter out known benign errors
4. Update detection logic

## Configuration

Error patterns and recovery strategies are defined in:
```
watchers/error_recovery_watchdog.py
```

To add new error patterns:
1. Edit `_load_error_patterns()` method
2. Add pattern, severity, and component
3. Implement recovery strategy if needed
4. Test detection and recovery

## Examples

### Example 1: Automatic Rate Limit Recovery

```
Error detected: "Rate limit exceeded"
Severity: Medium
Component: API
Recovery: Automatic backoff
Action: Retry in 15 minutes
Result: Success - request completed after retry
```

### Example 2: Manual Authentication Review

```
Error detected: "Authentication failed"
Severity: High
Component: Authentication
Recovery: Manual review required
Action: Created task ERROR_REVIEW_20260227_140000.md
Result: User updated credentials, task moved to Done/
```

### Example 3: Automatic Disk Cleanup

```
Error detected: "Disk full"
Severity: Critical
Component: Filesystem
Recovery: Automatic cleanup
Action: Deleted 15 old log files (500MB freed)
Result: Success - disk space recovered
```

## Monitoring Commands

```bash
# Scan for errors
python3 watchers/error_recovery_watchdog.py --scan

# Check system health
python3 watchers/error_recovery_watchdog.py --health

# View recent alerts
tail -20 AI_Employee_Vault/Logs/watchdog_alerts.log

# View recovery attempts
tail -20 AI_Employee_Vault/Logs/error_recovery.log

# Count errors by type
grep "error_type" AI_Employee_Vault/Logs/watchdog_alerts.log | sort | uniq -c
```

## Next Steps

After setup:
1. Start watchdog daemon
2. Monitor for 24 hours
3. Review alerts and recovery attempts
4. Adjust error patterns as needed
5. Integrate with CEO Briefing
6. Set up alerting notifications

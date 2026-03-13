---
name: audit-logging
description: Comprehensive audit logging for compliance, security, and operations tracking
version: 1.0.0
---

# Comprehensive Audit Logging

This skill provides comprehensive audit logging for all operations, user actions, and system events in the Personal AI Employee system.

## Features

- **Event Tracking** - Logs all operations with timestamps and actors
- **Category-Based Logging** - Separate logs for different event types
- **Query & Reporting** - Search and analyze audit events
- **Compliance Support** - Meets audit and compliance requirements
- **Security Monitoring** - Tracks authentication and authorization
- **Export Capabilities** - Export logs for external analysis

## Event Categories

### Authentication
- Login attempts
- Logout events
- Token generation
- Credential updates

### Authorization
- Permission checks
- Access grants/denials
- Role changes

### Data Access
- File reads
- Database queries
- API data retrieval

### Data Modification
- File creates/updates/deletes
- Database modifications
- Configuration changes

### System Operations
- Service starts/stops
- Configuration changes
- System health checks

### User Actions
- Task completions
- Approval decisions
- Manual interventions

### API Calls
- External API requests
- Response codes
- Rate limit events

### File Operations
- File creates
- File reads
- File updates
- File deletes

### Email Operations
- Emails sent
- Emails received
- Email processing

### Social Media
- Posts published
- Posts scheduled
- Posts deleted
- Engagement tracking

### Financial
- Invoices created
- Payments recorded
- Reports generated
- Transactions searched

### Approvals
- Approval requests
- Approval decisions
- Rejection reasons

### Error Events
- Errors detected
- Recovery attempts
- Manual reviews

## Available Operations

### 1. Log Events

Events are automatically logged by the system for all operations. Manual logging:

```python
from watchers.audit_logger import AuditLogger

audit = AuditLogger('/path/to/vault')

# Log file operation
audit.log_file_operation(
    actor='claude',
    operation='create',
    file_path='AI_Employee_Vault/Done/TASK_001.md',
    result='success'
)

# Log API call
audit.log_api_call(
    actor='claude',
    api='odoo',
    endpoint='/api/invoices',
    method='POST',
    result='success'
)

# Log approval
audit.log_approval(
    actor='user',
    action='approve_invoice',
    resource='INV-001',
    decision='approved'
)
```

### 2. Query Events

Search audit logs:

```bash
# Query all events from last 7 days
python3 watchers/audit_logger.py --query --days 7

# Query specific category
python3 watchers/audit_logger.py --query --category financial --days 30

# Query by actor
python3 watchers/audit_logger.py --query --actor claude --days 7
```

### 3. Generate Reports

Create audit reports:

```bash
# Generate report for last 7 days
python3 watchers/audit_logger.py --report --days 7

# Generate monthly report
python3 watchers/audit_logger.py --report --days 30
```

### 4. Export Logs

Export audit logs for external analysis:

```bash
# Export all events
python3 watchers/audit_logger.py --export audit_export.json --days 30

# Export specific category
python3 watchers/audit_logger.py --export financial_audit.json --category financial --days 90
```

## Audit Event Structure

Each audit event contains:

```json
{
  "timestamp": "2026-02-27T18:00:00",
  "event_id": "a1b2c3d4e5f6g7h8",
  "event_type": "create",
  "category": "financial",
  "actor": "claude",
  "action": "create_invoice",
  "resource": "odoo",
  "resource_id": "INV-001",
  "result": "success",
  "details": {
    "amount": 5000.00,
    "currency": "USD",
    "customer": "Acme Corp"
  }
}
```

## Log Files

Audit logs are stored in `AI_Employee_Vault/Logs/audit/`:

- `master_audit.log` - All events
- `authentication.log` - Authentication events
- `authorization.log` - Authorization events
- `data_access.log` - Data access events
- `data_modification.log` - Data modification events
- `system_operation.log` - System operations
- `user_action.log` - User actions
- `api_call.log` - API calls
- `file_operation.log` - File operations
- `email_operation.log` - Email operations
- `social_media.log` - Social media events
- `financial.log` - Financial operations
- `approval.log` - Approval decisions
- `error_event.log` - Error events

## Integration with Other Systems

### CEO Briefing Integration

Audit metrics included in weekly briefings:
- Total operations this week
- Operations by category
- Top actors
- Error rate
- Approval rate

### Dashboard Integration

Real-time audit metrics:
- Operations today
- Recent events
- Error count
- Approval pending

### Error Recovery Integration

Error events automatically logged:
- Error detection
- Recovery attempts
- Manual reviews

### All System Operations

All features automatically log events:
- Email processing
- Social media posts
- Financial operations
- File operations
- Approvals

## Compliance & Security

### Compliance Features

- **Immutable Logs** - Append-only log files
- **Timestamp Accuracy** - ISO format timestamps
- **Actor Tracking** - All actions attributed to actor
- **Result Tracking** - Success/failure recorded
- **Detail Preservation** - Full context captured

### Security Features

- **Authentication Logging** - All auth attempts logged
- **Authorization Logging** - Permission checks logged
- **Access Tracking** - Data access monitored
- **Modification Tracking** - Changes recorded
- **Error Logging** - Security errors captured

### Audit Trail

Complete audit trail for:
- Who did what
- When it happened
- What resource was affected
- What was the result
- What were the details

## Reporting

### Daily Report

```bash
python3 watchers/audit_logger.py --report --days 1
```

Shows:
- Total events today
- Events by category
- Top actors
- Top actions
- Errors

### Weekly Report

```bash
python3 watchers/audit_logger.py --report --days 7
```

Shows:
- Total events this week
- Trends by category
- Most active actors
- Most common actions
- Error summary

### Monthly Report

```bash
python3 watchers/audit_logger.py --report --days 30
```

Shows:
- Total events this month
- Category breakdown
- Actor activity
- Action frequency
- Error analysis

### Custom Report

```python
from watchers.audit_logger import AuditLogger
from datetime import datetime, timedelta

audit = AuditLogger('/path/to/vault')

end_date = datetime.now()
start_date = end_date - timedelta(days=90)

report = audit.generate_audit_report(start_date, end_date)
```

## Query Examples

### Find All Financial Operations

```bash
python3 watchers/audit_logger.py --query --category financial --days 30
```

### Find All Actions by Specific Actor

```bash
python3 watchers/audit_logger.py --query --actor claude --days 7
```

### Find All Errors

```bash
python3 watchers/audit_logger.py --query --category error_event --days 7
```

### Find All Approvals

```bash
python3 watchers/audit_logger.py --query --category approval --days 30
```

## Best Practices

1. **Regular Reviews** - Review audit logs weekly
2. **Export Regularly** - Export logs monthly for archival
3. **Monitor Errors** - Check error_event.log daily
4. **Track Approvals** - Monitor approval patterns
5. **Analyze Trends** - Look for unusual patterns
6. **Secure Logs** - Protect audit logs from modification
7. **Retention Policy** - Define log retention period

## Troubleshooting

### Logs Not Being Created

1. Check vault path is correct
2. Verify Logs/audit/ directory exists
3. Check file permissions
4. Review application logs

### Query Returns No Results

1. Check date range
2. Verify category name
3. Check actor name spelling
4. Ensure events were logged

### Export Fails

1. Check output path permissions
2. Verify disk space
3. Check date range
4. Review error message

## Security Considerations

- **Log Protection** - Audit logs should be read-only
- **Access Control** - Limit who can access audit logs
- **Encryption** - Consider encrypting sensitive logs
- **Backup** - Regularly backup audit logs
- **Retention** - Define and enforce retention policy

## Compliance Use Cases

### SOC 2 Compliance

Audit logs provide evidence for:
- Access controls
- Change management
- Incident response
- Monitoring and logging

### GDPR Compliance

Audit logs support:
- Data access tracking
- Data modification tracking
- User consent tracking
- Data deletion verification

### Financial Audits

Audit logs provide:
- Transaction history
- Approval workflows
- Financial operation tracking
- Error and exception logging

## Next Steps

After setup:
1. Review log files structure
2. Test event logging
3. Generate test reports
4. Set up regular exports
5. Integrate with monitoring
6. Define retention policy
7. Train team on audit queries

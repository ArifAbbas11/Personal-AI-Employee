---
name: odoo-accounting
description: Manage accounting and financial operations through Odoo ERP
version: 1.0.0
---

# Odoo Accounting Integration

This skill provides access to Odoo accounting features for the Personal AI Employee system.

## Available Operations

### 1. Check Account Balances

Get current balance for accounts:

```
Check the balance of account 100000 (bank account)
```

```
Show me all account balances
```

### 2. Create Invoices

Create customer or vendor invoices:

```
Create an invoice for Acme Corp for $5,000 for consulting services
```

```
Create a vendor invoice for Office Supplies Inc for $250 for office supplies
```

**Note:** Invoices above the approval threshold require manual approval.

### 3. Record Payments

Record payments against invoices:

```
Record a payment of $5,000 for invoice INV/2024/0001
```

```
Record payment for invoice 123 amount $250 dated 2024-02-15
```

### 4. Generate Financial Reports

Generate profit & loss, balance sheet, or cash flow reports:

```
Generate a profit and loss report for last month
```

```
Show me the balance sheet as of today
```

```
Generate cash flow report for the last 30 days
```

### 5. Search Transactions

Search for transactions by partner, reference, or description:

```
Search for all transactions with Acme Corp
```

```
Find invoice INV/2024/0001
```

## Workflow Integration

### Automatic Invoice Creation from Emails

When processing emails requesting invoices:

1. Extract customer name, amount, and description
2. Create invoice in Odoo (draft state)
3. If amount > threshold, create approval request
4. After approval, post invoice
5. Send invoice to customer via email

### Monthly Financial Reports

Automatically generate and include in CEO Briefing:

1. Profit & Loss for the month
2. Cash flow summary
3. Outstanding invoices
4. Payment collection rate

### Payment Reminders

Monitor overdue invoices and send reminders:

1. Check for invoices past due date
2. Generate reminder email
3. Create approval request
4. Send reminder after approval

## Human-in-the-Loop (HITL)

The following operations require approval:

- **Create Invoice:** If amount > approval_threshold
- **Record Payment:** Always requires approval
- **Post Invoice:** Always requires approval
- **Create Partner:** Always requires approval

Approval requests are created in `AI_Employee_Vault/Needs_Action/APPROVAL_*.md`

## Configuration

Odoo credentials are stored in:
```
AI_Employee_Vault/Config/odoo_config.json
```

Required fields:
- `url`: Odoo instance URL
- `database`: Database name
- `username`: Odoo username
- `password`: Odoo password or API key
- `approval_threshold`: Amount requiring approval

## Error Handling

If Odoo operations fail:

1. Log error to `AI_Employee_Vault/Logs/odoo_errors.log`
2. Create manual review task in `Needs_Action/`
3. Notify user of failure
4. Provide troubleshooting steps

## Examples

### Example 1: Process Invoice Request Email

```
Email received: "Please invoice us for the consulting work completed last week.
Total: $7,500. Reference: Project Alpha."

Actions:
1. Extract: Customer=sender, Amount=$7,500, Description="Consulting - Project Alpha"
2. Create invoice in Odoo (draft)
3. Amount > threshold → Create approval request
4. Wait for approval
5. Post invoice
6. Send invoice PDF to customer
7. Move email to Done/
```

### Example 2: Monthly Financial Close

```
Task: Generate monthly financial reports

Actions:
1. Get profit & loss for the month
2. Get balance sheet as of month end
3. Get cash flow for the month
4. Calculate key metrics (profit margin, cash position)
5. Generate summary report
6. Include in CEO Briefing
7. Create approval request for review
```

### Example 3: Payment Reconciliation

```
Email received: "Payment of $5,000 sent via wire transfer for INV/2024/0001"

Actions:
1. Search for invoice INV/2024/0001
2. Verify amount matches
3. Create approval request for payment recording
4. After approval, record payment in Odoo
5. Send payment confirmation to customer
6. Update dashboard
7. Move email to Done/
```

## Integration with Other Systems

### CEO Briefing Integration

Financial data automatically included in weekly briefings:
- Revenue this week
- Expenses this week
- Outstanding invoices
- Cash position
- Profit margin

### Email Integration

Automatically process:
- Invoice requests
- Payment notifications
- Financial inquiries

### Dashboard Integration

Real-time financial metrics:
- Current cash balance
- Monthly revenue
- Outstanding receivables
- Upcoming payables

## Troubleshooting

### Connection Issues

If Odoo connection fails:
1. Check `odoo_config.json` credentials
2. Verify Odoo instance is running
3. Test connection: `curl http://localhost:8069/web/database/selector`
4. Check firewall/network settings

### Authentication Issues

If authentication fails:
1. Verify username/password
2. Check user has accounting permissions
3. Try logging in via web interface
4. Generate API key if using 2FA

### Tool Execution Issues

If tools fail:
1. Check Odoo logs: `/var/log/odoo/odoo-server.log`
2. Verify accounting module is installed
3. Check user permissions for the operation
4. Review error in `AI_Employee_Vault/Logs/odoo_errors.log`

## Security Notes

- Credentials stored in config file (not in git)
- All financial operations logged
- Approval required for sensitive operations
- API access limited to accounting operations
- No direct database access

## Next Steps

After setup:
1. Test connection with simple balance check
2. Create test invoice
3. Generate test report
4. Integrate with email processing
5. Add to CEO Briefing data collection

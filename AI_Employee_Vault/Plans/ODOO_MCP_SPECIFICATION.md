# Odoo MCP Server Technical Specification

---
created: 2026-02-26
component: odoo-accounting-mcp
status: specification
tier: gold
---

## Overview

The Odoo MCP Server provides Claude Code with tools to interact with a self-hosted Odoo Community Edition accounting system via JSON-RPC API. All financial actions require human approval before execution.

## Architecture

```
┌─────────────────┐
│  Claude Code    │
│                 │
└────────┬────────┘
         │
         │ MCP Protocol
         │
┌────────▼────────┐
│  Odoo MCP       │
│  Server         │
│  (Node.js)      │
└────────┬────────┘
         │
         │ JSON-RPC
         │
┌────────▼────────┐
│  Odoo 19        │
│  Community      │
│  (PostgreSQL)   │
└─────────────────┘
```

## Installation

### Prerequisites
- Node.js 24+ LTS
- Odoo 19 Community Edition running locally
- Odoo database configured with accounting module

### Setup Steps

```bash
# Create MCP server directory
mkdir -p mcp-servers/odoo-accounting
cd mcp-servers/odoo-accounting

# Initialize Node.js project
npm init -y

# Install dependencies
npm install @anthropic/mcp-server
npm install axios
npm install dotenv

# Create environment file
cat > .env << EOF
ODOO_URL=http://localhost:8069
ODOO_DB=your_database_name
ODOO_USERNAME=admin
ODOO_PASSWORD=your_password
EOF

# Add to .gitignore
echo ".env" >> .gitignore
```

### Project Structure

```
mcp-servers/odoo-accounting/
├── package.json
├── .env
├── .env.example
├── index.js                 # Main MCP server entry point
├── src/
│   ├── odoo-client.js       # JSON-RPC client wrapper
│   ├── tools/
│   │   ├── invoice.js       # Invoice operations
│   │   ├── expense.js       # Expense tracking
│   │   ├── payment.js       # Payment processing
│   │   ├── report.js        # Financial reports
│   │   └── customer.js      # Customer/vendor management
│   └── utils/
│       ├── validator.js     # Input validation
│       └── formatter.js     # Data formatting
└── README.md
```

## Odoo JSON-RPC Client

### Authentication

```javascript
// src/odoo-client.js
const axios = require('axios');

class OdooClient {
  constructor(url, db, username, password) {
    this.url = url;
    this.db = db;
    this.username = username;
    this.password = password;
    this.uid = null;
  }

  async authenticate() {
    const response = await axios.post(`${this.url}/jsonrpc`, {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        service: 'common',
        method: 'authenticate',
        args: [this.db, this.username, this.password, {}]
      },
      id: Math.floor(Math.random() * 1000000)
    });

    if (response.data.error) {
      throw new Error(`Odoo authentication failed: ${response.data.error.message}`);
    }

    this.uid = response.data.result;
    return this.uid;
  }

  async execute(model, method, args = [], kwargs = {}) {
    if (!this.uid) {
      await this.authenticate();
    }

    const response = await axios.post(`${this.url}/jsonrpc`, {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        service: 'object',
        method: 'execute_kw',
        args: [
          this.db,
          this.uid,
          this.password,
          model,
          method,
          args,
          kwargs
        ]
      },
      id: Math.floor(Math.random() * 1000000)
    });

    if (response.data.error) {
      throw new Error(`Odoo API error: ${response.data.error.message}`);
    }

    return response.data.result;
  }

  async search(model, domain = [], fields = [], limit = null) {
    const kwargs = { fields };
    if (limit) kwargs.limit = limit;

    const ids = await this.execute(model, 'search', [domain], { limit });
    if (ids.length === 0) return [];

    return await this.execute(model, 'read', [ids], { fields });
  }

  async create(model, values) {
    return await this.execute(model, 'create', [values]);
  }

  async write(model, ids, values) {
    return await this.execute(model, 'write', [ids, values]);
  }
}

module.exports = OdooClient;
```

## MCP Tools

### Tool 1: Create Invoice Draft

**Purpose:** Create a draft invoice in Odoo requiring human approval before posting.

```javascript
// src/tools/invoice.js
async function createInvoiceDraft(odooClient, params) {
  const {
    customer_name,
    customer_email,
    invoice_lines,  // Array of {description, quantity, price}
    due_date,
    notes
  } = params;

  // Find or create customer
  let partner = await odooClient.search(
    'res.partner',
    [['email', '=', customer_email]],
    ['id', 'name']
  );

  if (partner.length === 0) {
    // Create new customer
    const partnerId = await odooClient.create('res.partner', {
      name: customer_name,
      email: customer_email,
      customer_rank: 1
    });
    partner = [{ id: partnerId, name: customer_name }];
  }

  // Prepare invoice lines
  const lines = invoice_lines.map(line => [0, 0, {
    name: line.description,
    quantity: line.quantity,
    price_unit: line.price
  }]);

  // Create draft invoice
  const invoiceId = await odooClient.create('account.move', {
    partner_id: partner[0].id,
    move_type: 'out_invoice',
    invoice_date: new Date().toISOString().split('T')[0],
    invoice_date_due: due_date,
    invoice_line_ids: lines,
    narration: notes,
    state: 'draft'  // CRITICAL: Keep as draft
  });

  // Fetch created invoice details
  const invoice = await odooClient.search(
    'account.move',
    [['id', '=', invoiceId]],
    ['name', 'amount_total', 'state']
  );

  return {
    success: true,
    invoice_id: invoiceId,
    invoice_number: invoice[0].name,
    amount: invoice[0].amount_total,
    status: 'draft',
    message: 'Invoice created as DRAFT. Requires approval to post.'
  };
}

module.exports = { createInvoiceDraft };
```

**MCP Tool Definition:**
```javascript
{
  name: 'create_invoice_draft',
  description: 'Create a draft invoice in Odoo. Invoice remains in draft state and requires human approval before posting to customer.',
  inputSchema: {
    type: 'object',
    properties: {
      customer_name: {
        type: 'string',
        description: 'Customer full name'
      },
      customer_email: {
        type: 'string',
        description: 'Customer email address'
      },
      invoice_lines: {
        type: 'array',
        description: 'Array of invoice line items',
        items: {
          type: 'object',
          properties: {
            description: { type: 'string' },
            quantity: { type: 'number' },
            price: { type: 'number' }
          },
          required: ['description', 'quantity', 'price']
        }
      },
      due_date: {
        type: 'string',
        description: 'Invoice due date (YYYY-MM-DD)'
      },
      notes: {
        type: 'string',
        description: 'Additional notes for invoice'
      }
    },
    required: ['customer_name', 'customer_email', 'invoice_lines', 'due_date']
  }
}
```

### Tool 2: Record Expense

**Purpose:** Log a business expense in Odoo for tracking and categorization.

```javascript
// src/tools/expense.js
async function recordExpense(odooClient, params) {
  const {
    description,
    amount,
    category,
    date,
    vendor,
    receipt_path  // Optional: path to receipt file
  } = params;

  // Find expense account based on category
  const categoryMap = {
    'software': 'Software Subscriptions',
    'office': 'Office Supplies',
    'travel': 'Travel & Entertainment',
    'marketing': 'Marketing & Advertising',
    'utilities': 'Utilities',
    'other': 'General Expenses'
  };

  const accountName = categoryMap[category] || categoryMap['other'];

  // Find account
  const account = await odooClient.search(
    'account.account',
    [['name', 'ilike', accountName]],
    ['id', 'name'],
    1
  );

  if (account.length === 0) {
    throw new Error(`Account not found for category: ${category}`);
  }

  // Create expense journal entry
  const moveId = await odooClient.create('account.move', {
    move_type: 'entry',
    date: date,
    ref: description,
    line_ids: [
      [0, 0, {
        name: description,
        account_id: account[0].id,
        debit: amount,
        credit: 0
      }],
      [0, 0, {
        name: description,
        account_id: account[0].id,  // Should be bank/cash account
        debit: 0,
        credit: amount
      }]
    ]
  });

  return {
    success: true,
    expense_id: moveId,
    amount: amount,
    category: category,
    message: 'Expense recorded successfully'
  };
}

module.exports = { recordExpense };
```

### Tool 3: Get Account Balance

**Purpose:** Fetch current balance for specified account.

```javascript
// src/tools/report.js
async function getAccountBalance(odooClient, params) {
  const { account_type = 'bank' } = params;

  // Map account types to Odoo account codes
  const accountTypeMap = {
    'bank': ['type', '=', 'liquidity'],
    'receivable': ['type', '=', 'receivable'],
    'payable': ['type', '=', 'payable']
  };

  const domain = accountTypeMap[account_type] || accountTypeMap['bank'];

  // Get accounts
  const accounts = await odooClient.search(
    'account.account',
    [domain],
    ['id', 'name', 'code', 'current_balance']
  );

  const totalBalance = accounts.reduce((sum, acc) => sum + acc.current_balance, 0);

  return {
    success: true,
    account_type: account_type,
    accounts: accounts.map(acc => ({
      name: acc.name,
      code: acc.code,
      balance: acc.current_balance
    })),
    total_balance: totalBalance
  };
}

module.exports = { getAccountBalance };
```

### Tool 4: Generate Financial Report

**Purpose:** Generate P&L or Balance Sheet for specified period.

```javascript
async function generateFinancialReport(odooClient, params) {
  const {
    report_type,  // 'profit_loss' or 'balance_sheet'
    start_date,
    end_date
  } = params;

  // This is simplified - actual implementation would use Odoo's reporting engine
  const domain = [
    ['date', '>=', start_date],
    ['date', '<=', end_date],
    ['state', '=', 'posted']
  ];

  const moves = await odooClient.search(
    'account.move',
    domain,
    ['id', 'name', 'date', 'amount_total', 'move_type']
  );

  // Calculate totals
  const revenue = moves
    .filter(m => m.move_type === 'out_invoice')
    .reduce((sum, m) => sum + m.amount_total, 0);

  const expenses = moves
    .filter(m => m.move_type === 'in_invoice')
    .reduce((sum, m) => sum + m.amount_total, 0);

  const netIncome = revenue - expenses;

  return {
    success: true,
    report_type: report_type,
    period: { start_date, end_date },
    revenue: revenue,
    expenses: expenses,
    net_income: netIncome,
    profit_margin: revenue > 0 ? (netIncome / revenue * 100).toFixed(2) : 0
  };
}
```

### Tool 5: List Unpaid Invoices

**Purpose:** Get all outstanding invoices for accounts receivable tracking.

```javascript
async function listUnpaidInvoices(odooClient, params) {
  const { overdue_only = false } = params;

  const domain = [
    ['move_type', '=', 'out_invoice'],
    ['state', '=', 'posted'],
    ['payment_state', 'in', ['not_paid', 'partial']]
  ];

  if (overdue_only) {
    const today = new Date().toISOString().split('T')[0];
    domain.push(['invoice_date_due', '<', today]);
  }

  const invoices = await odooClient.search(
    'account.move',
    domain,
    ['name', 'partner_id', 'invoice_date', 'invoice_date_due', 'amount_total', 'amount_residual']
  );

  const totalOutstanding = invoices.reduce((sum, inv) => sum + inv.amount_residual, 0);

  return {
    success: true,
    count: invoices.length,
    total_outstanding: totalOutstanding,
    invoices: invoices.map(inv => ({
      invoice_number: inv.name,
      customer: inv.partner_id[1],  // partner_id is [id, name]
      invoice_date: inv.invoice_date,
      due_date: inv.invoice_date_due,
      amount: inv.amount_total,
      outstanding: inv.amount_residual,
      days_overdue: overdue_only ? calculateDaysOverdue(inv.invoice_date_due) : 0
    }))
  };
}

function calculateDaysOverdue(dueDate) {
  const due = new Date(dueDate);
  const today = new Date();
  const diffTime = today - due;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return Math.max(0, diffDays);
}
```

## Main MCP Server Entry Point

```javascript
// index.js
const { MCPServer } = require('@anthropic/mcp-server');
const OdooClient = require('./src/odoo-client');
const { createInvoiceDraft } = require('./src/tools/invoice');
const { recordExpense } = require('./src/tools/expense');
const { getAccountBalance, generateFinancialReport } = require('./src/tools/report');
const { listUnpaidInvoices } = require('./src/tools/invoice');

require('dotenv').config();

const odooClient = new OdooClient(
  process.env.ODOO_URL,
  process.env.ODOO_DB,
  process.env.ODOO_USERNAME,
  process.env.ODOO_PASSWORD
);

const server = new MCPServer({
  name: 'odoo-accounting',
  version: '1.0.0'
});

// Register tools
server.addTool({
  name: 'create_invoice_draft',
  description: 'Create a draft invoice in Odoo',
  inputSchema: { /* schema from above */ },
  handler: async (params) => await createInvoiceDraft(odooClient, params)
});

server.addTool({
  name: 'record_expense',
  description: 'Record a business expense',
  inputSchema: { /* schema */ },
  handler: async (params) => await recordExpense(odooClient, params)
});

server.addTool({
  name: 'get_account_balance',
  description: 'Get current account balance',
  inputSchema: { /* schema */ },
  handler: async (params) => await getAccountBalance(odooClient, params)
});

server.addTool({
  name: 'generate_financial_report',
  description: 'Generate P&L or Balance Sheet',
  inputSchema: { /* schema */ },
  handler: async (params) => await generateFinancialReport(odooClient, params)
});

server.addTool({
  name: 'list_unpaid_invoices',
  description: 'List all unpaid invoices',
  inputSchema: { /* schema */ },
  handler: async (params) => await listUnpaidInvoices(odooClient, params)
});

// Start server
server.start();
console.log('Odoo MCP Server running on stdio');
```

## Claude Code Configuration

Add to `~/.config/claude-code/mcp.json`:

```json
{
  "servers": [
    {
      "name": "odoo-accounting",
      "command": "node",
      "args": ["/path/to/mcp-servers/odoo-accounting/index.js"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "your_database",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "your_password"
      }
    }
  ]
}
```

## Human-in-the-Loop Workflow

### Invoice Approval Flow

1. **AI detects invoice request** (email, WhatsApp)
2. **AI calls `create_invoice_draft`** → Invoice created in Odoo as DRAFT
3. **AI creates approval file** in `/Pending_Approval/`:

```markdown
---
type: approval_request
action: post_invoice
invoice_id: 123
odoo_invoice_number: INV/2026/0001
customer: Client A
amount: 1500.00
created: 2026-02-26T10:30:00Z
expires: 2026-02-27T10:30:00Z
status: pending
---

## Invoice Details
- Customer: Client A (client@example.com)
- Amount: $1,500.00
- Due Date: 2026-03-15
- Items:
  - Consulting Services (10 hours @ $150/hr)

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

4. **Human reviews and approves** → Moves file to `/Approved/`
5. **Approval processor detects approval** → Calls Odoo API to post invoice
6. **Invoice posted** → Email sent to customer (via Email MCP)
7. **Logged** → Action logged in `/Logs/`

## Error Handling

### Common Errors

1. **Authentication Failure**
   - Retry once with fresh credentials
   - If fails, alert human and pause Odoo operations

2. **Invalid Customer Data**
   - Create approval request for human to verify
   - Don't auto-create customers with incomplete data

3. **Duplicate Invoice**
   - Check for existing invoices before creating
   - Alert if potential duplicate detected

4. **Network Timeout**
   - Retry with exponential backoff (3 attempts)
   - If fails, queue operation for later

### Retry Logic

```javascript
async function withRetry(operation, maxAttempts = 3) {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await operation();
    } catch (error) {
      if (attempt === maxAttempts) throw error;

      const delay = Math.min(1000 * Math.pow(2, attempt), 10000);
      console.log(`Attempt ${attempt} failed, retrying in ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}
```

## Testing

### Unit Tests

```javascript
// test/invoice.test.js
const { createInvoiceDraft } = require('../src/tools/invoice');

describe('Invoice Creation', () => {
  it('should create draft invoice', async () => {
    const result = await createInvoiceDraft(mockOdooClient, {
      customer_name: 'Test Client',
      customer_email: 'test@example.com',
      invoice_lines: [
        { description: 'Service', quantity: 1, price: 100 }
      ],
      due_date: '2026-03-15'
    });

    expect(result.success).toBe(true);
    expect(result.status).toBe('draft');
  });
});
```

### Integration Test

```bash
# Test MCP server manually
node index.js

# In another terminal, test with Claude Code
claude "Create a draft invoice for Test Client (test@example.com) for $500 consulting services"
```

## Security Considerations

1. **Credentials:** Never commit `.env` file
2. **Permissions:** Odoo user should have minimal required permissions
3. **Validation:** Validate all inputs before sending to Odoo
4. **Audit:** Log all Odoo operations
5. **Approval:** All posting/payment actions require human approval

## Performance Optimization

1. **Connection Pooling:** Reuse authenticated sessions
2. **Caching:** Cache frequently accessed data (customers, accounts)
3. **Batch Operations:** Group multiple operations when possible
4. **Lazy Loading:** Only fetch required fields

## Maintenance

### Regular Tasks

- **Weekly:** Review Odoo logs for errors
- **Monthly:** Update customer/vendor data
- **Quarterly:** Backup Odoo database
- **Annually:** Review and update chart of accounts

### Monitoring

- Track API response times
- Monitor authentication failures
- Alert on repeated errors
- Track approval-to-execution ratio

---

**Status:** Ready for implementation
**Next Steps:** Install Odoo 19, create MCP server, test with simple invoice creation

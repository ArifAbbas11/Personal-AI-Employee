# Odoo Accounting Integration - Installation & Setup Guide

---
created: 2026-02-27
status: ready_for_installation
tier: gold
feature: odoo_accounting
---

## 📋 Overview

This guide walks you through installing Odoo ERP and integrating it with your Personal AI Employee system for complete financial management.

**What You'll Get:**
- Full accounting system (invoices, payments, reports)
- Automated financial data in CEO Briefings
- Email-to-invoice automation
- Payment tracking and reminders
- Financial insights and recommendations

**Time Required:** 2-3 hours for complete setup

---

## 🎯 Prerequisites

Before starting, ensure you have:

- [ ] Ubuntu/Debian Linux or WSL2 (Windows)
- [ ] Python 3.8+ installed
- [ ] PostgreSQL database (will install if needed)
- [ ] 4GB+ RAM available
- [ ] 10GB+ disk space
- [ ] Admin/sudo access

---

## 📦 Part 1: Install Odoo

### Option A: Docker Installation (Recommended for Testing)

**Fastest way to get started:**

```bash
# Install Docker if not already installed
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Create Odoo directory
mkdir -p ~/odoo-data

# Run Odoo with PostgreSQL
docker run -d \
  --name odoo-postgres \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -e POSTGRES_DB=postgres \
  postgres:13

docker run -d \
  --name odoo \
  --link odoo-postgres:db \
  -p 8069:8069 \
  -v ~/odoo-data:/var/lib/odoo \
  odoo:16.0

# Wait 30 seconds for Odoo to start
sleep 30

# Check if running
curl http://localhost:8069/web/database/selector
```

**Access Odoo:**
- Open browser: http://localhost:8069
- Create database: `ai_employee_accounting`
- Master password: `admin` (change this!)
- Admin email: your email
- Admin password: create strong password

### Option B: Native Installation (Production)

**For production use:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install PostgreSQL
sudo apt install postgresql postgresql-client -y

# Create Odoo user
sudo useradd -m -d /opt/odoo -U -r -s /bin/bash odoo

# Install dependencies
sudo apt install -y python3-pip python3-dev libxml2-dev libxslt1-dev \
  libldap2-dev libsasl2-dev libtiff5-dev libjpeg8-dev libopenjp2-7-dev \
  zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev \
  libfribidi-dev libxcb1-dev libpq-dev git node-less npm

# Install wkhtmltopdf (for PDF reports)
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bionic_amd64.deb
sudo dpkg -i wkhtmltox_0.12.6-1.bionic_amd64.deb
sudo apt-get install -f -y

# Clone Odoo
sudo su - odoo
git clone https://www.github.com/odoo/odoo --depth 1 --branch 16.0 /opt/odoo/odoo16
exit

# Install Python dependencies
sudo pip3 install -r /opt/odoo/odoo16/requirements.txt

# Create PostgreSQL user
sudo su - postgres -c "createuser -s odoo"

# Create Odoo config
sudo nano /etc/odoo.conf
```

**Odoo config file (`/etc/odoo.conf`):**

```ini
[options]
admin_passwd = YOUR_MASTER_PASSWORD
db_host = localhost
db_port = 5432
db_user = odoo
db_password = False
addons_path = /opt/odoo/odoo16/addons
logfile = /var/log/odoo/odoo-server.log
xmlrpc_port = 8069
```

**Start Odoo:**

```bash
# Create log directory
sudo mkdir /var/log/odoo
sudo chown odoo:odoo /var/log/odoo

# Start Odoo
sudo su - odoo
/opt/odoo/odoo16/odoo-bin -c /etc/odoo.conf
```

---

## 🔧 Part 2: Configure Odoo for AI Employee

### Step 1: Install Accounting Module

1. Open Odoo: http://localhost:8069
2. Login with admin credentials
3. Go to **Apps** menu
4. Search for "Accounting"
5. Click **Install** on "Accounting" module
6. Wait for installation (2-3 minutes)

### Step 2: Configure Company

1. Go to **Settings** → **General Settings**
2. Under **Companies**, click **Update Info**
3. Fill in:
   - Company Name
   - Address
   - Phone
   - Email
   - Currency (USD, EUR, etc.)
4. Click **Save**

### Step 3: Configure Chart of Accounts

1. Go to **Accounting** → **Configuration** → **Chart of Accounts**
2. Review default accounts
3. Add custom accounts if needed:
   - Click **Create**
   - Enter Code (e.g., 100000)
   - Enter Name (e.g., "Main Bank Account")
   - Select Type (e.g., "Bank and Cash")
   - Click **Save**

### Step 4: Create API User

For security, create a dedicated API user:

1. Go to **Settings** → **Users & Companies** → **Users**
2. Click **Create**
3. Fill in:
   - Name: "AI Employee API"
   - Email: api@yourcompany.com
   - Access Rights: Check "Accounting"
4. Click **Save**
5. Set password (save this for config)

### Step 5: Test API Access

```bash
# Test connection
python3 << 'EOF'
import xmlrpc.client

url = "http://localhost:8069"
db = "ai_employee_accounting"
username = "api@yourcompany.com"
password = "your_api_password"

# Authenticate
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if uid:
    print(f"✅ Connected successfully! User ID: {uid}")
else:
    print("❌ Authentication failed")
EOF
```

---

## 🔗 Part 3: Integrate with AI Employee

### Step 1: Configure Odoo Credentials

```bash
cd /mnt/d/AI/Personal-AI-Employee

# Copy template
cp AI_Employee_Vault/Config/odoo_config.json.template \
   AI_Employee_Vault/Config/odoo_config.json

# Edit config
nano AI_Employee_Vault/Config/odoo_config.json
```

**Update with your credentials:**

```json
{
  "url": "http://localhost:8069",
  "database": "ai_employee_accounting",
  "username": "api@yourcompany.com",
  "password": "your_api_password",
  "company_id": 1,
  "default_currency": "USD",
  "approval_required": true,
  "approval_threshold": 1000.0
}
```

### Step 2: Install Python Dependencies

```bash
pip install xmlrpc python-frontmatter
```

### Step 3: Test MCP Server

```bash
cd /mnt/d/AI/Personal-AI-Employee

# Test financial data collector
python3 watchers/data_collectors/financial_collector.py AI_Employee_Vault
```

**Expected output:**

```json
{
  "available": true,
  "period": "2026-02-20 to 2026-02-27",
  "profit_loss": {
    "available": true,
    "revenue": 0.0,
    "expenses": 0.0,
    "net_profit": 0.0,
    "profit_margin": 0.0
  },
  "cash_flow": {
    "available": true,
    "inflows": 0.0,
    "outflows": 0.0,
    "net_cash_flow": 0.0,
    "transactions": 0
  }
}
```

### Step 4: Test CEO Briefing Integration

```bash
# Generate briefing with financial data
python3 watchers/simple_ceo_briefing.py --vault AI_Employee_Vault

# Check output
cat AI_Employee_Vault/Briefings/*_Weekly_Briefing.md
```

You should see a new "Financial Overview" section in the briefing!

---

## 🧪 Part 4: Test Accounting Features

### Test 1: Create a Customer

```bash
# In Odoo web interface:
# 1. Go to Accounting → Customers → Customers
# 2. Click Create
# 3. Name: "Test Customer Inc"
# 4. Email: test@customer.com
# 5. Save
```

### Test 2: Create an Invoice via Claude

```bash
cd /mnt/d/AI/Personal-AI-Employee

# Use Claude Code to create invoice
claude "Create an invoice for Test Customer Inc for $500 for consulting services"
```

**Expected behavior:**
1. Claude uses Odoo skill
2. Invoice created in draft state
3. Approval request created (if > threshold)
4. You approve via approval workflow
5. Invoice posted to Odoo

### Test 3: Check Account Balance

```bash
claude "Show me the current account balances"
```

### Test 4: Generate Financial Report

```bash
claude "Generate a profit and loss report for this month"
```

---

## 📊 Part 5: Verify Integration

### Checklist

- [ ] Odoo running and accessible at http://localhost:8069
- [ ] Accounting module installed
- [ ] API user created and tested
- [ ] Config file created with correct credentials
- [ ] Financial data collector working
- [ ] CEO Briefing shows financial data
- [ ] Can create invoices via Claude
- [ ] Can check balances via Claude
- [ ] Can generate reports via Claude

### Verification Commands

```bash
# 1. Check Odoo is running
curl -s http://localhost:8069/web/database/selector | grep -q "odoo" && echo "✅ Odoo running" || echo "❌ Odoo not running"

# 2. Check config exists
test -f AI_Employee_Vault/Config/odoo_config.json && echo "✅ Config exists" || echo "❌ Config missing"

# 3. Test financial collector
python3 watchers/data_collectors/financial_collector.py AI_Employee_Vault 2>&1 | grep -q "available" && echo "✅ Collector working" || echo "❌ Collector failed"

# 4. Generate test briefing
python3 watchers/simple_ceo_briefing.py --vault AI_Employee_Vault && echo "✅ Briefing generated" || echo "❌ Briefing failed"
```

---

## 🔄 Part 6: Automated Workflows

### Email-to-Invoice Automation

When you receive an email requesting an invoice:

1. Email lands in `Needs_Action/EMAIL_*.md`
2. Claude processes email
3. Extracts: customer, amount, description
4. Creates invoice in Odoo (draft)
5. Creates approval request
6. After approval, posts invoice
7. Sends invoice PDF to customer
8. Moves email to Done/

**Example email processing:**

```bash
# Create test email
cat > AI_Employee_Vault/Needs_Action/EMAIL_INVOICE_REQUEST.md << 'EOF'
---
type: email
from: client@example.com
subject: Invoice Request
---

Hi,

Please invoice us for the consulting work completed last week.
Total: $2,500
Reference: Project Alpha Phase 1

Thanks!
EOF

# Process with Claude
claude "Process all emails in Needs_Action/"
```

### Weekly Financial Reports

Add to your scheduler (cron):

```bash
# Add to crontab
crontab -e

# Run every Monday at 9 AM
0 9 * * 1 cd /mnt/d/AI/Personal-AI-Employee && python3 watchers/simple_ceo_briefing.py --vault AI_Employee_Vault
```

---

## 🚨 Troubleshooting

### Issue: "Odoo not running"

```bash
# Check Docker containers
docker ps | grep odoo

# Restart Odoo
docker restart odoo odoo-postgres

# Check logs
docker logs odoo
```

### Issue: "Authentication failed"

```bash
# Verify credentials
python3 << 'EOF'
import json
with open('AI_Employee_Vault/Config/odoo_config.json') as f:
    config = json.load(f)
    print(f"URL: {config['url']}")
    print(f"Database: {config['database']}")
    print(f"Username: {config['username']}")
    print("Password: [hidden]")
EOF

# Test in Odoo web interface
# Try logging in with same credentials
```

### Issue: "Module not found"

```bash
# Install missing Python packages
pip install xmlrpc python-frontmatter

# Verify installation
python3 -c "import xmlrpc.client; print('✅ xmlrpc installed')"
python3 -c "import frontmatter; print('✅ frontmatter installed')"
```

### Issue: "Financial data not available"

```bash
# Check config file exists
ls -la AI_Employee_Vault/Config/odoo_config.json

# Test connection manually
python3 watchers/data_collectors/financial_collector.py AI_Employee_Vault

# Check Odoo logs
docker logs odoo | tail -50
```

---

## 🎯 Next Steps

After successful installation:

1. **Add Real Data:**
   - Create your actual customers/vendors
   - Import existing invoices
   - Set up bank accounts
   - Configure payment terms

2. **Customize Workflows:**
   - Adjust approval thresholds
   - Configure email templates
   - Set up automatic reminders
   - Create custom reports

3. **Integrate with Other Features:**
   - Link to social media (invoice announcements)
   - Connect to email automation
   - Add to dashboard metrics
   - Include in daily summaries

4. **Production Hardening:**
   - Change default passwords
   - Enable HTTPS
   - Set up backups
   - Configure firewall rules
   - Enable audit logging

---

## 📚 Additional Resources

### Odoo Documentation
- Official Docs: https://www.odoo.com/documentation/16.0/
- Accounting Guide: https://www.odoo.com/documentation/16.0/applications/finance/accounting.html
- API Reference: https://www.odoo.com/documentation/16.0/developer/reference/external_api.html

### AI Employee Integration
- Odoo Skill: `.claude/skills/odoo-accounting.md`
- MCP Server: `watchers/odoo_mcp_server.py`
- Financial Collector: `watchers/data_collectors/financial_collector.py`
- CEO Briefing: `watchers/simple_ceo_briefing.py`

### Support
- Odoo Community: https://www.odoo.com/forum
- GitHub Issues: Create issue in your repo
- Documentation: Review all `*.md` files in project

---

## ✅ Success Criteria

You've successfully integrated Odoo when:

- ✅ Odoo accessible and accounting module installed
- ✅ API connection working
- ✅ CEO Briefing shows financial data
- ✅ Can create invoices via Claude
- ✅ Can generate financial reports
- ✅ Email-to-invoice workflow functioning
- ✅ Weekly briefings include financial insights

**Congratulations! You now have complete financial management integrated with your AI Employee!** 🎉

---

**Installation Status:** Ready for deployment
**Estimated Setup Time:** 2-3 hours
**Difficulty:** Intermediate
**Prerequisites:** Linux/WSL, Python, Docker (optional)

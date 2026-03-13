# Automated Deployment Guide - Gold Tier Features

---
created: 2026-02-27
status: complete
deployment_type: automated
estimated_time: 30_minutes_to_6_hours
---

## 🎯 Overview

This guide provides automated deployment scripts for all Gold Tier features. The scripts simplify deployment by automating configuration, testing, and verification steps.

## 📊 Deployment Scripts

### 1. Odoo Deployment Script
**File:** `deploy_odoo.sh`
**Purpose:** Automated Odoo ERP deployment with Docker
**Time:** 30 minutes - 2 hours
**Prerequisites:** Docker installed and running

### 2. Social Media Deployment Script
**File:** `deploy_social_media.sh`
**Purpose:** Automated social media platform configuration
**Time:** 30 minutes - 2 hours
**Prerequisites:** Developer accounts for platforms

### 3. Deployment Verification Script
**File:** `verify_deployment.sh`
**Purpose:** Comprehensive deployment verification
**Time:** 2-5 minutes
**Prerequisites:** None

## 🚀 Quick Start

### Deploy Everything (Recommended Order)

```bash
# 1. Verify current deployment status
./verify_deployment.sh

# 2. Deploy Odoo (if needed)
./deploy_odoo.sh

# 3. Deploy Social Media (if needed)
./deploy_social_media.sh

# 4. Verify final deployment
./verify_deployment.sh
```

## 📋 Detailed Deployment Instructions

### Step 1: Verify Current Status

Before deploying, check what's already operational:

```bash
./verify_deployment.sh
```

**What it checks:**
- All 6 Gold Tier features
- Configuration files
- Running services
- System health
- Documentation

**Output:**
- ✓ Passed: Features operational
- ⚠ Warnings: Optional features not configured
- ✗ Failed: Critical issues

**Example output:**
```
Feature 1: Ralph Wiggum (Autonomous Loops)
-----------------------------------
✓ Helper script executable
✓ Stop hook executable
✓ Ralph skill exists
✓ User guide exists
✓ Required directories exist
✓ Test files available

...

Verification Summary
========================================
Passed: 35
Warnings: 8
Failed: 0

Deployment Status: 81% operational
```

### Step 2: Deploy Odoo (Optional)

Deploy Odoo ERP for financial management:

```bash
./deploy_odoo.sh
```

**What it does:**
1. Checks prerequisites (Docker)
2. Checks for existing installation
3. Deploys PostgreSQL container
4. Deploys Odoo container
5. Guides through database setup
6. Creates configuration file
7. Tests connection
8. Runs test suite

**Interactive prompts:**
- Remove existing containers? (if found)
- Database setup confirmation
- Configuration details (URL, database, username, password)

**Time required:**
- Docker deployment: 5-10 minutes
- Database setup: 5-10 minutes
- Configuration: 5 minutes
- Testing: 5 minutes
- **Total:** 30 minutes - 1 hour

**What you'll need:**
- Docker installed and running
- Web browser for Odoo setup
- Database credentials (can use defaults)

**After deployment:**
- Odoo accessible at http://localhost:8069
- Configuration saved to `AI_Employee_Vault/Config/odoo_config.json`
- Test suite results displayed

### Step 3: Deploy Social Media (Optional)

Configure social media platform integrations:

```bash
./deploy_social_media.sh
```

**What it does:**
1. Checks prerequisites (Python, requests)
2. Prompts for platform selection
3. Opens developer portals in browser
4. Guides through credential collection
5. Creates configuration file
6. Tests connections
7. Optionally creates test post
8. Optionally starts scheduler

**Interactive prompts:**
- Which platforms to configure?
- Credentials for each platform
- Create test post?
- Start scheduler?

**Time required:**
- Platform selection: 1 minute
- Credential collection per platform: 10-20 minutes
- Configuration: 5 minutes
- Testing: 5 minutes
- **Total:** 30 minutes - 2 hours (depending on platforms)

**What you'll need:**
- Developer accounts for each platform
- Apps created in developer portals
- API credentials (App ID, Secret, Access Tokens)

**After deployment:**
- Configuration saved to `AI_Employee_Vault/Config/social_media_config.json`
- Connection tests completed
- Optional test post created
- Optional scheduler running

### Step 4: Verify Final Deployment

After deploying features, verify everything is operational:

```bash
./verify_deployment.sh
```

**Expected results:**
- Higher deployment percentage
- Fewer warnings
- All critical features passing

## 🔧 Script Details

### deploy_odoo.sh

**Features:**
- Automated Docker deployment
- PostgreSQL setup
- Odoo container configuration
- Interactive database setup
- Configuration file creation
- Connection testing
- Test suite execution

**Options:**
- Environment variables:
  - `ODOO_VERSION` - Odoo version (default: 14)
  - `ODOO_PORT` - Odoo port (default: 8069)
  - `POSTGRES_PORT` - PostgreSQL port (default: 5432)
  - `ODOO_DB` - Database name (default: odoo_db)
  - `ODOO_USER` - Username (default: admin)
  - `ODOO_PASSWORD` - Password (default: admin)

**Example with custom settings:**
```bash
ODOO_VERSION=15 ODOO_PORT=8070 ./deploy_odoo.sh
```

**Docker containers created:**
- `odoo-db` - PostgreSQL database
- `odoo` - Odoo application

**Managing containers:**
```bash
# View logs
docker logs odoo
docker logs odoo-db

# Stop containers
docker stop odoo odoo-db

# Start containers
docker start odoo-db odoo

# Remove containers
docker stop odoo odoo-db
docker rm odoo odoo-db
```

### deploy_social_media.sh

**Features:**
- Platform selection
- Automated browser opening
- Credential collection
- Configuration file creation
- Connection testing
- Test posting
- Scheduler startup

**Platforms supported:**
- Facebook
- Instagram
- Twitter
- LinkedIn

**Configuration structure:**
```json
{
  "facebook": {
    "app_id": "your_app_id",
    "app_secret": "your_app_secret",
    "access_token": "your_access_token"
  },
  "instagram": { ... },
  "twitter": { ... },
  "linkedin": { ... }
}
```

**Credential requirements:**

**Facebook:**
- App ID
- App Secret
- Access Token (with pages_manage_posts, pages_read_engagement)

**Instagram:**
- App ID
- App Secret
- Access Token (Instagram Business account required)

**Twitter:**
- API Key
- API Secret
- Access Token
- Access Token Secret

**LinkedIn:**
- Client ID
- Client Secret
- Access Token

### verify_deployment.sh

**Features:**
- Comprehensive feature checking
- Configuration verification
- Service status checking
- System health monitoring
- Deployment percentage calculation
- Actionable recommendations

**Checks performed:**
- File existence
- Script executability
- Module imports
- Service connectivity
- Container status
- Daemon processes
- Disk space
- Directory permissions

**Exit codes:**
- 0: All critical checks passed
- 1: Critical failures detected

## 🎯 Deployment Scenarios

### Scenario 1: Fresh Installation

**Goal:** Deploy all Gold Tier features from scratch

**Steps:**
```bash
# 1. Verify current status
./verify_deployment.sh

# 2. Deploy Odoo
./deploy_odoo.sh

# 3. Deploy Social Media
./deploy_social_media.sh

# 4. Verify deployment
./verify_deployment.sh

# 5. Test Ralph Wiggum
./ralph_wiggum_setup.sh -s file_movement \
  -f "AI_Employee_Vault/Needs_Action/RALPH_TEST_LOOP.md" \
  "Complete the RALPH_TEST_LOOP.md task"
ccr code "Complete the RALPH_TEST_LOOP.md task"

# 6. Generate CEO Briefing
python3 watchers/simple_ceo_briefing.py
```

**Time:** 2-4 hours
**Result:** All 6 features operational

### Scenario 2: Core Features Only

**Goal:** Deploy core features without external integrations

**Steps:**
```bash
# 1. Verify current status
./verify_deployment.sh

# 2. Test Ralph Wiggum
./ralph_wiggum_setup.sh -s file_movement \
  -f "AI_Employee_Vault/Needs_Action/RALPH_TEST_LOOP.md" \
  "Complete the RALPH_TEST_LOOP.md task"
ccr code "Complete the RALPH_TEST_LOOP.md task"

# 3. Generate CEO Briefing
python3 watchers/simple_ceo_briefing.py

# 4. Start Error Recovery Watchdog
python3 watchers/error_recovery_watchdog.py --daemon &

# 5. Verify deployment
./verify_deployment.sh
```

**Time:** 30 minutes
**Result:** Core features operational (Ralph, CEO Briefing, Error Recovery, Audit Logging)

### Scenario 3: Odoo Only

**Goal:** Add financial management to existing deployment

**Steps:**
```bash
# 1. Deploy Odoo
./deploy_odoo.sh

# 2. Generate CEO Briefing with financial data
python3 watchers/simple_ceo_briefing.py

# 3. Verify deployment
./verify_deployment.sh
```

**Time:** 1-2 hours
**Result:** Financial management operational

### Scenario 4: Social Media Only

**Goal:** Add social media management to existing deployment

**Steps:**
```bash
# 1. Deploy Social Media
./deploy_social_media.sh

# 2. Start scheduler
python3 watchers/social_media_scheduler.py --daemon &

# 3. Verify deployment
./verify_deployment.sh
```

**Time:** 1-2 hours
**Result:** Social media management operational

## 🚨 Troubleshooting

### Issue: Docker not found

**Error:**
```
✗ Docker not found
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io

# macOS
brew install docker

# Start Docker daemon
sudo systemctl start docker
```

### Issue: Docker daemon not running

**Error:**
```
✗ Docker daemon not running
```

**Solution:**
```bash
# Start Docker
sudo systemctl start docker

# Enable Docker on boot
sudo systemctl enable docker

# Check status
sudo systemctl status docker
```

### Issue: Port already in use

**Error:**
```
Error: Port 8069 already in use
```

**Solution:**
```bash
# Find process using port
sudo lsof -i :8069

# Kill process
sudo kill -9 <PID>

# Or use different port
ODOO_PORT=8070 ./deploy_odoo.sh
```

### Issue: Odoo connection failed

**Error:**
```
✗ Odoo connection failed
```

**Solutions:**
1. Verify Odoo is running:
   ```bash
   docker ps | grep odoo
   ```

2. Check Odoo logs:
   ```bash
   docker logs odoo
   ```

3. Verify database was created in Odoo web interface

4. Check credentials in config file:
   ```bash
   cat AI_Employee_Vault/Config/odoo_config.json
   ```

5. Test connection manually:
   ```bash
   python3 watchers/odoo_mcp_server.py --test
   ```

### Issue: Social media connection failed

**Error:**
```
✗ Facebook connection failed
```

**Solutions:**
1. Verify access token is valid (tokens expire)

2. Check app permissions in developer portal

3. Regenerate access token

4. Verify app is not in development mode restrictions

5. Test connection manually:
   ```bash
   python3 watchers/social_media_mcp_server.py --test facebook
   ```

### Issue: Verification script shows warnings

**Warning:**
```
⚠ Odoo not configured
⚠ Social Media not configured
```

**Solution:**
These are optional features. Deploy them if needed:
```bash
./deploy_odoo.sh
./deploy_social_media.sh
```

## 📊 Deployment Checklist

### Pre-Deployment
- [ ] Docker installed (for Odoo)
- [ ] Python 3.8+ installed
- [ ] Git repository cloned
- [ ] All scripts executable
- [ ] Sufficient disk space (5GB+)

### Core Features
- [ ] Ralph Wiggum tested
- [ ] CEO Briefing generated
- [ ] Error Recovery operational
- [ ] Audit Logging operational

### External Integrations
- [ ] Odoo deployed (optional)
- [ ] Social Media configured (optional)
- [ ] Schedulers running (optional)

### Post-Deployment
- [ ] Verification script passed
- [ ] All features tested
- [ ] Documentation reviewed
- [ ] Team trained

## 🎯 Success Criteria

### Minimum (Core Features)
- ✅ Ralph Wiggum working
- ✅ CEO Briefing generating
- ✅ Error Recovery detecting errors
- ✅ Audit Logging ready
- ✅ Verification: 70%+ operational

### Recommended (With Odoo)
- ✅ All core features
- ✅ Odoo deployed and connected
- ✅ Financial data in CEO Briefing
- ✅ Verification: 85%+ operational

### Complete (All Features)
- ✅ All core features
- ✅ Odoo deployed and connected
- ✅ Social Media configured
- ✅ All schedulers running
- ✅ Verification: 95%+ operational

## 📚 Additional Resources

### Documentation
- `GOLD_TIER_DEPLOYMENT_GUIDE.md` - Manual deployment guide
- `GOLD_TIER_PRODUCTION_READINESS_CHECKLIST.md` - Production checklist
- `RALPH_WIGGUM_REFINED_GUIDE.md` - Ralph Wiggum user guide
- `ODOO_INSTALLATION_GUIDE.md` - Detailed Odoo installation
- `SOCIAL_MEDIA_INSTALLATION_GUIDE.md` - Detailed social media setup

### Scripts
- `deploy_odoo.sh` - Odoo deployment
- `deploy_social_media.sh` - Social Media deployment
- `verify_deployment.sh` - Deployment verification
- `ralph_wiggum_setup.sh` - Ralph Wiggum setup

### Test Files
- `AI_Employee_Vault/Needs_Action/RALPH_TEST_LOOP.md` - Ralph test
- `RALPH_QUICK_TEST_REFERENCE.md` - Quick test commands

## 🎉 Next Steps After Deployment

### Immediate (Day 1)
1. Test Ralph Wiggum with real tasks
2. Review first CEO Briefing
3. Monitor error detection
4. Verify audit logging

### Short Term (Week 1)
1. Create invoices in Odoo
2. Post to social media platforms
3. Schedule content
4. Generate weekly CEO Briefing

### Medium Term (Month 1)
1. Optimize performance
2. Refine error recovery strategies
3. Customize CEO Briefing insights
4. Expand social media presence

### Long Term (Quarter 1)
1. Production hardening
2. Security audit
3. Performance optimization
4. Plan Platinum Tier features

---

**Guide Version:** 1.0
**Created:** 2026-02-27
**Status:** Complete
**Estimated Total Time:** 30 minutes - 6 hours (depending on features)

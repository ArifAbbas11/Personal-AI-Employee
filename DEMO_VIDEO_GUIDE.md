# Demo Video Guide - Personal AI Employee Hackathon Submission

**Target Duration:** 5-10 minutes
**Tier:** Gold Tier Complete
**Innovation:** Groq API-powered autonomous reasoning

---

## 🎬 Video Structure

### Opening (30 seconds)
**Script:**
> "Hi, I'm demonstrating my Personal AI Employee for the hackathon. This is a Gold Tier submission featuring autonomous email processing, social media management, and accounting integration - all powered by Groq API's Llama 3.3 70B model for zero-cost reasoning."

**Show:**
- Project directory structure
- Docker containers running: `docker ps`

---

## 📋 Section 1: System Overview (1 minute)

### What to Show
1. **Obsidian Vault Structure**
   ```bash
   ls -la AI_Employee_Vault/
   ```
   - Point out: Needs_Action, Pending_Approval, Approved, Done folders
   - Show Dashboard.md in Obsidian or cat command

2. **Docker Architecture**
   ```bash
   docker ps
   docker logs ai-employee-watchers --tail 20
   ```
   - 3 containers: watchers, odoo, postgres
   - All healthy and running

3. **Agent Skills**
   ```bash
   ls .claude/skills/
   ```
   - Show 10+ skills including generate_ceo_briefing, process_inbox

**Script:**
> "The system uses Obsidian as the knowledge base, Docker for containerization, and Claude Code Agent Skills for automation. All watchers run 24/7 monitoring Gmail, filesystem, and generating responses."

---

## 📧 Section 2: Email Processing Demo (2 minutes)

### Setup
1. Show current email in Pending_Approval:
   ```bash
   ls AI_Employee_Vault/Pending_Approval/emails/
   cat AI_Employee_Vault/Pending_Approval/emails/EMAIL_RESPONSE_20260312_124155_19ce1e87.md
   ```

2. Show the drafted response (professional demo request reply)

### Demonstrate Workflow
**Script:**
> "Here's an email from a client requesting a demo. The system automatically drafted a professional response. Let me show the approval workflow."

```bash
# Show the approval request
cat AI_Employee_Vault/Pending_Approval/emails/EMAIL_RESPONSE_20260312_124155_19ce1e87.md

# Approve it
mv AI_Employee_Vault/Pending_Approval/emails/EMAIL_RESPONSE_20260312_124155_19ce1e87.md \
   AI_Employee_Vault/Approved/emails/

# Show it moved
ls AI_Employee_Vault/Approved/emails/
```

**Script:**
> "Within 60 seconds, the GmailAutoResponder will automatically send this email. This demonstrates the human-in-the-loop approval workflow - sensitive actions require explicit approval."

---

## 🤖 Section 3: Ralph Groq Autonomous Agent (2 minutes)

### The Innovation
**Script:**
> "The key innovation is Ralph Groq - an autonomous agent using Groq's free API instead of Claude Code. This gives us 14,400 free requests per day with Llama 3.3 70B."

### Live Demo
1. Create a test task:
   ```bash
   cat > AI_Employee_Vault/Needs_Action/TEST_TASK.md << 'EOF'
   ---
   type: test_task
   priority: medium
   ---

   # Test Task

   Please create a summary of the current system status and save it to Done/general/SYSTEM_STATUS_SUMMARY.md
   EOF
   ```

2. Run Ralph Groq:
   ```bash
   export $(grep -v '^#' .env | xargs)
   ./ralph_groq_setup.sh -s empty_folder "Process the test task in Needs_Action. Read it, create the requested summary, and move to Done/general/"
   ```

3. Show the result:
   ```bash
   ls AI_Employee_Vault/Done/general/
   cat AI_Employee_Vault/Done/general/SYSTEM_STATUS_SUMMARY.md
   ```

**Script:**
> "Ralph Groq autonomously read the task, analyzed the system, created the summary, and moved it to Done. It uses a continuous iteration loop - it keeps working until the task is complete or max iterations reached."

---

## 📊 Section 4: Gold Tier Features (2 minutes)

### 1. Odoo Accounting Integration
```bash
# Show Odoo is running
docker logs ai-employee-odoo --tail 10

# Show MCP server configuration
cat ~/.config/claude-code/mcp.json | grep -A 10 "odoo"
```

**Script:**
> "Odoo Community Edition runs in Docker, integrated via MCP server using JSON-RPC APIs. The AI can create invoices, track expenses, and generate financial reports."

### 2. Social Media Integration
```bash
# Show social media configuration
ls watchers/*social*.py
cat .env | grep -E "(TWITTER|FACEBOOK|INSTAGRAM)"
```

**Script:**
> "Twitter, Facebook, and Instagram are integrated. The system can draft posts, schedule content, and generate engagement summaries."

### 3. Automated Scheduling
```bash
# Show cron jobs
crontab -l | grep -A 20 "Personal AI Employee"
```

**Script:**
> "12 automated tasks run on schedule: CEO briefing every Monday, Gmail checks every 10 minutes, health monitoring every 15 minutes, daily backups at 3 AM."

### 4. CEO Briefing
```bash
# Show CEO briefing skill
cat .claude/skills/generate_ceo_briefing/skill.md | head -30
```

**Script:**
> "The Monday Morning CEO Briefing is the standout feature - it autonomously audits business performance, identifies bottlenecks, and provides proactive suggestions. This transforms the AI from reactive to proactive."

---

## 🔧 Section 5: Technical Architecture (1 minute)

### Show Key Components
```bash
# Watchers
ls watchers/*.py | wc -l

# Agent Skills
ls .claude/skills/ | wc -l

# MCP Servers
cat ~/.config/claude-code/mcp.json | grep "command" | wc -l

# Code statistics
find . -name "*.py" -not -path "./venv/*" | xargs wc -l | tail -1
```

**Script:**
> "The system has 20+ Python watchers, 10+ Agent Skills, 5 MCP servers, and over 16,000 lines of code. Everything runs in Docker for portability and reliability."

---

## 🎯 Section 6: Hackathon Compliance (1 minute)

### Bronze Tier ✅
- Obsidian vault with required files
- Working watcher (Gmail)
- Claude Code integration
- Folder structure

### Silver Tier ✅
- Multiple watchers (6 active)
- LinkedIn automation
- Plan.md generation
- MCP servers (5 configured)
- Human-in-the-loop workflow
- Automated scheduling (cron)

### Gold Tier ✅
- Cross-domain integration
- Odoo accounting (self-hosted)
- Social media (3 platforms)
- Multiple MCP servers
- CEO Briefing
- Error recovery
- Audit logging
- Ralph Wiggum loop
- Complete documentation

**Script:**
> "This submission meets all Gold Tier requirements plus adds the innovation of Groq API integration for zero-cost autonomous reasoning."

---

## 🏁 Closing (30 seconds)

### Show Dashboard
```bash
cat AI_Employee_Vault/Dashboard.md | head -50
```

**Script:**
> "The Dashboard shows real-time system status. All watchers are running, containers are healthy, and the system is fully operational. This AI Employee can manage emails, social media, accounting, and business operations 24/7 with minimal human intervention. Thank you for watching!"

---

## 📝 Recording Tips

### Before Recording
1. ✅ Start all Docker containers: `docker-compose up -d`
2. ✅ Clear terminal history: `clear`
3. ✅ Set terminal to readable font size (14-16pt)
4. ✅ Close unnecessary applications
5. ✅ Test audio and screen recording
6. ✅ Have all commands ready in a script

### During Recording
- Speak clearly and at moderate pace
- Show commands before running them
- Explain what you're doing as you do it
- Highlight key innovations (Groq API, Ralph Wiggum)
- Keep energy high and enthusiasm visible

### After Recording
- Edit out long pauses or errors
- Add title card with project name and tier
- Add captions for key points
- Export in 1080p MP4 format
- Keep under 10 minutes

---

## 🎥 Quick Recording Script

```bash
#!/bin/bash
# Run this before recording to prepare the demo

# 1. Start containers
docker-compose up -d
sleep 10

# 2. Create test task
cat > AI_Employee_Vault/Needs_Action/DEMO_TASK.md << 'EOF'
---
type: demo
priority: high
---

# Demo Task

Create a brief system status report and save to Done/general/
EOF

# 3. Prepare environment
export $(grep -v '^#' .env | xargs)

# 4. Clear logs
> logs/orchestrator.log

echo "✅ Demo environment ready!"
echo "Start recording now."
```

---

## 📤 Submission Checklist

After recording the video:

- [ ] Video is 5-10 minutes long
- [ ] Shows all Gold Tier features
- [ ] Demonstrates Ralph Groq autonomous agent
- [ ] Shows human-in-the-loop approval workflow
- [ ] Explains Groq API innovation
- [ ] Shows system architecture
- [ ] Demonstrates live email processing
- [ ] Shows automated scheduling
- [ ] Displays Dashboard and vault structure
- [ ] Includes closing summary

Upload to YouTube (unlisted) and include link in hackathon submission form.

---

**Good luck with your demo! 🚀**

# Social Media Integration - Installation & Setup Guide

---
created: 2026-02-27
status: ready_for_installation
tier: gold
feature: social_media_integration
---

## 📋 Overview

This guide walks you through setting up multi-platform social media management for your Personal AI Employee system.

**What You'll Get:**
- Post to Facebook, Instagram, Twitter/X, and LinkedIn
- Schedule posts for optimal times
- Track engagement and analytics
- Automated content workflows
- Weekly social media reports in CEO Briefing

**Time Required:** 2-3 hours for complete setup

---

## 🎯 Prerequisites

Before starting, ensure you have:

- [ ] Business accounts on desired platforms
- [ ] Admin access to social media accounts
- [ ] Python 3.8+ installed
- [ ] Internet connection
- [ ] Email access for verification

---

## 📦 Part 1: Platform Setup

### Facebook Setup

**Step 1: Create Facebook App**

1. Go to https://developers.facebook.com/
2. Click "My Apps" → "Create App"
3. Select "Business" as app type
4. Fill in app details:
   - App Name: "AI Employee Social Manager"
   - Contact Email: your email
5. Click "Create App"

**Step 2: Add Facebook Login**

1. In app dashboard, click "Add Product"
2. Select "Facebook Login" → "Set Up"
3. Choose "Web" platform
4. Enter Site URL: `http://localhost`

**Step 3: Get Access Token**

1. Go to Tools → Graph API Explorer
2. Select your app
3. Click "Generate Access Token"
4. Grant permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_show_list`
5. Copy the access token (save for later)

**Step 4: Get Page ID**

1. Go to your Facebook Page
2. Click "About"
3. Scroll to "Page ID" (or use Graph API Explorer)
4. Copy Page ID (save for later)

**Step 5: Get Long-Lived Token**

```bash
# Exchange short-lived token for long-lived token
curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_TOKEN"
```

Save the long-lived access token.

---

### Instagram Setup

**Prerequisites:**
- Instagram Business Account
- Facebook Page linked to Instagram account

**Step 1: Link Instagram to Facebook**

1. Go to Instagram app → Settings → Account
2. Select "Linked Accounts"
3. Link to your Facebook Page

**Step 2: Get Instagram Business Account ID**

```bash
# Using Facebook access token
curl -X GET "https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_FB_ACCESS_TOKEN"

# Find your page, then get Instagram account
curl -X GET "https://graph.facebook.com/v18.0/PAGE_ID?fields=instagram_business_account&access_token=YOUR_FB_ACCESS_TOKEN"
```

Copy the Instagram Business Account ID.

**Step 3: Verify Permissions**

Required permissions:
- `instagram_basic`
- `instagram_content_publish`
- `pages_read_engagement`

---

### Twitter/X Setup

**Step 1: Create Twitter Developer Account**

1. Go to https://developer.twitter.com/
2. Click "Sign up" (use your Twitter account)
3. Apply for developer access
4. Fill in application:
   - Use case: "Building social media management tool"
   - Will you make Twitter content available to government: No
5. Wait for approval (usually instant to 24 hours)

**Step 2: Create Twitter App**

1. Go to Developer Portal → Projects & Apps
2. Click "Create App"
3. Fill in app details:
   - App Name: "AI Employee Social"
   - Description: "Social media management"
4. Click "Create"

**Step 3: Get API Keys**

1. In app settings, go to "Keys and tokens"
2. Generate and save:
   - API Key
   - API Secret Key
   - Bearer Token
   - Access Token
   - Access Token Secret

**Step 4: Set Permissions**

1. Go to app settings → "User authentication settings"
2. Set permissions to "Read and Write"
3. Save changes

---

### LinkedIn Setup

**Step 1: Create LinkedIn App**

1. Go to https://www.linkedin.com/developers/
2. Click "Create app"
3. Fill in details:
   - App Name: "AI Employee Social"
   - LinkedIn Page: Select your company page
   - Privacy Policy URL: your URL
   - App Logo: upload logo
4. Click "Create app"

**Step 2: Request Access**

1. In app settings, go to "Products"
2. Request access to:
   - "Share on LinkedIn"
   - "Sign In with LinkedIn"
3. Wait for approval (usually instant)

**Step 3: Get Credentials**

1. Go to "Auth" tab
2. Copy:
   - Client ID
   - Client Secret

**Step 4: Get Access Token (OAuth 2.0)**

```bash
# Step 1: Get authorization code
# Open in browser:
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost&scope=w_member_social

# Step 2: Exchange code for access token
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_AUTH_CODE" \
  -d "redirect_uri=http://localhost" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

Save the access token.

**Step 5: Get Person URN**

```bash
curl -X GET https://api.linkedin.com/v2/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Copy the `id` field (this is your Person URN).

---

## 🔧 Part 2: Configure AI Employee

### Step 1: Install Python Dependencies

```bash
pip install requests
```

### Step 2: Create Configuration File

```bash
cd /mnt/d/AI/Personal-AI-Employee

# Copy template
cp AI_Employee_Vault/Config/social_media_config.json.template \
   AI_Employee_Vault/Config/social_media_config.json

# Edit config
nano AI_Employee_Vault/Config/social_media_config.json
```

### Step 3: Fill in Credentials

Update `social_media_config.json` with your credentials:

```json
{
  "queue_path": "/tmp/social_media_queue",
  "facebook": {
    "enabled": true,
    "access_token": "YOUR_FACEBOOK_LONG_LIVED_TOKEN",
    "page_id": "YOUR_FACEBOOK_PAGE_ID",
    "api_version": "v18.0"
  },
  "instagram": {
    "enabled": true,
    "access_token": "YOUR_FACEBOOK_ACCESS_TOKEN",
    "account_id": "YOUR_INSTAGRAM_BUSINESS_ACCOUNT_ID",
    "api_version": "v18.0"
  },
  "twitter": {
    "enabled": true,
    "api_key": "YOUR_TWITTER_API_KEY",
    "api_secret": "YOUR_TWITTER_API_SECRET",
    "access_token": "YOUR_TWITTER_ACCESS_TOKEN",
    "access_secret": "YOUR_TWITTER_ACCESS_SECRET",
    "bearer_token": "YOUR_TWITTER_BEARER_TOKEN"
  },
  "linkedin": {
    "enabled": true,
    "access_token": "YOUR_LINKEDIN_ACCESS_TOKEN",
    "person_urn": "urn:li:person:YOUR_PERSON_ID"
  },
  "posting_rules": {
    "require_approval": true,
    "max_posts_per_day": 10,
    "min_interval_minutes": 30
  }
}
```

---

## 🧪 Part 3: Test Integration

### Test 1: Test Facebook Posting

```bash
cd /mnt/d/AI/Personal-AI-Employee

# Test via Claude
claude "Post to Facebook: 'Testing AI Employee social media integration! 🤖'"
```

**Expected behavior:**
1. Claude uses social media skill
2. Creates approval request
3. You approve
4. Post published to Facebook
5. Returns post URL

### Test 2: Test Instagram Posting

```bash
# Note: Instagram requires an image
claude "Post to Instagram: 'Hello from AI Employee!' with image from /path/to/image.jpg"
```

### Test 3: Test Twitter Posting

```bash
claude "Tweet: 'Just set up automated social media management with AI Employee! 🚀'"
```

### Test 4: Test LinkedIn Posting

```bash
claude "Post to LinkedIn: 'Excited to share our progress on AI-powered business automation.'"
```

### Test 5: Test Scheduling

```bash
claude "Schedule a Facebook post for tomorrow at 10 AM: 'Good morning everyone!'"
```

**Verify scheduled post:**

```bash
python3 watchers/social_media_scheduler.py --list
```

### Test 6: Process Scheduled Posts

```bash
# Dry run (don't actually post)
python3 watchers/social_media_scheduler.py --process --dry-run

# Actually process queue
python3 watchers/social_media_scheduler.py --process
```

---

## 📊 Part 4: Verify Integration

### Checklist

- [ ] All desired platforms configured
- [ ] Test post successful on each platform
- [ ] Scheduling working correctly
- [ ] Scheduler can process queue
- [ ] Posts appear on platforms
- [ ] Approval workflow functioning

### Verification Commands

```bash
# 1. Check config exists
test -f AI_Employee_Vault/Config/social_media_config.json && echo "✅ Config exists" || echo "❌ Config missing"

# 2. Test MCP server
echo '{"tool": "get_platform_stats", "params": {"platform": "facebook", "days": 7}}' | python3 watchers/social_media_mcp_server.py

# 3. List scheduled posts
python3 watchers/social_media_scheduler.py --list

# 4. Check queue directory
ls -la /tmp/social_media_queue/
```

---

## 🔄 Part 5: Automated Workflows

### Start Scheduler Daemon

Run scheduler as background service:

```bash
# Start scheduler daemon
nohup python3 watchers/social_media_scheduler.py --daemon --interval 60 > /tmp/social_scheduler.log 2>&1 &

# Check if running
ps aux | grep social_media_scheduler

# View logs
tail -f /tmp/social_scheduler.log
```

### Add to Cron (Alternative)

```bash
# Edit crontab
crontab -e

# Add line to check queue every 5 minutes
*/5 * * * * cd /mnt/d/AI/Personal-AI-Employee && python3 watchers/social_media_scheduler.py --process >> /tmp/social_scheduler.log 2>&1
```

### Weekly Content Generation

```bash
# Add to crontab for Monday 9 AM
0 9 * * 1 cd /mnt/d/AI/Personal-AI-Employee && claude "Generate 5 social media posts for this week and schedule them"
```

---

## 🚨 Troubleshooting

### Issue: "Platform not configured"

```bash
# Check config file
cat AI_Employee_Vault/Config/social_media_config.json | grep enabled

# Verify platform is enabled: true
```

### Issue: "Authentication failed"

```bash
# Test access token manually
# Facebook:
curl "https://graph.facebook.com/v18.0/me?access_token=YOUR_TOKEN"

# Twitter:
curl -H "Authorization: Bearer YOUR_BEARER_TOKEN" "https://api.twitter.com/2/users/me"

# LinkedIn:
curl -H "Authorization: Bearer YOUR_TOKEN" "https://api.linkedin.com/v2/me"
```

### Issue: "Rate limit exceeded"

- Wait 15-60 minutes
- Check platform rate limits
- Reduce posting frequency
- Increase `min_interval_minutes` in config

### Issue: "Media upload failed"

- Verify image format (JPG, PNG)
- Check file size (< 5MB for most platforms)
- Ensure image URL is accessible
- Try different image

---

## 📈 Part 6: Analytics & Monitoring

### View Platform Stats

```bash
claude "Show me Facebook stats for the last 7 days"
claude "Get Instagram analytics"
claude "Show Twitter engagement metrics"
```

### Weekly Report

Social media metrics automatically included in CEO Briefing:
- Posts published per platform
- Total engagement
- Top performing posts
- Scheduling status

### Monitor Queue

```bash
# List pending posts
python3 watchers/social_media_scheduler.py --list

# Clear completed posts
python3 watchers/social_media_scheduler.py --clear
```

---

## 🎯 Next Steps

After successful installation:

1. **Create Content Calendar:**
   - Plan weekly content themes
   - Schedule posts in advance
   - Maintain consistent posting schedule

2. **Set Up Monitoring:**
   - Enable platform notifications
   - Monitor engagement metrics
   - Track follower growth

3. **Integrate with Workflows:**
   - Email-to-social automation
   - Content approval process
   - Analytics reporting

4. **Optimize Performance:**
   - Test different posting times
   - Analyze engagement patterns
   - Refine content strategy

---

## 📚 Additional Resources

### Platform Documentation
- Facebook Graph API: https://developers.facebook.com/docs/graph-api
- Instagram API: https://developers.facebook.com/docs/instagram-api
- Twitter API: https://developer.twitter.com/en/docs
- LinkedIn API: https://docs.microsoft.com/en-us/linkedin/

### AI Employee Integration
- Social Media Skill: `.claude/skills/social-media.md`
- MCP Server: `watchers/social_media_mcp_server.py`
- Scheduler: `watchers/social_media_scheduler.py`

### Best Practices
- Post during optimal times for each platform
- Use platform-appropriate content formats
- Engage with comments and messages
- Monitor analytics regularly
- Maintain brand consistency

---

## ✅ Success Criteria

You've successfully integrated social media when:

- ✅ All desired platforms configured
- ✅ Can post to each platform via Claude
- ✅ Scheduling system working
- ✅ Scheduler daemon running
- ✅ Approval workflow functioning
- ✅ Analytics accessible
- ✅ Posts appearing on platforms

**Congratulations! You now have complete social media management integrated with your AI Employee!** 🎉

---

**Installation Status:** Ready for deployment
**Estimated Setup Time:** 2-3 hours
**Difficulty:** Intermediate
**Prerequisites:** Business accounts on social platforms, API access

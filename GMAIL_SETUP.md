# Gmail Watcher Setup Guide

This guide walks you through setting up Gmail integration for your Personal AI Employee.

## Prerequisites

- Python 3.8 or higher
- Google account with Gmail
- Internet connection

## Step 1: Install Required Libraries

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Step 2: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Name it something like "Personal AI Employee"

## Step 3: Enable Gmail API

1. In Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Gmail API"
3. Click on "Gmail API" and click **Enable**

## Step 4: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: **External** (unless you have a Google Workspace)
   - App name: "Personal AI Employee"
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add `https://www.googleapis.com/auth/gmail.readonly`
   - Test users: Add your email address
   - Click **Save and Continue**

4. Create OAuth Client ID:
   - Application type: **Desktop app**
   - Name: "Personal AI Employee Desktop"
   - Click **Create**

5. Download the credentials:
   - Click the download icon (⬇️) next to your newly created OAuth client
   - Save the file as `credentials.json` in your project root directory

## Step 5: Place Credentials File

Move the downloaded `credentials.json` to your project directory:

```bash
mv ~/Downloads/credentials.json /mnt/d/AI/Personal-AI-Employee/credentials.json
```

## Step 6: First-Time Authentication

Run the Gmail watcher for the first time to authenticate:

```bash
cd /mnt/d/AI/Personal-AI-Employee/watchers
python gmail_watcher.py ../AI_Employee_Vault ../credentials.json
```

This will:
1. Open your browser automatically
2. Ask you to sign in to your Google account
3. Request permission to read your Gmail (read-only access)
4. Save the authentication token to `token.pickle`

**Important:** The watcher only requests **read-only** access. It cannot send emails, delete emails, or modify your Gmail account.

## Step 7: Verify Setup

After authentication, you should see:

```
✅ Gmail authentication successful
🔍 Starting Gmail Watcher...
📁 Vault: /mnt/d/AI/Personal-AI-Employee/AI_Employee_Vault
⏱️  Check interval: 2 minutes
Connected to Gmail: your.email@gmail.com
```

The watcher will now:
- Check your Gmail inbox every 2 minutes
- Look for unread, important, or starred emails
- Create action items in `AI_Employee_Vault/Needs_Action/` for new emails

## Step 8: Test the Watcher

1. Send yourself a test email and mark it as important
2. Wait up to 2 minutes
3. Check `AI_Employee_Vault/Needs_Action/` for a new `EMAIL_*.md` file

## Configuration

### Adjust Check Interval

Edit `gmail_watcher.py` line 14 to change the check interval:

```python
def __init__(self, vault_path: str, credentials_path: str, check_interval: int = 120):
```

Change `120` (2 minutes) to your preferred interval in seconds.

### Add Important Senders

Edit `gmail_watcher.py` line 40 to add email addresses that should always be flagged as important:

```python
self.important_senders = [
    'boss@company.com',
    'client@important.com'
]
```

### Customize Urgent Keywords

Edit `gmail_watcher.py` lines 33-38 to customize keywords that trigger high priority:

```python
self.urgent_keywords = [
    'urgent', 'asap', 'important', 'critical',
    'invoice', 'payment', 'overdue', 'deadline',
    'meeting', 'call', 'emergency'
]
```

## Running as a Service

### Option 1: Background Process

```bash
cd /mnt/d/AI/Personal-AI-Employee/watchers
nohup python gmail_watcher.py ../AI_Employee_Vault ../credentials.json > ../logs/gmail_watcher.log 2>&1 &
```

### Option 2: Systemd Service (Linux)

Create `/etc/systemd/system/gmail-watcher.service`:

```ini
[Unit]
Description=Personal AI Employee - Gmail Watcher
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/mnt/d/AI/Personal-AI-Employee/watchers
ExecStart=/usr/bin/python3 gmail_watcher.py ../AI_Employee_Vault ../credentials.json
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable gmail-watcher
sudo systemctl start gmail-watcher
sudo systemctl status gmail-watcher
```

### Option 3: Cron Job

Add to crontab (runs every 5 minutes):

```bash
crontab -e
```

Add this line:

```
*/5 * * * * cd /mnt/d/AI/Personal-AI-Employee/watchers && python gmail_watcher.py ../AI_Employee_Vault ../credentials.json >> ../logs/gmail_watcher.log 2>&1
```

## Troubleshooting

### Error: "credentials.json not found"

Make sure you downloaded the OAuth credentials and placed them in the correct location:

```bash
ls -la /mnt/d/AI/Personal-AI-Employee/credentials.json
```

### Error: "Access blocked: This app's request is invalid"

Your OAuth consent screen needs to be configured:
1. Go to Google Cloud Console > APIs & Services > OAuth consent screen
2. Add your email to "Test users"
3. Make sure the app is in "Testing" mode (not "Production")

### Error: "The user has not granted the app..."

You need to complete the OAuth flow:
1. Delete `token.pickle` if it exists
2. Run the watcher again
3. Complete the browser authentication flow

### Error: "Token has been expired or revoked"

Your authentication token expired. Delete it and re-authenticate:

```bash
rm /mnt/d/AI/Personal-AI-Employee/token.pickle
cd /mnt/d/AI/Personal-AI-Employee/watchers
python gmail_watcher.py ../AI_Employee_Vault ../credentials.json
```

### No Emails Being Detected

Check the Gmail query in `gmail_watcher.py` line 53:

```python
query = 'is:unread (is:important OR is:starred)'
```

You can modify this to:
- `is:unread` - All unread emails
- `is:unread from:specific@email.com` - Unread from specific sender
- `is:unread subject:invoice` - Unread with "invoice" in subject

## Security Notes

1. **Read-Only Access:** The watcher only requests `gmail.readonly` scope
2. **Local Storage:** Authentication tokens are stored locally in `token.pickle`
3. **No Cloud Storage:** Your emails are never sent to external servers
4. **Revoke Access:** You can revoke access anytime at [Google Account Permissions](https://myaccount.google.com/permissions)

## Privacy

- The AI Employee only reads email metadata (from, subject, date) and snippets
- Full email bodies are only accessed when you explicitly process an action item
- All data stays on your local machine
- No email content is sent to external services

## Next Steps

Once Gmail watcher is running:
1. Test with a few emails to verify it works
2. Adjust priority keywords and important senders
3. Set up the watcher to run automatically (systemd or cron)
4. Use the `/process-inbox` skill to handle email action items

## Support

If you encounter issues:
1. Check the logs: `tail -f /mnt/d/AI/Personal-AI-Employee/logs/gmail_watcher.log`
2. Verify credentials are valid
3. Check Google Cloud Console for API quota limits
4. Review the troubleshooting section above

---

**Setup Complete!** Your Gmail watcher is now monitoring your inbox and creating action items for important emails.

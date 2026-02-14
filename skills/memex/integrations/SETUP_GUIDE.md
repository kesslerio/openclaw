````markdown
# Gmail & Calendar Integration Setup Guide

Complete setup guide for Gmail and Calendar integrations with Memex.

## Overview

This integration allows Memex to fetch:

- **Emails** from Gmail (both work and personal accounts)
- **Calendar events** from Google Calendar

**Accounts configured**:

- Work: `arvind@copperdigital.com`
- Personal: `arvind.sarin@gmail.com` (21+ years of history!)

---

## Prerequisites

### 1. Google Cloud Project (5 minutes)

You need OAuth2 credentials from Google Cloud Console.

#### Step-by-step:

1. **Go to Google Cloud Console**:
   - https://console.cloud.google.com

2. **Create or select project**:
   - Click project dropdown → "New Project"
   - Name: "Memex Integrations"
   - Click "Create"

3. **Enable APIs**:
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API" → Enable
   - Search for "Google Calendar API" → Enable

4. **Create OAuth2 Credentials**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Name: "Memex Desktop Client"
   - Click "Create"

5. **Download credentials**:
   - Click the download icon (⬇️) next to your new OAuth client
   - Save as `credentials.json`

6. **Place credentials file**:
   ```bash
   mv ~/Downloads/credentials.json ~/openclaw/credentials.json
   ```
````

### 2. Install Dependencies (1 minute)

```bash
cd ~/Cursor/Claude-2026/openclaw
pip install -r memex/integrations/requirements.txt
```

Dependencies installed:

- `google-api-python-client` - Gmail/Calendar API client
- `google-auth-oauthlib` - OAuth2 flow
- `google-auth-httplib2` - HTTP transport
- `google-auth` - Authentication library

---

## Setup Process

### Step 1: Authorize Accounts (10 minutes)

Run the setup script to authorize all accounts:

```bash
cd ~/Cursor/Claude-2026/openclaw
python memex/scripts/setup_gmail_calendar.py --authorize-all
```

**What happens**:

1. Opens browser for work account Gmail authorization
2. Opens browser for work account Calendar authorization
3. Opens browser for personal account Gmail authorization
4. Opens browser for personal account Calendar authorization

**For each authorization**:

- Sign in with the appropriate Google account
- Review permissions (read-only access)
- Click "Allow"
- Browser will show "The authentication flow has completed"
- Close browser tab

**Tokens saved to**:

- `~/openclaw/.tokens/gmail_arvind@copperdigital.com.json`
- `~/openclaw/.tokens/gmail_arvind.sarin@gmail.com.json`
- `~/openclaw/.tokens/calendar_arvind@copperdigital.com.json`
- `~/openclaw/.tokens/calendar_arvind.sarin@gmail.com.json`

### Step 2: Test Connections (2 minutes)

Verify everything works:

```bash
python memex/scripts/setup_gmail_calendar.py --test-all
```

**Expected output**:

```
🧪 Testing Gmail connection for arvind@copperdigital.com...
✅ Connection successful!
   Found 42 emails from last 7 days

📧 Sample (latest 3):
   • 2026-02-04 - Weekly Standup Notes
   • 2026-02-03 - CopperAI Product Update
   • 2026-02-02 - Meeting with LarCare

🧪 Testing Calendar connection for arvind@copperdigital.com...
✅ Connection successful!
   Found 3 calendars
   Found 15 events from last 7 days

📅 Sample (latest 3):
   • 2026-02-04 10:00 - Team Standup
   • 2026-02-04 14:00 - Client Demo
   • 2026-02-03 09:00 - Weekly Planning

✅ All tests passed!
```

---

## Usage

### Sync Data

#### Sync Last 30 Days (Default)

```bash
cd ~/Cursor/Claude-2026/openclaw
python memex/scripts/sync_gmail_calendar.py
```

Fetches:

- Gmail: Last 30 days of emails from both accounts
- Calendar: Last 30 days of events from both accounts

#### Sync Specific Date Range

```bash
# Sync January 2026
python memex/scripts/sync_gmail_calendar.py \
    --start-date 2026-01-01 \
    --end-date 2026-01-31

# Sync last 90 days
python memex/scripts/sync_gmail_calendar.py \
    --start-date 2025-11-06 \
    --end-date 2026-02-04
```

#### Sync Only Gmail

```bash
python memex/scripts/sync_gmail_calendar.py --gmail-only
```

#### Sync Only Calendar

```bash
python memex/scripts/sync_gmail_calendar.py --calendar-only
```

#### Sync Specific Account

```bash
# Work email only
python memex/scripts/sync_gmail_calendar.py \
    --email arvind@copperdigital.com

# Personal email only
python memex/scripts/sync_gmail_calendar.py \
    --email arvind.sarin@gmail.com
```

### Data Output

Data is saved to:

```
~/Cursor/Claude-2026/openclaw/skills/memex/data/integrations/
├── gmail/
│   ├── arvind@copperdigital.com/
│   │   ├── manifest.json
│   │   ├── 2026-02-01/
│   │   │   ├── email_<message_id>.json
│   │   │   └── ...
│   │   ├── 2026-02-02/
│   │   └── ...
│   └── arvind.sarin@gmail.com/
│       └── ...
└── calendar/
    ├── arvind@copperdigital.com/
    │   ├── manifest.json
    │   ├── 2026-02-01/
    │   │   ├── event_<event_id>.json
    │   │   └── ...
    │   └── ...
    └── arvind.sarin@gmail.com/
        └── ...
```

**File structure**:

- Organized by date (`YYYY-MM-DD` folders)
- One JSON file per email/event
- Manifest file with sync metadata

### Python API Usage

#### Gmail

```python
from memex.integrations import GmailService, GmailConfig
from datetime import datetime, timedelta

# Configure
config = GmailConfig(
    credentials_path="~/openclaw/credentials.json",
    token_dir="~/openclaw/.tokens"
)

# Create service
service = GmailService(
    config=config,
    account_email="arvind@copperdigital.com"
)

# Connect
service.connect()

# Fetch emails
start_date = datetime.now() - timedelta(days=7)
emails = service.fetch_emails(
    start_date=start_date,
    max_emails=100
)

# Process emails
for email in emails:
    print(f"{email.date}: {email.subject}")
    print(f"From: {email.from_}")
    print(f"To: {', '.join(str(p) for p in email.to)}")
    print(f"Body: {email.body_text[:200]}...")
    print()
```

#### Calendar

```python
from memex.integrations import CalendarService, CalendarConfig
from datetime import datetime, timedelta

# Configure
config = CalendarConfig(
    credentials_path="~/openclaw/credentials.json",
    token_dir="~/openclaw/.tokens"
)

# Create service
service = CalendarService(
    config=config,
    account_email="arvind@copperdigital.com"
)

# Connect
service.connect()

# Fetch events
start_date = datetime.now() - timedelta(days=7)
events = service.fetch_events(
    calendar_id="primary",
    start_date=start_date,
    max_events=50
)

# Process events
for event in events:
    print(f"{event.start.strftime('%Y-%m-%d %H:%M')}: {event.summary}")
    print(f"Location: {event.location}")
    print(f"Attendees: {len(event.attendees)}")
    if event.meet_link:
        print(f"Meet: {event.meet_link}")
    print()
```

---

## Features

### Gmail Integration

**Capabilities**:

- ✅ Fetch emails by date range
- ✅ Parse email headers (from, to, cc, bcc, subject, date)
- ✅ Extract text and HTML body
- ✅ Extract attachment metadata
- ✅ Label information (inbox, sent, starred, etc.)
- ✅ Read/unread status
- ✅ Thread grouping
- ✅ Multiple account support

**Rate limits**:

- 5 requests/second (configurable)
- Gmail API allows 250 req/user/second
- Automatic rate limiting built-in

**Data stored**:

- Message ID (unique identifier)
- Thread ID (for conversation grouping)
- All participants (from, to, cc, bcc)
- Date and time
- Full text body
- HTML body
- All headers
- Attachments (metadata, not files)
- Labels and flags

### Calendar Integration

**Capabilities**:

- ✅ Fetch events by date range
- ✅ List all calendars
- ✅ Parse event details (title, description, location)
- ✅ Extract attendees and response status
- ✅ Conference links (Google Meet, Hangouts)
- ✅ Recurring event handling
- ✅ All-day event support
- ✅ Multiple account support

**Rate limits**:

- 5 requests/second (configurable)
- Calendar API allows 500 req/user/second
- Automatic rate limiting built-in

**Data stored**:

- Event ID (unique identifier)
- Calendar ID
- Summary (title)
- Description
- Location
- Start/end times
- All-day flag
- All attendees with response status
- Organizer
- Conference links (Meet, Hangouts)
- Recurrence rules
- Created/updated timestamps

---

## Permissions Requested

### Gmail Scopes

```
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.modify
```

**What this allows**:

- Read all email messages
- Read email metadata (headers, labels)
- Modify labels (mark as read/unread) - future feature
- **Does NOT allow**:
  - Sending emails
  - Deleting emails
  - Composing drafts

### Calendar Scopes

```
https://www.googleapis.com/auth/calendar.readonly
https://www.googleapis.com/auth/calendar.events.readonly
```

**What this allows**:

- Read all calendar events
- Read event metadata
- List calendars
- **Does NOT allow**:
  - Creating events
  - Modifying events
  - Deleting events

---

## Troubleshooting

### Issue: "Credentials file not found"

**Solution**:

```bash
# Check if file exists
ls ~/openclaw/credentials.json

# If not, download from Google Cloud Console
# Place at: ~/openclaw/credentials.json
```

### Issue: "No valid credentials for <email>"

**Solution**:

```bash
# Re-authorize the account
python memex/scripts/setup_gmail_calendar.py \
    --authorize-gmail arvind@copperdigital.com
```

### Issue: "Token has been expired or revoked"

**Solution**:

```bash
# Delete old token
rm ~/.tokens/gmail_arvind@copperdigital.com.json

# Re-authorize
python memex/scripts/setup_gmail_calendar.py \
    --authorize-gmail arvind@copperdigital.com
```

### Issue: "API not enabled"

**Solution**:

1. Go to https://console.cloud.google.com
2. Select your project
3. Go to "APIs & Services" → "Library"
4. Search for "Gmail API" → Enable
5. Search for "Google Calendar API" → Enable

### Issue: "Rate limit exceeded"

**Solution**:

```python
# Slow down requests in config
config = GmailConfig(requests_per_second=1.0)
```

### Issue: "Wrong account authorized"

**Solution**:
When the browser opens for authorization:

1. Look for "Choose an account" screen
2. Sign out if wrong account is selected
3. Sign in with correct account
4. Complete authorization

---

## Performance

### Expected Performance

| Operation         | Items | Time       |
| ----------------- | ----- | ---------- |
| Authorize account | 1     | ~30s       |
| Fetch 100 emails  | 100   | ~20s       |
| Fetch 1000 emails | 1000  | ~3 minutes |
| Fetch 100 events  | 100   | ~5s        |
| Fetch 1000 events | 1000  | ~20s       |

### Optimization Tips

1. **Use date ranges**: Don't fetch all 21 years at once!

   ```bash
   # Start with last 30 days
   python sync_gmail_calendar.py --start-date 2026-01-05

   # Then expand gradually
   python sync_gmail_calendar.py --start-date 2025-12-01
   ```

2. **Incremental syncs**: Use manifest to track what's synced

   ```python
   # Check manifest to see last sync date
   # Only fetch new items
   ```

3. **Parallel accounts**: Sync accounts in parallel

   ```bash
   # Terminal 1
   python sync_gmail_calendar.py --email arvind@copperdigital.com &

   # Terminal 2
   python sync_gmail_calendar.py --email arvind.sarin@gmail.com &
   ```

---

## Security

### Token Storage

Tokens are stored locally:

- Location: `~/openclaw/.tokens/`
- Format: JSON files
- Permissions: 600 (owner read/write only)
- **Never commit to git!**

### Credential Protection

```bash
# Make sure these are gitignored
cat ~/Cursor/Claude-2026/openclaw/.gitignore

# Should include:
credentials.json
.tokens/
*.token
```

### Token Refresh

Tokens expire after 1 hour but are automatically refreshed.

To manually revoke access:

1. Go to https://myaccount.google.com/permissions
2. Find "Memex Integrations"
3. Click "Remove Access"

---

## Next Steps

After setup:

1. **Sync historical data**:

   ```bash
   # Sync last 90 days
   python memex/scripts/sync_gmail_calendar.py \
       --start-date 2025-11-05 \
       --end-date 2026-02-04
   ```

2. **Set up automated syncs** (cron):

   ```bash
   # Add to crontab (sync daily at 6 AM)
   crontab -e

   # Add line:
   0 6 * * * cd ~/Cursor/Claude-2026/openclaw && python memex/scripts/sync_gmail_calendar.py >> ~/openclaw/logs/sync.log 2>&1
   ```

3. **Integrate with Memex pipeline**:
   - Ingest emails/events into database
   - Generate embeddings
   - Include in daily journals

4. **Build timeline**:
   - Merge emails, events, and Plaud transcripts
   - Sort by date
   - Generate comprehensive daily summaries

---

## API Documentation

See Python docstrings for complete API:

```python
# Gmail
help(GmailService)
help(GmailService.fetch_emails)
help(GmailService.batch_export)

# Calendar
help(CalendarService)
help(CalendarService.fetch_events)
help(CalendarService.batch_export)
```

---

## Support

**Issues?**

1. Check logs: `~/openclaw/logs/`
2. Run with debug logging:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```
3. Test individual components:
   ```bash
   python memex/scripts/setup_gmail_calendar.py --test-gmail <email>
   ```

---

**Status**: ✅ Ready to use
**Last Updated**: 2026-02-04
**Version**: 1.0.0

```

```

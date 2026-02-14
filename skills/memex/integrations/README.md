# Memex Gmail & Calendar Integrations

OAuth2-based integrations for fetching emails and calendar events from Google accounts.

## Quick Start

### 1. Prerequisites

- Google Cloud OAuth2 credentials (`credentials.json`)
- Python 3.11+

### 2. Install

```bash
pip install -r requirements.txt
```

### 3. Authorize Accounts

```bash
python ../scripts/setup_gmail_calendar.py --authorize-all
```

### 4. Sync Data

```bash
python ../scripts/sync_gmail_calendar.py
```

## Accounts Configured

- **Work**: `arvind@copperdigital.com`
- **Personal**: `arvind.sarin@gmail.com` (21+ years of history)

## Features

### Gmail

- ✅ Fetch emails by date range
- ✅ Parse headers, body, attachments
- ✅ Label and read status
- ✅ Thread grouping
- ✅ Multiple accounts

### Calendar

- ✅ Fetch events by date range
- ✅ Parse details, location, attendees
- ✅ Google Meet links
- ✅ Recurring events
- ✅ Multiple accounts

## Documentation

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for complete setup instructions.

## Files

```
integrations/
├── __init__.py              # Module exports
├── models.py                # Data models (EmailData, CalendarEvent)
├── gmail_service.py         # Gmail integration (420 lines)
├── calendar_service.py      # Calendar integration (380 lines)
├── requirements.txt         # Dependencies
├── SETUP_GUIDE.md           # Complete setup guide
└── README.md                # This file

../scripts/
├── setup_gmail_calendar.py  # Authorization and testing
└── sync_gmail_calendar.py   # Data sync script
```

## Usage

### Python API

```python
from memex.integrations import GmailService, CalendarService
from datetime import datetime, timedelta

# Gmail
gmail = GmailService(account_email="arvind@copperdigital.com")
gmail.connect()
emails = gmail.fetch_emails(
    start_date=datetime.now() - timedelta(days=7),
    max_emails=100
)

# Calendar
calendar = CalendarService(account_email="arvind@copperdigital.com")
calendar.connect()
events = calendar.fetch_events(
    start_date=datetime.now() - timedelta(days=7),
    max_events=50
)
```

### CLI

```bash
# Test connections
python ../scripts/setup_gmail_calendar.py --test-all

# Sync last 30 days
python ../scripts/sync_gmail_calendar.py

# Sync custom date range
python ../scripts/sync_gmail_calendar.py \
    --start-date 2026-01-01 \
    --end-date 2026-02-04

# Sync specific account
python ../scripts/sync_gmail_calendar.py \
    --email arvind@copperdigital.com
```

## Data Output

```
~/Cursor/Claude-2026/openclaw/skills/memex/data/integrations/
├── gmail/
│   ├── arvind@copperdigital.com/
│   │   ├── manifest.json
│   │   └── 2026-02-04/
│   │       ├── email_msg123.json
│   │       └── ...
│   └── arvind.sarin@gmail.com/
│       └── ...
└── calendar/
    ├── arvind@copperdigital.com/
    │   ├── manifest.json
    │   └── 2026-02-04/
    │       ├── event_evt123.json
    │       └── ...
    └── arvind.sarin@gmail.com/
        └── ...
```

## Rate Limits

- **Gmail**: 5 req/s (API allows 250/user/s)
- **Calendar**: 5 req/s (API allows 500/user/s)
- Automatic rate limiting included

## Security

- Tokens stored in `~/openclaw/.tokens/`
- Read-only access
- OAuth2 refresh handling
- No credentials in code

## Troubleshooting

See [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting) for common issues.

## Performance

| Operation         | Items | Time   |
| ----------------- | ----- | ------ |
| Fetch 100 emails  | 100   | ~20s   |
| Fetch 1000 emails | 1000  | ~3 min |
| Fetch 100 events  | 100   | ~5s    |
| Fetch 1000 events | 1000  | ~20s   |

---

**Status**: ✅ Production ready
**Version**: 1.0.0
**Last Updated**: 2026-02-04

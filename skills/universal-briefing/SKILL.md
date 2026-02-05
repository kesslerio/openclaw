---
name: universal-briefing
description: |
  Unified cross-platform daily intelligence briefing and response assistant. Aggregates messages
  from Email (Gmail), WhatsApp, iMessage, Telegram, Slack, and Discord into a single actionable
  briefing with classification (Urgent/FYI/Noise), commitment detection, calendar integration,
  and AI-generated draft replies.

  Use this skill when the user wants to:
  - Get a daily briefing of all important messages across platforms
  - Find messages that need responses/action
  - Summarize high-volume group chats and channels
  - Track commitments and promises from messages
  - Auto-create calendar events for deadlines mentioned in messages
  - Generate draft replies matching platform norms
  - Never miss important messages buried in noise

  Triggers: "daily briefing", "message summary", "what needs my attention", "urgent messages",
  "catch up on messages", "/brief", "cross-platform summary", "message digest", "inbox zero",
  "what did I miss", "summarize my chats"
---

# Universal Briefing

Cross-platform message intelligence that transforms chaos into clarity.

## Quick Start

```bash
# Generate 24-hour briefing
python -m scripts.cli brief

# Generate 6-hour briefing
python -m scripts.cli brief --hours 6

# Save to file
python -m scripts.cli brief --output briefing.md

# View pending follow-ups
python -m scripts.cli followups

# Mark follow-up complete
python -m scripts.cli complete 42
```

## Supported Platforms

| Platform      | Method  | Real-time | Historical |
| ------------- | ------- | --------- | ---------- |
| Email (Gmail) | API     | ✅        | ✅         |
| iMessage      | chat.db | ✅        | ✅         |
| WhatsApp      | Webhook | ✅        | ❌         |
| Telegram      | Bot API | ✅        | ❌         |
| Slack         | Web API | ✅        | ✅         |
| Discord       | Bot API | ✅        | ❌         |

## Classification Rules

### 🚨 Urgent (Needs Reply)

- Direct questions addressed to user
- Action/decision/approval requests
- Deadlines and blocking dependencies
- Explicit @mentions

### ℹ️ FYI (Informational)

- News, announcements, updates
- Status reports
- No explicit response required

### 🔇 Noise (Filtered)

- Reactions, acknowledgments
- System messages
- Bot messages
- Own messages

## Configuration

Set environment variables:

```bash
# Required
export ANTHROPIC_API_KEY="sk-..."

# User identity (for filtering own messages)
export USER_EMAILS="me@example.com,work@company.com"
export USER_PHONE_NUMBERS="+1234567890"
export USER_NAMES="John,John Doe"

# Platform-specific (configure those you use)
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_USER_ID="U12345"

export TELEGRAM_BOT_TOKEN="123:ABC..."
export TELEGRAM_USER_ID="12345678"

export DISCORD_BOT_TOKEN="..."
export DISCORD_USER_ID="12345678"

export WHATSAPP_ACCESS_TOKEN="..."
export WHATSAPP_PHONE_NUMBER_ID="..."
```

## Platform Setup

### Gmail

1. Create OAuth credentials at https://console.cloud.google.com
2. Download JSON and save to `~/.universal-briefing/gmail_credentials.json`
3. Run briefing - it will open browser for first-time auth
4. Token saved to `~/.universal-briefing/gmail_token.pickle`

### iMessage (macOS only)

1. Grant Full Disk Access to Terminal in System Settings
2. No additional setup required - reads from `~/Library/Messages/chat.db`

### Slack

1. Create Slack App at https://api.slack.com/apps
2. Add OAuth scopes: `channels:history`, `channels:read`, `users:read`, `im:history`
3. Install to workspace
4. Set `SLACK_BOT_TOKEN` and `SLACK_USER_ID` environment variables

### Telegram

1. Create bot via @BotFather on Telegram
2. Get bot token
3. Get your user ID from @userinfobot
4. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_USER_ID`

### Discord

1. Create bot at https://discord.com/developers/applications
2. Enable MESSAGE CONTENT intent
3. Invite bot to servers
4. Set `DISCORD_BOT_TOKEN` and `DISCORD_USER_ID`

### WhatsApp

1. Requires WhatsApp Business API access
2. Set up webhook endpoint
3. Set `WHATSAPP_ACCESS_TOKEN` and `WHATSAPP_PHONE_NUMBER_ID`

## Output Format

```markdown
# 🧠 Universal Briefing

## 🚨 Urgent — Action Required

- **[Sender | Platform | Context]**
  - Summary
  - ⏰ Deadline (if detected)
  - 🔧 Suggested Reply:
    > Draft response

## ℹ️ FYI — For Awareness

- **[Topic / Channel]**
  - Summary
  - Key takeaways

## 🔇 Noise

- High-level summary only

## 📅 Commitments Detected

- Who committed to what, by when
```

## Features

### 🎯 Smart Classification

Uses Claude to classify messages into Urgent, FYI, or Noise based on:

- Direct questions
- Action requests
- Mentions
- Message type (DM vs group)
- Content urgency signals

### 📅 Commitment Detection

Automatically extracts:

- Promises ("I'll send this tomorrow")
- Deadlines ("by EOD Friday")
- Action items ("Let me review and get back")
- Who committed (sender or recipient)

### 🗓️ Calendar Integration

- Auto-creates Google Calendar events for deadlines
- 15-minute reminders
- Conflict detection
- Links back to original message

### 💬 Draft Replies

Generates platform-appropriate responses:

- Email: Professional, formal
- Slack: Professional-casual
- WhatsApp/iMessage: Very casual
- Matches sender's tone

### 🔍 Semantic Grouping

Groups related messages by topic, not just sender:

- Collapses redundant updates
- Summarizes group discussions
- Highlights key points

## Advanced Usage

### Custom Time Windows

```bash
# Last 6 hours
python -m scripts.cli brief --hours 6

# Last 3 days
python -m scripts.cli brief --hours 72
```

### Follow-up Management

```bash
# View pending commitments
python -m scripts.cli followups

# Mark completed
python -m scripts.cli complete 5
```

### Automation with Cron

```bash
# Add to crontab for daily 9am briefing
0 9 * * * cd /path/to/universal-briefing && python -m scripts.cli brief --output ~/briefing.md
```

## Dependencies

```
pip install -r requirements.txt
```

Required packages:

- `anthropic` - Claude AI classification
- `google-auth`, `google-api-python-client` - Gmail/Calendar
- `python-telegram-bot` - Telegram
- `discord.py` - Discord
- `slack-sdk` - Slack
- `dateparser` - Natural date parsing
- `pytz` - Timezone support

## Troubleshooting

### No messages found

- Check platform credentials are set
- Verify time window (increase `--hours`)
- Check user identifiers match your accounts

### Classification errors

- Ensure `ANTHROPIC_API_KEY` is set
- Check API quota/billing

### Calendar events not created

- Verify Google Calendar credentials
- Check `~/.universal-briefing/gcal_credentials.json`

### iMessage errors (macOS)

- Grant Full Disk Access to Terminal
- System Settings → Privacy & Security → Full Disk Access

## Privacy & Security

- All processing happens locally
- Only Claude API calls leave your machine
- Credentials stored in `~/.universal-briefing/`
- No data sent to third parties
- SQLite database for tracking only

## Roadmap

- [ ] Sentiment analysis
- [ ] Priority scoring
- [ ] Auto-reply mode
- [ ] Email/Slack digest delivery
- [ ] Multi-language support
- [ ] Custom classification rules
- [ ] Webhook integrations

---

**Built for OpenClaw** - The universal AI messaging gateway

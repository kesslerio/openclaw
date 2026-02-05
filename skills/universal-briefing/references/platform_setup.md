# Platform Setup Guide

Complete setup instructions for each supported platform.

## Gmail

### 1. Enable Gmail API

1. Go to https://console.cloud.google.com/
2. Create new project or select existing
3. Enable Gmail API and Google Calendar API
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Application type: "Desktop app"
6. Download JSON file

### 2. Configure Credentials

```bash
mkdir -p ~/.universal-briefing
mv ~/Downloads/client_secret_*.json ~/.universal-briefing/gmail_credentials.json
```

### 3. First Run

```bash
python -m scripts.cli brief --hours 1
# Opens browser for OAuth authorization
# Grants read-only Gmail access
# Token saved to ~/.universal-briefing/gmail_token.pickle
```

## Google Calendar

Uses same OAuth credentials as Gmail. Enable Google Calendar API in console.

## iMessage (macOS only)

### Requirements

- macOS Catalina or later
- Messages app configured with iCloud

### Grant Access

1. System Settings → Privacy & Security → Full Disk Access
2. Add Terminal (or your terminal emulator)
3. Restart terminal

### Verify

```bash
sqlite3 ~/Library/Messages/chat.db "SELECT COUNT(*) FROM message;"
# Should return message count
```

## Slack

### 1. Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "Universal Briefing"
4. Select workspace

### 2. Add OAuth Scopes

Navigate to "OAuth & Permissions":

- `channels:history` - Read messages from public channels
- `channels:read` - View basic channel info
- `groups:history` - Read private channels (optional)
- `im:history` - Read direct messages
- `mpim:history` - Read group DMs
- `users:read` - View user info

### 3. Install to Workspace

1. Click "Install to Workspace"
2. Authorize permissions
3. Copy "Bot User OAuth Token"

### 4. Get Your User ID

1. In Slack, click your profile
2. Click "..." → "Copy member ID"

### 5. Set Environment Variables

```bash
export SLACK_BOT_TOKEN="xoxb-your-token-here"
export SLACK_USER_ID="U01234567"
```

## Telegram

### 1. Create Bot

1. Open Telegram
2. Message @BotFather
3. Send `/newbot`
4. Follow prompts to create bot
5. Copy bot token

### 2. Get Your User ID

1. Message @userinfobot
2. Copy your user ID

### 3. Start Bot

1. Find your bot in Telegram
2. Send `/start` message

### 4. Set Environment Variables

```bash
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_USER_ID="987654321"
```

## Discord

### 1. Create Application

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Name: "Universal Briefing"

### 2. Create Bot

1. Navigate to "Bot" tab
2. Click "Add Bot"
3. Enable "MESSAGE CONTENT INTENT" (required!)
4. Copy bot token

### 3. Get Your User ID

1. Enable Developer Mode in Discord (User Settings → Advanced)
2. Right-click your username
3. "Copy User ID"

### 4. Invite Bot to Server

1. Go to "OAuth2" → "URL Generator"
2. Select scopes: `bot`
3. Select permissions:
   - Read Messages/View Channels
   - Read Message History
4. Copy generated URL
5. Open URL, select server, authorize

### 5. Set Environment Variables

```bash
export DISCORD_BOT_TOKEN="your-bot-token"
export DISCORD_USER_ID="123456789012345678"
```

## WhatsApp Business

### Requirements

- WhatsApp Business Account
- Facebook Developer Account
- Verified business

### 1. Set Up WhatsApp Business API

1. Go to https://developers.facebook.com/
2. Create app → Business → WhatsApp
3. Add WhatsApp product
4. Get phone number ID
5. Generate access token

### 2. Configure Webhook (Required for Real-time)

Universal Briefing stores messages in memory via webhook.

```bash
# Example webhook endpoint
POST https://your-server.com/whatsapp/webhook

# Verify token in WhatsApp settings
```

### 3. Set Environment Variables

```bash
export WHATSAPP_ACCESS_TOKEN="your-access-token"
export WHATSAPP_PHONE_NUMBER_ID="your-phone-number-id"
```

### Note

WhatsApp API doesn't support historical message retrieval. Messages are collected via webhook as they arrive.

## User Identity Configuration

To filter out your own messages, set these across all platforms:

```bash
# All email addresses you use
export USER_EMAILS="personal@gmail.com,work@company.com"

# All phone numbers (E.164 format)
export USER_PHONE_NUMBERS="+12025551234,+14155559876"

# All display names you use
export USER_NAMES="John Doe,John,JD"
```

## Verification

Test each platform:

```bash
# Test all platforms
python -c "
from scripts.main import UniversalBriefing
ub = UniversalBriefing()
for platform, connector in ub.connectors.items():
    print(f'{platform.value}: {'✅' if connector.is_available() else '❌'}')
"
```

Expected output:

```
email: ✅
imessage: ✅
whatsapp: ❌  # Unless webhook configured
telegram: ✅
slack: ✅
discord: ✅
```

## Security Best Practices

### Credentials Storage

- Never commit credentials to git
- Use `.env` files or system keychain
- Rotate tokens regularly

### OAuth Tokens

- Gmail/Calendar tokens stored in `~/.universal-briefing/`
- Protect with file permissions: `chmod 600 ~/.universal-briefing/*.pickle`

### Bot Tokens

- Use environment variables
- Never hardcode in scripts
- Revoke immediately if leaked

## Troubleshooting

### Gmail "insufficient permissions"

- Re-run OAuth flow
- Check enabled scopes in console
- Delete `gmail_token.pickle` and re-authorize

### Slack "not_in_channel"

- Invite bot to channels: `/invite @UniversalBriefing`
- Or grant bot access to all public channels

### Telegram "Unauthorized"

- Verify bot token is correct
- Make sure you've sent `/start` to bot

### Discord "Missing Access"

- Check MESSAGE CONTENT intent is enabled
- Re-invite bot with updated permissions

### iMessage "permission denied"

- Grant Full Disk Access to Terminal
- Restart terminal after granting access

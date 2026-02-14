---
name: gohighlevel
description: GoHighLevel CRM integration for managing contacts, opportunities, and campaigns. Use for sales pipeline management, contact lookups, and automated follow-ups.
version: 1.0.0
trigger: ghl
author: Nike (Arvind's AI)
tags: crm, sales, contacts, pipeline, gohighlevel
metadata:
  openclaw:
    emoji: "📊"
    requires:
      bins: ["node"]
    primaryEnv: GHL_API_KEY
---

# GoHighLevel CRM Integration

Manage your GoHighLevel CRM directly from OpenClaw. Track contacts, opportunities, and sales pipeline.

## Setup

Set your GHL API credentials in `~/.env` or environment:

```bash
GHL_API_KEY=your-api-key
GHL_LOCATION_ID=your-location-id
```

Get your API key from GoHighLevel Settings → API Keys.

## Commands

### List Contacts

```bash
node ~/Cursor/Claude-2026/openclaw/skills/gohighlevel/scripts/ghl.js contacts list
node ~/Cursor/Claude-2026/openclaw/skills/gohighlevel/scripts/ghl.js contacts search "John Doe"
```

### Get Contact Details

```bash
node ~/Cursor/Claude-2026/openclaw/skills/gohighlevel/scripts/ghl.js contacts get <contact_id>
```

### List Opportunities (Pipeline)

```bash
node ~/Cursor/Claude-2026/openclaw/skills/gohighlevel/scripts/ghl.js opportunities list
node ~/Cursor/Claude-2026/openclaw/skills/gohighlevel/scripts/ghl.js opportunities list --pipeline "Sales Pipeline"
```

### Create Contact

```bash
node ~/Cursor/Claude-2026/openclaw/skills/gohighlevel/scripts/ghl.js contacts create --name "Jane Doe" --email "jane@example.com" --phone "+15551234567"
```

## Use Cases

- **Before a call**: Look up contact history and notes
- **After a call**: Update opportunity stage, add notes
- **Pipeline review**: List all opportunities by stage
- **Lead capture**: Create new contacts from conversations

# AI Email Analyzer - Design Doc

## Purpose

Analyze email summaries to extract actionable insights, create todos, and identify urgent items.

## Input

- Email summary file: `memory/email-summary-YYYY-MM-DD.md`
- Contains: From, Subject, Date for unread emails

## Output

1. **Urgent emails** - Require immediate attention
2. **Action items** - Todos to add to kanban
3. **Spam/Low-priority** - Can be archived
4. **Summary** - Human-readable digest for morning brief

## Analysis Criteria

### Urgency Detection

**High Priority Indicators:**

- Keywords: URGENT, ASAP, IMMEDIATE, CRITICAL, DEADLINE, TODAY
- Sender patterns: clients, executives, known contacts
- Subject patterns: "Re: Re: Re:" (long threads), "Action Required"
- Time sensitivity: mentions of dates/times

**Low Priority Indicators:**

- Marketing emails
- Newsletters
- Automated notifications
- Unsubscribe links present

### Todo Extraction

**Patterns that indicate action items:**

- "Can you..."
- "Please..."
- "Need you to..."
- "By [date]..."
- "Action required"
- Questions requiring response
- Calendar invites
- Document review requests

### Smart Categorization

```
Categories:
1. Client Communication - High priority
2. Internal Team - Medium priority
3. Vendor/Partner - Medium priority
4. Marketing/Newsletter - Low priority
5. System Notifications - Low priority
6. Spam - Archive
```

## Workflow

```
1. Read email summary file
   ↓
2. For each email:
   - Extract: sender, subject, date
   - Analyze urgency
   - Extract action items
   - Categorize
   ↓
3. Generate outputs:
   - Urgent alerts (if any)
   - Kanban tasks (action items)
   - Archive list (low priority)
   - Daily digest
   ↓
4. Actions:
   - Send urgent alerts to Telegram/WhatsApp
   - Add todos to kanban
   - Mark low-priority as read (optional)
   - Include digest in morning brief
```

## Implementation Strategy

Since I can't call external APIs directly from a script, I'll:

1. Create a structured prompt
2. Process it during heartbeat
3. Use my AI capabilities to analyze
4. Update kanban programmatically
5. Send alerts via message tool

## Example Analysis

**Input:**

```
From: john@client.com
Subject: URGENT: Production issue - site down
Date: Feb 1, 08:30 AM
```

**Output:**

```json
{
  "urgency": "HIGH",
  "category": "Client Communication",
  "action_items": [
    "Investigate production issue for client site",
    "Respond to john@client.com about status"
  ],
  "alert": true,
  "alert_message": "🚨 URGENT: Client production issue - site down (john@client.com)",
  "estimated_effort": "1-2 hours",
  "deadline": "Immediate"
}
```

## Integration Points

1. **Heartbeat** - Run analysis every 4 hours
2. **Kanban** - Auto-add action items as tasks
3. **Morning Brief** - Include email digest
4. **Alerts** - Telegram/WhatsApp for urgent items
5. **Memory** - Save analysis results for context

## Future Enhancements

1. **Learn from feedback** - Track which emails Arvind acts on
2. **Sender reputation** - Build trust scores for senders
3. **Auto-responses** - Draft replies for common patterns
4. **Thread tracking** - Follow conversation context
5. **Calendar integration** - Add deadlines from emails to calendar

---

**Status:** Design complete, ready to implement in heartbeat workflow

# Classification Rules

Detailed logic for message classification into Urgent, FYI, or Noise.

## Overview

Universal Briefing uses a two-tier classification system:

1. **Quick heuristics** - Fast pattern matching for obvious cases
2. **LLM classification** - Claude Sonnet for ambiguous messages

## Classification Categories

### 🚨 Urgent (Action Required)

Messages that need your response or action.

**High-confidence signals:**

- Direct questions with `?` and explicit mention
- Keywords: "asap", "urgent", "deadline"
- Phrases: "need your", "can you", "please respond", "waiting for"
- Direct messages containing questions
- @mentions requesting action

**Examples:**

```
✅ "@john can you review this PR by EOD?"
✅ "Urgent: production is down"
✅ "Need your approval to proceed"
✅ "When can you send that report?"
✅ "Waiting for your feedback"
```

**Confidence thresholds:**

- 0.85+ with strong signals
- 0.8+ for DM questions
- 0.6-0.8 marked as Ambiguous for review

### ℹ️ FYI (Informational)

Messages for awareness with no expected response.

**Characteristics:**

- Status updates
- News and announcements
- Shared links/resources
- Meeting notes
- Progress reports
- No direct question or request

**Examples:**

```
✅ "Deployed v2.1 to production"
✅ "New blog post: [link]"
✅ "Reminder: team meeting tomorrow at 10am"
✅ "FYI - updated the docs"
✅ "Here's the recording from today's call"
```

### 🔇 Noise (Low Signal)

Low-value messages that clutter feeds.

**Quick filters (0.95 confidence):**

- Very short (< 5 chars)
- Pure reactions: "ok", "thanks", "👍", "lol"
- Acknowledgments: "got it", "sounds good"

**Additional patterns:**

- Social chatter
- Memes and jokes
- Off-topic discussions
- Emoji-only messages
- Duplicate/redundant messages

**Examples:**

```
✅ "k"
✅ "👍"
✅ "haha nice"
✅ "thanks!"
✅ "lol"
```

### ⚠️ Ambiguous (Review Recommended)

Messages with low classification confidence (< 0.6).

**Reasons for ambiguity:**

- Mixed signals (urgent tone but no clear ask)
- Context-dependent meaning
- Unclear intent
- LLM parse errors

**Handling:**

- Grouped with Urgent for visibility
- Flagged for manual review
- User can reclassify

## Quick Heuristics

Bypasses LLM for performance and cost optimization.

### Noise Detection

```python
if len(content) < 5:
    → Noise (0.95 confidence)

if content.lower() in ['ok', 'okay', 'k', 'thanks', ...]:
    → Noise (0.95 confidence)
```

### Urgent Detection

```python
if '?' in content and is_mention:
    → Urgent (0.85 confidence, "Question with mention")

if 'asap' in content:
    → Urgent (0.85 confidence, "ASAP mentioned")

if is_direct_message and '?' in content:
    → Urgent (0.8 confidence, "Direct question in DM")
```

### Fallback

If no quick rule matches, send to Claude.

## LLM Classification

### Prompt Structure

```
Message context:
- Platform: slack
- Sender: alice
- Channel: #engineering
- Content: "..."
- Has mention: true/false
- Is DM: true/false

Categories:
🚨 URGENT - [criteria]
ℹ️ FYI - [criteria]
🔇 NOISE - [criteria]

Output JSON:
{
  "classification": "urgent",
  "confidence": 0.85,
  "reason": "Direct question with deadline"
}
```

### Confidence Scoring

| Range    | Meaning   | Action               |
| -------- | --------- | -------------------- |
| 0.9-1.0  | Very high | Trust classification |
| 0.7-0.89 | High      | Trust classification |
| 0.6-0.69 | Medium    | Accept but monitor   |
| 0.0-0.59 | Low       | Mark as Ambiguous    |

### Edge Cases

**Group mentions without context:**

```
"@channel FYI" → FYI (not urgent despite mention)
```

**Rhetorical questions:**

```
"Can you believe this?" → FYI or Noise (not a real ask)
```

**Delayed responses:**

```
"Thanks for the help last week" → Noise (acknowledgment of past)
```

**Forward-looking statements:**

```
"Let me know if you need anything" → FYI (offer, not request)
```

## Platform-Specific Adjustments

### Email

- Professional tone expected
- Longer messages are normal
- Subject line considered in classification

### Slack/Discord

- Casual tone acceptable
- Channel messages less urgent than DMs
- Threads treated as context units

### WhatsApp/iMessage

- Very casual
- Short messages are normal
- Emoji use is common, not noise

### Telegram

- Mix of personal and groups
- Bot commands filtered as noise
- Channels are informational

## Filter Combinations

Messages pass through filters before classification:

1. **Own message filter** - Excludes messages sent by user
2. **System message filter** - Removes platform notifications
3. **Bot filter** - Excludes automated messages
4. **Duplicate filter** - Removes repeated content

Only after filtering is classification applied.

## Customization

Future enhancement: User-defined rules

```yaml
custom_rules:
  urgent:
    - keyword: "production"
      confidence: 0.9
    - sender: "boss@company.com"
      boost: +0.1

  noise:
    - channel: "#random"
      confidence: 0.8
    - pattern: "^[A-Z]{3,}$" # All caps
```

## Performance Optimization

### LLM Usage

- Only 20-40% of messages require LLM
- Quick heuristics handle majority
- Batch processing reduces API calls

### Caching

- Classification confidence logged for analysis
- Patterns learned from corrections
- Future: ML model trained on user feedback

## Testing

Verify classification accuracy:

```bash
# Run on sample dataset
python -m tests.test_classifier --dataset samples/messages.json

# Expected accuracy:
# Urgent: 85%+
# FYI: 80%+
# Noise: 95%+
```

# Reply Templates

Platform-specific reply patterns and examples.

## Overview

Universal Briefing generates draft replies that match:

- Platform communication norms
- Sender's tone
- Message urgency
- Cultural context

## Platform Norms

### Email (Professional)

**Style:** Formal, complete sentences, proper greeting/closing

**Structure:**

```
Hi [Name],

[Acknowledgment]
[Response to question/request]
[Next steps if applicable]

Best regards,
[User]
```

**Examples:**

Request for review:

```
From: alice@company.com
"Can you review the Q4 budget by Friday?"

Draft Reply:
Hi Alice,

Thanks for sending this over. I'll review the Q4 budget and have feedback to you by Thursday EOD.

Best regards,
John
```

Question about timeline:

```
From: bob@client.com
"When can we expect the prototype?"

Draft Reply:
Hi Bob,

The prototype will be ready for review by next Wednesday, March 15th. I'll send you a calendar invite for a demo that afternoon.

Best regards,
John
```

### Slack (Professional-Casual)

**Style:** Friendly but clear, can use formatting and emoji

**Structure:**

```
[Acknowledgment]
[Bulleted action items if multiple]
[Timeline]
[Optional emoji for friendliness]
```

**Examples:**

Request for help:

```
From: @alice in #engineering
"Can someone help debug the CI pipeline? It's blocking deploys"

Draft Reply:
On it! I'll:
• Check the build logs
• Test locally
• Report back in #engineering

ETA: 30 min 👍
```

Question about feature:

```
From: @bob in #product
"Do we support SSO with Azure AD?"

Draft Reply:
Yes! Azure AD is supported via SAML.

Setup docs: [link to docs]
If you need help configuring, ping me!
```

### WhatsApp (Casual)

**Style:** Very brief, conversational, light emoji okay

**Structure:**

```
[Quick acknowledgment]
[Answer/commitment]
[Optional emoji]
```

**Examples:**

Request to send file:

```
From: Alice
"Can you send me that presentation?"

Draft Reply:
Sure! Sending it now 👍
```

Question about meeting:

```
From: Bob
"What time is the meeting tomorrow?"

Draft Reply:
10am. I'll send a reminder!
```

### iMessage (Very Casual)

**Style:** Extremely brief, emoji common, no formality

**Structure:**

```
[Answer] [emoji]
```

**Examples:**

Simple request:

```
From: Mom
"Can you pick up milk?"

Draft Reply:
On it! 🛒
```

Question:

```
From: Friend
"Wanna grab lunch?"

Draft Reply:
Sure, noon work?
```

### Telegram (Casual)

**Style:** Brief but complete, emoji acceptable

**Structure:**

```
[Answer]
[Details if needed]
[Optional emoji]
```

**Examples:**

Technical question:

```
From: @alice
"How do I export data from the API?"

Draft Reply:
Use the /export endpoint with your API key.

Docs: https://docs.example.com/export

Let me know if you hit any issues!
```

### Discord (Gaming-Casual)

**Style:** Very casual, gaming lingo okay, emoji common

**Structure:**

```
[Quick response]
[Details]
[Emoji]
```

**Examples:**

Request for help:

```
From: @gamer123
"anyone wanna help with this raid?"

Draft Reply:
I'm down! What time? 🎮
```

## Tone Matching

The reply generator analyzes sender's tone:

### Formal Sender

```
Sender: "Please advise on the best approach."
Reply: "I recommend [approach]. Happy to discuss further."
```

### Casual Sender

```
Sender: "thoughts on this?"
Reply: "Looks good! Maybe add [suggestion]"
```

### Urgent Sender

```
Sender: "URGENT: site is down!"
Reply: "On it - investigating now. Will update in 10 min."
```

## Action-Oriented Responses

Always be specific and actionable:

### Bad (Vague)

```
"I'll take a look"
"Let me check"
"I'll get back to you"
```

### Good (Specific)

```
"I'll review the doc and have feedback by EOD"
"Checking the logs now - will report back in 15 min"
"I'll send you the file this afternoon"
```

## Commitment Language

When making commitments, be explicit:

### Timeline Commitments

```
"by 3pm today"
"tomorrow morning"
"Friday EOD"
"next week"
```

### Action Commitments

```
"I'll review the PR"
"I'll send the report"
"I'll schedule the meeting"
"I'll investigate and get back to you"
```

### Conditional Commitments

```
"I can review this if I finish the other task by noon"
"Let me check my calendar and confirm"
"I'll try to get to this today, but may need until tomorrow"
```

## Declining/Deferring

When you can't commit:

### Polite Decline

```
Email: "Thanks for thinking of me, but I'm fully booked this week. Would next week work?"
Slack: "I'm swamped today, but could help tomorrow if that works?"
```

### Redirect

```
"@alice might be better suited for this - looping her in"
"This is outside my area - try asking in #engineering"
```

### Defer with Timeline

```
"I'm in meetings until 3pm - can I get back to you this afternoon?"
"Can this wait until Friday? I'm finishing a deadline"
```

## Edge Cases

### Multiple Questions

```
From: alice
"Can you review the doc? Also, when is the meeting? And did you see my email?"

Draft Reply:
Sure! I'll:
• Review the doc by EOD
• Meeting is tomorrow at 2pm
• Yes, saw your email - will respond this afternoon
```

### Vague Request

```
From: bob
"Thoughts?"

Draft Reply:
Can you clarify what you'd like feedback on? Happy to review once I know what you're looking for.
```

### Already Answered

```
Context: User already replied
Detection: Check message timestamps
Action: Skip reply generation
```

## Quality Checks

Generated replies are validated for:

1. **Length** - Appropriate for platform
2. **Tone** - Matches sender and context
3. **Actionability** - Specific next steps
4. **Completeness** - Addresses all questions
5. **Grammar** - Professional for formal platforms

## Customization

Future: User preferences

```yaml
reply_preferences:
  tone: professional # or casual
  sign_off: "Cheers" # custom closing
  max_length: 100 # word limit
  emoji_usage: moderate # none, light, moderate, heavy
```

## Examples by Scenario

### Approval Request

```
Q: "Can you approve the expense report?"
A: "Approved! You should see it processed by tomorrow."
```

### Technical Question

```
Q: "Why is the API returning 500 errors?"
A: "Looks like a DB connection issue. Investigating now - will update in #incidents."
```

### Meeting Request

```
Q: "Can we meet this week to discuss the project?"
A: "Sure! I'm free Thursday 2-3pm or Friday morning. Which works for you?"
```

### Feedback Request

```
Q: "What do you think of this design?"
A: "Looks great! One suggestion: increase the contrast on the CTA button for accessibility."
```

### Deadline Question

```
Q: "When can you finish the report?"
A: "I'll have the first draft to you by Friday. Final version early next week."
```

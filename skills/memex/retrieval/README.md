# 🔍 Memex Retrieval - Chat Query Engine

**Natural language interface to your memory**

---

## Overview

The Retrieval package provides a conversational query engine that lets you ask questions about your past conversations in natural language. It combines:

- **Intent detection** - Understands what you're really asking
- **Recency bias** - Recent memories rank higher (via Historian)
- **Source attribution** - Always shows where answers come from
- **Conversation context** - Remembers what you just asked
- **Confidence scoring** - Tells you how sure it is

---

## Quick Start

### Basic Usage

```python
from retrieval import QueryEngine

engine = QueryEngine()

# Ask a question
response = engine.query("What did I promise Mark about the demo?")

print(response.answer)
# You promised to send the demo by Friday (2026-01-28)

# Check sources
for source in response.sources:
    print(f"📅 {source.date}: {source.snippet}")
```

### Command Line

```bash
cd /home/ubuntu/clawd/memex/retrieval
python query_engine.py "What did I discuss this week?"
```

---

## Features

### 1. Intent Detection 🎯

Automatically classifies queries into types:

| Intent Type    | Example                      | Behavior               |
| -------------- | ---------------------------- | ---------------------- |
| **Factual**    | "What is the status of X?"   | Standard search        |
| **Temporal**   | "When did I last talk to Y?" | Date-focused           |
| **Commitment** | "What did I promise?"        | High confidence bar    |
| **Summary**    | "Summarize my week"          | Multi-source synthesis |

**Example:**

```python
engine._parse_intent("What did I promise Mark?")
# {
#   'type': 'commitment',
#   'temporal_focus': 'all',
#   'confidence_threshold': 0.8
# }
```

### 2. Conversation History 💬

Remembers recent questions for context:

```python
# First query
response1 = engine.query("What did I discuss with Mark?")

# Follow-up (resolves "him" to "Mark")
response2 = engine.query("What did I promise him?")
```

Keeps last 5 exchanges automatically.

### 3. Smart Source Ranking 📊

Different strategies based on query type:

**Commitments:**

- Boosts sources with promise keywords ("I'll", "commit", "promise")
- Requires high confidence

**Summaries:**

- Diversifies across dates
- Prefers representative samples over chronological

**Factual:**

- Standard recency-biased search
- Recent wins over old

### 4. Source Attribution 📚

Every answer cites its sources:

```python
response = engine.query("What's the roadmap?")

for source in response.sources:
    print(f"{source.date}: {source.snippet}")
    print(f"  Score: {source.score}")
    print(f"  File: {source.transcript_path}")
```

### 5. Confidence Scoring 📈

Tells you how reliable the answer is:

```python
response = engine.query("Did I ever mention X?")
print(f"Confidence: {response.confidence:.0%}")
print(f"Reasoning: {response.reasoning}")

# Output:
# Confidence: 85%
# Reasoning: Synthesized from 3 sources (avg score: 0.87)
```

---

## Query Types & Examples

### Factual Questions

```python
engine.query("What is the status of Copper AI?")
engine.query("Who is handling the Texas outreach?")
engine.query("What's our pricing strategy?")
```

### Temporal Questions

```python
engine.query("When did I last talk to Mark?")
engine.query("What happened yesterday?")
engine.query("What did I work on this week?")
```

### Commitment Tracking

```python
engine.query("What did I promise to deliver?")
engine.query("What did I commit to Mark?")
engine.query("What deadlines do I have?")
```

### Summaries

```python
engine.query("Summarize my property deals")
engine.query("Give me an overview of the partnership discussions")
engine.query("Tell me about my conversations with Mark")
```

---

## Architecture

```
QueryEngine
├── _parse_intent()       # Classify query type
├── _expand_with_history() # Add context from previous queries
├── search.search()        # Vector search (via Historian)
├── _rank_sources()        # Intent-specific ranking
└── _synthesize_answer()   # GPT-4 synthesis with sources
```

### Data Flow

```
User Query
    ↓
Intent Detection
    ↓
History Expansion (if applicable)
    ↓
Vector Search (Historian + Recency)
    ↓
Source Ranking (intent-specific)
    ↓
Answer Synthesis (GPT-4o-mini)
    ↓
Response + Sources + Confidence
```

---

## Configuration

### Environment Variables

```bash
# Required for GPT synthesis
export OPENAI_API_KEY="sk-..."

# Optional: Change model
export MEMEX_MODEL="gpt-4o"  # Default: gpt-4o-mini
```

### Initialization Options

```python
engine = QueryEngine(
    search=custom_search,      # Custom search instance
    api_key="sk-...",           # OpenAI key
    model="gpt-4o-mini"         # GPT model
)
```

---

## Advanced Usage

### Date Filtering

```python
response = engine.query(
    "What did I work on?",
    date_filter=("2026-01-01", "2026-01-31")
)
```

### Max Sources

```python
response = engine.query(
    "Summarize my work",
    max_sources=10  # Get more context
)
```

### Disable History

```python
response = engine.query(
    "What is X?",
    use_history=False  # Fresh query
)
```

### Clear History

```python
engine.clear_history()  # Start fresh conversation
```

### Get Recent Queries

```python
recent = engine.get_recent_queries(limit=5)
for q in recent:
    print(f"{q['timestamp']}: {q['query']}")
```

---

## Integration with Other Phases

### With HISTORIAN (Phase 2) ✅

```python
from historian import MemorySearch
from retrieval import QueryEngine

# Uses Historian's search + recency ranking
search = MemorySearch()
engine = QueryEngine(search=search)
```

### With JOURNALIST (Phase 3) ✅

```python
# Query mentions from journals
response = engine.query("What action items did I capture this week?")
# → Searches both transcripts AND generated journals
```

### With PARTNER (Phase 4 - Next!) 🚧

```python
# Chat interface will use QueryEngine
# React frontend → API → QueryEngine → Response
```

---

## Testing

### Run Tests

```bash
cd /home/ubuntu/clawd/memex
pytest tests/test_query_engine.py -v
```

### Test Coverage

**14 test classes covering:**

- ✅ Intent parsing (7 tests)
- ✅ History expansion (4 tests)
- ✅ Source ranking (3 tests)
- ✅ Answer synthesis (4 tests)
- ✅ Context building (1 test)
- ✅ System prompts (4 tests)
- ✅ History management (4 tests)
- ✅ Integration (1 test)

**Total: 28 comprehensive tests**

---

## Cost Analysis

### Per Query

Using `gpt-4o-mini`:

- Input: ~500 tokens (context) = $0.0008
- Output: ~200 tokens (answer) = $0.0012
- **Total: ~$0.002 per query**

### Monthly (30 queries/day)

- Queries: 900/month × $0.002 = **$1.80/month**
- With embeddings: + $0.09/month
- **Total: ~$2/month**

**Very affordable!**

### Upgrade to GPT-4o

For better answers:

- Input: ~500 tokens = $0.0025
- Output: ~200 tokens = $0.0060
- **Total: ~$0.009 per query**
- Monthly: **$8/month** (30 queries/day)

---

## Examples

### Example 1: Commitment Tracking

```python
response = engine.query("What did I promise Mark about the demo?")

print(response.answer)
# You promised to send the demo materials by Friday, January 31st.
# You also committed to scheduling a follow-up call for Feb 5th.

print(f"Confidence: {response.confidence:.0%}")
# Confidence: 92%

for source in response.sources:
    print(f"📅 {source.date}: {source.snippet}")
# 📅 2026-01-28: In the meeting with Mark, I said "I'll send..."
# 📅 2026-01-29: Confirmed with Mark that Friday is the deadline...
```

### Example 2: Weekly Summary

```python
response = engine.query(
    "Summarize my week",
    date_filter=("2026-01-27", "2026-02-02")
)

print(response.answer)
# This week focused on three main areas:
#
# **Copper AI Sales:**
# - Created EVV sales materials
# - Built caregiver no-show calculator
# - 199 Texas leads ready for outreach
#
# **Memex Development:**
# - Completed Phases 2 & 3
# - Built HISTORIAN and JOURNALIST
# - Started PARTNER (query engine)
#
# **Property Deals:**
# - Negotiating 2000 Canyons offer
# - Following up on Crane Street
#
# **Action Items:** 7 tasks completed, 12 in progress
```

### Example 3: Follow-up Questions

```python
# First query
r1 = engine.query("Who did I talk to this week?")
# "You had conversations with Mark, Darwin, Nathan, and the Colorado prospect..."

# Follow-up (uses history)
r2 = engine.query("What did I discuss with him?")
# Expands to "What did I discuss with Mark?" (most recent person mentioned)
```

---

## Fallback Behavior

### No OpenAI API Key

Falls back to simple synthesis:

```python
# Without GPT
engine = QueryEngine(api_key=None)
response = engine.query("What happened?")

# Returns simple concatenation
print(response.answer)
# "On 2026-01-28: Had meeting with Mark about..."
```

### No Matching Sources

```python
response = engine.query("What is the meaning of life?")

print(response.answer)
# "I don't have enough information to answer that confidently."

print(response.confidence)
# 0.0

print(response.reasoning)
# "No relevant sources found in memory."
```

---

## Best Practices

### 1. Clear Queries

❌ Bad:

```python
engine.query("thing")
```

✅ Good:

```python
engine.query("What is the status of the Copper AI partnership?")
```

### 2. Use Date Filters for Speed

```python
# Faster - searches only recent
engine.query(
    "What did I work on?",
    date_filter=("2026-01-27", "2026-02-02")
)

# Slower - searches all time
engine.query("What did I work on?")
```

### 3. Check Confidence

```python
response = engine.query("Did I ever mention quantum computing?")

if response.confidence < 0.5:
    print("⚠️ Low confidence - answer may not be reliable")
```

### 4. Clear History for New Topics

```python
# Discussing project A
engine.query("What's the status?")
engine.query("Who's working on it?")

# Switch to project B - clear history
engine.clear_history()
engine.query("What's the timeline?")
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'openai'"

```bash
pip install openai
```

### "No module named 'historian'"

Make sure you're in the memex directory:

```bash
cd /home/ubuntu/clawd/memex
python retrieval/query_engine.py "test query"
```

### Low Confidence Scores

Check:

1. Are there relevant transcripts in the vector DB?
2. Is recency bias too strong? (Adjust in RecencyRanker)
3. Is the query too vague?

### GPT Synthesis Errors

Falls back to simple synthesis automatically. Check:

```python
print(response.reasoning)
# "GPT synthesis failed: [error message]"
```

---

## Roadmap

### Current (Phase 4.1) ✅

- Intent detection
- History expansion
- Source ranking
- GPT synthesis
- Confidence scoring

### Next (Phase 4.2) 🚧

- React frontend
- WebSocket for streaming responses
- Rich text formatting
- Source highlighting

### Future 🔮

- Multi-language support
- Voice queries
- Graph-based reasoning
- Fine-tuned models

---

## Files

```
retrieval/
├── __init__.py           # Package exports
├── query_engine.py       # Main engine (430 lines)
├── README.md             # This file
└── (tests in ../tests/)

../tests/
└── test_query_engine.py  # 28 comprehensive tests
```

---

## Dependencies

From `historian`:

- `MemorySearch` - Vector search
- `RecencyRanker` - Time-based ranking

External:

- `openai` - GPT synthesis (optional)

---

## Performance

Typical query latency:

| Operation         | Time           |
| ----------------- | -------------- |
| Intent parsing    | < 1ms          |
| History expansion | < 1ms          |
| Vector search     | 50-200ms       |
| Source ranking    | 10-50ms        |
| GPT synthesis     | 500-2000ms     |
| **Total**         | **600-2300ms** |

**Optimization tips:**

1. Use date filters to reduce search scope
2. Limit max_sources to 3-5 for faster synthesis
3. Use gpt-4o-mini instead of gpt-4o
4. Cache common queries

---

## Contributing

To add new intent types:

1. Add detection in `_parse_intent()`:

```python
if 'new_pattern' in query_lower:
    intent['type'] = 'new_type'
```

2. Add ranking logic in `_rank_sources()`:

```python
elif intent['type'] == 'new_type':
    # Custom ranking logic
```

3. Add system prompt in `_get_system_prompt()`:

```python
elif intent['type'] == 'new_type':
    base += "\n6. Special instructions for new type"
```

4. Add tests in `test_query_engine.py`

---

## License

MIT (same as Memex)

---

## Credits

Built by Nike 🐾 for Arvind's Memex  
2026-02-02

**Inspired by:**

- Vannevar Bush's Memex
- Andy Matuschak's notes
- Notion AI
- Perplexity's citation system

---

🚀 **Now your memory can answer back!**

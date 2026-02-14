# Memex Trails

<!-- codex_nike -->

Associative trails are replayable paths across memories, inspired by Vannevar Bush’s Memex.

## Trail schema

```json
{
  "id": "trail_abc123",
  "name": "Launch plan threads",
  "created_at": "2026-02-04T19:44:00Z",
  "description": "Key updates + decisions",
  "tags": ["launch", "product"],
  "nodes": [
    {
      "source": "universal-briefing",
      "source_id": "whatsapp:abc",
      "title": "Darwin update",
      "uri": "memex://transcripts/...",
      "context": {
        "time_bucket": "2026-02-04",
        "people": ["Darwin"],
        "platform": "whatsapp",
        "channel": "Darwin",
        "thread": null,
        "tags": ["urgent"]
      }
    }
  ]
}
```

## CLI

Create a trail from a JSON file of nodes:

```bash
python scripts/create_trail.py \
  --name "Launch threads" \
  --nodes-file /path/to/nodes.json \
  --tags launch,product
```

List trails:

```bash
python scripts/create_trail.py --list
```

# Plaud.AI Scraper - Quick Start Guide

Get up and running with the Plaud.AI scraper in 5 minutes.

## Prerequisites

```bash
# Install Playwright
pip install playwright
playwright install chromium
```

## Step 1: Basic Test (2 minutes)

Try the simplest example to verify everything works:

```bash
cd /Users/arvindsarin/Cursor/Claude-2026/clawd/memex/scraper

# Run example 1 (basic usage)
python3 example_usage.py \
    --email your@email.com \
    --password yourpassword \
    --example 1
```

This will:

1. Login to Plaud.AI
2. Save your session to `plaud_session.json`
3. Fetch your last 7 days of transcripts
4. Download the first transcript
5. Display transcript info

## Step 2: Session Reuse (30 seconds)

Once you have a saved session, you don't need to login again:

```bash
# Run example 2 (session reuse)
python3 example_usage.py --example 2
```

This will fetch transcripts using your saved session (no login needed).

## Step 3: Batch Export (5-10 minutes)

Export all your transcripts from the last 30 days:

```bash
# Run example 3 (batch export)
python3 example_usage.py \
    --email your@email.com \
    --password yourpassword \
    --example 3
```

This will:

1. Export all transcripts from last 30 days
2. Save in `./data/transcripts/`
3. Create date-based subdirectories
4. Generate a summary report
5. Track progress in real-time

**Output structure:**

```
data/transcripts/
├── manifest.json          # Tracks what's been exported
├── export-report.md       # Summary report
└── 2026-02-03/           # Date-based folders
    ├── meeting_001.json
    └── meeting_001.txt
```

## Step 4: Incremental Export (1-2 minutes)

Run the export again - it will skip already downloaded transcripts:

```bash
# Run example 4 (incremental)
python3 example_usage.py --example 4
```

This will only download transcripts that aren't in `manifest.json`.

## CLI Usage (Alternative)

Instead of examples, use the main CLI directly:

```bash
# Export with email/password
python3 -m memex.scraper.plaud_scraper \
    --email your@email.com \
    --password yourpassword \
    --output ./data/transcripts \
    --headless

# Export with saved session
python3 -m memex.scraper.plaud_scraper \
    --session plaud_session.json \
    --output ./data/transcripts \
    --headless

# Export specific date range
python3 -m memex.scraper.plaud_scraper \
    --session plaud_session.json \
    --start-date 2026-01-01 \
    --end-date 2026-01-31 \
    --output ./data/transcripts \
    --formats json,txt,srt \
    --headless
```

## Python API Usage

For programmatic use:

```python
import asyncio
from datetime import datetime
from pathlib import Path
from memex.scraper import PlaudScraper, ScraperConfig, PlaudCredentials

async def main():
    # Create scraper
    config = ScraperConfig(headless=True)
    scraper = PlaudScraper(config)

    await scraper.start()

    # Login
    credentials = PlaudCredentials(
        email="your@email.com",
        password="yourpassword"
    )
    await scraper.login(credentials)

    # Batch export
    result = await scraper.batch_export(
        output_dir=Path("./data/transcripts")
    )

    print(f"Exported {result.success_count} transcripts")

    await scraper.close()

asyncio.run(main())
```

## Common Issues

### Issue: "Please install playwright"

**Solution:**

```bash
pip install playwright
playwright install chromium
```

### Issue: "Login failed"

**Solution:**

- Check email/password are correct
- Try without `--headless` to see browser
- If using 2FA, use example 5

### Issue: "Session expired"

**Solution:**

- Delete `plaud_session.json`
- Login again with email/password

### Issue: Rate limit errors

**Solution:**
Edit config to slow down:

```python
config = ScraperConfig(
    rate_limit_per_second=0.1  # 1 request per 10 seconds
)
```

## Viewing Results

### Check what was exported

```bash
cat data/transcripts/manifest.json
```

### View the report

```bash
cat data/transcripts/export-report.md
```

### Count transcripts

```bash
find data/transcripts -name "*.json" | grep -v manifest | wc -l
```

### View a transcript

```bash
# JSON format
cat data/transcripts/2026-02-03/meeting_001.json | jq .

# Text format
cat data/transcripts/2026-02-03/meeting_001.txt
```

## Next Steps

After exporting transcripts:

1. **Import to database** (see roadmap for schema)
2. **Generate embeddings** for vector search
3. **Create daily journals** using HISTORIAN
4. **Build search API** with FastAPI

## Getting Help

- **Full documentation**: See `README.md`
- **Implementation details**: See `IMPLEMENTATION_SUMMARY.md`
- **Code examples**: See `example_usage.py`

## Performance

Expected performance:

- **Rate**: 1 transcript per 5 seconds
- **100 transcripts**: ~8-10 minutes
- **Session lifetime**: 1 hour

## Tips

1. **Use session reuse** to avoid repeated logins
2. **Run incremental exports** regularly (via cron)
3. **Use headless mode** for production
4. **Monitor the manifest** to track progress
5. **Check export reports** for failures

## Example Cron Job

Export new transcripts daily at 2am:

```bash
# Add to crontab
0 2 * * * cd /path/to/clawd/memex/scraper && python3 -m memex.scraper.plaud_scraper --session plaud_session.json --output ./data/transcripts --headless >> export.log 2>&1
```

---

**Ready to start?** Run Step 1 above to get going!

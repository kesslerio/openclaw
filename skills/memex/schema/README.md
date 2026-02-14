# Memex Database Schema

PostgreSQL schema for transcript storage with full-text search and vector embeddings.

## Overview

The schema supports:

- **Full-text search** using PostgreSQL's built-in tsvector
- **Vector embeddings** using pgvector for semantic search
- **Speaker diarization** with time tracking
- **Segment-level timestamps** for precise retrieval
- **Automatic processing status** tracking

## Tables

### `transcripts`

Main table storing transcript metadata and full text.

Key fields:

- `external_id`: Unique ID from source system (e.g., Plaud)
- `search_vector`: Auto-generated full-text search index
- `processed_at`: Timestamp of processing completion
- `embedding_generated`, `journal_generated`: Processing flags

### `transcript_speakers`

Speaker identification and statistics per transcript.

Tracks:

- Speaker labels (SPEAKER_00, SPEAKER_01, etc.)
- Optional identified names
- Speaking time and word count per speaker

### `transcript_segments`

Individual transcript segments with timestamps and embeddings.

Features:

- Millisecond-precision timestamps
- Confidence scores from transcription
- Vector embeddings (1536d) for semantic search

## Indexes

### Performance Indexes

- `idx_transcripts_recorded_at`: Fast date-based queries
- `idx_transcripts_search`: GIN index for full-text search
- `idx_segments_time_range`: Fast segment lookup by time
- `idx_segments_embedding`: HNSW index for vector similarity

### Operational Indexes

- `idx_transcripts_pending_embeddings`: Find unprocessed transcripts
- `idx_transcripts_pending_journal`: Find transcripts needing journals

## Views

### `v_recent_transcripts`

Recent transcripts with speaker and segment counts.

### `v_pending_transcripts`

Transcripts needing processing (embeddings or journals).

### `v_speaker_stats`

Aggregated statistics by identified speaker.

## Functions

### `search_transcripts(query_text, limit, offset)`

Full-text search with ranking and highlighted snippets.

Returns:

- Transcript ID, title, recorded date
- Text snippet with `<mark>` tags around matches
- Relevance rank score

Example:

```sql
SELECT * FROM search_transcripts('heart failure medication', 10, 0);
```

### `search_similar_segments(query_embedding, limit, threshold)`

Vector similarity search for semantic queries.

Returns:

- Segment ID, transcript ID, text
- Similarity score (0-1)
- Timestamp range

Example:

```sql
SELECT * FROM search_similar_segments('[1.2, 0.5, ...]'::vector(1536), 10, 0.7);
```

## Migration Instructions

### Prerequisites

1. **Supabase project** with PostgreSQL database
2. **Database password** from Supabase dashboard:
   - Go to Project Settings > Database
   - Copy the password from "Connection String"
3. **Add to `.env`**:
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_DB_PASSWORD=your_database_password
   ```

### Apply Migration

#### Option 1: Supabase SQL Editor (Recommended)

1. Open Supabase Dashboard > SQL Editor
2. Copy contents of `001_transcripts.sql`
3. Paste and run
4. Verify tables created in Table Editor

#### Option 2: psql Command Line

```bash
# Set environment variables
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_DB_PASSWORD="your_password"

# Parse project reference
PROJECT_REF=$(echo $SUPABASE_URL | cut -d'/' -f3 | cut -d'.' -f1)

# Connect and run migration
psql "postgresql://postgres:$SUPABASE_DB_PASSWORD@db.$PROJECT_REF.supabase.co:5432/postgres?sslmode=require" \
  -f 001_transcripts.sql
```

#### Option 3: Python Script

```python
from memex.db import get_db_connection

with open('memex/schema/001_transcripts.sql', 'r') as f:
    migration_sql = f.read()

with get_db_connection() as conn:
    with conn.cursor() as cur:
        cur.execute(migration_sql)
    conn.commit()

print("Migration complete!")
```

### Verify Migration

```sql
-- Check tables exist
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- Check indexes
SELECT indexname FROM pg_indexes WHERE schemaname = 'public';

-- Check views
SELECT viewname FROM pg_views WHERE schemaname = 'public';

-- Test full-text search function
SELECT * FROM search_transcripts('test', 1, 0);
```

## Usage Examples

### Insert Transcript

```python
from memex.db import insert_transcript

transcript_id = insert_transcript(
    external_id="plaud_20260203_001",
    source="plaud",
    recorded_at="2026-02-03T10:30:00-08:00",
    raw_text="This is the full transcript text...",
    title="Morning meeting notes",
    duration_seconds=1200,
    word_count=500,
    speaker_count=2
)
```

### Search Transcripts

```python
from memex.db import search_transcripts_fulltext

results = search_transcripts_fulltext(
    search_query="diabetes medication",
    limit=10,
    offset=0
)

for result in results:
    print(f"{result['title']}: {result['snippet']}")
```

### Get Pending Transcripts

```python
from memex.db import get_pending_transcripts

pending = get_pending_transcripts()

for transcript in pending:
    if transcript['needs_embeddings']:
        # Generate embeddings
        pass
    if transcript['needs_journal']:
        # Generate journal entry
        pass
```

### Update Processing Status

```python
from memex.db import update_processing_status

update_processing_status(
    transcript_id="uuid-here",
    embedding_generated=True,
    journal_generated=True
)
```

## Performance Tuning

### Analyze Query Performance

```sql
EXPLAIN ANALYZE
SELECT * FROM search_transcripts('medication', 10, 0);
```

### Update Statistics

```sql
ANALYZE transcripts;
ANALYZE transcript_segments;
```

### Monitor Index Usage

```sql
SELECT * FROM v_index_usage;
```

### Check Table Sizes

```sql
SELECT * FROM v_table_sizes;
```

## Backup Strategy

### Automated Backups

Supabase provides daily automatic backups (retention depends on plan).

### Manual Backup

```bash
PROJECT_REF="your-project-ref"
DB_PASSWORD="your-password"

pg_dump "postgresql://postgres:$DB_PASSWORD@db.$PROJECT_REF.supabase.co:5432/postgres?sslmode=require" \
  -t transcripts -t transcript_speakers -t transcript_segments \
  > memex_backup_$(date +%Y%m%d).sql
```

### Restore from Backup

```bash
psql "postgresql://postgres:$DB_PASSWORD@db.$PROJECT_REF.supabase.co:5432/postgres?sslmode=require" \
  < memex_backup_20260203.sql
```

## Monitoring

### Connection Pool Status

```python
from memex.db import check_database_health

health = check_database_health()
print(health)
# {
#   "status": "healthy",
#   "transcripts": 150,
#   "pending_embeddings": 5,
#   "pool_size": "2-10"
# }
```

### Long-Running Queries

```sql
SELECT
    pid,
    now() - query_start as duration,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
  AND query NOT LIKE '%pg_stat_activity%'
ORDER BY duration DESC;
```

### Kill Long Query

```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE pid = 12345;
```

## Troubleshooting

### Connection Issues

**Error**: `connection refused`

- Check `SUPABASE_DB_PASSWORD` is set correctly
- Verify Supabase project is not paused
- Check network/firewall allows port 5432

**Error**: `SSL required`

- Supabase requires SSL connections
- Connection string should include `sslmode=require`

### Query Timeouts

**Error**: `statement timeout`

- Increase `DB_QUERY_TIMEOUT` in `.env`
- Optimize query with indexes
- Use pagination for large result sets

### Vector Index Issues

**Error**: `index creation failed`

- HNSW index requires pgvector extension
- For large datasets, use IVFFlat instead:
  ```sql
  DROP INDEX idx_segments_embedding;
  CREATE INDEX idx_segments_embedding ON transcript_segments
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
  ```

### Out of Memory

- Reduce `MAX_CONNECTIONS` in `.env`
- Use smaller batch sizes for bulk operations
- Enable query result streaming

## Security

### Row-Level Security (RLS)

To enable RLS for multi-tenant scenarios:

```sql
ALTER TABLE transcripts ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_transcripts ON transcripts
    FOR ALL
    USING (user_id = auth.uid());
```

### API Key Rotation

When rotating Supabase credentials:

1. Update `SUPABASE_DB_PASSWORD` in `.env`
2. Restart application to reload connection pool
3. Or call `close_pool()` to force reconnection

## Extensions

### Add Custom Embeddings

For different embedding dimensions:

```sql
-- For different model (e.g., 384d sentence-transformers)
ALTER TABLE transcript_segments
    ADD COLUMN embedding_384 VECTOR(384);

CREATE INDEX idx_segments_embedding_384 ON transcript_segments
    USING hnsw (embedding_384 vector_cosine_ops);
```

### Add Tags

```sql
CREATE TABLE transcript_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transcript_id UUID REFERENCES transcripts(id) ON DELETE CASCADE,
    tag VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(transcript_id, tag)
);

CREATE INDEX idx_tags_transcript ON transcript_tags(transcript_id);
CREATE INDEX idx_tags_tag ON transcript_tags(tag);
```

## Resources

- [Supabase Documentation](https://supabase.com/docs)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

## Support

For issues or questions:

1. Check logs in `/Users/arvindsarin/Cursor/Claude-2026/openclaw/logs/`
2. Run health check: `python -m memex.db.connection`
3. Review Supabase Dashboard > Database > Query Performance

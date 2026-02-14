-- =============================================================================
-- Memex Transcript Storage Schema
-- Migration: 001_transcripts
-- Purpose: Full-text search and vector embeddings for transcript management
-- Date: 2026-02-03
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =============================================================================
-- Main Transcripts Table
-- =============================================================================

CREATE TABLE transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id VARCHAR(255) UNIQUE NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'plaud',
    title VARCHAR(500),
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_seconds INTEGER,
    raw_text TEXT NOT NULL,
    speaker_count INTEGER,
    word_count INTEGER,
    language VARCHAR(10) DEFAULT 'en',

    -- Processing status
    processed_at TIMESTAMP WITH TIME ZONE,
    embedding_generated BOOLEAN DEFAULT FALSE,
    journal_generated BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Full-text search vector (auto-generated)
    search_vector TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(raw_text, '')), 'B')
    ) STORED,

    -- Constraints
    CONSTRAINT valid_duration CHECK (duration_seconds >= 0),
    CONSTRAINT valid_speaker_count CHECK (speaker_count >= 0),
    CONSTRAINT valid_word_count CHECK (word_count >= 0)
);

-- Indexes for transcripts table
CREATE INDEX idx_transcripts_recorded_at ON transcripts(recorded_at DESC);
CREATE INDEX idx_transcripts_source ON transcripts(source);
CREATE INDEX idx_transcripts_external_id ON transcripts(external_id);
CREATE INDEX idx_transcripts_search ON transcripts USING GIN(search_vector);
CREATE INDEX idx_transcripts_processed ON transcripts(processed_at) WHERE processed_at IS NOT NULL;
CREATE INDEX idx_transcripts_pending_embeddings ON transcripts(embedding_generated) WHERE embedding_generated = FALSE;
CREATE INDEX idx_transcripts_pending_journal ON transcripts(journal_generated) WHERE journal_generated = FALSE;

-- Trigram index for fuzzy title search
CREATE INDEX idx_transcripts_title_trgm ON transcripts USING GIN(title gin_trgm_ops);

-- =============================================================================
-- Transcript Speakers Table
-- =============================================================================

CREATE TABLE transcript_speakers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transcript_id UUID NOT NULL REFERENCES transcripts(id) ON DELETE CASCADE,
    speaker_label VARCHAR(100) NOT NULL,
    identified_name VARCHAR(255),
    speaking_time_seconds INTEGER,
    word_count INTEGER,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    UNIQUE(transcript_id, speaker_label),
    CONSTRAINT valid_speaking_time CHECK (speaking_time_seconds >= 0),
    CONSTRAINT valid_speaker_word_count CHECK (word_count >= 0)
);

-- Indexes for speakers table
CREATE INDEX idx_speakers_transcript ON transcript_speakers(transcript_id);
CREATE INDEX idx_speakers_identified_name ON transcript_speakers(identified_name) WHERE identified_name IS NOT NULL;

-- =============================================================================
-- Transcript Segments Table (with vector embeddings)
-- =============================================================================

CREATE TABLE transcript_segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transcript_id UUID NOT NULL REFERENCES transcripts(id) ON DELETE CASCADE,
    speaker_label VARCHAR(100),
    start_time_ms INTEGER NOT NULL,
    end_time_ms INTEGER NOT NULL,
    text TEXT NOT NULL,
    confidence FLOAT,

    -- Vector embedding for semantic search (OpenAI ada-002: 1536 dimensions)
    embedding VECTOR(1536),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_time_range CHECK (end_time_ms > start_time_ms),
    CONSTRAINT valid_confidence CHECK (confidence >= 0 AND confidence <= 1)
);

-- Indexes for segments table
CREATE INDEX idx_segments_transcript ON transcript_segments(transcript_id);
CREATE INDEX idx_segments_time_range ON transcript_segments(transcript_id, start_time_ms, end_time_ms);
CREATE INDEX idx_segments_speaker ON transcript_segments(speaker_label) WHERE speaker_label IS NOT NULL;

-- Vector similarity search index (IVFFlat for cosine distance)
-- Note: IVFFlat requires data before creating. Run after initial data load:
-- CREATE INDEX idx_segments_embedding ON transcript_segments
--   USING ivfflat (embedding vector_cosine_ops)
--   WITH (lists = 100);

-- For initial setup with no data, use HNSW index (slower build, faster query):
CREATE INDEX idx_segments_embedding ON transcript_segments
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- =============================================================================
-- Triggers for automatic timestamp updates
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_transcripts_updated_at BEFORE UPDATE ON transcripts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_speakers_updated_at BEFORE UPDATE ON transcript_speakers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Views for common queries
-- =============================================================================

-- Recent transcripts with speaker count
CREATE OR REPLACE VIEW v_recent_transcripts AS
SELECT
    t.id,
    t.external_id,
    t.source,
    t.title,
    t.recorded_at,
    t.duration_seconds,
    t.word_count,
    t.speaker_count,
    t.processed_at,
    t.embedding_generated,
    t.journal_generated,
    COUNT(DISTINCT ts.speaker_label) as actual_speaker_count,
    COUNT(tseg.id) as segment_count
FROM transcripts t
LEFT JOIN transcript_speakers ts ON t.id = ts.transcript_id
LEFT JOIN transcript_segments tseg ON t.id = tseg.transcript_id
GROUP BY t.id
ORDER BY t.recorded_at DESC;

-- Unprocessed transcripts needing attention
CREATE OR REPLACE VIEW v_pending_transcripts AS
SELECT
    id,
    external_id,
    title,
    recorded_at,
    processed_at IS NULL as needs_processing,
    embedding_generated = FALSE as needs_embeddings,
    journal_generated = FALSE as needs_journal,
    created_at
FROM transcripts
WHERE processed_at IS NULL
   OR embedding_generated = FALSE
   OR journal_generated = FALSE
ORDER BY recorded_at DESC;

-- Speaker statistics
CREATE OR REPLACE VIEW v_speaker_stats AS
SELECT
    ts.identified_name,
    COUNT(DISTINCT t.id) as transcript_count,
    SUM(ts.speaking_time_seconds) as total_speaking_time,
    SUM(ts.word_count) as total_words,
    AVG(ts.speaking_time_seconds) as avg_speaking_time,
    MAX(t.recorded_at) as last_appearance
FROM transcript_speakers ts
JOIN transcripts t ON ts.transcript_id = t.id
WHERE ts.identified_name IS NOT NULL
GROUP BY ts.identified_name
ORDER BY transcript_count DESC;

-- =============================================================================
-- Utility functions for search and retrieval
-- =============================================================================

-- Full-text search function
CREATE OR REPLACE FUNCTION search_transcripts(
    query_text TEXT,
    limit_count INTEGER DEFAULT 10,
    offset_count INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    title VARCHAR,
    recorded_at TIMESTAMP WITH TIME ZONE,
    snippet TEXT,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id,
        t.title,
        t.recorded_at,
        ts_headline('english', t.raw_text, to_tsquery('english', query_text),
                   'MaxWords=50, MinWords=20, StartSel=<mark>, StopSel=</mark>') as snippet,
        ts_rank(t.search_vector, to_tsquery('english', query_text)) as rank
    FROM transcripts t
    WHERE t.search_vector @@ to_tsquery('english', query_text)
    ORDER BY rank DESC
    LIMIT limit_count
    OFFSET offset_count;
END;
$$ LANGUAGE plpgsql;

-- Vector similarity search function
CREATE OR REPLACE FUNCTION search_similar_segments(
    query_embedding VECTOR(1536),
    limit_count INTEGER DEFAULT 10,
    similarity_threshold FLOAT DEFAULT 0.7
)
RETURNS TABLE (
    segment_id UUID,
    transcript_id UUID,
    text TEXT,
    similarity FLOAT,
    start_time_ms INTEGER,
    end_time_ms INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ts.id as segment_id,
        ts.transcript_id,
        ts.text,
        1 - (ts.embedding <=> query_embedding) as similarity,
        ts.start_time_ms,
        ts.end_time_ms
    FROM transcript_segments ts
    WHERE ts.embedding IS NOT NULL
      AND 1 - (ts.embedding <=> query_embedding) >= similarity_threshold
    ORDER BY ts.embedding <=> query_embedding
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Performance monitoring queries
-- =============================================================================

-- Table size statistics
CREATE OR REPLACE VIEW v_table_sizes AS
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY bytes DESC;

-- Index usage statistics
CREATE OR REPLACE VIEW v_index_usage AS
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- =============================================================================
-- Grant permissions (adjust role names as needed)
-- =============================================================================

-- Grant basic access to authenticated users
-- GRANT SELECT, INSERT, UPDATE ON transcripts TO authenticated;
-- GRANT SELECT, INSERT, UPDATE ON transcript_speakers TO authenticated;
-- GRANT SELECT, INSERT, UPDATE ON transcript_segments TO authenticated;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- =============================================================================
-- Comments for documentation
-- =============================================================================

COMMENT ON TABLE transcripts IS 'Main table for storing transcript metadata and full text';
COMMENT ON TABLE transcript_speakers IS 'Speaker identification and statistics per transcript';
COMMENT ON TABLE transcript_segments IS 'Individual transcript segments with timestamps and embeddings';
COMMENT ON COLUMN transcripts.search_vector IS 'Auto-generated full-text search vector (title:A, text:B)';
COMMENT ON COLUMN transcript_segments.embedding IS 'Vector embedding for semantic similarity search (1536d OpenAI ada-002)';
COMMENT ON INDEX idx_segments_embedding IS 'HNSW index for fast vector similarity search';
COMMENT ON FUNCTION search_transcripts IS 'Full-text search with ranking and snippets';
COMMENT ON FUNCTION search_similar_segments IS 'Vector similarity search for semantic queries';

-- =============================================================================
-- Migration complete
-- =============================================================================

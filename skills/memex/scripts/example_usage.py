#!/usr/bin/env python3
"""
Example usage of Memex database operations.

Demonstrates:
- Inserting transcripts with speakers and segments
- Full-text search
- Vector similarity search
- Retrieving pending transcripts
- Updating processing status

Usage:
    python memex/scripts/example_usage.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from memex.db import (
    get_db_connection,
    execute_query,
    execute_transaction,
    insert_transcript,
    get_transcript_by_id,
    search_transcripts_fulltext,
    get_pending_transcripts,
    update_processing_status,
    check_database_health,
)


def example_1_insert_simple_transcript():
    """Example 1: Insert a simple transcript."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Insert Simple Transcript")
    print("=" * 60)

    transcript_id = insert_transcript(
        external_id=f"plaud_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        source="plaud",
        recorded_at=datetime.now().isoformat(),
        raw_text=(
            "Patient discussed managing their diabetes with diet and exercise. "
            "We talked about checking blood sugar regularly and the importance "
            "of taking medication as prescribed. Patient expressed concerns "
            "about side effects but agreed to continue current treatment plan."
        ),
        title="Diabetes Management Discussion",
        duration_seconds=180,
        word_count=42,
        speaker_count=2
    )

    print(f"Created transcript ID: {transcript_id}")
    return transcript_id


def example_2_insert_transcript_with_speakers(transcript_id):
    """Example 2: Insert speakers for a transcript."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Insert Speakers")
    print("=" * 60)

    speakers = [
        ("SPEAKER_00", "Dr. Smith", 120, 30),
        ("SPEAKER_01", "Patient John", 60, 12),
    ]

    operations = []
    for speaker_label, identified_name, speaking_time, word_count in speakers:
        query = """
            INSERT INTO transcript_speakers
            (transcript_id, speaker_label, identified_name, speaking_time_seconds, word_count)
            VALUES (%s, %s, %s, %s, %s)
        """
        operations.append((query, (transcript_id, speaker_label, identified_name, speaking_time, word_count)))

    success = execute_transaction(operations)
    print(f"Inserted {len(speakers)} speakers: {'Success' if success else 'Failed'}")


def example_3_insert_segments(transcript_id):
    """Example 3: Insert transcript segments."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Insert Segments")
    print("=" * 60)

    segments = [
        ("SPEAKER_00", 0, 5000, "Good morning. How are you feeling today?", 0.95),
        ("SPEAKER_01", 5000, 12000, "I'm doing okay, just worried about my blood sugar levels.", 0.92),
        ("SPEAKER_00", 12000, 25000, "Let's talk about your diet. What did you eat yesterday?", 0.94),
        ("SPEAKER_01", 25000, 40000, "I had oatmeal for breakfast and a salad for lunch.", 0.89),
        ("SPEAKER_00", 40000, 60000, "That's good. Keep monitoring your levels daily.", 0.96),
    ]

    operations = []
    for speaker_label, start_ms, end_ms, text, confidence in segments:
        query = """
            INSERT INTO transcript_segments
            (transcript_id, speaker_label, start_time_ms, end_time_ms, text, confidence)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        operations.append((query, (transcript_id, speaker_label, start_ms, end_ms, text, confidence)))

    success = execute_transaction(operations)
    print(f"Inserted {len(segments)} segments: {'Success' if success else 'Failed'}")


def example_4_full_text_search():
    """Example 4: Full-text search."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Full-Text Search")
    print("=" * 60)

    search_terms = ["diabetes", "blood sugar", "medication"]

    for term in search_terms:
        print(f"\nSearching for: '{term}'")
        results = search_transcripts_fulltext(term, limit=3)

        if results:
            for i, result in enumerate(results, 1):
                print(f"\n  Result {i}:")
                print(f"    Title: {result['title']}")
                print(f"    Date: {result['recorded_at']}")
                print(f"    Rank: {result['rank']:.3f}")
                print(f"    Snippet: {result['snippet'][:100]}...")
        else:
            print("  No results found")


def example_5_get_transcript_details(transcript_id):
    """Example 5: Retrieve transcript with details."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Retrieve Transcript Details")
    print("=" * 60)

    # Get transcript
    transcript = get_transcript_by_id(transcript_id)
    if transcript:
        print(f"\nTranscript ID: {transcript['id']}")
        print(f"Title: {transcript['title']}")
        print(f"Recorded: {transcript['recorded_at']}")
        print(f"Duration: {transcript['duration_seconds']}s")
        print(f"Speakers: {transcript['speaker_count']}")
        print(f"Processed: {transcript['processed_at'] or 'Not yet'}")

        # Get speakers
        speakers = execute_query(
            "SELECT * FROM transcript_speakers WHERE transcript_id = %s",
            (transcript_id,)
        )
        print(f"\nSpeakers ({len(speakers) if speakers else 0}):")
        for speaker in (speakers or []):
            print(f"  - {speaker['identified_name']}: {speaker['speaking_time_seconds']}s, {speaker['word_count']} words")

        # Get segments
        segments = execute_query(
            "SELECT * FROM transcript_segments WHERE transcript_id = %s ORDER BY start_time_ms",
            (transcript_id,)
        )
        print(f"\nSegments ({len(segments) if segments else 0}):")
        for segment in (segments or [])[:3]:  # Show first 3
            print(f"  - {segment['speaker_label']} ({segment['start_time_ms']}-{segment['end_time_ms']}ms)")
            print(f"    {segment['text'][:50]}...")


def example_6_pending_transcripts():
    """Example 6: Get pending transcripts."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Pending Transcripts")
    print("=" * 60)

    pending = get_pending_transcripts()

    print(f"\nFound {len(pending) if pending else 0} pending transcripts")

    for transcript in (pending or [])[:5]:  # Show first 5
        print(f"\n  {transcript['title']}")
        print(f"    External ID: {transcript['external_id']}")
        print(f"    Recorded: {transcript['recorded_at']}")
        if transcript['needs_processing']:
            print("    ⚠ Needs processing")
        if transcript['needs_embeddings']:
            print("    ⚠ Needs embeddings")
        if transcript['needs_journal']:
            print("    ⚠ Needs journal generation")


def example_7_update_status(transcript_id):
    """Example 7: Update processing status."""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Update Processing Status")
    print("=" * 60)

    print("\nMarking transcript as processed...")

    # Update embeddings status
    success = update_processing_status(
        transcript_id=transcript_id,
        embedding_generated=True
    )
    print(f"Updated embeddings status: {'Success' if success else 'Failed'}")

    # Update journal status
    success = update_processing_status(
        transcript_id=transcript_id,
        journal_generated=True
    )
    print(f"Updated journal status: {'Success' if success else 'Failed'}")

    # Verify
    transcript = get_transcript_by_id(transcript_id)
    if transcript:
        print(f"\nVerification:")
        print(f"  Embeddings generated: {transcript['embedding_generated']}")
        print(f"  Journal generated: {transcript['journal_generated']}")
        print(f"  Processed at: {transcript['processed_at']}")


def example_8_statistics():
    """Example 8: Database statistics."""
    print("\n" + "=" * 60)
    print("EXAMPLE 8: Database Statistics")
    print("=" * 60)

    # Total counts
    stats = execute_query("""
        SELECT
            (SELECT COUNT(*) FROM transcripts) as total_transcripts,
            (SELECT COUNT(*) FROM transcript_speakers) as total_speakers,
            (SELECT COUNT(*) FROM transcript_segments) as total_segments,
            (SELECT COUNT(*) FROM transcripts WHERE embedding_generated = TRUE) as with_embeddings,
            (SELECT COUNT(*) FROM transcripts WHERE journal_generated = TRUE) as with_journals
    """)

    if stats:
        stat = stats[0]
        print(f"\nTotal Statistics:")
        print(f"  Transcripts: {stat['total_transcripts']}")
        print(f"  Speakers: {stat['total_speakers']}")
        print(f"  Segments: {stat['total_segments']}")
        print(f"  With embeddings: {stat['with_embeddings']}")
        print(f"  With journals: {stat['with_journals']}")

    # Speaker statistics
    speaker_stats = execute_query("SELECT * FROM v_speaker_stats LIMIT 5")
    if speaker_stats:
        print(f"\nTop Speakers:")
        for speaker in speaker_stats:
            print(f"  - {speaker['identified_name']}: "
                  f"{speaker['transcript_count']} transcripts, "
                  f"{speaker['total_words']} words")

    # Recent activity
    recent = execute_query("""
        SELECT title, recorded_at, duration_seconds
        FROM transcripts
        ORDER BY recorded_at DESC
        LIMIT 5
    """)

    if recent:
        print(f"\nRecent Transcripts:")
        for transcript in recent:
            print(f"  - {transcript['title']} ({transcript['recorded_at'].strftime('%Y-%m-%d %H:%M')})")


def example_9_custom_query():
    """Example 9: Custom SQL queries."""
    print("\n" + "=" * 60)
    print("EXAMPLE 9: Custom Queries")
    print("=" * 60)

    # Find transcripts by speaker
    print("\nTranscripts with Dr. Smith:")
    results = execute_query("""
        SELECT DISTINCT t.title, t.recorded_at
        FROM transcripts t
        JOIN transcript_speakers ts ON t.id = ts.transcript_id
        WHERE ts.identified_name LIKE %s
        ORDER BY t.recorded_at DESC
        LIMIT 5
    """, ('%Dr. Smith%',))

    for result in (results or []):
        print(f"  - {result['title']} ({result['recorded_at'].strftime('%Y-%m-%d')})")

    # Find long segments
    print("\nLongest segments:")
    results = execute_query("""
        SELECT
            speaker_label,
            (end_time_ms - start_time_ms) / 1000.0 as duration_sec,
            LEFT(text, 50) as preview
        FROM transcript_segments
        ORDER BY (end_time_ms - start_time_ms) DESC
        LIMIT 5
    """)

    for result in (results or []):
        print(f"  - {result['speaker_label']}: {result['duration_sec']:.1f}s - {result['preview']}...")


def example_10_health_check():
    """Example 10: Database health check."""
    print("\n" + "=" * 60)
    print("EXAMPLE 10: Health Check")
    print("=" * 60)

    health = check_database_health()

    print("\nDatabase Health:")
    for key, value in health.items():
        print(f"  {key}: {value}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("MEMEX DATABASE EXAMPLES")
    print("=" * 60)

    try:
        # Example 10: Health check first
        example_10_health_check()

        # Example 1: Insert transcript
        transcript_id = example_1_insert_simple_transcript()

        # Example 2: Add speakers
        example_2_insert_transcript_with_speakers(transcript_id)

        # Example 3: Add segments
        example_3_insert_segments(transcript_id)

        # Example 5: Get details
        example_5_get_transcript_details(transcript_id)

        # Example 7: Update status
        example_7_update_status(transcript_id)

        # Example 6: Check pending
        example_6_pending_transcripts()

        # Example 8: Statistics
        example_8_statistics()

        # Example 4: Search
        example_4_full_text_search()

        # Example 9: Custom queries
        example_9_custom_query()

        print("\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

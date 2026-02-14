"""
Memex API - FastAPI Backend

Serves transcript search and browsing from ChromaDB + Plaud exports.

Usage:
    python3 -m memex.api.main
    # or: uvicorn memex.api.main:app --host 0.0.0.0 --port 8765
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import json
import logging
import sys
import threading
import time

# Add parent dirs to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from memex.historian.transcript_indexer import TranscriptIndexer, PLAUD_EXPORT_DIR
from memex.api.notes_parser import (
    get_parsed_notes_for_transcript,
    get_all_action_items,
    get_all_decisions,
    get_meeting_briefing,
    load_all_transcripts_metadata,
)
from memex.api.schedule_service import ScheduleService

# Import model enforcer - try both package and relative paths
try:
    from memex.config.model_enforcer import ModelEnforcer
except ModuleNotFoundError:
    from config.model_enforcer import ModelEnforcer

logger = logging.getLogger(__name__)

# Shared Claude client (same as journal generator)
_claude_client = None
_claude_model = "claude-sonnet-4-20250514"

def get_claude():
    global _claude_client
    if _claude_client is None:
        _claude_client = ModelEnforcer.get_client()
    return _claude_client

app = FastAPI(
    title="Memex API",
    description="Meeting intelligence - search and browse your transcripts",
    version="0.4.0",
)

# CORS - allow frontend from any origin on this machine
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy-init indexer (loads model on first use)
_indexer = None

def get_indexer() -> TranscriptIndexer:
    global _indexer
    if _indexer is None:
        _indexer = TranscriptIndexer()
    return _indexer


# Lazy-init schedule service (connects to Calendar + Gmail APIs)
_schedule_service = None

def get_schedule_service() -> ScheduleService:
    global _schedule_service
    if _schedule_service is None:
        _schedule_service = ScheduleService()
        _schedule_service.connect_all()
    return _schedule_service


# ── Request/Response Models ──────────────────────────────────────────

class ChatQueryRequest(BaseModel):
    query: str

class ChatQueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    count: int
    query: str

class JournalResponse(BaseModel):
    journals: List[Dict[str, Any]]
    count: int


# ── Health ───────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": "Memex API",
        "version": "0.4.0",
        "status": "running",
        "endpoints": {
            "chat": "/api/chat/query",
            "search": "/api/search",
            "journals": "/api/journals",
            "transcripts": "/api/transcripts",
            "action_items": "/api/action-items",
            "decisions": "/api/decisions",
            "briefing": "/api/meetings/briefing",
            "today_events": "/api/today/events",
            "today_events_range": "/api/today/events/range",
            "today_briefing": "/api/today/briefing/{event_id}",
            "today_emails": "/api/today/emails",
            "email_compose": "/api/email/compose",
            "integrations": "/api/integrations/status",
            "status": "/api/status",
        },
    }

@app.get("/api/status")
async def status():
    indexer = get_indexer()
    s = indexer.stats()
    return {
        "api": "healthy",
        "indexed_transcripts": s["indexed_transcripts"],
        "total_chunks": s["total_chunks"],
        "timestamp": datetime.now().isoformat(),
    }


# ── Search ───────────────────────────────────────────────────────────

@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Semantic vector search across all transcripts."""
    indexer = get_indexer()
    try:
        raw = indexer.search(request.query, n_results=request.limit or 10)
        results = []
        for doc, meta, dist in zip(
            raw["documents"][0], raw["metadatas"][0], raw["distances"][0]
        ):
            similarity = 1 - dist
            results.append({
                "text": doc,
                "score": round(similarity, 3),
                "final_score": round(similarity, 3),
                "metadata": {
                    "date": meta.get("date", ""),
                    "speaker": meta.get("speakers", ""),
                    "source_file": meta.get("source_dir", ""),
                    "title": meta.get("title", ""),
                    "transcript_id": meta.get("transcript_id", ""),
                    "content_type": meta.get("content_type", "transcript"),
                },
            })
        return SearchResponse(query=request.query, results=results, count=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# ── Chat (Claude-powered synthesis) ──────────────────────────────────

@app.post("/api/chat/query", response_model=ChatQueryResponse)
async def chat_query(request: ChatQueryRequest):
    """
    Chat-style query. Searches transcripts via vector DB, then uses
    Claude (same model as daily journal) to synthesize a natural answer.
    """
    indexer = get_indexer()
    try:
        raw = indexer.search(request.query, n_results=5)

        if not raw["documents"][0]:
            return ChatQueryResponse(
                query=request.query,
                answer="No matching transcripts found for your query.",
                sources=[],
                confidence=0.0,
            )

        # Collect sources and build context for Claude
        context_parts = []
        sources = []
        for i, (doc, meta, dist) in enumerate(zip(
            raw["documents"][0], raw["metadatas"][0], raw["distances"][0]
        )):
            similarity = 1 - dist
            title = meta.get("title", "Unknown")
            date = meta.get("date", "")
            speakers = meta.get("speakers", "")

            context_parts.append(
                f"[Source {i+1}] {title} ({date})\n"
                f"Speakers: {speakers}\n"
                f"{doc}"
            )

            sources.append({
                "date": date,
                "snippet": doc[:200],
                "score": round(similarity, 3),
                "transcript_path": meta.get("source_dir", ""),
            })

        # Synthesize answer with Claude
        context_block = "\n\n---\n\n".join(context_parts)
        try:
            client = get_claude()
            response = client.messages.create(
                model=_claude_model,
                max_tokens=1024,
                temperature=0.3,
                system=(
                    "You are Memex, a meeting intelligence assistant for Arvind Sarin. "
                    "Answer questions based on the transcript excerpts provided. "
                    "Be concise and direct. Cite which meeting/date when referencing specifics. "
                    "If the excerpts don't contain enough info, say so honestly. "
                    "Use markdown formatting."
                ),
                messages=[{
                    "role": "user",
                    "content": (
                        f"Question: {request.query}\n\n"
                        f"Relevant transcript excerpts:\n\n{context_block}"
                    ),
                }],
            )
            answer = response.content[0].text
        except Exception as e:
            logger.warning(f"Claude synthesis failed, falling back to raw results: {e}")
            # Fallback: return raw snippets if Claude is unavailable
            answer_parts = []
            for i, (doc, meta, dist) in enumerate(zip(
                raw["documents"][0], raw["metadatas"][0], raw["distances"][0]
            )):
                title = meta.get("title", "Unknown")
                date = meta.get("date", "")
                speakers = meta.get("speakers", "")
                answer_parts.append(
                    f"**{title}** ({date})\n"
                    f"*Speakers: {speakers}*\n\n"
                    f"{doc[:400]}{'...' if len(doc) > 400 else ''}"
                )
            answer = (
                f"Found {len(sources)} relevant transcript segments:\n\n"
                + "\n\n---\n\n".join(answer_parts)
            )

        return ChatQueryResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            confidence=round(sources[0]["score"], 2) if sources else 0.0,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


# ── Journals (notes.md per transcript, grouped by date) ──────────────

@app.get("/api/journals", response_model=JournalResponse)
async def get_journals(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Return transcript notes grouped by date."""
    try:
        if not PLAUD_EXPORT_DIR.exists():
            return JournalResponse(journals=[], count=0)

        journals_by_date: Dict[str, list] = {}

        for tdir in sorted(PLAUD_EXPORT_DIR.iterdir()):
            if not tdir.is_dir():
                continue
            meta_path = tdir / "metadata.json"
            notes_path = tdir / "notes.md"

            if not notes_path.exists():
                continue

            meta = {}
            if meta_path.exists():
                with open(meta_path) as f:
                    meta = json.load(f)

            start_time = meta.get("start_time", 0)
            if start_time:
                date_str = datetime.fromtimestamp(start_time / 1000).strftime("%Y-%m-%d")
            else:
                continue

            # Filter by date range
            if start_date and date_str < start_date:
                continue
            if end_date and date_str > end_date:
                continue

            notes_content = notes_path.read_text().strip()
            if not notes_content:
                continue

            title = meta.get("filename", tdir.name)

            if date_str not in journals_by_date:
                journals_by_date[date_str] = []
            journals_by_date[date_str].append({
                "title": title,
                "content": notes_content,
                "duration_ms": meta.get("duration_ms", 0),
            })

        # Build journal entries
        journals = []
        for date_str in sorted(journals_by_date.keys(), reverse=True):
            entries = journals_by_date[date_str]
            combined = f"# Meetings - {date_str}\n\n"
            action_items = []

            for entry in entries:
                duration_min = entry["duration_ms"] // 60000
                combined += f"## {entry['title']} ({duration_min} min)\n\n"
                combined += entry["content"] + "\n\n---\n\n"

                # Extract action items
                for line in entry["content"].split("\n"):
                    stripped = line.strip()
                    if stripped.startswith("- [ ]"):
                        action_items.append(stripped[6:].strip())

            journals.append({
                "date": date_str,
                "content": combined,
                "action_items": action_items,
                "transcript_count": len(entries),
            })

        return JournalResponse(journals=journals, count=len(journals))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load journals: {str(e)}")


# ── Transcript List ──────────────────────────────────────────────────

@app.get("/api/transcripts")
async def list_transcripts(
    limit: int = 50,
    offset: int = 0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
):
    """List all exported transcripts with metadata. Supports date range and title search."""
    try:
        all_transcripts = load_all_transcripts_metadata()

        # Apply filters
        if start_date:
            all_transcripts = [t for t in all_transcripts if t["date_only"] >= start_date]
        if end_date:
            all_transcripts = [t for t in all_transcripts if t["date_only"] <= end_date]
        if search:
            q = search.lower()
            all_transcripts = [t for t in all_transcripts if q in t["title"].lower()]

        total = len(all_transcripts)
        page = all_transcripts[offset:offset + limit]

        return {"transcripts": page, "total": total}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transcripts/{file_id}")
async def get_transcript(file_id: str):
    """Get full transcript content by file_id, including parsed notes."""
    try:
        for tdir in PLAUD_EXPORT_DIR.iterdir():
            if not tdir.is_dir():
                continue
            meta_path = tdir / "metadata.json"
            if not meta_path.exists():
                continue
            with open(meta_path) as f:
                meta = json.load(f)
            if meta.get("file_id") == file_id:
                start_time = meta.get("start_time", 0)
                date_only = datetime.fromtimestamp(start_time / 1000).strftime("%Y-%m-%d") if start_time else ""
                title = meta.get("filename", tdir.name)

                result = {"metadata": meta, "dir_name": tdir.name}

                transcript_path = tdir / "transcript.json"
                if transcript_path.exists():
                    with open(transcript_path) as f:
                        result["segments"] = json.load(f)

                notes_path = tdir / "notes.md"
                if notes_path.exists():
                    result["notes"] = notes_path.read_text()

                txt_path = tdir / "transcript.txt"
                if txt_path.exists():
                    result["text"] = txt_path.read_text()

                # Parse structured notes
                parsed = get_parsed_notes_for_transcript(
                    str(tdir), title=title, file_id=file_id, meeting_date=date_only
                )
                if parsed:
                    result["parsed_notes"] = parsed.to_dict()

                return result

        raise HTTPException(status_code=404, detail=f"Transcript {file_id} not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Action Items ─────────────────────────────────────────────────────

@app.get("/api/action-items")
async def action_items(
    status: Optional[str] = None,
    owner: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Aggregate action items across all transcripts."""
    try:
        items = get_all_action_items(
            status_filter=status or "",
            owner_filter=owner or "",
            start_date=start_date or "",
            end_date=end_date or "",
        )
        return {"action_items": items, "count": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Decisions ────────────────────────────────────────────────────────

@app.get("/api/decisions")
async def decisions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    keyword: Optional[str] = None,
):
    """Aggregate decisions across all transcripts."""
    try:
        items = get_all_decisions(
            start_date=start_date or "",
            end_date=end_date or "",
            keyword=keyword or "",
        )
        return {"decisions": items, "count": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Meeting Briefing ─────────────────────────────────────────────────

@app.get("/api/meetings/briefing")
async def meeting_briefing(attendees: str):
    """
    Pre-meeting briefing: given comma-separated attendee names,
    find past meetings with those people and return context.
    """
    try:
        names = [n.strip() for n in attendees.split(",") if n.strip()]
        if not names:
            raise HTTPException(status_code=400, detail="Provide comma-separated attendee names")
        briefing = get_meeting_briefing(names)
        return briefing
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Today's Schedule ─────────────────────────────────────────────────

@app.get("/api/today/events")
async def today_events(date: Optional[str] = None):
    """Get calendar events for a day, enriched with meeting context."""
    try:
        svc = get_schedule_service()
        events = svc.get_today_events(date=date)
        return {"events": events, "count": len(events), "date": date or datetime.now().strftime("%Y-%m-%d")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")


@app.get("/api/today/events/range")
async def today_events_range(start: str, end: str):
    """Get calendar events for a date range, grouped by date."""
    try:
        svc = get_schedule_service()
        events_by_date = svc.get_events_for_range(start_date=start, end_date=end)
        total = sum(len(v) for v in events_by_date.values())
        return {"events_by_date": events_by_date, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch events range: {str(e)}")


@app.get("/api/today/briefing/{event_id}")
async def event_briefing(event_id: str, attendees: str = "", summary: str = ""):
    """
    Full meeting briefing for an event.
    attendees format: "Name:email,Name:email,..."
    summary: event title (used to extract names when attendee display names are missing)
    """
    try:
        names = []
        emails = []
        if attendees:
            for pair in attendees.split(","):
                pair = pair.strip()
                if ":" in pair:
                    name, email = pair.split(":", 1)
                    names.append(name.strip())
                    emails.append(email.strip())
                else:
                    names.append(pair)

        if not names:
            raise HTTPException(status_code=400, detail="Provide attendees as Name:email,Name:email")

        svc = get_schedule_service()
        result = svc.get_event_briefing(names, emails, summary=summary)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Briefing failed: {str(e)}")


@app.get("/api/today/emails")
async def attendee_emails(attendees: str = ""):
    """Search Gmail threads involving specific attendee emails."""
    try:
        if not attendees:
            raise HTTPException(status_code=400, detail="Provide comma-separated email addresses")

        email_list = [e.strip() for e in attendees.split(",") if e.strip()]
        svc = get_schedule_service()
        results = svc.search_emails_for_attendees(email_list, days_back=30)
        return {"emails": results, "count": len(results)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email search failed: {str(e)}")


class EmailComposeRequest(BaseModel):
    to: List[str]
    cc: Optional[List[str]] = None
    subject: str
    body: str


@app.post("/api/email/compose")
async def compose_email(request: EmailComposeRequest):
    """
    Compose email. Currently gmail.send scope is not available,
    so this returns the formatted email for clipboard copy.
    """
    return {
        "status": "draft",
        "message": "Gmail send scope not available. Email formatted for clipboard copy.",
        "draft": {
            "to": request.to,
            "cc": request.cc or [],
            "subject": request.subject,
            "body": request.body,
        },
    }


@app.get("/api/integrations/status")
async def integration_status():
    """Connection status for Calendar and Gmail per account."""
    try:
        svc = get_schedule_service()
        return svc.get_integration_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


# ── Plaud Sync ───────────────────────────────────────────────────────

# Sync state (shared across requests)
_sync_state = {
    "running": False,
    "last_result": None,
    "last_run": None,
    "started_at": None,
    "phase": "",
}
_sync_lock = threading.Lock()


def _run_sync_background():
    """Background thread: export from Plaud + index into FAISS."""
    global _indexer
    try:
        _sync_state["phase"] = "Downloading from Plaud..."
        from memex.scraper.plaud_api_client import PlaudExporter

        exporter = PlaudExporter()
        export_stats = exporter.export_all(
            limit=0, skip_existing=True, rate_limit=0.8,
        )

        _sync_state["phase"] = "Indexing into FAISS..."
        indexer = TranscriptIndexer()
        index_stats = indexer.index_directory()

        # Replace the global indexer so searches pick up new data
        _indexer = indexer

        _sync_state["last_result"] = {
            "export": export_stats,
            "index": index_stats,
            "error": None,
        }
    except Exception as e:
        _sync_state["last_result"] = {
            "export": {},
            "index": {},
            "error": str(e),
        }
    finally:
        _sync_state["running"] = False
        _sync_state["last_run"] = datetime.now().isoformat()
        _sync_state["phase"] = ""
        _sync_state["started_at"] = None


@app.post("/api/sync")
async def start_sync():
    """Start a Plaud sync (export new transcripts + reindex). Runs in background."""
    with _sync_lock:
        if _sync_state["running"]:
            return {
                "status": "already_running",
                "phase": _sync_state["phase"],
                "started_at": _sync_state["started_at"],
            }
        _sync_state["running"] = True
        _sync_state["started_at"] = datetime.now().isoformat()
        _sync_state["phase"] = "Starting..."

    thread = threading.Thread(target=_run_sync_background, daemon=True)
    thread.start()

    return {"status": "started", "started_at": _sync_state["started_at"]}


@app.get("/api/sync/status")
async def sync_status():
    """Check sync status."""
    return {
        "running": _sync_state["running"],
        "phase": _sync_state["phase"],
        "started_at": _sync_state["started_at"],
        "last_run": _sync_state["last_run"],
        "last_result": _sync_state["last_result"],
    }


# ── Run ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    print("Starting Memex API on 0.0.0.0:8765")
    print("Docs: http://100.99.190.40:8765/docs")

    uvicorn.run(
        "memex.api.main:app",
        host="0.0.0.0",
        port=8765,
        reload=False,
        log_level="info",
    )

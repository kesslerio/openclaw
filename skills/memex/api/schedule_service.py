"""
Schedule Service - Orchestrates Calendar + Gmail + Notes for live meeting context.

Provides today's calendar events enriched with past meeting context,
attendee-based briefings, and Gmail thread search.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

ACCOUNTS = ["arvind@copperdigital.com", "arvind.sarin@gmail.com"]
# The user's own names — excluded from attendee matching so we only match
# on *other* people in the meeting, not the user's own ubiquitous name.
SELF_NAMES = {"arvind sarin", "arvind"}
SELF_EMAILS = set(ACCOUNTS)
CREDENTIALS_PATH = str(Path.home() / ".openclaw" / "credentials" / "google_credentials.json")
TOKEN_DIR = str(Path.home() / ".openclaw" / "credentials" / ".tokens")


def _names_from_email(email: str) -> list:
    """Derive candidate name parts from an email local part.
    e.g. 'manas.gupta@company.com' -> ['manas', 'gupta']
         'priscillaoworld@gmail.com' -> ['priscillaoworld']
    """
    local = email.split("@")[0].lower()
    # Split on dots, underscores, hyphens, plus
    import re
    parts = re.split(r'[._\-+]', local)
    # Filter out very short or numeric-only tokens
    return [p for p in parts if len(p) >= 3 and not p.isdigit()]


def _names_from_summary(summary: str) -> list:
    """Extract non-self proper names from event titles like:
    '5 Min Quick Connect between Arvind Sarin and Priscilla Oware-Amoateng'
    'Ben Jie and Arvind Sarin'
    'Kathy PODCAST - 60 Min Working Session between Arvind Sarin and Kathy Chen'
    Returns lowercase name tokens (first names + full names) excluding self.
    """
    import re
    s = summary.strip()

    # Try "between X and Y" pattern first
    m = re.search(r'between\s+(.+?)\s+and\s+(.+?)(?:\s*[-–—]|$)', s, re.IGNORECASE)
    if m:
        candidates = [m.group(1).strip(), m.group(2).strip()]
    else:
        # Try "X and Y" at start of title or separated by " - "
        # Split on common delimiters first
        segment = re.split(r'\s*[-–—]\s*', s)[0]
        m2 = re.match(r'^(.+?)\s+and\s+(.+?)$', segment, re.IGNORECASE)
        if m2:
            candidates = [m2.group(1).strip(), m2.group(2).strip()]
        else:
            candidates = []

    names = []
    for cand in candidates:
        cand_lower = cand.lower()
        # Skip if it's the user's own name
        if cand_lower in SELF_NAMES:
            continue
        # Skip if it's not name-like (all lowercase or very short)
        if len(cand) < 3:
            continue
        # Add full name and first name as separate patterns
        names.append(cand_lower)
        first = cand.split()[0].lower() if ' ' in cand else None
        if first and len(first) >= 3 and first not in SELF_NAMES:
            names.append(first)

    return names


def _naive(dt):
    """Strip timezone info so mixed aware/naive datetimes can be compared."""
    return dt.replace(tzinfo=None) if dt.tzinfo else dt


class ScheduleService:
    """Orchestrates Calendar, Gmail, and transcript context for schedule views."""

    def __init__(self):
        self._calendar_services = {}  # email -> CalendarService
        self._gmail_services = {}     # email -> GmailService
        self._account_status = {}     # email -> {calendar: str, gmail: str}
        self._metadata_cache = None
        self._metadata_cache_time = 0
        self._notes_cache = {}        # dir_path -> (parsed_notes, cache_time)
        self.CACHE_TTL = 300          # 5 minutes

    def connect_all(self):
        """Try connecting Calendar + Gmail for all accounts."""
        from memex.integrations.calendar_service import CalendarService, CalendarConfig
        from memex.integrations.gmail_service import GmailService, GmailConfig

        for email in ACCOUNTS:
            self._account_status[email] = {"calendar": "disconnected", "gmail": "disconnected"}

            # Calendar
            try:
                cal_config = CalendarConfig(
                    credentials_path=CREDENTIALS_PATH,
                    token_dir=TOKEN_DIR,
                )
                cal_svc = CalendarService(config=cal_config, account_email=email)
                cal_svc.connect()
                self._calendar_services[email] = cal_svc
                self._account_status[email]["calendar"] = "connected"
                logger.info(f"Calendar connected: {email}")
            except Exception as e:
                self._account_status[email]["calendar"] = f"error: {str(e)[:100]}"
                logger.warning(f"Calendar connection failed for {email}: {e}")

            # Gmail
            try:
                gmail_config = GmailConfig(
                    credentials_path=CREDENTIALS_PATH,
                    token_dir=TOKEN_DIR,
                )
                gmail_svc = GmailService(config=gmail_config, account_email=email)
                gmail_svc.connect()
                self._gmail_services[email] = gmail_svc
                self._account_status[email]["gmail"] = "connected"
                logger.info(f"Gmail connected: {email}")
            except Exception as e:
                self._account_status[email]["gmail"] = f"error: {str(e)[:100]}"
                logger.warning(f"Gmail connection failed for {email}: {e}")

    def get_integration_status(self) -> Dict[str, Any]:
        """Return per-account connection status."""
        accounts = []
        for email in ACCOUNTS:
            status = self._account_status.get(email, {"calendar": "disconnected", "gmail": "disconnected"})
            accounts.append({
                "email": email,
                "calendar": status["calendar"],
                "gmail": status["gmail"],
            })

        calendar_connected = any(s["calendar"] == "connected" for s in accounts)
        gmail_connected = any(s["gmail"] == "connected" for s in accounts)

        return {
            "accounts": accounts,
            "calendar_connected": calendar_connected,
            "gmail_connected": gmail_connected,
            "gmail_send_available": False,  # We only have readonly + modify scopes
        }

    def _get_cached_metadata(self) -> List[Dict]:
        """Load transcript metadata with 5-minute cache."""
        now = time.time()
        if self._metadata_cache is not None and (now - self._metadata_cache_time) < self.CACHE_TTL:
            return self._metadata_cache

        from memex.api.notes_parser import load_all_transcripts_metadata
        self._metadata_cache = load_all_transcripts_metadata()
        self._metadata_cache_time = now
        return self._metadata_cache

    def _get_cached_notes(self, dir_path: str, title: str, file_id: str, meeting_date: str):
        """Load parsed notes with 5-minute cache."""
        now = time.time()
        cached = self._notes_cache.get(dir_path)
        if cached and (now - cached[1]) < self.CACHE_TTL:
            return cached[0]

        from memex.api.notes_parser import get_parsed_notes_for_transcript
        parsed = get_parsed_notes_for_transcript(dir_path, title=title, file_id=file_id, meeting_date=meeting_date)
        self._notes_cache[dir_path] = (parsed, now)
        return parsed

    def get_events_for_range(self, start_date: str, end_date: str) -> Dict[str, List]:
        """Fetch events for a date range, grouped by date string.

        Args:
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD (inclusive)

        Returns:
            { "2026-02-08": [event_dicts], "2026-02-10": [event_dicts], ... }
        """
        from zoneinfo import ZoneInfo

        tz = ZoneInfo("America/Chicago")
        range_start = datetime.strptime(start_date, "%Y-%m-%d")
        range_end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

        all_events = []
        seen = set()

        for email, cal_svc in self._calendar_services.items():
            try:
                events = cal_svc.fetch_events(
                    calendar_id="primary",
                    start_date=range_start,
                    end_date=range_end,
                    max_events=500,
                )
                for ev in events:
                    dedup_key = (ev.summary.strip().lower(), ev.start.isoformat()[:16])
                    if dedup_key in seen:
                        continue
                    seen.add(dedup_key)
                    all_events.append(ev)
            except Exception as e:
                logger.error(f"Failed to fetch calendar range for {email}: {e}")

        all_events.sort(key=lambda e: _naive(e.start))
        enriched = self._enrich_events(all_events)

        # Group by date
        events_by_date: Dict[str, List] = {}
        for ev in enriched:
            # Use the start time to determine the day
            start_str = ev.get("start", "")
            if start_str:
                day_key = start_str[:10]  # "YYYY-MM-DD" from ISO string
            else:
                continue
            events_by_date.setdefault(day_key, []).append(ev)

        return events_by_date

    def get_today_events(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch events from all calendar accounts for a given day.
        Deduplicates by (summary, start_time), sorts chronologically.
        """
        from zoneinfo import ZoneInfo

        tz = ZoneInfo("America/Chicago")

        if date:
            target = datetime.strptime(date, "%Y-%m-%d")
        else:
            target = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
            target = target.replace(tzinfo=None)

        day_start = target.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        all_events = []
        seen = set()

        for email, cal_svc in self._calendar_services.items():
            try:
                events = cal_svc.fetch_events(
                    calendar_id="primary",
                    start_date=day_start,
                    end_date=day_end,
                    max_events=100,
                )
                for ev in events:
                    dedup_key = (ev.summary.strip().lower(), ev.start.isoformat()[:16])
                    if dedup_key in seen:
                        continue
                    seen.add(dedup_key)
                    all_events.append(ev)
            except Exception as e:
                logger.error(f"Failed to fetch calendar for {email}: {e}")

        # Sort by start time
        all_events.sort(key=lambda e: _naive(e.start))

        # Convert to dicts and enrich with context
        return self._enrich_events(all_events)

    def _enrich_events(self, events) -> List[Dict[str, Any]]:
        """Add context tags from past transcripts to each event."""
        metadata = self._get_cached_metadata()

        results = []
        for ev in events:
            event_dict = ev.to_dict()

            # Extract attendee names for matching (exclude self)
            attendee_names = []
            attendee_emails = []
            for att in ev.attendees:
                if att.email and att.email.lower() in SELF_EMAILS:
                    continue
                if att.name and att.name.lower() in SELF_NAMES:
                    continue
                if att.name:
                    attendee_names.append(att.name)
                elif att.email:
                    # Derive name from email when name is missing
                    attendee_names.extend(_names_from_email(att.email))
                if att.email:
                    attendee_emails.append(att.email)

            # Also extract names from the event title (e.g. "between X and Y")
            summary_names = _names_from_summary(ev.summary or "")
            for sn in summary_names:
                if sn not in [n.lower() for n in attendee_names]:
                    attendee_names.append(sn)

            # Quick count of past meetings and open items
            past_count = 0
            open_items = 0
            has_transcript = False

            if attendee_names:
                name_patterns = [n.lower() for n in attendee_names if n]
                for t in metadata:
                    if not t["has_notes"]:
                        continue
                    title_lower = t["title"].lower()
                    match = any(name in title_lower for name in name_patterns)
                    if match:
                        past_count += 1
                        if t["has_transcript"]:
                            has_transcript = True
                        # Count open items from cached notes
                        parsed = self._get_cached_notes(
                            t["dir_path"], t["title"], t["file_id"], t["date_only"]
                        )
                        if parsed:
                            open_items += sum(1 for ai in parsed.action_items if ai.status == "open")

            event_dict["context"] = {
                "past_meeting_count": past_count,
                "open_items_count": open_items,
                "has_transcript": has_transcript,
            }

            # Clean up raw_data to reduce payload
            event_dict.pop("raw_data", None)

            results.append(event_dict)

        return results

    def get_event_briefing(
        self, attendee_names: List[str], attendee_emails: List[str],
        summary: str = "",
    ) -> Dict[str, Any]:
        """Full meeting briefing: past meetings, action items, decisions, emails."""
        from memex.api.notes_parser import get_meeting_briefing
        from memex.api.context_synthesizer import ContextSynthesizer

        # Filter out user's own name so we only match on the other attendees
        external_names = [
            n for n in attendee_names
            if n.lower() not in SELF_NAMES
        ]
        # Also derive names from emails for attendees without a display name
        external_emails = [e for e in attendee_emails if e.lower() not in SELF_EMAILS]
        for email in external_emails:
            external_names.extend(_names_from_email(email))
        # Also extract names from event title (e.g. "between X and Y")
        if summary:
            for sn in _names_from_summary(summary):
                if sn not in [n.lower() for n in external_names]:
                    external_names.append(sn)
        # Deduplicate
        external_names = list(dict.fromkeys(external_names))
        names_for_query = external_names if external_names else attendee_names

        briefing = get_meeting_briefing(names_for_query)

        # Synthesize context for < 10 past meetings
        synthesized_context = None
        total = briefing.get("total_past_meetings", 0)
        if 0 < total < 10:
            try:
                synthesizer = ContextSynthesizer()
                synthesized_context = synthesizer.get_or_synthesize(names_for_query, briefing)
            except Exception as e:
                logger.error(f"Context synthesis failed: {e}")

        # Search Gmail for attendee threads
        emails = self.search_emails_for_attendees(attendee_emails, days_back=30)

        return {
            "briefing": briefing,
            "emails": emails,
            "synthesized_context": synthesized_context,
        }

    def search_emails_for_attendees(
        self, emails: List[str], days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Search Gmail for threads involving these email addresses."""
        if not emails or not self._gmail_services:
            return []

        # Build query: from:e1 OR to:e1 OR from:e2 OR to:e2
        # Filter out our own accounts
        external_emails = [e for e in emails if e not in ACCOUNTS]
        if not external_emails:
            # If only our own accounts, search between them
            external_emails = emails[:2]

        query_parts = []
        for e in external_emails[:5]:  # limit to prevent giant queries
            query_parts.append(f"from:{e}")
            query_parts.append(f"to:{e}")
        query = " OR ".join(query_parts)

        start_date = datetime.now() - timedelta(days=days_back)

        all_emails = []
        seen_threads = set()

        for email, gmail_svc in self._gmail_services.items():
            try:
                fetched = gmail_svc.fetch_emails(
                    start_date=start_date,
                    max_emails=20,
                    query=query,
                )
                for em in fetched:
                    if em.thread_id in seen_threads:
                        continue
                    seen_threads.add(em.thread_id)
                    all_emails.append({
                        "message_id": em.message_id,
                        "thread_id": em.thread_id,
                        "subject": em.subject,
                        "from": {"email": em.from_.email, "name": em.from_.name},
                        "to": [{"email": p.email, "name": p.name} for p in em.to],
                        "date": em.date.isoformat(),
                        "snippet": (em.body_text or "")[:200],
                        "body": (em.body_text or "")[:2000],
                        "is_read": em.is_read,
                        "account": email,
                    })
            except Exception as e:
                logger.error(f"Gmail search failed for {email}: {e}")

        # Sort by date descending
        all_emails.sort(key=lambda x: x["date"], reverse=True)
        return all_emails[:30]

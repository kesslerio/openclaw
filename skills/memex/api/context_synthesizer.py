"""
Context Synthesizer - Meeting context synthesis from structured data.

Uses Claude (same model as daily journal) to synthesize concise
meeting briefings from parsed notes, action items, and decisions.
Falls back to template-based synthesis if Claude is unavailable.
"""

import hashlib
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
try:
    from memex.config.model_enforcer import ModelEnforcer
except ModuleNotFoundError:
    from config.model_enforcer import ModelEnforcer

logger = logging.getLogger(__name__)

_CLAUDE_MODEL = "claude-sonnet-4-20250514"


class ContextSynthesizer:
    CACHE_DIR = Path(__file__).parent.parent / "data" / "context_cache"
    MAX_MEETINGS_FOR_SYNTHESIS = 9  # Only synthesize < 10

    def __init__(self):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                self._client = ModelEnforcer.get_client()
            except Exception as e:
                logger.warning(f"Could not init Claude client: {e}")
        return self._client

    def get_or_synthesize(self, attendee_names: list, briefing_data: dict) -> Optional[str]:
        """
        Return a synthesized context narrative, using cache when possible.

        Args:
            attendee_names: List of external attendee names (not the user).
            briefing_data: The briefing dict from get_meeting_briefing().

        Returns:
            Synthesized markdown string, or None if no meetings.
        """
        total = briefing_data.get("total_past_meetings", 0)

        if total == 0 or total > self.MAX_MEETINGS_FOR_SYNTHESIS:
            return None

        cache_key = self._build_cache_key(attendee_names)
        cached = self._load_cache(cache_key)

        if cached and cached.get("meeting_count") == total:
            logger.info(f"Context cache hit ({total} meetings)")
            return cached["synthesized"]

        logger.info(f"Synthesizing context for {len(attendee_names)} attendees ({total} meetings)")
        synthesis = self._synthesize_from_structured_data(briefing_data)
        if synthesis:
            self._save_cache(cache_key, synthesis, total)
        return synthesis

    def _synthesize_from_structured_data(self, briefing_data: dict) -> str:
        """Build a context narrative from structured briefing data using Claude."""
        meetings = briefing_data.get("matching_meetings", [])
        action_items = briefing_data.get("unresolved_action_items", [])
        decisions = briefing_data.get("key_decisions", [])
        total = briefing_data.get("total_past_meetings", 0)

        if not meetings:
            return None

        # Build structured data for Claude
        structured = self._build_template_synthesis(briefing_data)

        # Try Claude synthesis
        client = self._get_client()
        if client:
            try:
                response = client.messages.create(
                    model=_CLAUDE_MODEL,
                    max_tokens=512,
                    temperature=0.3,
                    system=(
                        "You are Memex, a meeting intelligence assistant for Arvind Sarin. "
                        "Synthesize a concise pre-meeting briefing from the structured data below. "
                        "Highlight what matters most: open action items, recent decisions, and relationship context. "
                        "Be brief (3-5 sentences max for narrative, then bullet lists). Use markdown."
                    ),
                    messages=[{
                        "role": "user",
                        "content": f"Create a meeting prep briefing from this data:\n\n{structured}",
                    }],
                )
                return response.content[0].text
            except Exception as e:
                logger.warning(f"Claude synthesis failed, using template fallback: {e}")

        # Fallback: template-based synthesis
        return structured

    def _build_template_synthesis(self, briefing_data: dict) -> str:
        """Template-based fallback synthesis (no LLM)."""
        meetings = briefing_data.get("matching_meetings", [])
        action_items = briefing_data.get("unresolved_action_items", [])
        decisions = briefing_data.get("key_decisions", [])
        total = briefing_data.get("total_past_meetings", 0)

        parts = []

        # --- Meeting cadence & date range ---
        dates = []
        for m in meetings:
            date_str = m.get("date", "")
            if date_str:
                try:
                    dates.append(datetime.strptime(date_str[:10], "%Y-%m-%d"))
                except ValueError:
                    pass

        if dates:
            earliest = min(dates)
            latest = max(dates)
            span_days = (latest - earliest).days
            if span_days > 0:
                freq = round(span_days / max(total - 1, 1))
                parts.append(
                    f"{total} meetings since {earliest.strftime('%b %Y')}, "
                    f"roughly every {freq} days. "
                    f"Most recent: {latest.strftime('%b %d, %Y')}."
                )
            else:
                parts.append(
                    f"{total} meetings on {latest.strftime('%b %d, %Y')}."
                )

        # --- Topics from meeting titles ---
        topics = self._extract_topics(meetings)
        if topics:
            parts.append("Topics: " + ", ".join(topics[:5]) + ".")

        # --- Open action items ---
        if action_items:
            parts.append(f"\n{len(action_items)} unresolved action items:")
            for item in action_items[:5]:
                owner = item.get("owner", "")
                owner_tag = f" (@{owner})" if owner and owner != "Unassigned" else ""
                date_tag = f" [{item['meeting_date']}]" if item.get("meeting_date") else ""
                parts.append(f"  - {item['description']}{owner_tag}{date_tag}")
            if len(action_items) > 5:
                parts.append(f"  - ...and {len(action_items) - 5} more")

        # --- Recent decisions ---
        if decisions:
            parts.append(f"\n{len(decisions)} key decisions:")
            for dec in decisions[:3]:
                date_tag = f" [{dec['meeting_date']}]" if dec.get("meeting_date") else ""
                parts.append(f"  - {dec['description']}{date_tag}")
            if len(decisions) > 3:
                parts.append(f"  - ...and {len(decisions) - 3} more")

        return "\n".join(parts) if parts else None

    def _extract_topics(self, meetings: list) -> list:
        """Extract meaningful topic phrases from meeting titles."""
        # Common filler words to strip from titles
        stop_words = {
            "meeting", "between", "and", "with", "min", "quick", "connect",
            "weekly", "daily", "standup", "sync", "check", "in", "the",
            "for", "deep", "dive", "working", "session", "arvind", "sarin",
            "project", "status", "update", "review",
        }
        # Date-like prefixes (e.g. "01-30", "11-02")
        date_prefix = re.compile(r'^\d{2}-\d{2}\s*')

        topics = []
        seen = set()
        for m in meetings:
            title = m.get("title", "")
            # Strip date prefix
            title = date_prefix.sub("", title)
            # Strip "between X and Y" suffix
            title = re.sub(r'\s*between\s+.+$', '', title, flags=re.IGNORECASE)
            # Split on common delimiters
            for segment in re.split(r'\s*[-–—:,&]\s*', title):
                segment = segment.strip()
                words = segment.lower().split()
                # Keep segments with at least one non-stop word and 2+ words
                meaningful = [w for w in words if w not in stop_words and len(w) > 2]
                if meaningful and len(segment) > 5:
                    clean = segment.strip()
                    key = clean.lower()
                    if key not in seen:
                        seen.add(key)
                        topics.append(clean)

        return topics

    def _build_cache_key(self, names: list) -> str:
        normalized = sorted(n.strip().lower() for n in names if n.strip())
        joined = "_".join(normalized)
        return hashlib.sha256(joined.encode()).hexdigest()[:16]

    def _load_cache(self, key: str) -> Optional[dict]:
        cache_file = self.CACHE_DIR / f"{key}.json"
        if not cache_file.exists():
            return None
        try:
            return json.loads(cache_file.read_text())
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load cache {cache_file}: {e}")
            return None

    def _save_cache(self, key: str, synthesis: str, meeting_count: int):
        cache_file = self.CACHE_DIR / f"{key}.json"
        data = {
            "synthesized": synthesis,
            "meeting_count": meeting_count,
            "generated_at": datetime.now().isoformat(),
        }
        try:
            cache_file.write_text(json.dumps(data, indent=2))
            logger.info(f"Cached synthesis to {cache_file}")
        except OSError as e:
            logger.warning(f"Failed to write cache {cache_file}: {e}")

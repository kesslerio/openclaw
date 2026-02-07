"""
Anthropic API client with exponential backoff retry logic.
Wraps the anthropic SDK to handle transient failures gracefully.
"""
from __future__ import annotations

import time
from typing import Any

import anthropic

from .constants import MAX_RETRIES, RETRY_BASE_DELAY, RETRY_MAX_DELAY, ANTHROPIC_MODEL
from .logging_config import get_logger

logger = get_logger("api_client")


class AnthropicClient:
    """Thin wrapper around anthropic.Anthropic with automatic retry."""

    def __init__(self, api_key: str | None = None):
        if not api_key:
            self._client = None
            return
        self._client = anthropic.Anthropic(api_key=api_key)

    @property
    def available(self) -> bool:
        return self._client is not None

    def create_message(
        self,
        *,
        model: str = ANTHROPIC_MODEL,
        max_tokens: int = 200,
        messages: list[dict[str, Any]],
        **kwargs: Any,
    ) -> anthropic.types.Message:
        """Send a message with retry on rate-limit and transient errors."""
        if not self._client:
            raise RuntimeError("Anthropic client not configured (missing API key)")

        last_exc: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return self._client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=messages,
                    **kwargs,
                )
            except anthropic.RateLimitError as exc:
                last_exc = exc
                delay = min(RETRY_BASE_DELAY * (2 ** (attempt - 1)), RETRY_MAX_DELAY)
                logger.warning(
                    "Rate limited (attempt %d/%d), retrying in %.1fs",
                    attempt,
                    MAX_RETRIES,
                    delay,
                )
                time.sleep(delay)
            except anthropic.APIError as exc:
                # Retry on 5xx server errors, not on 4xx client errors
                if exc.status_code and 500 <= exc.status_code < 600:
                    last_exc = exc
                    delay = min(RETRY_BASE_DELAY * (2 ** (attempt - 1)), RETRY_MAX_DELAY)
                    logger.warning(
                        "Server error %s (attempt %d/%d), retrying in %.1fs",
                        exc.status_code,
                        attempt,
                        MAX_RETRIES,
                        delay,
                    )
                    time.sleep(delay)
                else:
                    raise

        raise last_exc  # type: ignore[misc]

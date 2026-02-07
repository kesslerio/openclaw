"""
Real-time listeners for Universal Briefing.
Provides webhook server and bot polling to ingest messages into storage.
Signed-off-by: codex_nike
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import signal
import threading
import time
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from typing import Optional

import requests

from .config import config
from .connectors.whatsapp_waha_connector import WhatsAppWAHAConnector
from .connectors.whatsapp_connector import WhatsAppConnector
from .connectors.telegram_connector import TelegramConnector
from .connectors.discord_connector import DiscordConnector
from .connectors.email_connector import EmailConnector
from .connectors.slack_connector import SlackConnector
from .storage import MessageStore
from .models import Platform, UnifiedMessage, Classification
from .processors.classifier import MessageClassifier
from .openclaw_integration import send_to_openclaw, should_respond_to_message
from .logging_config import get_logger

logger = get_logger("listeners")

# Global shutdown event for graceful termination
_shutdown_event = threading.Event()


def run_whatsapp_webhook_server(host: str = "0.0.0.0", port: int = 8080) -> None:
    # Support both WAHA instances (personal + business) and WhatsApp Business API
    waha_personal = WhatsAppWAHAConnector(waha_url="http://localhost:3000")
    waha_business = WhatsAppWAHAConnector(waha_url="http://localhost:3001")
    business_api_connector = WhatsAppConnector()

    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, body: str, content_type: str = "text/plain") -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

        def do_GET(self):  # noqa: N802
            # WhatsApp webhook verification
            try:
                params = self._parse_query()
                mode = params.get("hub.mode")
                verify_token = params.get("hub.verify_token")
                challenge = params.get("hub.challenge")
                if mode == "subscribe" and challenge:
                    if config.WHATSAPP_VERIFY_TOKEN and verify_token != config.WHATSAPP_VERIFY_TOKEN:
                        self._send(403, "Forbidden")
                        return
                    self._send(200, str(challenge))
                    return
                self._send(400, "Bad Request")
            except Exception:
                self._send(500, "Server Error")

        def _verify_hmac(self, body: bytes) -> bool:
            """Verify HMAC-SHA256 signature if WEBHOOK_SECRET is configured."""
            secret = os.getenv("WEBHOOK_SECRET", "")
            if not secret:
                return True  # No secret configured — allow (backward compat)
            sig_header = self.headers.get("X-Webhook-Signature", "")
            if not sig_header:
                logger.warning("REJECTED: missing X-Webhook-Signature header")
                return False
            expected = hmac.new(
                secret.encode(), body, hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(sig_header, expected):
                logger.warning("REJECTED: invalid HMAC signature")
                return False
            return True

        def do_POST(self):  # noqa: N802
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw_body = self.rfile.read(length)

                # Verify webhook HMAC signature
                if not self._verify_hmac(raw_body):
                    self._send(403, "Forbidden")
                    return

                body = raw_body.decode("utf-8")
                payload = json.loads(body) if body else {}

                # Route based on webhook path
                path = self.path.split('?')[0]

                # Route to correct connector and handle auto-reply
                if "event" in payload:
                    # WAHA webhook - determine which instance by checking the account phone
                    msg_payload = payload.get("payload", {})
                    from_number = msg_payload.get("from", "")
                    to_number = msg_payload.get("to", "")

                    # Check if this is from/to the business number
                    is_business = False
                    if "14087537403" in from_number or "14087537403" in to_number:
                        is_business = True
                    elif "14697421095" in from_number or "14697421095" in to_number:
                        is_business = False
                    elif path == "/webhook/whatsapp/business":
                        is_business = True

                    if is_business:
                        logger.info("WAHA Business webhook received")
                        waha_business.add_webhook_message(payload)
                        connector = waha_business
                    else:
                        logger.info("WAHA Personal webhook received")
                        waha_personal.add_webhook_message(payload)
                        connector = waha_personal

                    # Auto-reply with OpenClaw (async to avoid blocking webhook)
                    if payload.get("event") == "message":
                        msg_payload = payload.get("payload", {})
                        message_text = msg_payload.get("body", "")
                        sender_name = msg_payload.get("notifyName", "User")
                        sender_id = msg_payload.get("from", "")
                        chat_id = msg_payload.get("chatId") or sender_id

                        if message_text and should_respond_to_message(
                            message_text,
                            "whatsapp",
                            chat_id=chat_id,
                            sender_id=sender_id,
                        ):
                            logger.info("Queuing auto-reply for DM from %s: %s...", sender_id, message_text[:50])
                            # Run auto-reply in background thread to not block webhook
                            def async_reply():
                                try:
                                    response = send_to_openclaw(message_text, sender_name, sender_id)
                                    if response:
                                        connector.send_message(chat_id, response)
                                        logger.info("Auto-reply sent to %s", chat_id)
                                except Exception as e:
                                    logger.error("Auto-reply error: %s", e)

                            reply_thread = threading.Thread(target=async_reply, daemon=True)
                            reply_thread.start()
                        else:
                            logger.debug("Skipping auto-reply for %s", chat_id)

                elif "entry" in payload:
                    # WhatsApp Business API webhook (bot)
                    logger.info("Routing to Business API connector (bot)")
                    business_api_connector.add_webhook_message(payload)
                else:
                    logger.warning("Unknown webhook format: %s", list(payload.keys()))

                self._send(200, "OK")
            except Exception as e:
                logger.error("Webhook error: %s", e, exc_info=True)
                self._send(500, "Server Error")

        def log_message(self, format, *args):  # noqa: A003
            # Silence default logging
            return

        def _parse_query(self) -> dict:
            query = self.path.split("?", 1)[-1] if "?" in self.path else ""
            out = {}
            for pair in query.split("&"):
                if not pair:
                    continue
                if "=" in pair:
                    k, v = pair.split("=", 1)
                else:
                    k, v = pair, ""
                out[k] = v
            return out

    server = HTTPServer((host, port), Handler)
    logger.info("WhatsApp webhook listening on http://%s:%d", host, port)
    while not _shutdown_event.is_set():
        server.handle_request()
    server.server_close()
    logger.info("WhatsApp webhook server stopped")


def run_telegram_polling(poll_interval: float = 2.0) -> None:
    connector = TelegramConnector()

    if not connector.is_available():
        logger.error("Telegram connector not available. Check TELEGRAM_BOT_TOKEN.")
        return

    token = config.TELEGRAM_BOT_TOKEN
    offset: Optional[int] = None
    logger.info("Telegram polling started")

    message_count = 0
    retry_count = 0
    max_retries = 3

    while not _shutdown_event.is_set():
        try:
            params = {"timeout": 30}
            if offset is not None:
                params["offset"] = offset

            resp = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", params=params, timeout=35)
            data = resp.json()

            # Reset retry counter on success
            retry_count = 0

            if data.get("ok"):
                updates = data.get("result", [])
                if updates:
                    logger.debug("Received %d Telegram updates", len(updates))

                for update in updates:
                    connector.add_update(update)
                    message_count += 1

                    update_id = update.get("update_id")
                    if update_id is not None:
                        offset = update_id + 1
            else:
                logger.error("Telegram API error: %s", data)

        except requests.RequestException as e:
            retry_count += 1
            logger.error("Telegram network error (attempt %d/%d): %s", retry_count, max_retries, e)
            if retry_count >= max_retries:
                logger.error("Max retries reached, waiting 5 seconds before continuing...")
                _shutdown_event.wait(5)
                retry_count = 0
            else:
                # Exponential backoff
                _shutdown_event.wait(2 ** retry_count)
            continue
        except Exception as e:
            logger.error("Telegram polling exception: %s: %s", type(e).__name__, e, exc_info=True)

        _shutdown_event.wait(poll_interval)

    logger.info("Telegram polling stopped")


def run_discord_gateway() -> None:
    connector = DiscordConnector()
    try:
        import discord
    except Exception:
        logger.error("discord.py not installed. Install to enable Discord listener.")
        return

    if not connector.is_available():
        logger.error("Discord connector not available. Check DISCORD_BOT_TOKEN.")
        return

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.messages = True
    intents.members = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logger.info("Discord connected as %s", client.user)

    @client.event
    async def on_message(message):
        try:
            data = {
                "id": str(message.id),
                "content": message.content or "",
                "timestamp": message.created_at.isoformat(),
                "author": {
                    "id": str(message.author.id),
                    "username": message.author.name,
                    "bot": bool(message.author.bot),
                },
                "channel": {
                    "id": str(message.channel.id),
                    "name": getattr(message.channel, "name", None),
                    "type": getattr(message.channel, "type", None).value
                    if getattr(message.channel, "type", None)
                    else 0,
                },
                "mentions": [{"id": str(m.id)} for m in message.mentions],
                "attachments": [{"id": str(a.id)} for a in message.attachments],
                "type": 0,
            }
            connector.add_message(data)
        except Exception:
            pass

    client.run(config.DISCORD_BOT_TOKEN)


def run_listeners(
    whatsapp: bool = False,
    telegram: bool = False,
    discord: bool = False,
    all_listeners: bool = False,
    host: str = "0.0.0.0",
    port: int = 8080,
) -> None:
    if all_listeners:
        whatsapp = True
        telegram = True
        discord = True

    threads = []

    # Register signal handlers for graceful shutdown
    def _handle_signal(signum, frame):
        logger.info("Received signal %d, shutting down...", signum)
        _shutdown_event.set()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    if whatsapp:
        t = threading.Thread(target=run_whatsapp_webhook_server, args=(host, port), daemon=True)
        threads.append(t)
        t.start()

    if telegram:
        t = threading.Thread(target=run_telegram_polling, daemon=True)
        threads.append(t)
        t.start()

    if discord:
        t = threading.Thread(target=run_discord_gateway, daemon=True)
        threads.append(t)
        t.start()

    if not threads:
        logger.error("No listeners started. Pass --whatsapp/--telegram/--discord.")
        return

    try:
        while not _shutdown_event.is_set():
            _shutdown_event.wait(1)
    except KeyboardInterrupt:
        _shutdown_event.set()

    logger.info("Stopped listeners")


def status_report(hours_back: Optional[int] = None) -> None:
    store = MessageStore()
    platforms = [Platform.WHATSAPP, Platform.TELEGRAM, Platform.DISCORD]
    since = None
    if hours_back is not None and hours_back > 0:
        since = datetime.utcnow() - timedelta(hours=hours_back)

    print("📊 Universal Briefing Listener Status")
    print("")
    for platform in platforms:
        connector = {
            Platform.WHATSAPP: WhatsAppWAHAConnector,
            Platform.TELEGRAM: TelegramConnector,
            Platform.DISCORD: DiscordConnector,
        }[platform]()
        available = connector.is_available()
        count = store.count_messages(platform=platform, since=since)
        window = f"last {hours_back}h" if since else "all time"
        print(f"- {platform.value}: {'✅' if available else '❌'} | stored {count} messages ({window})")


def _fetch_and_filter_messages(
    store: MessageStore,
    classifier: MessageClassifier,
    params: dict,
) -> tuple:
    """Shared logic for /messages and /export endpoints.

    Returns (messages, platform, error_response) where error_response is
    a (status, payload) tuple if there was a problem, or None on success.
    """
    platform_key = (params.get("platform") or [""])[0].strip().lower()
    if not platform_key:
        return None, None, (400, {"error": "platform is required"})
    try:
        platform = Platform(platform_key)
    except Exception:
        return None, None, (
            400,
            {
                "error": f"unknown platform '{platform_key}'",
                "supported": ["whatsapp", "telegram", "discord", "email", "slack"],
            },
        )

    hours = (params.get("hours") or ["0"])[0]
    limit = (params.get("limit") or ["200"])[0]
    channel = (params.get("channel") or [""])[0] or None
    query_text = (params.get("q") or [""])[0].strip().lower()
    classify_flag = (params.get("classify") or ["0"])[0].strip() == "1"
    classification_filter = (params.get("classification") or [""])[0].strip().lower()

    try:
        hours_int = int(hours)
    except Exception:
        hours_int = 0
    since = datetime.utcnow() - timedelta(hours=hours_int) if hours_int > 0 else datetime.min

    try:
        limit_int = int(limit)
    except Exception:
        limit_int = 200

    source = (params.get("source") or ["store"])[0].strip().lower()
    persist = (params.get("persist") or ["1"])[0].strip() == "1"

    if platform in (Platform.WHATSAPP, Platform.TELEGRAM, Platform.DISCORD):
        # Use FTS5 search when a query is provided and source is store
        if query_text and source == "store":
            messages = store.search_messages(
                query=query_text,
                platform=platform_key,
                limit=limit_int,
            )
            # FTS already searched; skip the in-memory filter below
            query_text = ""
        else:
            messages = store.fetch_messages(
                platform=platform,
                since=since,
                channel_filter=channel,
                limit=limit_int,
            )
    else:
        if source not in ("live", "api"):
            return None, None, (
                400,
                {
                    "error": "email/slack require source=live",
                    "hint": "use ?source=live&hours=24",
                },
            )
        connector = EmailConnector() if platform == Platform.EMAIL else SlackConnector()
        if not connector.is_available():
            return None, None, (503, {"error": f"{platform.value} connector unavailable"})
        messages = connector.fetch_messages(
            hours_back=hours_int if hours_int > 0 else 24,
            channel_filter=channel,
        )
        messages = messages[: max(1, min(limit_int, len(messages)))]
        if persist:
            store.save_messages(messages)

    # Optional classification + filtering
    if classify_flag or classification_filter:
        messages = classifier.classify_messages(messages)
        if classification_filter:
            wanted = {c.strip() for c in classification_filter.split(",") if c.strip()}
            messages = [
                m for m in messages
                if m.classification and m.classification.value in wanted
            ]
    if query_text:
        messages = [
            m for m in messages
            if query_text in (m.content or "").lower()
            or query_text in (m.sender_name or "").lower()
            or query_text in (m.channel_name or "").lower()
        ]

    return messages, platform, None


def run_api_server(host: str = "127.0.0.1", port: int = 8090) -> None:
    store = MessageStore()
    classifier = MessageClassifier()

    def _serialize(msg: UnifiedMessage) -> dict:
        return {
            "id": msg.id,
            "platform": msg.platform.value,
            "sender_id": msg.sender_id,
            "sender_name": msg.sender_name,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
            "channel_id": msg.channel_id,
            "channel_name": msg.channel_name,
            "message_type": msg.message_type.value,
            "thread_id": msg.thread_id,
            "reply_to_id": msg.reply_to_id,
            "is_mention": msg.is_mention,
            "has_attachment": msg.has_attachment,
            "attachment_type": msg.attachment_type,
            "classification": msg.classification.value if msg.classification else None,
            "classification_confidence": msg.classification_confidence,
            "classification_reason": msg.classification_reason,
        }

    class ApiHandler(BaseHTTPRequestHandler):
        def _cors(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, X-UB-Token")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

        def _require_auth(self, params: dict) -> bool:
            """Check auth. Returns True if access is allowed."""
            if not config.API_TOKEN:
                return True  # No token configured — allow open access
            token = self.headers.get("X-UB-Token", "") or (params.get("token") or [""])[0]
            return token == config.API_TOKEN

        def _unauthorized(self):
            self._send_json(401, {"error": "unauthorized"})

        def _send_json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False)
            self.send_response(status)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

        def do_POST(self):  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path
            params = parse_qs(parsed.query or "")

            if path == "/messages/read":
                if not self._require_auth(params):
                    self._unauthorized()
                    return
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    raw = self.rfile.read(length).decode("utf-8")
                    body = json.loads(raw) if raw else {}
                except (json.JSONDecodeError, ValueError):
                    self._send_json(400, {"error": "invalid JSON body"})
                    return

                platform_key = body.get("platform", "")
                message_ids = body.get("ids", [])
                if not platform_key or not message_ids:
                    self._send_json(400, {"error": "platform and ids are required"})
                    return

                updated = store.mark_read(platform_key, message_ids)
                self._send_json(200, {"updated": updated})
                return

            self._send_json(404, {"error": "not found"})

        def do_GET(self):  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path
            params = parse_qs(parsed.query or "")

            if path == "/health":
                if not self._require_auth(params):
                    self._unauthorized()
                    return
                counts = {
                    p.value: store.count_messages(platform=p)
                    for p in [Platform.WHATSAPP, Platform.TELEGRAM, Platform.DISCORD]
                }
                self._send_json(
                    200,
                    {
                        "status": "ok",
                        "time": datetime.utcnow().isoformat(),
                        "db_path": str(store.path),
                        "counts": counts,
                    },
                )
                return

            if path == "/stats":
                if not self._require_auth(params):
                    self._unauthorized()
                    return
                stats = store.get_stats()
                stats["time"] = datetime.utcnow().isoformat()
                self._send_json(200, stats)
                return

            if path == "/messages":
                if not self._require_auth(params):
                    self._unauthorized()
                    return
                messages, platform, error = _fetch_and_filter_messages(store, classifier, params)
                if error:
                    self._send_json(error[0], error[1])
                    return
                source = (params.get("source") or ["store"])[0].strip().lower()
                self._send_json(
                    200,
                    {
                        "platform": platform.value,
                        "count": len(messages),
                        "source": source if platform in (Platform.EMAIL, Platform.SLACK) else "store",
                        "messages": [_serialize(m) for m in messages],
                    },
                )
                return

            if path == "/export":
                if not self._require_auth(params):
                    self._unauthorized()
                    return
                fmt = (params.get("format") or ["csv"])[0].strip().lower()
                # Set defaults for export
                if "limit" not in params:
                    params["limit"] = ["1000"]
                if "classify" not in params:
                    params["classify"] = ["1"]

                messages, platform, error = _fetch_and_filter_messages(store, classifier, params)
                if error:
                    self._send_json(error[0], error[1])
                    return

                if fmt == "json":
                    self._send_json(
                        200,
                        {
                            "platform": platform.value,
                            "count": len(messages),
                            "messages": [_serialize(m) for m in messages],
                        },
                    )
                    return

                # CSV export
                headers = [
                    "id", "platform", "sender_id", "sender_name", "content",
                    "timestamp", "channel_id", "channel_name", "message_type",
                    "thread_id", "reply_to_id", "is_mention", "has_attachment",
                    "classification", "classification_confidence", "classification_reason",
                ]
                lines = [",".join(headers)]
                for msg in messages:
                    row = _serialize(msg)
                    row["content"] = (row["content"] or "").replace("\n", " ").replace("\r", " ")
                    row["classification"] = row.get("classification") or ""
                    row["classification_confidence"] = row.get("classification_confidence") or ""
                    row["classification_reason"] = row.get("classification_reason") or ""
                    values = [
                        str(row.get("id", "")),
                        row.get("platform", ""),
                        row.get("sender_id", ""),
                        row.get("sender_name", ""),
                        row.get("content", "").replace('"', '""'),
                        row.get("timestamp", ""),
                        row.get("channel_id", "") or "",
                        row.get("channel_name", "") or "",
                        row.get("message_type", ""),
                        row.get("thread_id", "") or "",
                        row.get("reply_to_id", "") or "",
                        str(row.get("is_mention", "")),
                        str(row.get("has_attachment", "")),
                        row.get("classification", ""),
                        str(row.get("classification_confidence", "")),
                        row.get("classification_reason", "").replace('"', '""'),
                    ]
                    lines.append(",".join(f'"{v}"' for v in values))
                body = "\n".join(lines)
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "text/csv")
                self.end_headers()
                self.wfile.write(body.encode("utf-8"))
                return

            if path == "/new_ui.html":
                if not self._require_auth(params):
                    self._unauthorized()
                    return
                # Serve the static new_ui.html file
                html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "new_ui.html")
                try:
                    with open(html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    self.send_response(200)
                    self._cors()
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(html_content.encode("utf-8"))
                except FileNotFoundError:
                    self._send_json(404, {"error": "new_ui.html not found"})
                return

            if path == "/ui":
                if not self._require_auth(params):
                    self._unauthorized()
                    return
                token = (params.get("token") or [""])[0]
                page = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Universal Briefing</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
      background: linear-gradient(135deg, #f5f7fa 0%, #e8f0f7 100%);
      color: #1d1d1f;
      line-height: 1.5;
      padding: 0;
      margin: 0;
      min-height: 100vh;
    }

    .header {
      background: rgba(255, 255, 255, 0.8);
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      border-bottom: 1px solid rgba(0, 0, 0, 0.06);
      padding: 16px 24px;
      position: sticky;
      top: 0;
      z-index: 100;
    }

    .header-content {
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }

    .logo {
      font-size: 20px;
      font-weight: 600;
      color: #1d1d1f;
      letter-spacing: -0.5px;
    }

    .search-bar {
      flex: 1;
      max-width: 500px;
      position: relative;
    }

    .search-input {
      width: 100%;
      padding: 10px 16px 10px 40px;
      border: none;
      border-radius: 20px;
      background: rgba(142, 142, 147, 0.12);
      font-size: 15px;
      font-family: inherit;
      transition: all 0.2s ease;
    }

    .search-input:focus {
      outline: none;
      background: rgba(255, 255, 255, 0.9);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }

    .search-icon {
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      color: #86868b;
      font-size: 16px;
    }

    .status {
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 500;
      white-space: nowrap;
    }

    .status.loading {
      background: #C5E3F6;
      color: #0066CC;
    }

    .status.success {
      background: #B8E6D5;
      color: #00875A;
    }

    .status.error {
      background: #FFE4E1;
      color: #DE350B;
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px;
    }

    .filters {
      display: flex;
      gap: 8px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }

    .filter-btn {
      padding: 8px 16px;
      border: 1px solid rgba(0, 0, 0, 0.08);
      border-radius: 20px;
      background: white;
      font-size: 14px;
      font-family: inherit;
      cursor: pointer;
      transition: all 0.2s ease;
      font-weight: 500;
    }

    .filter-btn:hover {
      background: rgba(0, 0, 0, 0.03);
      border-color: rgba(0, 0, 0, 0.12);
    }

    .filter-btn.active {
      background: #007AFF;
      color: white;
      border-color: #007AFF;
    }

    .messages {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .message-card {
      background: white;
      border-radius: 16px;
      padding: 20px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
      transition: all 0.2s ease;
      position: relative;
      overflow: hidden;
    }

    .message-card:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      transform: translateY(-2px);
    }

    .message-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
    }

    .platform-badge {
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .platform-badge.email {
      background: linear-gradient(135deg, #B8E6D5 0%, #A5D9C8 100%);
      color: #00875A;
    }

    .platform-badge.telegram {
      background: linear-gradient(135deg, #C5E3F6 0%, #B3D4E8 100%);
      color: #0066CC;
    }

    .platform-badge.slack {
      background: linear-gradient(135deg, #F4E5FF 0%, #E6D3F7 100%);
      color: #6B2EB5;
    }

    .platform-badge.discord {
      background: linear-gradient(135deg, #E6E6FA 0%, #D8D8F6 100%);
      color: #5865F2;
    }

    .platform-badge.whatsapp {
      background: linear-gradient(135deg, #D4EDDA 0%, #C3E6CB 100%);
      color: #25D366;
    }

    .sender-name {
      font-weight: 600;
      font-size: 15px;
      color: #1d1d1f;
      flex: 1;
    }

    .timestamp {
      font-size: 13px;
      color: #86868b;
    }

    .message-subject {
      font-weight: 600;
      font-size: 16px;
      color: #1d1d1f;
      margin-bottom: 8px;
      line-height: 1.3;
    }

    .message-content {
      font-size: 14px;
      color: #424245;
      line-height: 1.6;
      white-space: pre-wrap;
      word-wrap: break-word;
    }

    .message-content.truncated {
      max-height: 100px;
      overflow: hidden;
      position: relative;
    }

    .message-content.truncated::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 40px;
      background: linear-gradient(transparent, white);
    }

    .show-more {
      margin-top: 12px;
      padding: 6px 12px;
      background: rgba(0, 0, 0, 0.04);
      border: none;
      border-radius: 12px;
      font-size: 13px;
      font-weight: 500;
      color: #007AFF;
      cursor: pointer;
      font-family: inherit;
      transition: all 0.2s ease;
    }

    .show-more:hover {
      background: rgba(0, 0, 0, 0.08);
    }

    .empty-state {
      text-align: center;
      padding: 60px 20px;
    }

    .empty-state-icon {
      font-size: 64px;
      margin-bottom: 16px;
      opacity: 0.3;
    }

    .empty-state-text {
      font-size: 18px;
      color: #86868b;
      font-weight: 500;
    }

    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 4px solid rgba(0, 122, 255, 0.2);
      border-top-color: #007AFF;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      margin: 40px auto;
    }

    @keyframes spin {{
      to {{ transform: rotate(360deg); }}
    }}

    @media (max-width: 768px) {
      .header-content {
        flex-direction: column;
        align-items: stretch;
      }

      .search-bar {
        max-width: none;
      }

      .container {
        padding: 16px;
      }

      .message-card {
        padding: 16px;
      }
    }
  </style>
</head>
<body>
  <div class="header">
    <div class="header-content">
      <div class="logo">📬 Universal Briefing</div>
      <div class="search-bar">
        <span class="search-icon">🔍</span>
        <input type="text" class="search-input" id="searchInput" placeholder="Search messages...">
      </div>
      <div class="status" id="status"></div>
    </div>
  </div>

  <div class="container">
    <div class="filters" id="filters">
      <button class="filter-btn active" data-platform="all">All Messages</button>
      <button class="filter-btn" data-platform="email">📧 Email</button>
      <button class="filter-btn" data-platform="telegram">💬 Telegram</button>
      <button class="filter-btn" data-platform="slack">💼 Slack</button>
      <button class="filter-btn" data-platform="discord">🎮 Discord</button>
      <button class="filter-btn" data-platform="whatsapp">📱 WhatsApp</button>
    </div>

    <div class="filters" id="classificationFilters" style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(0,0,0,0.08);">
      <span style="font-size: 13px; color: #86868b; font-weight: 500; margin-right: 12px;">Priority:</span>
      <button class="filter-btn classification-btn active" data-classification="all">All</button>
      <button class="filter-btn classification-btn" data-classification="urgent" style="background: #FFE4E1; color: #DE350B; border-color: #FFE4E1;">🔴 Urgent</button>
      <button class="filter-btn classification-btn" data-classification="fyi" style="background: #E3F2FD; color: #0066CC; border-color: #E3F2FD;">📘 FYI</button>
      <button class="filter-btn classification-btn" data-classification="noise" style="background: #F5F5F5; color: #666; border-color: #F5F5F5;">🔇 Noise</button>
    </div>

    <div class="messages" id="messages"></div>
  </div>

  <script>
    const API_BASE = window.location.origin;
    let allMessages = [];
    let activeFilter = 'all';
    let activeClassification = 'all';
    let searchQuery = '';

    function showStatus(text, type = 'loading') {
      const status = document.getElementById('status');
      status.textContent = text;
      status.className = `status ${type}`;
      status.style.display = text ? 'block' : 'none';

      if (type === 'success') {
        setTimeout(() => {
          status.style.display = 'none';
        }, 3000);
      }
    }

    function formatTimestamp(timestamp) {
      const date = new Date(timestamp);
      const now = new Date();
      const diff = now - date;
      const minutes = Math.floor(diff / 60000);
      const hours = Math.floor(diff / 3600000);
      const days = Math.floor(diff / 86400000);

      if (minutes < 1) return 'just now';
      if (minutes < 60) return `${minutes}m ago`;
      if (hours < 24) return `${hours}h ago`;
      if (days < 7) return `${days}d ago`;

      return date.toLocaleDateString();
    }

    function truncateContent(content, maxLength = 300) {
      if (content.length <= maxLength) return content;
      return content.substring(0, maxLength);
    }

    function highlightSearch(text, query) {
      if (!query) return text;
      const regex = new RegExp(`(${query})`, 'gi');
      return text.replace(regex, '<mark style="background: #FFEB3B; padding: 2px 4px; border-radius: 3px;">$1</mark>');
    }

    function renderMessages(messages) {
      const container = document.getElementById('messages');

      if (messages.length === 0) {
        container.innerHTML = `
          <div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <div class="empty-state-text">No messages found</div>
          </div>
        `;
        return;
      }

      container.innerHTML = messages.map(msg => {
        const content = truncateContent(msg.content);
        const needsTruncate = msg.content.length > 300;
        const displayContent = highlightSearch(content, searchQuery);

        return `
          <div class="message-card" data-id="${msg.id}">
            <div class="message-header">
              <span class="platform-badge ${msg.platform}">${msg.platform}</span>
              <span class="sender-name">${msg.sender_name}</span>
              <span class="timestamp">${formatTimestamp(msg.timestamp)}</span>
            </div>
            ${msg.channel_name ? `<div class="message-subject">${msg.channel_name}</div>` : ''}
            <div class="message-content ${needsTruncate ? 'truncated' : ''}" data-full="${needsTruncate}" id="content-${msg.id}">
              ${displayContent}
            </div>
            ${needsTruncate ? `<button class="show-more" onclick="toggleContent('${msg.id}')">Show More</button>` : ''}
          </div>
        `;
      }).join('');
    }

    function toggleContent(id) {
      const content = document.getElementById(`content-${id}`);
      const button = content.nextElementSibling;
      const message = allMessages.find(m => m.id === id);

      if (content.classList.contains('truncated')) {
        content.classList.remove('truncated');
        content.innerHTML = highlightSearch(message.content, searchQuery);
        button.textContent = 'Show Less';
      } else {
        content.classList.add('truncated');
        content.innerHTML = highlightSearch(truncateContent(message.content), searchQuery);
        button.textContent = 'Show More';
      }
    }

    function filterMessages() {
      let filtered = allMessages;

      // Filter by platform
      if (activeFilter !== 'all') {
        filtered = filtered.filter(m => m.platform === activeFilter);
      }

      // Filter by classification
      if (activeClassification !== 'all') {
        filtered = filtered.filter(m => m.classification === activeClassification);
      }

      // Filter by search
      if (searchQuery) {
        filtered = filtered.filter(m =>
          m.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
          m.sender_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (m.channel_name && m.channel_name.toLowerCase().includes(searchQuery.toLowerCase()))
        );
      }

      renderMessages(filtered);
      const classText = activeClassification !== 'all' ? ` (${activeClassification})` : '';
      showStatus(`${filtered.length} message${filtered.length === 1 ? '' : 's'}${classText}`, 'success');
    }

    async function loadAllMessages() {
      showStatus('Loading messages...', 'loading');
      allMessages = [];

      const platforms = ['email', 'telegram', 'slack', 'discord', 'whatsapp'];

      for (const platform of platforms) {
        try {
          const source = platform === 'email' || platform === 'slack' ? 'live' : 'store';
          const response = await fetch(`${API_BASE}/messages?platform=${platform}&source=${source}&hours=168&limit=100`);

          if (response.ok) {
            const data = await response.json();
            if (data.messages && data.messages.length > 0) {
              allMessages = allMessages.concat(data.messages);
            }
          }
        } catch (err) {
          console.error(`Error loading ${platform}:`, err);
        }
      }

      // Sort by timestamp (newest first)
      allMessages.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

      filterMessages();
    }

    // Event listeners
    document.getElementById('filters').addEventListener('click', (e) => {
      if (e.target.classList.contains('filter-btn') && !e.target.classList.contains('classification-btn')) {
        document.querySelectorAll('#filters .filter-btn:not(.classification-btn)').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        activeFilter = e.target.dataset.platform;
        filterMessages();
      }
    });

    document.getElementById('classificationFilters').addEventListener('click', (e) => {
      if (e.target.classList.contains('classification-btn')) {
        document.querySelectorAll('.classification-btn').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        activeClassification = e.target.dataset.classification;
        filterMessages();
      }
    });

    document.getElementById('searchInput').addEventListener('input', (e) => {
      searchQuery = e.target.value;
      filterMessages();
    });

    // Auto-load on page load
    window.addEventListener('DOMContentLoaded', () => {
      loadAllMessages();
    });
  </script>
</body>
</html>

"""
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(page.encode("utf-8"))
                return

            self._send_json(404, {"error": "not found"})

        def log_message(self, format, *args):  # noqa: A003
            return

        def do_OPTIONS(self):  # noqa: N802
            self.send_response(204)
            self._cors()
            self.end_headers()

    server = HTTPServer((host, port), ApiHandler)
    logger.info("Universal Briefing API listening on http://%s:%d", host, port)
    server.serve_forever()

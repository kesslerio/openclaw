"""
Claude CLI Proxy - Routes Anthropic API calls through Claude Code CLI.

Uses the Max plan authentication (no separate API credits needed).
Runs as a local HTTP server that mimics the Anthropic Messages API,
forwarding requests to `claude -p` under the hood.

Usage:
    python3 -m memex.api.claude_proxy
    # Runs on port 8766, then point ANTHROPIC_BASE_URL=http://localhost:8766
"""

import json
import subprocess
import time
import uuid
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

app = FastAPI(title="Claude CLI Proxy", version="1.0.0")


@app.get("/")
async def root():
    return {"status": "running", "proxy": "claude-cli", "plan": "max"}


@app.post("/v1/messages")
async def messages(request: Request):
    """
    Proxy for Anthropic Messages API.
    Accepts standard Anthropic request format, routes through claude CLI.
    """
    body = await request.json()

    model = body.get("model", "sonnet")
    max_tokens = body.get("max_tokens", 1024)
    temperature = body.get("temperature", 1.0)
    system_prompt = body.get("system", "")
    messages = body.get("messages", [])

    # Build the prompt from messages
    prompt_parts = []
    if system_prompt:
        prompt_parts.append(f"<system>\n{system_prompt}\n</system>\n")
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if isinstance(content, list):
            # Handle content blocks (text only for now)
            text_parts = [b["text"] for b in content if b.get("type") == "text"]
            content = "\n".join(text_parts)
        prompt_parts.append(content)

    full_prompt = "\n\n".join(prompt_parts)

    # Map model names to claude CLI aliases
    model_alias = "sonnet"
    if "opus" in model:
        model_alias = "opus"
    elif "haiku" in model:
        model_alias = "haiku"

    # Call claude CLI
    cmd = [
        "claude", "-p", full_prompt,
        "--model", model_alias,
        "--output-format", "json",
        "--no-session-persistence",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            logger.error(f"claude CLI error: {result.stderr}")
            return JSONResponse(
                status_code=500,
                content={
                    "type": "error",
                    "error": {
                        "type": "cli_error",
                        "message": f"Claude CLI failed: {result.stderr[:500]}",
                    },
                },
            )

        # Parse CLI JSON output
        try:
            cli_output = json.loads(result.stdout)
            response_text = cli_output.get("result", result.stdout)
        except json.JSONDecodeError:
            response_text = result.stdout.strip()

        # Return in Anthropic Messages API format
        msg_id = f"msg_{uuid.uuid4().hex[:24]}"
        return JSONResponse(content={
            "id": msg_id,
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": response_text,
                }
            ],
            "model": model,
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0,
            },
        })

    except subprocess.TimeoutExpired:
        return JSONResponse(
            status_code=504,
            content={
                "type": "error",
                "error": {"type": "timeout", "message": "Claude CLI timed out (120s)"},
            },
        )
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "type": "error",
                "error": {"type": "proxy_error", "message": str(e)},
            },
        )


if __name__ == "__main__":
    import uvicorn

    print("Starting Claude CLI Proxy on 0.0.0.0:8766")
    print("Routes Anthropic API calls through Claude Code (Max plan)")
    uvicorn.run(
        "memex.api.claude_proxy:app",
        host="0.0.0.0",
        port=8766,
        log_level="info",
    )

from __future__ import annotations

import json
import logging
import os
from typing import Any, List, Optional

# Try to load a .env file when python-dotenv is available (development convenience).
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    # dotenv is optional; ignore if not installed
    pass

logger = logging.getLogger(__name__)


def _extract_user_text(messages: List[dict[str, Any]]) -> str:
    # Best-effort extraction for fallback responses
    try:
        content = messages[-1]["content"]
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for c in content:
                if not isinstance(c, dict):
                    continue
                typ = c.get("type")
                if typ in {"text", "input_text"}:
                    parts.append(c.get("text", ""))
            return "\n".join(p for p in parts if p)
    except Exception:
        pass
    return "(no content)"


def respond(
    messages: List[dict[str, Any]],
    model: str = "gpt-5-nano",
    timeout: int = 30,
    instructions: Optional[str] = None,
    reasoning_effort: Optional[str] = None,
) -> str:
    """
    Call OpenAI Responses API with a messages payload. If OPENAI_API_KEY is not set or the
    SDK/network is unavailable, return a deterministic local fallback.
    """
    # Ensure the API key is available
    api_key = (os.getenv("OPENAI_API_KEY", "") or "").strip()
    if not api_key:
        user_text = _extract_user_text(messages)
        return f"[dev:fallback] {user_text}"

    # Normalize messages -> input payload
    last = messages[-1]
    content = last.get("content", "")
    if isinstance(content, str):
        input_payload = [
            {"role": "user", "content": [{"type": "input_text", "text": content}]}
        ]
    else:
        norm_content: list[dict[str, Any]] = []
        for c in content:
            if isinstance(c, dict) and c.get("type") == "text":
                cc = dict(c)
                cc["type"] = "input_text"
                norm_content.append(cc)
            else:
                norm_content.append(c)
        input_payload = [{"role": "user", "content": norm_content}]

    # Defaults from environment if not explicitly provided
    if instructions is None:
        instructions = os.getenv("OPENAI_INSTRUCTIONS") or None
    if reasoning_effort is None:
        reasoning_effort = os.getenv("OPENAI_REASONING_EFFORT") or None

    create_kwargs: dict[str, Any] = {
        "model": model,
        "input": input_payload,
        "timeout": timeout,
    }
    if instructions:
        create_kwargs["instructions"] = instructions
    if reasoning_effort:
        create_kwargs["reasoning"] = {"effort": reasoning_effort}

    # Try using the official SDK first. If unavailable or call fails, fall back to HTTP with Authorization header.
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        resp = client.responses.create(**create_kwargs)

        # Extract text
        if hasattr(resp, "output_text"):
            return resp.output_text
        return str(resp)
    except Exception as sdk_exc:
        # Log SDK import/call failure and try HTTP fallback
        logger.debug("OpenAI SDK unavailable or failed: %s", sdk_exc)

        try:
            import httpx

            url = "https://api.openai.com/v1/responses"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            # Create a JSON-safe body
            body = {k: v for k, v in create_kwargs.items() if v is not None}
            # httpx will handle timeout separately; remove it from JSON body
            timeout_val = body.pop("timeout", None)

            try:
                logger.debug("OpenAI HTTP request body: %s", json.dumps(body, ensure_ascii=False, default=str))
            except Exception:
                logger.debug("OpenAI HTTP request body (repr): %s", repr(body))

            # Issue the HTTP POST
            resp = httpx.post(url, headers=headers, json=body, timeout=timeout_val or 30)
            # Raise for HTTP errors to handle non-2xx
            resp.raise_for_status()
            data = resp.json()

            # Responses API may return 'output' with blocks or 'output_text'
            if isinstance(data, dict):
                # Prefer the SDK-like convenience field if present
                if "output_text" in data:
                    return data["output_text"]
                # Try to extract content text from output
                output = data.get("output")
                if isinstance(output, list) and output:
                    # join any text blocks
                    parts: list[str] = []
                    for item in output:
                        if isinstance(item, dict):
                            # often text is under 'content' or 'text'
                            cont = item.get("content") or item.get("text")
                            if isinstance(cont, str):
                                parts.append(cont)
                            elif isinstance(cont, list):
                                for b in cont:
                                    if isinstance(b, dict) and b.get("type") in {"output_text", "text"}:
                                        parts.append(b.get("text", ""))
                    if parts:
                        return "\n".join(p for p in parts if p)
                # Fallback: return whole response as string
                return json.dumps(data, ensure_ascii=False)
        except Exception as http_exc:
            logger.exception("HTTP fallback to OpenAI failed: %s", http_exc)

        # Final fallback for developer mode
        user_text = _extract_user_text(messages)
        return f"[fallback: error {type(sdk_exc).__name__}] {user_text}"

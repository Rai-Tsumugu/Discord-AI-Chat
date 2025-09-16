from __future__ import annotations

from typing import Any

from router import route
from services.openai_client import respond


def handle_text(message: Any, state: Any) -> str:
    # Example: use router for trivial commands; otherwise call LLM
    intent = route(message.content or "")
    if intent != "unknown command" and intent != "help":
        return intent

    messages = [{"role": "user", "content": message.content or ""}]
    return respond(messages=messages, model="gpt-5-nano")

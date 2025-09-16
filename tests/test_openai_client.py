import os

import pytest

from services.openai_client import respond


def test_respond_fallback_without_api_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    out = respond(
        messages=[{"role": "user", "content": "hello"}],
        model="gpt-5-nano",
        instructions="You are helpful.",
        reasoning_effort="low",
    )
    assert out == "[dev:fallback] hello"


def test_respond_fallback_with_image_content(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    content = [
        {"type": "text", "text": "describe this"},
        {"type": "input_image", "image_url": "https://example.com/img.png"},
    ]
    out = respond(messages=[{"role": "user", "content": content}], model="gpt-5-nano")
    # Fallback extracts only text blocks
    assert out == "[dev:fallback] describe this"


import pytest

from handlers.text import handle_text
from handlers.text_with_image import handle_text_with_image
from state import MemoryState


class Msg:
    def __init__(self, content: str, attachments=None):
        self.content = content
        self.attachments = attachments or []


def test_handle_text_uses_fallback_without_api_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    msg = Msg("hello world")
    out = handle_text(msg, MemoryState())
    assert out == "[dev:fallback] hello world"


def test_handle_text_with_image_url(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    out = handle_text_with_image("what is in this image?", "http://example.com/a.png")
    assert out == "[dev:fallback] what is in this image?"


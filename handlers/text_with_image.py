from __future__ import annotations

from typing import Optional

from services.image_utils import encode_base64, mime_type
from services.openai_client import respond


def _is_url(s: str) -> bool:
    return s.startswith("http://") or s.startswith("https://")


def handle_text_with_image(text: str, image_path_or_url: str) -> str:
    content: list[dict] = [{"type": "input_text", "text": text or ""}]

    if _is_url(image_path_or_url):
        content.append({"type": "input_image", "image_url": image_path_or_url})
    else:
        mt: Optional[str] = mime_type(image_path_or_url)
        image_b64 = encode_base64(image_path_or_url)
        content.append(
            {"type": "input_image", "image_data": image_b64, "mime_type": mt or "image/png"}
        )

    messages = [{"role": "user", "content": content}]
    return respond(messages=messages, model="gpt-5-nano")

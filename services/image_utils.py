from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional


SUPPORTED_EXT = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}


def is_supported_image(path: str) -> bool:
    p = Path(path)
    return p.suffix.lower() in SUPPORTED_EXT


def mime_type(path: str) -> Optional[str]:
    p = Path(path)
    return SUPPORTED_EXT.get(p.suffix.lower())


def encode_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


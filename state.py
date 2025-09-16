from time import time
from typing import Any, Optional


class MemoryState:
    def __init__(self, ttl_sec: Optional[int] | None = 600):
        self.ttl = ttl_sec
        self.store: dict[str, tuple[Any, Optional[float]]] = {}

    def get(self, key: str, default: Any | None = None):
        val = self.store.get(key)
        if not val:
            return default
        v, exp = val
        if self.ttl and exp and exp < time():
            self.store.pop(key, None)
            return default
        return v

    def set(self, key: str, value: Any):
        exp = time() + self.ttl if self.ttl else None
        self.store[key] = (value, exp)

    def clear(self, key: Optional[str] = None):
        return self.store.pop(key, None) if key else self.store.clear()


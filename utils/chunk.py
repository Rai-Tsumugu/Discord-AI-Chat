def chunk_2000(text: str, size: int = 2000) -> list[str]:
    if not text:
        return [""]
    return [text[i : i + size] for i in range(0, len(text), size)]


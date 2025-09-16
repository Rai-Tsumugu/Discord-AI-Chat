from utils.chunk import chunk_2000


def test_chunk_basic():
    text = "a" * 4500
    parts = chunk_2000(text)
    assert len(parts) == 3
    assert parts[0] == "a" * 2000
    assert parts[1] == "a" * 2000
    assert parts[2] == "a" * 500


def test_chunk_empty():
    assert chunk_2000("") == [""]


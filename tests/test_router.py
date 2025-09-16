from router import route


def test_route_ping():
    assert route("ping") == "pong"


def test_route_help():
    out = route("help")
    assert "Commands:" in out
    assert "ping" in out


def test_route_unknown():
    assert route("unknown") == "unknown command"


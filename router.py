from typing import Callable, Dict


Handlers: Dict[str, Callable[[str], str]] = {
    "ping": lambda _: "pong",
    "help": lambda _: (
        "Commands:\n"
        "- ping: healthcheck\n"
        "- help: show this help\n"
        "Just send a message (optionally with an image)."
    ),
}


def route(text: str) -> str:
    if not text or not text.strip():
        return "unknown command"
    cmd, *_ = text.strip().split(maxsplit=1)
    return Handlers.get(cmd.lower(), lambda _: "unknown command")(text)


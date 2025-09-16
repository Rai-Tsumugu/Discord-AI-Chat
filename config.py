import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

try:
    import tomllib  # type: ignore[attr-defined]

    def load_toml(path: str):
        with open(path, "rb") as f:
            return tomllib.load(f)
except Exception:  # pragma: no cover - fallback
    import toml as tomllib  # type: ignore

    def load_toml(path: str):
        return tomllib.load(path)


@dataclass
class Settings:
    openai_api_key: str
    discord_token: str
    log_level: str = "INFO"
    openai_instructions: str = ""
    openai_reasoning_effort: str = ""


def load_settings(path: str = "config/settings.toml") -> Settings:
    load_dotenv()
    data = load_toml(path) if Path(path).exists() else {}
    openai_api_key = (
        os.getenv("OPENAI_API_KEY", data.get("openai", {}).get("api_key", "")) or ""
    ).strip()
    discord_token = (
        os.getenv("DISCORD_BOT_TOKEN", data.get("discord", {}).get("token", "")) or ""
    ).strip()
    return Settings(
        openai_api_key=openai_api_key,
        discord_token=discord_token,
        log_level=os.getenv("LOG_LEVEL", data.get("logging", {}).get("level", "INFO")),
        openai_instructions=os.getenv(
            "OPENAI_INSTRUCTIONS", data.get("openai", {}).get("instructions", "")
        ),
        openai_reasoning_effort=os.getenv(
            "OPENAI_REASONING_EFFORT", data.get("openai", {}).get("reasoning_effort", "")
        ),
    )

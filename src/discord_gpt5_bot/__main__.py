import asyncio
import os
import logging
import logging.config
from pathlib import Path

import yaml

from config import load_settings
from core.discord_client import create_client


def setup_logging():
    path = Path("logging.yaml")
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            logging.config.dictConfig(yaml.safe_load(f))
    else:  # pragma: no cover - fallback
        logging.basicConfig(level=logging.INFO)


async def amain():
    settings = load_settings()
    setup_logging()
    # Validate Discord token early to provide a clear error instead of 401 later
    token = (settings.discord_token or "").strip()
    if not token:
        logging.error("DISCORD_BOT_TOKEN is empty. Set it in .env or config/settings.toml.")
        return
    if len(token) < 30:
        logging.error("DISCORD_BOT_TOKEN looks invalid (too short). Please regenerate and set it.")
        return
    # Propagate optional OpenAI controls to env for the client
    if settings.openai_instructions:
        os.environ.setdefault("OPENAI_INSTRUCTIONS", settings.openai_instructions)
    if settings.openai_reasoning_effort:
        os.environ.setdefault("OPENAI_REASONING_EFFORT", settings.openai_reasoning_effort)
    # Ensure OpenAI key from TOML is visible to SDK if not provided via env
    if settings.openai_api_key:
        os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
    bot = create_client(settings)
    await bot.load_extension("cogs.admin")
    await bot.start(token)


if __name__ == "__main__":
    asyncio.run(amain())

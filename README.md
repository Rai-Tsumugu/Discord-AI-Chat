# discord-gpt5-bot

Discord bot that accepts text or text+image and replies with text, using OpenAI Responses API. Structured for small, maintainable extensions and easy local dev.

## Features
- Text and text+image input → text output
- Router-based command dispatch (`ping`, `help`)
- Simple in-memory session state
- Clean separation: core, handlers, services, utils, cogs
- Config via `.env` and `config/settings.toml`
- Logging via `logging.yaml`

## Quickstart
1. Create and activate venv, then install:
   - Editable install: `pip install -e .[dev]`
   - Or: `pip install -r requirements.txt`
2. Copy config template and set secrets:
   - Windows: `copy config\settings.example.toml config\settings.toml`
   - Unix: `cp config/settings.example.toml config/settings.toml`
   - Fill `.env` from `.env.example` (`OPENAI_API_KEY`, `DISCORD_BOT_TOKEN`, optional `OPENAI_INSTRUCTIONS`, `OPENAI_REASONING_EFFORT`)
3. Run:
   - `python -m discord_gpt5_bot`
   - Dev helper: `bash scripts/run_dev.sh`

## Structure
```
.
  .env.example
  README.md
  pyproject.toml
  requirements.txt
  format.sh
  logging.yaml
  config.py
  router.py
  state.py
  services/
    openai_client.py
    image_utils.py
  handlers/
    text.py
    text_with_image.py
  cogs/
    admin.py
  utils/
    chunk.py
  config/
    settings.example.toml
  scripts/
    run_dev.sh
  src/
    discord_gpt5_bot/
      __main__.py
  tests/
    test_chunk.py
    test_router.py
  Dockerfile (optional)
```

## Notes
- Tests mock external I/O. Core tests cover router and chunking.
- If `OPENAI_API_KEY` is missing, the OpenAI client returns a safe fallback string for local dev.
- You can control the Responses API with:
  - `OPENAI_INSTRUCTIONS`: system instructions string
  - `OPENAI_REASONING_EFFORT`: e.g. `low`, `medium`, `high` (passed as `{reasoning: {effort: ...}}`)

## Troubleshooting
- 401 Unauthorized / LoginFailure: Improper token has been passed.
  - Ensure `DISCORD_BOT_TOKEN` is a valid Bot Token from Discord Developer Portal → Bot → Reset Token.
  - Save it in `.env` as `DISCORD_BOT_TOKEN=your_token_here` (no surrounding quotes or spaces).
  - Verify `.env` is in the project root and re-run the app.
  - In the Portal, enable the Message Content Intent (Bot → Privileged Gateway Intents) to receive message content.
- Keep handlers thin; move logic into `core/` or `services/` when complexity grows.

# Repository Guidelines

## Project Structure & Module Organization
- `src/discord_gpt5_bot/`: App package. Place `__main__.py` to run via `python -m discord_gpt5_bot`.
- `tests/`: Unit/integration tests mirroring `src/` (e.g., `tests/test_main.py`).
- `scripts/`: Dev helpers (e.g., `run_dev.sh`).
- `config/`: Environment-specific settings templates (e.g., `settings.example.toml`).
- Root files: `.env.example`, `README.md`, `pyproject.toml`, `requirements.txt`, `format.sh`, `logging.yaml`, `config.py`.

## Project Skeleton (discord-gpt5-bot)
```
discord-gpt5-bot/
  .env.example
  README.md
  pyproject.toml
  requirements.txt
  format.sh  # フォーマットリンタ
  router.py  # メッセージハンドラ振り分け
  state.py   # 簡易セッション（メモリ）
  config.py  # env+tomlの読み込み
  scripts/
    run_dev.sh  # 開発起動
  services/
    openai_client.py  # OpenAI呼び出し（Responses API）
    image_utils.py    # 画像判定・変換（base64 等）
  handlers/
    text.py           # テキストのみ
    text_with_image.py# テキスト画像入力
  cogs/               # Slash/管理系の拡張置き場
    admin.py
  utils/
    chunk.py          # 2000字分割
  core/
    discord_client.py  # Client生成・イベント登録
  src/
    discord_gpt5_bot/
      __main__.py
```

### Additional Skeleton Items
```
tests/
  test_chunk.py
  test_router.py
Dockerfile  # 任意
```

### App Entrypoint (src/bot variant)
```
src/
  bot/
    __init__.py
    main.py  # エントリーポイント
```
- Run: `python -m bot` または `python src/bot/main.py`

### Main Entrypoint（main.py）
- 役割: 起動。設定読込→ロギング初期化→Discordクライアント生成→イベントループ開始。
- 配置: `src/bot/main.py`（または `src/discord_gpt5_bot/__main__.py`）。
- 最小例:
  ```python
  import asyncio, yaml, logging.config
  from config import load_settings
  from core.discord_client import create_client

  def setup_logging():
      with open('logging.yaml', 'r', encoding='utf-8') as f:
          logging.config.dictConfig(yaml.safe_load(f))

  async def amain():
      settings = load_settings()
      setup_logging()
      bot = create_client(settings)
      await bot.load_extension('cogs.admin')
      await bot.start(settings.discord_token)

  if __name__ == '__main__':
      asyncio.run(amain())
  ```

### Discord Client (core)
- 役割: Discordクライアントの生成とイベント登録を集中管理。
- 配置: `core/discord_client.py`
- 例: `from core.discord_client import create_client` → `client = create_client(settings)`
- メモ: 分離を徹底する場合は `adapters/discord/` に置く選択も可。

### Message Router
- 役割: 受信メッセージ→コマンド/意図に応じたハンドラへ振り分け。
- 配置: `router.py`（または `src/bot/router.py`）。
- 例:
  ```python
  from typing import Callable, Dict

  Handlers: Dict[str, Callable[[str], str]] = {
      'ping': lambda _: 'pong',
      'help': lambda _: 'usage...'
  }

  def route(text: str) -> str:
      cmd, *_ = text.strip().split(maxsplit=1)
      return Handlers.get(cmd, lambda _: 'unknown command')(text)
  ```

### Session State
- 役割: ユーザー/チャンネル単位の簡易セッション管理（メモリ）。
- 配置: `state.py`（または `src/bot/state.py`）。
- 例:
  ```python
  from time import time

  class MemoryState:
      def __init__(self, ttl_sec: int | None = 600):
          self.ttl = ttl_sec
          self.store = {}  # key -> (value, expires_at)

      def get(self, key, default=None):
          val = self.store.get(key)
          if not val:
              return default
          v, exp = val
          if self.ttl and exp and exp < time():
              self.store.pop(key, None)
              return default
          return v

      def set(self, key, value):
          exp = time() + self.ttl if self.ttl else None
          self.store[key] = (value, exp)

      def clear(self, key=None):
          return self.store.pop(key, None) if key else self.store.clear()
  ```
  使用例: `state.set(f"session:{user_id}", {...}); state.get(f"session:{user_id}")`

### Services
- 役割: OpenAI呼び出しや画像ユーティリティなど外部サービス連携を集約。
- 配置: `services/openai_client.py`, `services/image_utils.py`
- 例（Responses API）:
  ```python
  from services.openai_client import respond
  reply = respond(messages=[{"role":"user","content":"hello"}], model="gpt-4.1-mini")
  ```
- 例（画像ユーティリティ）: `encode_base64(path)`, `is_supported_image(path)`

### Handlers
- 役割: 入力種別ごとのオーケストレーション。ビジネスロジックは `core` に寄せる。
- 配置: `handlers/text.py`
- 例:
  ```python
  from router import route
  from services.openai_client import respond

  def handle_text(message, state):
      intent = route(message.content)
      return respond(messages=[{"role":"user","content": message.content}], model="gpt-4.1-mini")
  ```

- 画像付きテキスト:
  ```python
  from services.openai_client import respond
  from services.image_utils import encode_base64

  def handle_text_with_image(text: str, image_path: str):
      b64 = encode_base64(image_path)
      content = [
          {"type": "text", "text": text},
          {"type": "input_image", "image_data": b64, "mime_type": "image/png"},
      ]
      return respond(messages=[{"role": "user", "content": content}], model="gpt-4.1-mini")
  ```

### Cogs
- 役割: Slash コマンドや管理系機能を拡張として分離。
- 配置: `cogs/`（例: `cogs/admin.py`）。
- 例（discord.py v2）:
  ```python
  from discord.ext import commands
  from discord import app_commands

  class Admin(commands.Cog):
      def __init__(self, bot: commands.Bot):
          self.bot = bot

      @app_commands.command(name="ping")
      async def ping(self, interaction):
          await interaction.response.send_message("pong")

  async def setup(bot: commands.Bot):
      await bot.add_cog(Admin(bot))
  ```
- 読み込み: 起動時に `await bot.load_extension("cogs.admin")`（または自動探索）。

### Utils
- 役割: 共通ユーティリティの集約。Discord の 2000 文字制限に合わせた分割など。
- 配置: `utils/chunk.py`
- 例（2000 文字分割）:
  ```python
  def chunk_2000(text: str, size: int = 2000) -> list[str]:
      return [text[i:i+size] for i in range(0, len(text), size)]

  # 送信例（discord.py）
  for part in chunk_2000(reply):
      await channel.send(part)
  ```

## Build, Test, and Development Commands
- Setup: `python -m venv .venv && .\.venv\Scripts\Activate.ps1 && pip install -e .[dev]`
- Setup (pip派): `python -m venv .venv && .\.venv\Scripts\Activate.ps1 && pip install -r requirements.txt`
- Run: `python -m discord_gpt5_bot`
- Dev run: `bash scripts/run_dev.sh`
- Test/Format: `pytest -q` / `bash format.sh` (e.g., `ruff check . && ruff format .`)

## Docker (Optional)
- Build: `docker build -t discord-gpt5-bot .`
- Run: `docker run --rm --env-file .env discord-gpt5-bot`
- Dev mount: `docker run --rm -v "$PWD":/app -w /app --env-file .env discord-gpt5-bot`

## Coding Style & Naming Conventions
- Indentation: 4 spaces; max line length 100.
- Names: `snake_case` for functions/vars; `PascalCase` for classes.
- Tools: `ruff` for lint/format; optionally `black`/`isort`.

## Testing Guidelines
- Framework: `pytest`; file pattern `tests/test_*.py`.
- Coverage: target >= 80%; mock external I/O (OpenAI, Discord, network).
- Run: `pytest -q`; keep tests deterministic and fast.

## Commit & Pull Request Guidelines
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`). Small, focused changes.
- PRs: description, linked issues, screenshots/CLI logs if relevant, and a test plan.

## Security & Configuration Tips
- Secrets: use `.env` (`OPENAI_API_KEY`, `DISCORD_BOT_TOKEN`); never commit secrets.
- Robustness: validate inputs; implement retries/backoff and timeout handling for API calls.
 - Config templates: use `config/settings.example.toml` per environment. Copy to `config/settings.toml` and adjust.
   - Windows: `copy config\\settings.example.toml config\\settings.toml`
   - Unix: `cp config/settings.example.toml config/settings.toml`

### Configuration Loader
- 役割: `.env` と `config/settings.toml` を読み込み、環境変数で上書きした設定を提供。
- 配置: `config.py`
- 例:
  ```python
  import os
  from dataclasses import dataclass
  from pathlib import Path
  from dotenv import load_dotenv
  try:
      import tomllib  # Python 3.11+
      def load_toml(path):
          with open(path, 'rb') as f:
              return tomllib.load(f)
  except Exception:
      import toml as tomllib
      def load_toml(path):
          return tomllib.load(path)

  @dataclass
  class Settings:
      openai_api_key: str
      discord_token: str
      log_level: str = 'INFO'

  def load_settings(path: str = 'config/settings.toml') -> Settings:
      load_dotenv()
      data = load_toml(path) if Path(path).exists() else {}
      return Settings(
          openai_api_key=os.getenv('OPENAI_API_KEY', data.get('openai', {}).get('api_key', '')),
          discord_token=os.getenv('DISCORD_BOT_TOKEN', data.get('discord', {}).get('token', '')),
          log_level=os.getenv('LOG_LEVEL', data.get('logging', {}).get('level', 'INFO')),
      )
  ```
  使用例: `from config import load_settings; settings = load_settings()`

## Minimal Split for Solo Dev（個人開発で拡張しやすい最小分割）
- `core/`: ドメインロジック（純粋関数）。外部依存なし。
- `adapters/`: OpenAI/Discord/HTTP/DB/FS などの接続層。
- `features/`: 機能単位のユースケース統合（例: chat, embeddings）。
- `cli/`: エントリポイント。`features` を呼び出すのみ。
- `configs/`: `.env` と設定スキーマ。
- `tests/`: `tests/core/` と `tests/features/` をミラー配置。外部はモック。
- 依存方向: `cli -> features -> (core, adapters)` の一方通行。逆依存なし。

## Logging
- File: `logging.yaml`（handlers/formatters/levels を定義）。
- Load (Python):
  ```python
  import yaml, logging.config
  with open('logging.yaml', 'r', encoding='utf-8') as f:
      logging.config.dictConfig(yaml.safe_load(f))
  ```
- Tips: `LOG_LEVEL` などは `.env` から読み込み、YAML の `level` を上書き。
- Per-env: `config/settings.toml` の値でログ出力先や詳細度を切替。

### 役割と拡張ポイント
- `router.py`: メッセージ→意図/コマンドへの振り分け。拡張: マップ/パーサに新コマンドを追加。
- `handlers/`: 入力種別ごとの実行制御。拡張: `text_with_image.py` のように新ハンドラを追加。
- `services/openai_client.py`: OpenAI 呼び出しの集約。拡張: モデル切替、ストリーミング、リトライ/バックオフの共通化。
- `services/image_utils.py`: 画像変換/判定。拡張: URL入力対応、MIME 自動判定、サイズ最適化。
- `core/discord_client.py`: Client 生成とイベント登録。拡張: Gateway Intents 追加、Cog 自動ロード。
- `cogs/`: Slash/管理機能の拡張置き場。拡張: `cogs/<name>.py` を作成し `load_extension` で読み込み。
- `state.py`: 簡易メモリセッション。拡張: `adapters/state/redis.py` など外部ストアへ差し替え。
- `config.py` + `config/settings.toml`: 設定の単一読み出し点。拡張: 新キー追加と `.env` での上書き。
- `logging.yaml`: ハンドラ/フォーマッタ定義。拡張: JSON 出力、レベル・出力先の環境別切替。
- `utils/chunk.py`: 送信テキスト分割。拡張: 埋め込み/添付に応じた分割戦略。
- `tests/`: 入口ごとに単体/結合テスト。拡張: OpenAI/Discord をモックし、失敗系（タイムアウト・レート制限）も網羅。

### 設計方針（拡張は最小限、ロジックは下層へ）
- cogs/handlers は入出力とオーケストレーションのみ。分岐・検証・再試行は `core`/`services`/`features` に移す。
- 薄い拡張: コマンド定義や配線は最小限に保ち、共通処理はユーティリティ化。
- テストは `core`/`features` を中心に。cogs/handlers は結合テストで最小確認。

## 指示: Discord Bot（テキスト+画像入力→テキスト出力）
- 入力: ユーザーのテキスト + 任意で画像1枚（添付/パス/URL）。
- 出力: テキストのみ（画像・埋め込みは返さない）。
- 主要フロー: `on_message` → `router.route` →
  - 画像あり: `handlers/text_with_image.handle_text_with_image(text, image_path)`
  - 画像なし: `handlers/text.handle_text(message, state)`
- OpenAI 呼び出し: `services/openai_client.respond` に text と `input_image`（base64 or URL）を渡す。既定モデル例: `gpt-4.1-mini`。
- 送信: 応答テキストは `utils/chunk.chunk_2000` で分割し順次送信。
- 例（疑似コード）:
  ```python
  if message.attachments:
      path_or_url = message.attachments[0].url
      reply = handle_text_with_image(message.content, path_or_url)
  else:
      reply = handle_text(message, state)
  for part in chunk_2000(reply):
      await channel.send(part)
  ```
- 留意点: 対応画像は PNG/JPEG を想定。サイズ大の画像は縮小/圧縮推奨。API エラー時はリトライ/フォールバック文面を返す。

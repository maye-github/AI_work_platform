"""環境設定。host/port は環境変数から取得する（ASM-105 / Q-107）。"""
from __future__ import annotations

import os


class Settings:
    host: str = os.getenv("R60_HOST", "localhost")
    port: str = os.getenv("R60_PORT", "8080")
    session_ttl_minutes: int = int(os.getenv("R60_SESSION_TTL_MIN", "30"))


settings = Settings()

"""Session ストア（模擬）。本番はサーバ側 Session に置き換える。"""
from __future__ import annotations

import time

from .config import settings

_STORE: dict[str, dict] = {}
_EXPIRES: dict[str, float] = {}


def save(session_id: str, user_info: dict) -> None:
    _STORE[session_id] = dict(user_info)
    _EXPIRES[session_id] = time.time() + settings.session_ttl_minutes * 60


def load(session_id: str) -> dict | None:
    if _EXPIRES.get(session_id, 0) < time.time():
        _STORE.pop(session_id, None)
        _EXPIRES.pop(session_id, None)
        return None
    return _STORE.get(session_id)

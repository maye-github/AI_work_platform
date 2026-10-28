"""L-115 確認メッセージと終了。"""
from __future__ import annotations

from ..core.errors import resolve


def confirm_close() -> dict:
    e = resolve("E-110")
    return {"messageId": e["message_id"], "message": e["message"], "close": True}

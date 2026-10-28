"""応答外形（errorCode 必須）。"""
from __future__ import annotations


def ok(**data) -> dict:
    return {"errorCode": "0", **data}


def err(code: str, message_id: str | None = None) -> dict:
    out = {"errorCode": code}
    if message_id:
        out["messageId"] = message_id
    return out

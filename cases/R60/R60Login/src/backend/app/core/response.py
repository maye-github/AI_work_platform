"""応答の外形を 1 箇所に集約する（errorCode を必ず含める）。"""
from __future__ import annotations


def ok(payload: dict | None = None) -> dict:
    body: dict = {"errorCode": "0"}
    if payload:
        body.update(payload)
    return body


def err(code: str, message: str | None = None) -> dict:
    body: dict = {"errorCode": code}
    if message:
        body["message"] = message
    return body

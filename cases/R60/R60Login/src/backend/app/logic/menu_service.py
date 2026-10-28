"""L-112 メニュー遷移。"""
from __future__ import annotations


def menu_redirect(startup_kbn: str) -> dict:
    return {"screenId": "MENU", "startupKbn": startup_kbn}

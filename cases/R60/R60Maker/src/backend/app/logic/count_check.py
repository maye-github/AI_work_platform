"""L-203 件数取得と上限判定（設計書 5.2-3）。"""
from __future__ import annotations


def check_count(count: int, upper_limit: int) -> str | None:
    """0 件は E-203、上限超過は E-204。問題なければ None。"""
    if count <= 0:
        return "E-203"
    if count > upper_limit:
        return "E-204"
    return None

"""L-204 ソートの白名单（設計書 5.2-5）。

指定できるのは MAKER_CD / MAKER_NM の 2 つだけ。白名单外は既定順に戻す。
"""
from __future__ import annotations

ALLOWED = {"MAKER_CD", "MAKER_NM"}
DEFAULT_ORDER = "DEL_FLG ASC, MAKER_CD ASC"


def build_order_by(field: str | None, descending: bool = False) -> str:
    key = (field or "").upper()
    if key in ALLOWED:
        direction = "DESC" if descending else "ASC"
        return f"DEL_FLG ASC, {key} {direction}, MAKER_CD ASC"
    return DEFAULT_ORDER

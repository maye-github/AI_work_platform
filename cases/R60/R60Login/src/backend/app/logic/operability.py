"""L-107 稼働状態チェック（3 端点の前処理）。"""
from __future__ import annotations

from ..core.errors import BizError


def ensure_online(online_flg: str | None) -> None:
    """オンライン可（Y）でなければ業務エラー E-103。"""
    if (online_flg or "").upper() != "Y":
        raise BizError("E-103")

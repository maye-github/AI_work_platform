"""L-114 稼働状態判定（3 端点のサーバ側前処理）。"""
from __future__ import annotations

from ..repository.masters import operation_repo


def is_online(sys_id: str = "R60") -> bool:
    row = operation_repo.get(sys_id)
    return bool(row) and row.get("ONLINE_FLG") == "1"

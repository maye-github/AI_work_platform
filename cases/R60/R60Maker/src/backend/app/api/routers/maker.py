"""R60Maker の端点（本版は検索系のみ実装）。"""
from __future__ import annotations

from fastapi import APIRouter

from ...core.response import err, ok
from ...logic.count_check import check_count
from ...logic.search_condition import (build_where, validate_maker_cd,
                                       validate_maker_nm)
from ...logic.sort_whitelist import build_order_by

router = APIRouter(prefix="/R60Maker", tags=["R60Maker"])

UPPER_LIMIT = 3000     # 設計書の例。実値は Q-203 で確認中


@router.post("/init")
def init(body: dict | None = None) -> dict:
    """初期表示：ユーザ情報・メッセージ・頁件数候補（本版は候補のみ空で返す）。"""
    return ok({"userInfo": {}, "messages": [], "pageSizeList": []})


@router.post("/search")
def search(body: dict) -> dict:
    """条件検索。実際の SQL 実行は repository 層（本版は未接続）。"""
    p = (body or {}).get("params") or {}
    code, name = p.get("makerCd") or "", p.get("makerNm") or ""
    bad = validate_maker_cd(code) or validate_maker_nm(name)
    if bad:
        from ...core.errors import resolve
        r = resolve(bad)
        return err(r["code"], r["message"])
    where, params = build_where(code, name, bool(p.get("includeDeleted")),
                                bool(p.get("pendingOnly")))
    order = build_order_by(p.get("sortField"), bool(p.get("sortDesc")))
    return ok({"where": where.strip(), "params": params, "orderBy": order,
               "rows": [], "count": 0})

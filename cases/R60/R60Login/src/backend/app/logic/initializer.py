"""L-101 初期表示データ取得 / L-102 候補整形 / L-103 初期値設定。"""
from __future__ import annotations

from ..repository.masters import kbn_list, screen_list


def fetch_init_data() -> dict:
    return {"pageList": screen_list(), "kbnList": kbn_list()}


def normalize_candidates(data: dict) -> dict:
    pages = [{"value": s["GMN_ID"], "label": s["GMN_NM"]}
             for s in data.get("pageList", [])]
    return {"pageList": pages, "kbnList": data.get("kbnList", [])}


def build_initial_values(data: dict) -> dict:
    pages = data.get("pageList", [])
    kbns = data.get("kbnList", [])
    return {
        "title": "共通マスタ　ログイン",
        "userId": "",
        "startupKbn": "3",
        "screen": pages[0]["value"] if pages else None,
        "authorityKbn": kbns[0]["value"] if kbns else "Y",
        "url": "",
    }

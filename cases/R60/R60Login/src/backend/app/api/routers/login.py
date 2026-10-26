"""R60Login の 3 端点。POST のみ。4 本目を足さない。"""
from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends

from ...core.config import settings
from ...core.errors import resolve
from ...core.response import err, ok
from ...logic.operability import ensure_online
from ...logic.stmt_cipher import decrypt, encrypt
from ...logic.url_builder import build_url
from ...logic.validate import validate_stf_cd
from ...repository import masters

router = APIRouter(prefix="/R60Login", tags=["R60Login"])

_KBN_LIST = [{"value": "Y", "label": "更新あり"}, {"value": "N", "label": "更新なし"}]


def _ymd() -> str:
    """当日鍵の材料。サーバ時刻（Asia/Tokyo）から作る。"""
    return dt.datetime.now().strftime("%Y%m%d")


def get_online_flg() -> str:
    """稼働状態（暫定: 常に Y。実装では repository から取得する）。"""
    return "Y"


def get_page_rows() -> list:
    """画面マスタの取得（暫定: 空。実装では repository で SELECT する）。"""
    return []


@router.post("/init")
def init(online_flg: str = Depends(get_online_flg)) -> dict:
    ensure_online(online_flg)
    try:
        pages = [masters.map_page(r) for r in get_page_rows()]
    except Exception:
        r = resolve("E-104")
        return err(r["code"], r["message"])
    return ok({"pageList": pages, "kbnList": _KBN_LIST})


@router.post("/login")
def login(body: dict, online_flg: str = Depends(get_online_flg)) -> dict:
    ensure_online(online_flg)
    params = (body or {}).get("params") or {}
    try:
        stf_cd = decrypt(params.get("stfCd") or "", _ymd())
    except Exception:
        r = resolve("E-105")
        return err(r["code"], r["message"])
    bad = validate_stf_cd(stf_cd)
    if bad:
        r = resolve(bad)
        return err(r["code"], r["message"])
    # 実装: repository で存在確認。該当なしは errorCode "1" のみ返す（顧客要求 §4.3）
    return err("1", resolve("E-102")["message"])


@router.post("/generateUrl")
def generate_url(body: dict, online_flg: str = Depends(get_online_flg)) -> dict:
    ensure_online(online_flg)
    params = (body or {}).get("params") or {}
    stf_cd = params.get("stfCd") or "NaN"      # 未入力は "NaN" を社員コードとして扱う（§4.4）
    bad = validate_stf_cd(stf_cd)
    if bad:
        r = resolve(bad)
        return err(r["code"], r["message"])
    enc = encrypt(stf_cd, _ymd())
    url = build_url(settings.url_scheme, settings.url_host, settings.url_port,
                    settings.url_context, settings.url_route,
                    enc, str(params.get("stfKbn") or "3"),
                    str(params.get("gmnId") or ""), str(params.get("kgnKbn") or "Y"))
    return ok({"url": url})

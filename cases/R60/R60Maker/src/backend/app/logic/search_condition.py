"""L-201 検索条件チェック / L-202 WHERE 生成。

設計書 5.2-1/5.2-2 のとおり。**値は必ずバインド変数で渡す**（文字列連結しない）。
"""
from __future__ import annotations

import re

_CODE = re.compile(r"^[0-9A-Za-z]{5}$")
_FORBIDDEN = set("\u0000\u0001<>\"'%;")

# 名称の桁数は「Byte」。UTF-8 で数えているが、業務の文字コードは標準仕様待ち（Q-207/ISS-201）。
NAME_BYTES = 30
NAME_ENCODING = "utf-8"


def validate_maker_cd(value: str | None) -> str | None:
    """空は許容（条件なし）。値があるときは半角英数字 5 文字。"""
    if not value:
        return None
    return None if _CODE.match(value) else "E-201"


def validate_maker_nm(value: str | None) -> str | None:
    """空は許容。値があるときは 30Byte 以内・禁止文字なし。"""
    if not value:
        return None
    if any(ch in _FORBIDDEN for ch in value):
        return "E-202"
    try:
        size = len(value.encode(NAME_ENCODING))
    except UnicodeEncodeError:
        return "E-202"
    return None if size <= NAME_BYTES else "E-202"


def build_where(code: str | None, name: str | None, include_deleted: bool,
                pending_only: bool) -> tuple[str, dict]:
    """(WHERE 句, バインド値) を返す。条件が無ければ空文字。"""
    conds: list[str] = []
    params: dict = {}
    if code:
        conds.append("MAKER_CD LIKE :maker_cd")          # 前方一致
        params["maker_cd"] = code + "%"
    if name:
        conds.append("MAKER_NM LIKE :maker_nm ESCAPE '\\'")   # 中間一致
        params["maker_nm"] = "%" + name + "%"
    if not include_deleted:
        conds.append("DEL_FLG = '0'")
    if pending_only:
        conds.append("REG_STS = '0'")
    return (" WHERE " + " AND ".join(conds)) if conds else "", params

"""L-104 ユーザーＩＤチェック / L-105 起動区分チェック。"""
from __future__ import annotations

import re

_USER_ID = re.compile(r"^[0-9]{7}$")


def validate_user_id(user_id: str) -> str | None:
    """妥当なら None、不可なら E-101 / E-102 を返す。"""
    if not user_id:
        return "E-101"
    if not _USER_ID.fullmatch(user_id):
        return "E-102"
    return None


def validate_startup_kbn(kbn: str) -> str | None:
    """1／2／3 以外は E-103（Q-110）。"""
    if kbn not in ("1", "2", "3"):
        return "E-103"
    return None

"""L-102 入力チェック：社員コードは必須かつ半角数字 7 桁。"""
from __future__ import annotations

import re

_PATTERN = re.compile(r"^[0-9]{7}$")


def validate_stf_cd(value: str | None) -> str | None:
    """妥当なら None、不正なら E-ID を返す。"""
    if not value:
        return "E-101"
    if not _PATTERN.match(value):
        return "E-101"
    return None

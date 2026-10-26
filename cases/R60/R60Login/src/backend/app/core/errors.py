"""エラー区分とコード解決。E-ID を唯一の出所にする（設計 ERR と 1 対 1）。"""
from __future__ import annotations

from dataclasses import dataclass

# 暫定の区分値（ISS-101。顧客の標準規約が来たらここだけ差し替える）
CODE_OK = "0"
CODE_BIZ = "1"
CODE_SYS = "9"

_MESSAGES: dict[str, str] = {
    "E-101": "ユーザーＩＤは半角7桁で入力してください。",
    "E-102": "入力された社員コードではログインできません。",
    "E-103": "ただいまオンライン利用できません。時間をおいて再度お試しください。",
    "E-104": "システムエラーが発生しました。",
    "E-105": "入力された社員コードではログインできません。",
}


@dataclass(frozen=True)
class BizError(Exception):
    """業務エラー（利用者に文言を見せる）。"""

    error_id: str


class SysError(Exception):
    """システムエラー（汎用文言のみ返す）。"""


def resolve(error_id: str) -> dict:
    """E-ID から応答用のコードと文言を返す。未知の ID はシステムエラーに倒す。"""
    if error_id not in _MESSAGES:
        return {"code": CODE_SYS, "message": _MESSAGES["E-104"]}
    code = CODE_SYS if error_id == "E-104" else CODE_BIZ
    return {"code": code, "message": _MESSAGES[error_id]}

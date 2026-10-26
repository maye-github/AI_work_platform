"""E-ID からコードと文言を解決する（設計 ERR と 1 対 1）。"""
from __future__ import annotations

CODE_OK = "0"
CODE_BIZ = "1"
CODE_SYS = "9"

_MESSAGES = {
    "E-201": "メーカーコードは半角英数字5文字で入力してください。",
    "E-202": "メーカー日本語名は30バイト以内で入力してください。",
    "E-203": "該当するデータがありません。",
    "E-204": "件数が上限を超えました。条件を絞ってください。",
    "E-205": "同じメーカーコードが既に登録されています。",
    "E-206": "参照されているため削除できません。",
    "E-207": "他の利用者が更新しました。再検索してやり直してください。",
}


def resolve(error_id: str) -> dict:
    if error_id not in _MESSAGES:
        return {"code": CODE_SYS, "message": "システムエラーが発生しました。"}
    return {"code": CODE_BIZ, "message": _MESSAGES[error_id]}

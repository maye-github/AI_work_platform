"""エラー定義（E-101〜E-111）。message は利用者に見せる業務の言葉。"""
from __future__ import annotations

ERRORS: dict[str, dict] = {
    "E-101": {"code": "1", "message_id": "R60W0101",
              "message": "ユーザーＩＤを入力してください。"},
    "E-102": {"code": "1", "message_id": "R60W0102",
              "message": "ユーザーＩＤは半角 7 桁で入力してください。"},
    "E-103": {"code": "1", "message_id": "R60W0103",
              "message": "起動区分は 1、2、3 のいずれかを指定してください。"},
    "E-104": {"code": "1", "message_id": "R60W0104",
              "message": "入力されたユーザーＩＤの社員が見つかりません。"},
    "E-105": {"code": "1", "message_id": "R60W0105",
              "message": "現在オンライン利用が許可されていません。時間をおいて再度お試しください。"},
    "E-106": {"code": "1", "message_id": "R60W0106",
              "message": "ログイン情報を確認できませんでした。画面を開き直してください。"},
    "E-107": {"code": "9", "message_id": "R60E0101",
              "message": "画面一覧を取得できませんでした。システム管理者に連絡してください。"},
    "E-108": {"code": "1", "message_id": "R60W0107",
              "message": "遷移先の画面を選択してください。"},
    "E-109": {"code": "1", "message_id": "R60W0108",
              "message": "遷移用 URL が長すぎるため生成できません。入力内容を確認してください。"},
    "E-110": {"code": "0", "message_id": "R60I0101",
              "message": "画面を閉じてもよろしいですか？"},
    "E-111": {"code": "9", "message_id": "R60E0102",
              "message": "システムエラーが発生しました。システム管理者に連絡してください。"},
}


def resolve(error_id: str) -> dict:
    return ERRORS[error_id]

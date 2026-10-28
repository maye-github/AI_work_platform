"""マスタ参照（模擬のインメモリ実装）。物理名・桁は暫定（ISS-102）。"""
from __future__ import annotations

EMPLOYEES: dict[str, dict] = {
    "1234567": {"STF_CD": "1234567", "CMP_CD": "0001", "JGY_CD": "0001",
                "STF_NM": "山田 太郎", "DEL_FLG": "0"},
    "7654321": {"STF_CD": "7654321", "CMP_CD": "0002", "JGY_CD": "0002",
                "STF_NM": "佐藤 花子", "DEL_FLG": "1"},
}

SCREENS: list[dict] = [
    {"GMN_ID": "GMN001", "GMN_NM": "単品マスタ", "YUKO_FLG": "1", "HYOJI_JUN": 1},
    {"GMN_ID": "GMN002", "GMN_NM": "取引先マスタ", "YUKO_FLG": "1", "HYOJI_JUN": 2},
    {"GMN_ID": "GMN003", "GMN_NM": "単品マスタ（シミュレーション）",
     "YUKO_FLG": "1", "HYOJI_JUN": 3},
    {"GMN_ID": "GMN009", "GMN_NM": "無効画面", "YUKO_FLG": "0", "HYOJI_JUN": 4},
]

KBN: list[dict] = [{"value": "Y", "label": "更新あり"},
                   {"value": "N", "label": "更新なし"}]

OPERATION: dict[str, dict] = {"R60": {"SYS_ID": "R60", "ONLINE_FLG": "1"}}


class _Repo:
    def __init__(self, rows: dict[str, dict]):
        self.rows = rows

    def get(self, key: str) -> dict | None:
        return self.rows.get(key)

    def list(self) -> list[dict]:
        return list(self.rows.values())


employee_repo = _Repo(EMPLOYEES)
operation_repo = _Repo(OPERATION)


def screen_list() -> list[dict]:
    """有効な画面だけを表示順昇順で返す（ASM-102）。"""
    return sorted([s for s in SCREENS if s["YUKO_FLG"] == "1"],
                  key=lambda s: s["HYOJI_JUN"])


def kbn_list() -> list[dict]:
    return KBN

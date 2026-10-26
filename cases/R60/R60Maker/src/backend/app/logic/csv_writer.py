"""L-210 CSV 生成（設計書 5.2 / イベント No8）。

文字コードは標準仕様待ち（Q-207）なので、**コードに埋め込まず引数で受ける**。
"""
from __future__ import annotations

COLUMNS = ("MAKER_CD", "MAKER_NM", "MAKER_ANM", "DEL_FLG")


def to_csv(rows: list[dict], encoding: str = "utf-8") -> bytes:
    """ヘッダ行＋明細。項目順は一覧と同じ。"""
    def esc(v) -> str:
        s = "" if v is None else str(v)
        if any(ch in s for ch in ',"\n'):
            s = '"' + s.replace('"', '""') + '"'
        return s

    lines = [",".join(COLUMNS)]
    for r in rows:
        lines.append(",".join(esc(r.get(c)) for c in COLUMNS))
    return ("\r\n".join(lines) + "\r\n").encode(encoding)

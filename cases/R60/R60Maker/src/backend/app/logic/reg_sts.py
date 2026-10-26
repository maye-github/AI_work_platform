"""L-211 REG_STS 再判定。

★設計書は「共通仕様参照」のみで本文が無い（Q-205 / ISS-201）。
ここは**弊社提案の暫定規則**。共通仕様が来たらこの関数だけ差し替える。
"""
from __future__ import annotations


def judge_reg_sts(maker_cd: str | None, maker_nm: str | None,
                  maker_anm: str | None) -> str:
    """3 項目がすべて非空なら登録済み('1')、それ以外は未登録('0')。"""
    return "1" if all(x and str(x).strip() for x in (maker_cd, maker_nm, maker_anm)) else "0"

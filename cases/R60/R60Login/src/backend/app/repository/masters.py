"""参照テーブルへのアクセス（SQL はすべて SELECT。DDL/DML を発行しない）。

接続は呼出側から注入する。単体テストでは接続を差し替える（DB 不要）。
"""
from __future__ import annotations

SQL_PAGES = """
SELECT GMN_ID, GMN_NM
  FROM R60_GMN_M_TBL
 WHERE VALID_FLG = 'Y'
 ORDER BY DSP_ORD, GMN_ID
"""

SQL_STAFF = """
SELECT STF_CD, CMP_CD, JIG_CD, STF_NM
  FROM R60_STF_M_TBL
 WHERE STF_CD = :stf_cd
   AND DEL_FLG = 'N'
"""

SQL_ONLINE = """
SELECT ONLINE_FLG
  FROM R60_OPR_STS
 WHERE STS_KEY = 'DEFAULT'
"""


def map_page(row) -> dict:
    return {"value": row[0], "label": row[1]}


def map_staff(row) -> dict:
    return {"stfCd": row[0], "cmpCd": row[1], "jigCd": row[2], "stfNm": row[3]}

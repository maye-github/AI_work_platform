"""L-105 遷移 URL の組立（パラメータの並びは顧客指定どおり）。"""
from __future__ import annotations

KGN_Y = "Y"   # 更新あり
KGN_N = "N"   # 更新なし


def build_url(scheme: str, host: str, port: str, context: str, route: str,
              stf_cd_encrypted: str, stf_kbn: str, gmn_id: str, kgn_kbn: str) -> str:
    """順序は stfCd → stfKbn → gmnId → kgnKbn（顧客要求 §3.6）。"""
    base = f"{scheme}://{host}:{port}{context}{route}"
    return (f"{base}?stfCd={stf_cd_encrypted}&stfKbn={stf_kbn}"
            f"&gmnId={gmn_id}&kgnKbn={kgn_kbn}")

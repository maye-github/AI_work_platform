"""L-113 URL出力要求 / L-117 遷移URL組立。"""
from __future__ import annotations

from urllib.parse import quote

from ..core.config import settings
from ..core.errors import resolve
from ..core.response import err, ok
from .stmt_cipher import encrypt_employee_code
from .validate import validate_startup_kbn


def build_url(stf_cd: str, startup_kbn: str, screen_id: str,
              authority_kbn: str) -> str:
    """パラメータ順を固定する（素材 §3.6）。未入力は "NaN" を社員コード扱い。"""
    code = stf_cd or "NaN"
    enc = quote(encrypt_employee_code(code), safe="")
    return (f"http://{settings.host}:{settings.port}/R60/Pages/index.jsp"
            f"?stfCd={enc}&stfKbn={quote(startup_kbn)}"
            f"&gmnId={quote(screen_id)}&kgnKbn={quote(authority_kbn)}")


def generate_url(params: dict) -> dict:
    stf_cd = params.get("stfCd") or ""
    startup_kbn = str(params.get("stfKbn") or "")
    screen_id = params.get("gmnId") or ""
    authority_kbn = params.get("kgnKbn") or "Y"

    bad = validate_startup_kbn(startup_kbn)
    if bad:
        e = resolve(bad)
        return err(e["code"], e["message_id"])

    if not screen_id:
        e = resolve("E-108")
        return err(e["code"], e["message_id"])

    url = build_url(stf_cd, startup_kbn, screen_id, authority_kbn)
    if len(url) > 150:
        e = resolve("E-109")
        return err(e["code"], e["message_id"])
    return ok(url=url)

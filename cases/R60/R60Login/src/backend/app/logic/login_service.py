"""L-107 ログイン / L-109 存在確認 / L-110 Session 保存 / L-111 遷移先決定。"""
from __future__ import annotations

from ..core import session_store
from ..core.errors import resolve
from ..core.response import err, ok
from ..repository.masters import employee_repo
from .stmt_cipher import decrypt_employee_code
from .validate import validate_startup_kbn, validate_user_id


def find_employee(stf_cd: str) -> dict | None:
    """存在し、かつ論理削除されていない社員だけ返す（ASM-101 / ASM-108）。"""
    row = employee_repo.get(stf_cd)
    if not row or row.get("DEL_FLG") != "0":
        return None
    return row


def save_session(session_id: str, row: dict) -> None:
    session_store.save(session_id, {
        "STF_CD": row["STF_CD"],
        "CMP_CD": row["CMP_CD"],
        "JGY_CD": row["JGY_CD"],
        "STF_NM": row["STF_NM"],
    })


def decide_redirect(screen_id: str | None, authority_kbn: str) -> dict:
    return {"screenId": screen_id, "authorityKbn": authority_kbn}


def login(params: dict) -> dict:
    stf_cd_enc = params.get("stfCd") or ""
    startup_kbn = str(params.get("stfKbn") or "")
    screen_id = params.get("gmnId")
    authority_kbn = params.get("kgnKbn") or "Y"

    bad = validate_startup_kbn(startup_kbn)
    if bad:
        e = resolve(bad)
        return err(e["code"], e["message_id"])

    try:
        stf_cd = decrypt_employee_code(stf_cd_enc)
    except Exception:
        e = resolve("E-106")
        return err(e["code"], e["message_id"])

    bad = validate_user_id(stf_cd)
    if bad:
        e = resolve(bad)
        return err(e["code"], e["message_id"])

    if not screen_id:
        e = resolve("E-108")
        return err(e["code"], e["message_id"])

    row = find_employee(stf_cd)
    if not row:
        e = resolve("E-104")
        return err(e["code"], e["message_id"])

    save_session(stf_cd, row)
    return ok(
        userInfo={"STF_CD": row["STF_CD"], "CMP_CD": row["CMP_CD"],
                  "JGY_CD": row["JGY_CD"], "STF_NM": row["STF_NM"]},
        mngInfo={"menuIds": ["GMN001", "GMN002", "GMN003"]},
        redirect=decide_redirect(screen_id, authority_kbn),
    )

"""R60Login の 3 端点（init / login / generateUrl）。"""
from __future__ import annotations

from fastapi import APIRouter

from ...core.errors import resolve
from ...core.response import err, ok
from ...logic.generate_url_service import generate_url
from ...logic.initializer import (build_initial_values, fetch_init_data,
                                  normalize_candidates)
from ...logic.login_service import login
from ...logic.operability import is_online

router = APIRouter(prefix="/R60Login", tags=["R60Login"])


def _operability_error() -> dict | None:
    if is_online():
        return None
    e = resolve("E-105")
    return err(e["code"], e["message_id"])


@router.post("/init")
def init(body: dict | None = None) -> dict:
    bad = _operability_error()
    if bad:
        return bad
    data = normalize_candidates(fetch_init_data())
    return ok(pageList=data["pageList"], kbnList=data["kbnList"],
              initial=build_initial_values(data))


@router.post("/login")
def login_endpoint(body: dict) -> dict:
    bad = _operability_error()
    if bad:
        return bad
    return login((body or {}).get("params") or {})


@router.post("/generateUrl")
def generate_url_endpoint(body: dict) -> dict:
    bad = _operability_error()
    if bad:
        return bad
    return generate_url((body or {}).get("params") or {})

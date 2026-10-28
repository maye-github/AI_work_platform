"""L-116 エラー区分と遷移。"""
from __future__ import annotations

from ..core.response import err


def is_business(error_code: str) -> bool:
    """errorCode "1" は業務エラー。"""
    return error_code == "1"


def classify(error_id: str, error_code: str) -> dict:
    return err(error_code, error_id)

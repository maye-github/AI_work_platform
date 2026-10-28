"""L-104 / L-105 / L-106 / L-108 の単体テスト（TC 本体は工程6）。"""
from __future__ import annotations

from app.logic.stmt_cipher import decrypt_employee_code, encrypt_employee_code
from app.logic.validate import validate_startup_kbn, validate_user_id


def test_validate_user_id():
    assert validate_user_id("") == "E-101"
    assert validate_user_id("123456") == "E-102"
    assert validate_user_id("1234567") is None
    assert validate_user_id("12345678") == "E-102"


def test_validate_startup_kbn():
    for value in ("1", "2", "3"):
        assert validate_startup_kbn(value) is None
    for value in ("0", "4", "", "A"):
        assert validate_startup_kbn(value) == "E-103"


def test_cipher_roundtrip():
    token = encrypt_employee_code("1234567")
    assert decrypt_employee_code(token) == "1234567"

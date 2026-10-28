"""L-106 暗号化 / L-108 復号 / L-117 の暗号化。

Q-111 の模拟方式: AES-128-CBC、鍵=SHA-256(yyyymmdd) の先頭 16 バイト、
IV=固定（全ゼロ）、暗号文=Base64URL。本番方式は Q-111 の確定後に差し替える。
"""
from __future__ import annotations

import base64
import hashlib
from datetime import date

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

_IV = b"\x00" * 16


def _key(day: str | None = None) -> bytes:
    d = day or date.today().strftime("%Y%m%d")
    return hashlib.sha256(d.encode("utf-8")).digest()[:16]


def _pad(data: bytes) -> bytes:
    n = 16 - len(data) % 16
    return data + bytes([n]) * n


def _unpad(data: bytes) -> bytes:
    return data[:-data[-1]]


def encrypt_employee_code(code: str, day: str | None = None) -> str:
    cipher = Cipher(algorithms.AES(_key(day)), modes.CBC(_IV))
    enc = cipher.encryptor()
    raw = enc.update(_pad(code.encode("utf-8"))) + enc.finalize()
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decrypt_employee_code(token: str, day: str | None = None) -> str:
    padded = token + "=" * (-len(token) % 4)
    raw = base64.urlsafe_b64decode(padded.encode("ascii"))
    cipher = Cipher(algorithms.AES(_key(day)), modes.CBC(_IV))
    dec = cipher.decryptor()
    plain = dec.update(raw) + dec.finalize()
    return _unpad(plain).decode("utf-8")

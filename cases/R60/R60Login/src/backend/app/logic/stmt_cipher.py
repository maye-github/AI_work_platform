"""L-106 社員コードの暗号化・復号（当日鍵 yyyymmdd）。

方式は弊社提案（顧客要求 §4.5「方式および鍵の運用は貴方の提案による」）。
★顧客の既存方式が提示されたら、**このファイルの中だけ**を差し替える（呼出側は変えない）。
"""
from __future__ import annotations

import hashlib

_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"


def _keystream(ymd: str, n: int) -> bytes:
    seed = hashlib.sha256(("R60|" + ymd).encode("utf-8")).digest()
    out = bytearray()
    while len(out) < n:
        seed = hashlib.sha256(seed).digest()
        out += seed
    return bytes(out[:n])


def encrypt(plain: str, ymd: str) -> str:
    """平文 → 当日鍵で暗号化した文字列（URL に載せられる形）。"""
    raw = plain.encode("utf-8")
    xored = bytes(a ^ b for a, b in zip(raw, _keystream(ymd, len(raw))))
    bits = "".join(f"{b:08b}" for b in xored)
    bits += "0" * (-len(bits) % 6)
    return "".join(_ALPHABET[int(bits[i:i + 6], 2)] for i in range(0, len(bits), 6))


def decrypt(cipher: str, ymd: str) -> str:
    """暗号文 → 平文。不正な文字列なら ValueError。"""
    idx = {c: i for i, c in enumerate(_ALPHABET)}
    try:
        bits = "".join(f"{idx[c]:06b}" for c in cipher)
    except KeyError as exc:
        raise ValueError("invalid character in cipher") from exc
    n = len(bits) // 8
    data = bytes(int(bits[i * 8:(i + 1) * 8], 2) for i in range(n))
    if not data:
        raise ValueError("empty cipher")
    out = bytes(a ^ b for a, b in zip(data, _keystream(ymd, len(data))))
    text = out.decode("utf-8")
    if not text:
        raise ValueError("empty plain")
    return text

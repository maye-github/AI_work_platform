"""純ロジックの単体テスト（DB もサーバも要らない）。

`unittest.TestCase` で書いてあるのは、pytest が入っていない環境でも
`python -m unittest` で走らせるため（pytest からもそのまま収集できる）。
"""
from __future__ import annotations

import unittest

from app.logic.operability import ensure_online
from app.logic.stmt_cipher import decrypt, encrypt
from app.logic.url_builder import build_url
from app.logic.validate import validate_stf_cd


class TestValidate(unittest.TestCase):
    def test_ok(self):
        self.assertIsNone(validate_stf_cd("0000001"))

    def test_empty(self):
        self.assertEqual(validate_stf_cd(""), "E-101")

    def test_six(self):
        self.assertEqual(validate_stf_cd("000001"), "E-101")

    def test_eight(self):
        self.assertEqual(validate_stf_cd("00000001"), "E-101")

    def test_alpha(self):
        self.assertEqual(validate_stf_cd("000000A"), "E-101")

    def test_fullwidth(self):
        self.assertEqual(validate_stf_cd("００００００１"), "E-101")


class TestCipher(unittest.TestCase):
    def test_roundtrip(self):
        self.assertEqual(decrypt(encrypt("0000001", "20261026"), "20261026"), "0000001")

    def test_differs_by_day(self):
        self.assertNotEqual(encrypt("0000001", "20261026"), encrypt("0000001", "20261027"))

    def test_other_day_fails(self):
        enc = encrypt("0000001", "20261026")
        with self.assertRaises(Exception):
            decrypt(enc, "20261027")

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            decrypt("", "20261026")


class TestUrl(unittest.TestCase):
    def test_order(self):
        u = build_url("http", "IP_1", "PORT_1", "/R60", "/Pages/index.jsp",
                      "ENC", "2", "GMN01", "N")
        self.assertTrue(u.startswith("http://IP_1:PORT_1/R60/Pages/index.jsp?"))
        self.assertLess(u.index("stfCd="), u.index("stfKbn="))
        self.assertLess(u.index("stfKbn="), u.index("gmnId="))
        self.assertLess(u.index("gmnId="), u.index("kgnKbn="))
        self.assertTrue(u.endswith("kgnKbn=N"))


class TestOperability(unittest.TestCase):
    def test_online(self):
        ensure_online("Y")

    def test_offline(self):
        with self.assertRaises(Exception):
            ensure_online("N")

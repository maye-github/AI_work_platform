"""メーカーマスタメンテの純ロジック単体テスト。"""
from __future__ import annotations

import unittest

from app.logic.count_check import check_count
from app.logic.csv_writer import to_csv
from app.logic.reg_sts import judge_reg_sts
from app.logic.search_condition import (build_where, validate_maker_cd,
                                        validate_maker_nm)
from app.logic.sort_whitelist import DEFAULT_ORDER, build_order_by


class TestMakerCode(unittest.TestCase):
    def test_valid(self):
        self.assertIsNone(validate_maker_cd("A1234"))

    def test_empty_allowed(self):
        self.assertIsNone(validate_maker_cd(""))

    def test_short(self):
        self.assertEqual(validate_maker_cd("A123"), "E-201")

    def test_long(self):
        self.assertEqual(validate_maker_cd("A12345"), "E-201")

    def test_fullwidth(self):
        self.assertEqual(validate_maker_cd("Ａ1234"), "E-201")


class TestMakerName(unittest.TestCase):
    def test_valid_ascii(self):
        self.assertIsNone(validate_maker_nm("ABC"))

    def test_30_bytes(self):
        self.assertIsNone(validate_maker_nm("a" * 30))

    def test_31_bytes(self):
        self.assertEqual(validate_maker_nm("a" * 31), "E-202")

    def test_japanese_bytes(self):
        # UTF-8 で 1 文字 3 バイト → 10 文字 = 30 バイト
        self.assertIsNone(validate_maker_nm("あ" * 10))
        self.assertEqual(validate_maker_nm("あ" * 11), "E-202")

    def test_forbidden(self):
        self.assertEqual(validate_maker_nm("A%B"), "E-202")


class TestWhere(unittest.TestCase):
    def test_prefix_match(self):
        w, p = build_where("A12", None, True, False)
        self.assertIn("MAKER_CD LIKE :maker_cd", w)
        self.assertEqual(p["maker_cd"], "A12%")

    def test_contains_match(self):
        w, p = build_where(None, "メーカー", True, False)
        self.assertIn("MAKER_NM LIKE :maker_nm", w)
        self.assertEqual(p["maker_nm"], "%メーカー%")

    def test_default_excludes_deleted(self):
        w, _ = build_where(None, None, False, False)
        self.assertIn("DEL_FLG = '0'", w)

    def test_pending_only(self):
        w, _ = build_where(None, None, True, True)
        self.assertIn("REG_STS = '0'", w)

    def test_no_condition(self):
        w, p = build_where(None, None, True, False)
        self.assertEqual(w, "")
        self.assertEqual(p, {})

    def test_values_are_bound(self):
        w, _ = build_where("A12", None, True, False)
        self.assertNotIn("A12", w)      # 値が SQL に埋まっていない（バインド）


class TestCount(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(check_count(0, 3000), "E-203")

    def test_at_limit(self):
        self.assertIsNone(check_count(3000, 3000))

    def test_over_limit(self):
        self.assertEqual(check_count(3001, 3000), "E-204")


class TestSort(unittest.TestCase):
    def test_allowed(self):
        self.assertIn("MAKER_NM", build_order_by("maker_nm"))

    def test_not_allowed(self):
        self.assertEqual(build_order_by("MAKER_ANM"), DEFAULT_ORDER)

    def test_empty(self):
        self.assertEqual(build_order_by(None), DEFAULT_ORDER)


class TestRegSts(unittest.TestCase):
    def test_all_filled(self):
        self.assertEqual(judge_reg_sts("A", "B", "C"), "1")

    def test_missing(self):
        self.assertEqual(judge_reg_sts("A", "B", ""), "0")


class TestCsv(unittest.TestCase):
    def test_header_and_row(self):
        b = to_csv([{"MAKER_CD": "A1", "MAKER_NM": "テスト", "MAKER_ANM": "テスト", "DEL_FLG": "0"}])
        t = b.decode("utf-8")
        self.assertTrue(t.startswith("MAKER_CD,MAKER_NM,MAKER_ANM,DEL_FLG"))
        self.assertIn('A1,テスト,テスト,0', t)

    def test_escape_comma(self):
        b = to_csv([{"MAKER_CD": "A,B", "MAKER_NM": "", "MAKER_ANM": "", "DEL_FLG": "0"}])
        self.assertIn('"A,B"', b.decode("utf-8"))

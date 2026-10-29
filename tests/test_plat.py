# -*- coding: utf-8 -*-
"""平台自身的回归测试。

门禁是「管别人质量」的，它自己必须先被验证。这里只测**会被门禁依赖的判定**：
- G3：`result: pass` 必须有证跡（否则空欄也能过门）
- G2：追溯是 DAG，不再产生 W4 噪音
- status：计数按条目，不按文件
- mask.prep：脱敏生效、未対応文件可见
"""
from __future__ import annotations

from pathlib import Path

from plat import gate, mask, model, status


def _base(id_: str, tp: str, related: list[str] | None = None) -> dict:
    return {
        "id": id_,
        "type": tp,
        "title": "t",
        "status": "confirmed",
        "version": "1",
        "related_ids": related or [],
        "owner": "o",
        "created_at": "2026-01-01",
        "updated_at": "2026-01-01",
        "sensitivity": "internal",
    }


def _art(tp: str, data: dict, stage: int) -> model.Artifact:
    return model.Artifact(
        path=Path("test.yaml"), rel="test.yaml",
        case="C", module="M", stage=stage, data=data,
    )


def _tc(result: str, actual: str | None, evidence: str | None = None) -> dict:
    d = _base("TC-101", "TC", ["L-101"])
    entry = {"id": "TC-101", "result": result, "actual": actual, "related_ids": ["L-101"]}
    if evidence is not None:
        entry["evidence"] = evidence
    d["cases"] = [entry]
    return d


# ---------------------------------------------------------------------------
# G3：pass 必须有证跡
# ---------------------------------------------------------------------------
def test_g3_pass_without_proof_is_error():
    ok, err, _warn = gate.g3({}, [_art("TC", _tc("pass", None), 6)])
    assert not ok
    assert any("証跡なし" in e for e in err), err


def test_g3_pass_with_simulated_proof_warns_but_passes():
    ok, err, warn = gate.g3({}, [_art("TC", _tc("pass", "【模拟】未実測"), 6)])
    assert ok, err
    assert any("W5" in w for w in warn), warn


def test_g3_not_run_without_proof_is_ok():
    ok, err, _warn = gate.g3({}, [_art("TC", _tc("not_run", None), 6)])
    assert ok, err


def test_g3_it_accepts_evidence_as_proof():
    d = _base("IT-101", "IT", ["R-101"])
    d["cases"] = [{"id": "IT-101", "result": "pass", "evidence": "実測ログ", "related_ids": ["R-101"]}]
    ok, err, _warn = gate.g3({}, [_art("IT", d, 7)])
    assert ok, err


# ---------------------------------------------------------------------------
# G2：DAG 追溯，不再有 W4 片方向噪音
# ---------------------------------------------------------------------------
def test_g2_does_not_emit_w4_noise():
    r = _base("R-101", "R", [])
    f = _base("F-101", "F", ["R-101"])
    tc = _base("TC-101", "TC", ["F-101"])
    ok, err, warn = gate.g2({}, [_art("R", r, 1), _art("F", f, 2), _art("TC", tc, 6)])
    assert ok, err
    assert not any("W4" in w for w in warn), warn


def test_g2_detects_orphan():
    r = _base("R-101", "R", [])
    f = _base("F-101", "F", [])  # どの R からも届かない
    ok, err, _warn = gate.g2({}, [_art("R", r, 1), _art("F", f, 2)])
    assert not ok
    assert any("孤立" in e for e in err), err


# ---------------------------------------------------------------------------
# status：按条目计数
# ---------------------------------------------------------------------------
def test_status_counts_entries_not_files():
    d = _base("R-101", "R", [])
    d["requirements"] = [{"id": f"R-{i}", "related_ids": []} for i in range(101, 111)]
    rendered = status.render("C", "M", [_art("R", d, 1)])
    assert "R 10" in rendered, rendered


# ---------------------------------------------------------------------------
# mask.prep：脱敏与未対応可见
# ---------------------------------------------------------------------------
def test_prep_masks_password(tmp_path: Path):
    src = tmp_path / "raw"
    src.mkdir()
    (src / "a.txt").write_text("password: hunter2\n", encoding="utf-8")
    out = tmp_path / "ai_input"

    res = mask.prep(src=src, out=out)

    text = (out / "a.md").read_text(encoding="utf-8")
    assert "hunter2" not in text
    assert res["files"] == 1


def test_prep_marks_unsupported_files(tmp_path: Path):
    src = tmp_path / "raw"
    src.mkdir()
    (src / "a.pdf").write_bytes(b"%PDF-1.4")
    out = tmp_path / "ai_input"

    res = mask.prep(src=src, out=out)

    assert res["unsupported"] == ["a.pdf"]
    report = (out / "MASK_REPORT.md").read_text(encoding="utf-8")
    assert "未脱敏" in report

# -*- coding: utf-8 -*-
"""現在地の判定 —— **成果物から現算する**（状態ファイルを持たない）。

状態を別ファイルに持つと必ず成果物と食い違う。だから本プラットフォームは
「成果物の front-matter が唯一の真実」とし、本モジュールは毎回そこから数え直す。
"""
from __future__ import annotations

from collections import Counter

from . import model, paths, rules_data as R


def module_status(case: str, module: str, arts: list[model.Artifact]) -> list[dict]:
    rows: list[dict] = []
    for s in R.STAGES:
        items = [a for a in arts if a.stage == s.no and a.type in s.produces]
        if not items and s.produces:
            rows.append({"stage": s, "state": "not_started", "items": []})
            continue
        if not items and not s.produces:
            # 管理文書だけを出す工程：台帳の management_docs の status で判定する
            docs = _stage_docs(case, module, s)
            if not docs:
                rows.append({"stage": s, "state": "not_started", "items": []})
            elif all(str(d.get("status")) in R.APPROVED_STATUS for d in docs):
                rows.append({"stage": s, "state": "approved", "items": []})
            else:
                rows.append({"stage": s, "state": "in_progress", "items": []})
            continue
        approved = [a for a in items if a.status in R.APPROVED_STATUS]
        state = "approved" if len(approved) == len(items) else "in_progress"
        rows.append({"stage": s, "state": state, "items": items})
    return rows


def _stage_docs(case: str, module: str, stage) -> list[dict]:
    """その工程のディレクトリ配下に置かれた管理文書（台帳登録済みのもの）。"""
    ledger = model.load_ledger()
    prefix = f"cases/{case}/{module}/{stage.artifact_dir.strip('/')}/"
    out = []
    for d in (ledger.get("management_docs") or []):
        if isinstance(d, dict) and str(d.get("path", "")).startswith(prefix):
            out.append(d)
    return out


def blocking_issues(arts: list[model.Artifact]) -> list[model.Artifact]:
    """`block: true` かつ未承認の未決事項。"""
    return [a for a in arts
            if a.type == "ISS" and a.data.get("block") is True
            and a.status not in R.APPROVED_STATUS]


def next_command(rows: list[dict]) -> tuple[str, int | None]:
    for r in rows:
        if r["state"] != "approved":
            return f"/{r['stage'].key}", r["stage"].no
    return "", None


def render(case: str, module: str, arts: list[model.Artifact]) -> str:
    rows = module_status(case, module, arts)
    lines = [f"模块 {case}/{module}"]
    for r in rows:
        s = r["stage"]
        icon = {"not_started": "⏸ 未開始", "in_progress": "▶ 進行中", "approved": "✅ 承認済"}[r["state"]]
        counts = Counter(a.type for a in r["items"])
        detail = " / ".join(f"{t} {n}" for t, n in sorted(counts.items())) or "—"
        lines.append(f"  {s.no} {s.name_ja:<16} {icon:<8} {detail}")
    cmd, _ = next_command(rows)
    blocks = blocking_issues(arts)
    if blocks:
        lines.append("  ★ 阻塞项（未承认的 ISS）:")
        for b in blocks:
            lines.append(f"     - {b.id} {b.data.get('title', '')}")
    lines.append(f"  次の 1 歩: {cmd or '（全工程 承認済）'}")
    return "\n".join(lines)


def render_all() -> str:
    mods = paths.modules()
    if not mods:
        return ("（案件がまだありません）\n"
                "次: /requirements を叩く前に cases/<案件>/<模块>/module.yaml を作る")
    out: list[str] = []
    all_arts = model.load_all()
    for case, module, _p in mods:
        arts = [a for a in all_arts if a.case == case and a.module == module]
        out.append(render(case, module, arts))
        out.append("")
    return "\n".join(out).rstrip()

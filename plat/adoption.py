# -*- coding: utf-8 -*-
"""採用率・修正量の測定 —— **初稿スナップショットと承認版の差分**。

## なぜ必要か
「承認到達率」（承認済÷生成済）は AI の精度を何も語らない。改稿してもしなくても同じ数字になる。
規格書 §13.1 が求めているのは「生成物の採用率」「レビューでの修正率」であり、
そのためには **初稿** と **承認版** の二つが要る。

## 仕組み
1. 成果物が**初めて書かれた瞬間**に、条目ごとのハッシュを `registry/adoption.yaml` へ保存（フックが自動でやる）
2. `/approve` で `confirmed` に変える瞬間に、現在の内容とスナップショットを比べる
3. 差分を「未改 / 修正 / 追加 / 削除」に分類して記録する

## 正直な限界（誇張しない）
**「人が手で直した」のか「人が指示して AI が直した」のかは区別できない。**
したがって本モジュールが出すのは「**承認までの修正量**」であって「人の修正率」ではない。
この区別は `使用手册.md` と `plat kpi` の出力にも明記する。

## 条目の単位
- `.yaml` … `id` を持つ dict のリスト（`requirements:` / `functions:` …）を 1 条目 1 件として数える
- `.md`   … `## ` 見出しごとに 1 条目
どちらも取れない成果物（管理文書など）は**ファイル全体を 1 条目**として扱う。
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path

import yaml

from . import model, paths

SECTION = re.compile(r"^##\s+(.+?)\s*$", re.M)


# =============================================================================
# 条目の抽出
# =============================================================================
def _h(obj) -> str:
    return hashlib.sha1(
        json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]


def items_of(art: model.Artifact) -> dict[str, str]:
    """条目キー → 内容ハッシュ。"""
    out: dict[str, str] = {}

    if art.suffix_yaml and isinstance(art.data, dict):
        for key, val in art.data.items():
            if not (isinstance(val, list) and val and all(isinstance(x, dict) for x in val)):
                continue
            for i, item in enumerate(val):
                ident = item.get("id") or item.get("code") or f"#{i + 1}"
                out[f"{key}/{ident}"] = _h(item)
        # 本文のリストが無い成果物（TECH_STACK など）は front-matter 全体で 1 条目
        if not out:
            out["(file)"] = _h({k: v for k, v in art.data.items() if k not in ("status", "updated_at")})
        return out

    # .md：見出し単位
    body = art.body or ""
    hits = list(SECTION.finditer(body))
    if not hits:
        out["(file)"] = _h(body or art.data)
        return out
    for i, m in enumerate(hits):
        start = m.end()
        end = hits[i + 1].start() if i + 1 < len(hits) else len(body)
        out[m.group(1).strip()] = _h(body[start:end])
    return out


# =============================================================================
# 保存
# =============================================================================
def _file() -> Path:
    return paths.root() / "registry" / "adoption.yaml"


def load() -> dict:
    p = _file()
    if not p.is_file():
        return {"schema": "1", "snapshots": {}, "results": {}}
    try:
        d = model.load_yaml_doc(p)
    except Exception:
        return {"schema": "1", "snapshots": {}, "results": {}}
    d.setdefault("snapshots", {})
    d.setdefault("results", {})
    return d


def save(d: dict) -> None:
    p = _file()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.dump(d, allow_unicode=True, sort_keys=True,
                           default_flow_style=False, width=4096), encoding="utf-8")


# =============================================================================
# スナップショット（初稿を固定する）
# =============================================================================
def snapshot(art: model.Artifact, force: bool = False) -> bool:
    """初稿スナップショットを取る。既にあれば何もしない（初稿は 1 回だけ）。

    承認済みの成果物は対象外（もう初稿ではない）。
    """
    if not art.id or art.error:
        return False
    if art.status not in ("draft", "reviewed"):
        return False
    d = load()
    if art.key in d["snapshots"] and not force:
        return False
    d["snapshots"][art.key] = {
        "captured_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "stage": art.stage,
        "items": items_of(art),
    }
    save(d)
    return True


def snapshot_module(case: str, module: str) -> list[str]:
    out = []
    for a in model.load_all():
        if a.case == case and a.module == module and snapshot(a):
            out.append(a.id)
    return out


# =============================================================================
# 差分（承認時に記録する）
# =============================================================================
def diff(art: model.Artifact) -> dict:
    d = load()
    snap = (d["snapshots"].get(art.key) or {}).get("items") or {}
    cur = items_of(art)
    unchanged = [k for k in cur if k in snap and snap[k] == cur[k]]
    modified = [k for k in cur if k in snap and snap[k] != cur[k]]
    added = [k for k in cur if k not in snap]
    removed = [k for k in snap if k not in cur]
    total = len(cur)
    return {
        "total": total,
        "unchanged": unchanged,
        "modified": modified,
        "added": added,
        "removed": removed,
        "has_snapshot": bool(snap),
    }


def record(art: model.Artifact, reasons: dict[str, str] | None = None) -> dict:
    """承認の瞬間に呼ぶ。差分を計算して残す。"""
    r = diff(art)
    if not r["has_snapshot"]:
        # スナップショットが無い（承認が先に来た等）→ 測れない。捏造しない。
        r["note"] = "スナップショットが無いため測定不能"
    d = load()
    d["results"][art.key] = {
        "approved_at": dt.date.today().isoformat(),
        "stage": art.stage,
        "total": r["total"],
        "unchanged": len(r["unchanged"]),
        "modified": len(r["modified"]),
        "added": len(r["added"]),
        "removed": len(r["removed"]),
        "modified_items": r["modified"],
        "added_items": r["added"],
        "removed_items": r["removed"],
        "reasons": reasons or {},
        "measurable": r["has_snapshot"],
    }
    save(d)
    return r


def note(artifact_id: str, item: str, text: str, module: str | None = None) -> str:
    """修正理由を 1 件書き足す（任意）。`/approve` で人が書く。"""
    d = load()
    hits = [k for k in d["results"] if k.endswith("/" + artifact_id)
            and (module is None or f"/{module}/" in k)]
    if not hits:
        raise SystemExit(f"承認記録がありません: {artifact_id}")
    key = hits[0]
    d["results"][key].setdefault("reasons", {})[item] = text
    save(d)
    return key


# =============================================================================
# 集計
# =============================================================================
def summary(case: str | None = None, module: str | None = None) -> dict:
    d = load()
    rows = []
    for key, r in d["results"].items():
        c, m, _id = model.split_key(key)
        if case and c != case:
            continue
        if module and m != module:
            continue
        if not r.get("measurable"):
            continue
        rows.append(r)
    if not rows:
        return {"measurable": 0}
    total = sum(r["total"] for r in rows)
    unchanged = sum(r["unchanged"] for r in rows)
    modified = sum(r["modified"] for r in rows)
    added = sum(r["added"] for r in rows)
    removed = sum(r["removed"] for r in rows)
    denom = total or 1
    return {
        "measurable": len(rows),
        "unmeasurable": len([r for r in d["results"].values() if not r.get("measurable")]),
        "items": total,
        "unchanged": unchanged,
        "modified": modified,
        "added": added,
        "removed": removed,
        "adoption_pct": round(unchanged / denom * 100, 1),
        "modified_pct": round(modified / denom * 100, 1),
        "added_pct": round(added / denom * 100, 1),
        "reasons": {k: v for r in rows for k, v in (r.get("reasons") or {}).items()},
    }


def render(s: dict, scope: str) -> str:
    if not s.get("measurable"):
        return (f"■ 採用率（{scope}）\n\n"
                "測定データがありません（まだ承認された成果物が無いか、"
                "スナップショットが取られていません）。\n"
                "**代理値で埋めない**のが本プラットフォームの方針です。")
    lines = [
        f"■ 採用率（{scope}）  ※「承認までの修正量」であり、人の修正率ではない",
        "",
        "| 指標 | 値 |",
        "|---|---|",
        f"| 承認版の条目数 | {s['items']} |",
        f"| **初稿のまま採用** | {s['unchanged']}（**採用率 {s['adoption_pct']}%**） |",
        f"| 修正された | {s['modified']}（{s['modified_pct']}%） |",
        f"| **人が追加**（AI の漏れ） | {s['added']}（{s['added_pct']}%） |",
        f"| 削除された（AI の書きすぎ） | {s['removed']} |",
        "",
        f"測定できた成果物 {s['measurable']} 件"
        + (f"／測定不能 {s['unmeasurable']} 件" if s.get("unmeasurable") else ""),
    ]
    if s.get("reasons"):
        lines.append("\n**修正理由**")
        for k, v in list(s["reasons"].items())[:10]:
            lines.append(f"- {k}: {v}")
    return "\n".join(lines)

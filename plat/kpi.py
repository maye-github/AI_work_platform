# -*- coding: utf-8 -*-
"""KPI 六维（规格书 §13.1 的最小实现）—— **全部从成果物现算，不额外采集**。

| 维 | 指标 | 算法 | 备注 |
|---|---|---|---|
| 生産性 | 工程別所要日数 | その工程の成果物の updated_at − created_at | 日単位 |
| 品質 | 門番ヒット数 / 手戻り件数 | gate の ERROR 数 / 台帳の changes 件数 | |
| AI 活用度 | 承認到達率 | 承認済 ÷ 生成済 | **採用率の代理指標**（修正量は記録していない） |
| 網羅性 | 要件カバレッジ | TC/IT に到達する R ÷ 全 R | 追跡グラフで判定 |
| リードタイム | 案件起算からの日数 | 最古 created_at → 今日 | |
| 知識資産 | 踩坑記録の件数 | `knowledge/traps.md` の `- ` 行数 | |

**誇張しないための注記**：本 KPI は「成果物から機械的に取れるもの」だけを出している。
工数（人月）や削減率は成果物からは取れないので、ここでは出さない。
"""
from __future__ import annotations

import datetime as dt
from collections import defaultdict, deque

from . import model, paths, rules_data as R


def _d(s: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except Exception:
        return None


def _reachable_roots(arts: list[model.Artifact]) -> tuple[int, int]:
    """(全 R 数, TC/IT に到達する R 数)。**条目単位**で数える（集約ファイルを 1 件と数えない）。"""
    node_rel: dict[str, list[str]] = {}
    node_type: dict[str, str] = {}
    for a in arts:
        for it in a.items():
            node_rel[it["id"]] = it["related_ids"]
            node_type[it["id"]] = a.type
    adj: dict[str, set[str]] = defaultdict(set)
    for nid, rels in node_rel.items():
        for rid in rels:
            if rid in node_rel:
                adj[nid].add(rid)
                adj[rid].add(nid)
    roots = [nid for nid, tp in node_type.items() if tp == "R"]
    ok = 0
    for r in roots:
        seen, q = {r}, deque([r])
        while q:
            cur = q.popleft()
            for nx in adj[cur]:
                if nx not in seen:
                    seen.add(nx)
                    q.append(nx)
        if any(model.id_type(x) in R.TERMINAL_TYPES for x in seen):
            ok += 1
    return len(roots), ok


def compute(case: str | None = None, module: str | None = None) -> dict:
    all_arts = model.load_all()
    # 管理文書（doc:）も含める。工程 4/5 は ID を産まないため、
    # ID 持ちだけを対象にすると所要日数が空欄になる。
    arts = [a for a in all_arts
            if (case is None or a.case == case) and (module is None or a.module == module)
            and (a.id or a.data.get("doc"))]
    ledger = model.load_ledger()

    # 生産性：工程別所要日数
    per_stage: dict[int, list[dt.date]] = defaultdict(list)
    per_stage_end: dict[int, list[dt.date]] = defaultdict(list)
    for a in arts:
        c, u = _d(a.data.get("created_at", "")), _d(a.data.get("updated_at", ""))
        if a.stage and c:
            per_stage[a.stage].append(c)
            per_stage_end[a.stage].append(u or c)
    productivity = {}
    for st, cs in sorted(per_stage.items()):
        productivity[st] = (max(per_stage_end[st]) - min(cs)).days

    # 品質
    from . import gate as gatemod
    gate_res = gatemod.run()
    gate_hits = sum(len(v["error"]) for v in gate_res["gates"].values())
    rework = len(ledger.get("changes") or [])

    # AI 活用度：承認到達率（到達の事実）＋ 採用率（初稿→承認版の実測）
    generated = len(arts)
    approved = len([a for a in arts if a.status in R.APPROVED_STATUS])
    reach = (approved / generated * 100) if generated else 0.0
    from . import adoption as adoptmod
    adopt = adoptmod.summary(case=case, module=module)

    # 網羅性
    total_r, covered_r = _reachable_roots(arts)
    coverage = (covered_r / total_r * 100) if total_r else 0.0

    # リードタイム
    starts = [d for cs in per_stage.values() for d in cs]
    lead = (dt.date.today() - min(starts)).days if starts else 0

    # 知識資産
    traps = paths.knowledge_dir() / "traps.md"
    traps_n = 0
    if traps.is_file():
        traps_n = sum(1 for ln in traps.read_text(encoding="utf-8").splitlines()
                      if ln.startswith("- "))

    return {
        "scope": f"{case or '*'}/{module or '*'}",
        "generated": generated,
        "approved": approved,
        "productivity": productivity,
        "quality": {"gate_hits": gate_hits, "rework": rework},
        "reach_pct": round(reach, 1),
        "adoption": adopt,
        "coverage": {"req_total": total_r, "req_covered": covered_r, "pct": round(coverage, 1)},
        "lead_time_days": lead,
        "knowledge": {"traps": traps_n},
    }


def render(k: dict) -> str:
    p = k["productivity"]
    prod = " / ".join(f"工程{s}:{d}日" for s, d in sorted(p.items())) or "—"
    lines = [
        f"■ KPI（{k['scope']}）",
        "",
        "| 维度 | 指标 | 值 |",
        "|---|---|---|",
        f"| 生産性 | 工程別所要日数 | {prod} |",
        f"| 品質 | 門番ヒット / 手戻り | {k['quality']['gate_hits']} / {k['quality']['rework']} |",
        f"| AI 活用度 | 承認到達率 | {k['reach_pct']}%（{k['approved']}/{k['generated']}） |",
        "| AI 活用度 | **採用率**（初稿→承認版の変動量） | "
        + (f"{k['adoption']['adoption_pct']}%（{k['adoption']['unchanged']}/{k['adoption']['items']}）"
           "／修正 " + str(k['adoption']['modified'])
           + "・追加 " + str(k['adoption']['added'])
           + "・削除 " + str(k['adoption']['removed'])
           if k['adoption'].get('measurable') else "未測定（承認実績なし）") + " |",
        f"| 網羅性 | 要件カバレッジ | {k['coverage']['pct']}%（{k['coverage']['req_covered']}/{k['coverage']['req_total']}） |",
        f"| リードタイム | 案件起算からの日数 | {k['lead_time_days']} 日 |",
        f"| 知識資産 | 踩坑記録 | {k['knowledge']['traps']} 件 |",
        "",
        "> ※ 採用率は「人の修正率」ではない。人が指示して AI が直した分も「修正」に含む。",
    ]
    return "\n".join(lines)

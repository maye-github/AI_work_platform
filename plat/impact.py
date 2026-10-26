# -*- coding: utf-8 -*-
"""変更影響分析 —— ID から下流・上流を逆引きする。

**言い方に注意**：ここが出すのは「影響する**候補**と規模」であって、承認ではない。
戻し先（どの工程から作り直すか）を決めるのは人（紅线③ と同じ考え方）。
"""
from __future__ import annotations

from collections import deque

from . import model, rules_data as R

# 上流→下流の順序（同じ工程内の並びもこれで決める）
_ORDER = ["Q", "ASM", "ISS", "CR", "R", "F", "I", "D", "L", "E", "TC", "IT", "BUG", "REL"]


def _rank(t: str) -> int:
    return _ORDER.index(t) if t in _ORDER else 99


def analyze(target: str, module: str | None = None) -> dict:
    arts = [a for a in model.load_all() if a.id]
    if module:
        arts = [a for a in arts if a.module == module]
    # 条目単位でノードを作る（集約ファイルでも 1 件ずつ逆引きできるように）
    by_id: dict[str, model.Artifact] = {}
    node_rel: dict[str, list[str]] = {}
    for a in arts:
        for it in a.items():
            by_id[it["id"]] = a
            node_rel[it["id"]] = it["related_ids"]
    if target not in by_id:
        raise SystemExit(f"成果物が見つかりません: {target}")

    adj: dict[str, set[str]] = {nid: set() for nid in node_rel}
    for nid, rels in node_rel.items():
        for rid in rels:
            if rid in adj:
                adj[nid].add(rid)
                adj[rid].add(nid)

    def walk(start: str, downward: bool) -> list[str]:
        seen, q, out = {start}, deque([start]), []
        r0 = _rank(by_id[start].type)
        while q:
            cur = q.popleft()
            for nx in adj[cur]:
                if nx in seen:
                    continue
                rel = _rank(by_id[nx].type) > r0
                if rel == downward:
                    seen.add(nx)
                    out.append(nx)
                    q.append(nx)
        return out

    down = walk(target, True)
    up = walk(target, False)

    def rows(ids: list[str]) -> list[dict]:
        return [
            {"id": i, "type": by_id[i].type, "stage": by_id[i].stage,
             "status": by_id[i].status,
             "title": next((x["raw"].get("title") or x["raw"].get("name") or ""
                            for x in by_id[i].items() if x["id"] == i), "")}
            for i in sorted(ids, key=lambda x: (_rank(by_id[x].type), x))
        ]

    stages = sorted({by_id[i].stage for i in down if by_id[i].stage})
    return {
        "target": target,
        "type": by_id[target].type,
        "downstream": rows(down),
        "upstream": rows(up),
        "reenter_from": stages[0] if stages else None,
    }


def render(r: dict) -> str:
    def table(items: list[dict]) -> list[str]:
        if not items:
            return ["  （なし）"]
        out = ["  | ID | 種別 | 工程 | 状態 | 標題 |", "  |---|---|---|---|---|"]
        for i in items:
            out.append(f"  | {i['id']} | {i['type']} | {i['stage']} | {i['status']} | {i['title']} |")
        return out

    lines = [
        f"■ 影響分析: {r['target']}（{r['type']}）",
        "",
        "**この結果は影響の候補と規模であり、承認ではありません。**",
        "戻し先を決めるのは人です。",
        "",
        f"## 下流（これを作り直す）: {len(r['downstream'])} 件",
        *table(r["downstream"]),
        "",
        f"## 上流（これを見直す）: {len(r['upstream'])} 件",
        *table(r["upstream"]),
        "",
        f"**作り直しの起点（候補）: 工程 {r['reenter_from'] or '—'}**",
    ]
    return "\n".join(lines)

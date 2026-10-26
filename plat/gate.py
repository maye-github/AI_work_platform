# -*- coding: utf-8 -*-
"""門番 6 道 —— 一条命令跑完，输出一行。

G1 ID 合法性   G2 追跡閉ループ   G3 成果物形式
G4 人工卡点     G5 文書一貫性     G6 機密ゼロヒット

**設計方針**
- 1 道でも FAIL したら Exit 1（`警告`は PASS 扱い。ERROR と WARN を混ぜない）。
- 出力は「人が 1 行で読める形」＋`--json` で機械可読。
- 成果物が 0 件でも動く（新規案件で空振り PASS する。落ちるのは「壊れた時」だけ）。
"""
from __future__ import annotations

import json
import re
from collections import defaultdict, deque
from pathlib import Path

from . import ids as idsmod
from . import model, paths, rules_data as R

SNAKE = re.compile(r"^[a-z][a-z0-9_]*$")
ALLOWED_KEY = re.compile(r"^[a-z][a-z0-9_]*$|^[A-Z][A-Z0-9_]*$|^x-")


# =============================================================================
# 共通
# =============================================================================
def _parents(stage: int) -> tuple[int, ...]:
    return tuple(s.no for s in R.STAGES if s.no < stage)


def _ids_by_module(arts: list[model.Artifact]) -> dict[tuple[str, str], list[model.Artifact]]:
    out: dict[tuple[str, str], list[model.Artifact]] = defaultdict(list)
    for a in arts:
        if a.id:
            out[(a.case, a.module)].append(a)
    return out


# =============================================================================
# G1 ID 合法性
# =============================================================================
def g1(ledger: dict, arts: list[model.Artifact]) -> tuple[bool, list[str], list[str]]:
    err, warn = idsmod.verify(ledger, arts)
    e = [x for x in err if re.match(r"^(E1|E2|E3|E4|E5|E6|E7|E8)\b", x)]
    w = [x for x in warn if x.startswith("W1")]
    return (not e), e, w


# =============================================================================
# G2 追跡閉ループ
# =============================================================================
def g2(ledger: dict, arts: list[model.Artifact]) -> tuple[bool, list[str], list[str]]:
    err: list[str] = []
    warn: list[str] = []
    by_mod = _ids_by_module(arts)

    for (case, module), lst in by_mod.items():
        # 条目単位でノードを作る（集約ファイルでも 1 件ずつ追溯できるように）
        node_rel: dict[str, list[str]] = {}
        node_type: dict[str, str] = {}
        for a in lst:
            for it in a.items():
                node_rel[it["id"]] = it["related_ids"]
                node_type[it["id"]] = a.type

        # 対称参照（W4）
        for nid, rels in node_rel.items():
            for rid in rels:
                if rid in node_rel and nid not in node_rel[rid]:
                    warn.append(f"W4 片方向参照: {nid} → {rid}（{rid} は {nid} を参照していない）")
        # 到達性
        adj: dict[str, set[str]] = defaultdict(set)
        for nid, rels in node_rel.items():
            for rid in rels:
                if rid in node_rel:
                    adj[nid].add(rid)
                    adj[rid].add(nid)   # 逆向きも辿る（「どこからも届かない」を防ぐ）
        roots = [nid for nid, tp in node_type.items() if tp == "R"]
        for r in roots:
            seen, q = {r}, deque([r])
            while q:
                cur = q.popleft()
                for nx in adj[cur]:
                    if nx not in seen:
                        seen.add(nx)
                        q.append(nx)
            terms = [x for x in seen if model.id_type(x) in R.TERMINAL_TYPES]
            has_terminal_anywhere = any(tp in R.TERMINAL_TYPES for tp in node_type.values())
            if has_terminal_anywhere and not terms:
                err.append(f"G2 {r} から TC/IT/REL に届きません（網羅性が閉じない）")
        # 孤立（どの R からも届かない）
        for nid, tp in node_type.items():
            if tp == "R":
                continue
            reachable = False
            for r in roots:
                seen, q = {r}, deque([r])
                while q:
                    cur = q.popleft()
                    for nx in adj[cur]:
                        if nx not in seen:
                            seen.add(nx)
                            q.append(nx)
                if nid in seen:
                    reachable = True
                    break
            if not reachable:
                err.append(f"G2 孤立: {nid} はどの要件からも辿れません")
    return (not err), err, warn


# =============================================================================
# G3 成果物形式
# =============================================================================
def g3(ledger: dict, arts: list[model.Artifact]) -> tuple[bool, list[str], list[str]]:
    err: list[str] = []
    warn: list[str] = []
    for a in arts:
        if a.error:
            err.append(f"G3 読めません: {a.rel}（{a.error}）")
            continue
        if not a.data:
            err.append(f"G3 front-matter がありません: {a.rel}")
            continue
        # 管理文書（`doc:` で識別）は業務 ID を持たない。別の必須項目で見る。
        if a.data.get("doc"):
            for k in ("doc", "title", "status", "version", "owner",
                      "created_at", "updated_at"):
                if not a.data.get(k):
                    err.append(f"G3 管理文書の必須項目なし: {a.rel} → {k}")
            if a.data.get("status") and a.data["status"] not in R.STATUS_VALUES:
                err.append(f"G3 管理文書の status 不正: {a.rel} → {a.data['status']}")
            continue
        for k in R.REQUIRED_FIELDS:
            if k not in a.data:
                err.append(f"G3 必須項目なし: {a.rel} → {k}")
        if a.status and a.status not in R.STATUS_VALUES:
            err.append(f"G3 status 不正: {a.rel} → {a.status}")
        sens = a.data.get("sensitivity")
        if sens and sens not in R.SENSITIVITY_VALUES:
            err.append(f"G3 sensitivity 不正: {a.rel} → {sens}")
        if not isinstance(a.data.get("related_ids"), (list, type(None))):
            err.append(f"G3 related_ids はリスト: {a.rel}")
        if a.type and a.type not in R.ID_TYPES:
            err.append(f"G3 type 不正: {a.rel} → {a.type}")
        # 集約ファイルの front `id` は、中身の ID のいずれかでなければならない
        # （集約ファイルは「最も小さい ID」を代表として名乗る規約。勝手な ID を立てない）
        inner = []
        for _k, _v in (a.data or {}).items():
            if isinstance(_v, list):
                inner += [x.get("id") for x in _v if isinstance(x, dict) and x.get("id")]
        if inner and a.id and a.id not in inner:
            err.append(f"G3 集約ファイルの id が中身にありません: {a.rel} → {a.id}")

        # 段の整合（成果物の置き場所と type が合っているか）
        want = R.stage_of_type(a.type)
        if want and a.stage and want != a.stage:
            err.append(f"G3 置き場所違い: {a.rel} は工程{a.stage} だが {a.type} は工程{want}")
    return (not err), err, warn


# =============================================================================
# G4 人工卡点
# =============================================================================
def g4(ledger: dict, arts: list[model.Artifact]) -> tuple[bool, list[str], list[str]]:
    """上流工程が全部 confirmed/frozen でなければ、下流工程の成果物は存在してはいけない。"""
    err: list[str] = []
    warn: list[str] = []
    # ID を持たない成果物（管理文書・ソース）も「その工程が始まっている」証拠になる。
    by_mod_all: dict[tuple[str, str], list[model.Artifact]] = defaultdict(list)
    for a in arts:
        by_mod_all[(a.case, a.module)].append(a)
    for (case, module), lst in by_mod_all.items():
        stages = sorted({a.stage for a in lst if a.stage})
        # 阻塞項（block: true の ISS）が止めている工程は、そもそも着手できない
        blockers = [a for a in lst
                    if a.type == "ISS" and a.data.get("block") is True
                    and a.status not in R.APPROVED_STATUS]
        for b in blockers:
            target = b.data.get("blocks_stage")
            if target and target in stages:
                err.append(
                    f"G4 阻塞: {module} 工程{target} の成果物がありますが、"
                    f"未解決の阻塞項 {b.id} が止めています（{b.data.get('title', '')}）"
                )
        for st in stages:
            bad = [a for a in lst
                   if a.stage in _parents(st) and a.status not in R.APPROVED_STATUS]
            if bad:
                sample = ", ".join(f"{a.id}({a.status})" for a in bad[:3])
                err.append(
                    f"G4 人工卡点違反: {module} 工程{st} の成果物がありますが、"
                    f"上流 {len(bad)} 件が未承認です（{sample}）"
                )
    return (not err), err, warn


# =============================================================================
# G5 文書一貫性
# =============================================================================
# コマンド判定は「バッククォート内」か「行頭」だけ。本文中のパス（/api/...）を誤検出しないため。
_CMD = re.compile(r"`/([a-z][a-z0-9-]{2,})`|^/([a-z][a-z0-9-]{2,})", re.M)


def g5(ledger: dict, arts: list[model.Artifact]) -> tuple[bool, list[str], list[str]]:
    err: list[str] = []
    warn: list[str] = []

    # (a) YAML のキーは snake_case（定義層）
    def walk(node, trail: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(k, str) and not ALLOWED_KEY.match(k):
                    err.append(f"G5 命名分区違反: {trail} → キー `{k}` は snake_case ではありません")
                walk(v, f"{trail}.{k}" if trail else str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{trail}[{i}]")

    for a in arts:
        if a.suffix_yaml and not a.error:
            walk(a.data, a.rel)

    # (b) 管理文档は台帳に登録されていること
    mg_paths = {str(d.get("path")) for d in (ledger.get("management_docs") or [])
                if isinstance(d, dict)}
    mg_names = {str(d.get("doc")) for d in (ledger.get("management_docs") or [])
                if isinstance(d, dict)}
    for a in arts:
        if isinstance(a.data, dict) and a.data.get("doc"):
            # パスで登録されているかを見る（名前だけだとモジュール間で取り違える）
            if a.rel not in mg_paths:
                err.append(f"G5 管理文書が未登録: {a.rel}（doc: {a.data['doc']}）")
            elif str(a.data["doc"]) not in mg_names:
                err.append(f"G5 管理文書名が不一致: {a.rel}（{a.data['doc']}）")

    # (c) 文書に書いたコマンドが実在するか／実在する skill が文書に載っているか
    root = paths.root()
    skills = {p.name for p in (root / ".claude" / "skills").iterdir() if p.is_dir()} \
        if (root / ".claude" / "skills").is_dir() else set()
    mentioned: set[str] = set()
    for doc in ("README.md", "使用手册.md"):
        p = root / doc
        if not p.is_file():
            continue
        for m in _CMD.finditer(p.read_text(encoding="utf-8")):
            mentioned.add(m.group(1) or m.group(2))
    for cmd in sorted(mentioned - skills):
        if cmd in ("approve", "status", "change") and cmd in skills:
            continue
        err.append(f"G5 文書に書かれたコマンドが存在しません: /{cmd}")
    for s in sorted(skills - mentioned):
        warn.append(f"G5 skill が文書に載っていません: /{s}")
    return (not err), err, warn


# =============================================================================
# G6 機密ゼロヒット
# =============================================================================
_PATTERNS = [(name, re.compile(rx)) for name, rx in R.SECRET_PATTERNS]


def _is_placeholder(text: str) -> bool:
    return any(tok in text for tok in R.PLACEHOLDER_TOKENS)


def scan_text(text: str) -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []
    for name, rx in _PATTERNS:
        for m in rx.finditer(text):
            frag = m.group(0)
            if _is_placeholder(frag):
                continue
            hits.append((name, frag))
    return hits


def g6(ledger: dict, arts: list[model.Artifact]) -> tuple[bool, list[str], list[str]]:
    err: list[str] = []
    warn: list[str] = []
    root = paths.root()
    exempt = {paths.root() / p for p in R.SECRET_EXEMPT}

    targets: list[Path] = []
    for a in arts:
        targets.append(a.path)
    for sub in (".claude", "templates", "plat", "registry", "knowledge"):
        d = root / sub
        if d.is_dir():
            targets.extend(p for p in d.rglob("*")
                           if p.is_file() and p.suffix.lower() in (".md", ".py", ".yaml", ".yml", ".txt", ".json"))
    for doc in ("README.md", "使用手册.md"):
        if (root / doc).is_file():
            targets.append(root / doc)

    seen: set[Path] = set()
    for p in targets:
        rp = p.resolve()
        if rp in seen or rp in {e.resolve() for e in exempt if e.exists()}:
            continue
        seen.add(rp)
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for name, frag in scan_text(text):
            masked = frag if len(frag) <= 4 else frag[:2] + "***" + frag[-2:]
            err.append(f"G6 機密の形を検出: {paths.rel(p)} [{name}] {masked}")
    return (not err), err, warn


# =============================================================================
# 実行
# =============================================================================
GATES = (
    ("gate1", "ID 合法性", g1),
    ("gate2", "追跡閉ループ", g2),
    ("gate3", "成果物形式", g3),
    ("gate4", "人工卡点", g4),
    ("gate5", "文書一貫性", g5),
    ("gate6", "機密ゼロヒット", g6),
)


def run(only: int | None = None) -> dict:
    ledger = model.load_ledger()
    arts = model.load_all()
    result: dict = {"gates": {}, "stats": {}}
    all_ok = True
    for i, (name, label, fn) in enumerate(GATES, start=1):
        if only and i != only:
            continue
        ok, err, warn = fn(ledger, arts)
        result["gates"][name] = {"label": label, "ok": ok, "error": err, "warn": warn}
        all_ok = all_ok and ok
    result["stats"] = {
        "ids": len(model.ledger_ids(ledger)),
        "artifacts": len([a for a in arts if a.id]),
        "orphans": sum(1 for v in result["gates"].values() for w in v["warn"] if w.startswith("W1")),
        "hits": sum(len(v["error"]) for v in result["gates"].values()),
        "gates_run": len(result["gates"]),
    }
    result["ok"] = all_ok
    return result


def format_line(res: dict) -> str:
    parts = [f"{k}={('PASS' if v['ok'] else 'FAIL')}" for k, v in res["gates"].items()]
    s = res["stats"]
    return ("[gate] " + " ".join(parts) +
            f" | ids={s['ids']} artifacts={s['artifacts']} orphans={s['orphans']} hits={s['hits']}")


def print_report(res: dict) -> None:
    for name, v in res["gates"].items():
        mark = "PASS" if v["ok"] else "FAIL"
        print(f"\n=== {name} {v['label']} : {mark}")
        for e in v["error"]:
            print(f"  ERROR {e}")
        for w in v["warn"]:
            print(f"  WARN  {w}")
    print()
    print(format_line(res))


def main(only: int | None = None, as_json: bool = False) -> int:
    res = run(only=only)
    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print_report(res)
    return 0 if res["ok"] else 1

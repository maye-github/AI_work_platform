# -*- coding: utf-8 -*-
"""`python -m plat <command>` —— プラットフォーム唯一の CLI 入口。

**すべての機械的な作業はここから**。skill は「人に何を聞くか」を決めるだけで、
検査・発番・書き出しは本 CLI が行う（AI に数えさせない）。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _utf8() -> None:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _need_module(name: str | None):
    from . import paths
    if not name:
        mods = paths.modules()
        if len(mods) == 1:
            return mods[0]
        if not mods:
            raise SystemExit("案件がありません。先に `plat init --case <案件> --module <模块> --block 100`")
        raise SystemExit("--module を指定してください（複数あります: "
                         + ", ".join(f"{c}/{m}" for c, m, _ in mods) + "）")
    hit = paths.find_module(name)
    if not hit:
        raise SystemExit(f"モジュールが見つかりません: {name}")
    return hit


# ---------------------------------------------------------------- サブコマンド
def cmd_init(a) -> int:
    import datetime as dt

    import yaml

    from . import ids as idsmod, model, paths
    mod = paths.module_dir(a.case, a.module)
    mod.mkdir(parents=True, exist_ok=True)
    mp = mod / "module.yaml"
    if mp.is_file():
        raise SystemExit(f"既にあります: {paths.rel(mp)}")
    today = dt.date.today().isoformat()
    mp.write_text(
        yaml.dump({
            "case": a.case, "module": a.module,
            "title": a.title or a.module,
            "owner": a.owner or "",
            "status": "draft", "version": "0.1",
            "created_at": today,
            "updated_at": today,
            "note": "module.yaml は人が書く。plat init がひな形を作る",
        }, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    ledger = model.load_ledger()
    idsmod.ensure_module(ledger, a.case, a.module, a.block)
    idsmod.save(ledger)
    print(f"[init] 作成: {paths.rel(mp)}（号段 {a.block}xx）")
    print("[init] 次の 1 歩: /requirements")
    return 0


def cmd_gate(a) -> int:
    from . import gate
    return gate.main(only=a.only, as_json=a.json)


def cmd_status(a) -> int:
    from . import status
    print(status.render_all())
    return 0


def cmd_ids(a) -> int:
    from . import ids as idsmod, model
    ledger = model.load_ledger()

    if a.action == "block":
        hit = _need_module(a.module)
        idsmod.ensure_module(ledger, hit[0], hit[1], a.block)
        idsmod.save(ledger)
        print(f"[ids] {hit[0]}/{hit[1]} の号段を {a.block}xx に設定")
        return 0

    if a.action == "alloc":
        hit = _need_module(a.module)
        out = idsmod.alloc(ledger, hit[0], hit[1], a.type, a.title or "", a.owner or "",
                           a.artifact or "", count=a.count)
        for i in out:
            print(f"[ids] 発番: {i}（{hit[1]}）")
        return 0

    if a.action == "list":
        items = model.ledger_ids(ledger)
        for k, v in sorted(items.items()):
            if a.module and a.module not in k:
                continue
            if a.status and v.get("status") != a.status:
                continue
            print(f"{k:<34} {v.get('status', ''):<10} {v.get('title', '')}")
        print(f"--- 計 {len(items)} 件")
        return 0

    if a.action == "verify":
        arts = model.load_all()
        err, warn = idsmod.verify(ledger, arts)
        for e in err:
            print("ERROR", e)
        for w in warn:
            print("WARN ", w)
        print(f"[ids] verify: ids={len(model.ledger_ids(ledger))} error={len(err)} warn={len(warn)}")
        return 0 if not err else 1

    if a.action == "doc":
        if not a.doc:
            raise SystemExit("--doc を指定してください")
        if a.status:
            idsmod.set_doc_status(ledger, a.doc, a.status, a.by,
                                  path=a.path, module=a.module)
            print(f"[ids] 管理文書 {a.doc} → {a.status}" + (f"（承認者 {a.by}）" if a.by else ""))
            return 0
        if not a.artifact:
            raise SystemExit("--artifact を指定してください（status を変える場合は --status）")
        e = idsmod.register_doc(ledger, a.doc, a.artifact, a.title or a.doc, a.owner or "")
        print(f"[ids] 管理文書を登録: {e['doc']} → {e['path']}")
        return 0

    if a.action in ("set-status", "deprecate"):
        hit = _need_module(a.module)
        if a.stage:
            keys = idsmod.keys_of_stage(ledger, hit[0], hit[1], a.stage)
        elif a.id:
            keys = [f"{hit[0]}/{hit[1]}/{i}" for i in a.id]
        else:
            raise SystemExit("--id か --stage を指定してください")
        if not keys:
            raise SystemExit("対象がありません")
        if a.action == "set-status":
            idsmod.set_status(ledger, keys, a.status, a.by)
            print(f"[ids] status → {a.status}: {len(keys)} 件" + (f"（承認者 {a.by}）" if a.by else ""))
        else:
            idsmod.deprecate(ledger, keys, a.note or "", a.by)
            print(f"[ids] deprecated: {len(keys)} 件")
        for k in keys:
            print("  ", k)
        return 0

    raise SystemExit(f"未知の action: {a.action}")


def cmd_kpi(a) -> int:
    from . import kpi
    print(kpi.render(kpi.compute(case=a.case, module=a.module)))
    return 0


def cmd_impact(a) -> int:
    from . import impact
    print(impact.render(impact.analyze(a.id, module=a.module)))
    return 0


def cmd_export(a) -> int:
    from . import export
    for line in export.run(module=a.module, case=a.case,
                           out_dir=Path(a.out) if a.out else None, fmt=a.fmt):
        print("[export]", line)
    return 0


def cmd_mask(a) -> int:
    from . import mask
    if a.action == "assign":
        if not a.plain or not a.code:
            raise SystemExit("--plain と --code を指定してください")
        e = mask.assign(a.plain, a.code, a.category)
        print(f"[mask] 登録: {e['plain']} → {e['code']}")
        return 0
    if a.action == "prep":
        if not a.module and not (a.src and a.out):
            raise SystemExit("--module か、--src と --out を指定してください")
        case = module = ""
        if a.module:
            hit = _need_module(a.module)
            case, module = hit[0], hit[1]
        res = mask.prep(case=case, module=module, src=a.src, out=a.out)
        print(f"[mask] prep: files={res['files']} known={res['known']} "
              f"patterns={res['patterns']} unsupported={len(res['unsupported'])} "
              f"candidates={res['candidates']}")
        print(f"[mask] 出力: {res['out']}")
        if res["unsupported"]:
            print("[mask] ⚠ 未脱敏（AI に渡さない）: " + ", ".join(res["unsupported"]))
            print("[mask]   人がテキスト化して raw/ に置き直し、再実行してください")
        return 0
    if a.action == "apply":
        changed = mask.apply(write=a.write)
        for p, n in changed:
            print(f"[mask] {'置換' if a.write else '（dry-run）置換候補'}: {p} : {n} 箇所")
        if not changed:
            print("[mask] 置換対象なし")
        if changed and not a.write:
            print("[mask] --write を付けると実際に書き換えます")
        return 0
    if a.action == "check":
        err = mask.check()
        for e in err:
            print("ERROR", e)
        print(f"[mask] check: error={len(err)}")
        return 0 if not err else 1
    if a.action == "list":
        for e in mask.load_map():
            plain = "****" if a.safe else e.get("plain")
            print(f"{e.get('code'):<14} {plain}")
        return 0
    raise SystemExit(f"未知の action: {a.action}")


def cmd_adopt(a) -> int:
    from . import adoption, model
    if a.action == "snapshot":
        arts = [x for x in model.load_all() if x.id]
        if a.module:
            arts = [x for x in arts if x.module == a.module]
        n = 0
        for art in arts:
            if adoption.snapshot(art, force=a.force):
                print(f"[adopt] 初稿を記録: {art.key}（{len(adoption.items_of(art))} 条目）")
                n += 1
        if not n:
            print("[adopt] 新しい初稿はありません（既に記録済み、または draft 以外）")
        return 0
    if a.action == "note":
        if not a.artifact_id or not a.item or not a.text:
            raise SystemExit("--artifact-id / --item / --text を指定してください")
        key = adoption.note(a.artifact_id, a.item, a.text, module=a.module)
        print(f"[adopt] 修正理由を記録: {key} / {a.item}")
        return 0
    s = adoption.summary(case=a.case, module=a.module)
    print(adoption.render(s, f"{a.case or '*'}/{a.module or '*'}"))
    return 0


def cmd_view(a) -> int:
    from . import view
    src = Path(a.source)
    if not src.is_file():
        raise SystemExit(f"見つかりません: {src}")
    out = view.convert(src, Path(a.out) if a.out else None)
    print(f"[view] {src} → {out}")
    return 0


def cmd_md(a) -> int:
    from . import render_md
    n = render_md.render(module=a.module, case=a.case, html=a.html)
    print(f"[md] {n} 件を readable/ に生成" + ("（.zh.html も生成）" if a.html else ""))
    return 0


def cmd_handoff(a) -> int:
    from . import handoff
    hit = _need_module(a.module)
    if a.write:
        out = handoff.write(hit[0], hit[1], session_id=a.session)
        print(f"[handoff] {out}")
    else:
        print(handoff.build(hit[0], hit[1], session_id=a.session))
    return 0


# ---------------------------------------------------------------- 入口
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="plat", description="AI 全链路软件工程平台 —— 検査・発番・書き出しの唯一入口")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="案件/モジュールを作る")
    s.add_argument("--case", required=True)
    s.add_argument("--module", required=True)
    s.add_argument("--block", type=int, default=100, help="号段の基数（100 → 101..199）")
    s.add_argument("--title")
    s.add_argument("--owner")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("gate", help="門番 6 道をまとめて実行")
    s.add_argument("--only", type=int, choices=range(1, 7))
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_gate)

    s = sub.add_parser("status", help="現在地（成果物から現算）")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("ids", help="ID 台帳の操作（台帳の唯一の書き込み口）")
    s.add_argument("action", choices=["alloc", "set-status", "deprecate", "verify", "list", "block", "doc"])
    s.add_argument("--doc", help="管理文書の識別子（TECH_STACK 等）")
    s.add_argument("--path", help="管理文書のパス（同名が複数あるときの特定用）")
    s.add_argument("--module")
    s.add_argument("--id", nargs="*")
    s.add_argument("--stage", type=int)
    s.add_argument("--type")
    s.add_argument("--title")
    s.add_argument("--owner")
    s.add_argument("--artifact")
    s.add_argument("--count", type=int, default=1)
    s.add_argument("--status")
    s.add_argument("--by")
    s.add_argument("--note")
    s.add_argument("--block", type=int)
    s.set_defaults(func=cmd_ids)

    s = sub.add_parser("kpi", help="KPI 六维（成果物から現算）")
    s.add_argument("--case")
    s.add_argument("--module")
    s.set_defaults(func=cmd_kpi)

    s = sub.add_parser("impact", help="変更影響分析")
    s.add_argument("id")
    s.add_argument("--module")
    s.set_defaults(func=cmd_impact)

    s = sub.add_parser("export", help="対外成果物（Excel/Word）へ書き出す")
    s.add_argument("--module")
    s.add_argument("--case")
    s.add_argument("--fmt", default="xlsx", choices=["xlsx", "docx"])
    s.add_argument("--out")
    s.set_defaults(func=cmd_export)

    s = sub.add_parser("mask", help="脱敏（対照表・置換・検査・取込前脱敏）")
    s.add_argument("action", choices=["assign", "apply", "check", "list", "prep"])
    s.add_argument("--plain")
    s.add_argument("--code")
    s.add_argument("--category", default="customer")
    s.add_argument("--write", action="store_true")
    s.add_argument("--safe", action="store_true")
    s.add_argument("--module")
    s.add_argument("--src", help="prep の入力（既定: requirements/raw/）")
    s.add_argument("--out", help="prep の出力（既定: requirements/ai_input/）")
    s.set_defaults(func=cmd_mask)

    s = sub.add_parser("adopt", help="採用率（初稿→承認版の修正量）")
    s.add_argument("action", nargs="?", default="report", choices=["report", "snapshot", "note"])
    s.add_argument("--module")
    s.add_argument("--case")
    s.add_argument("--force", action="store_true", help="既存スナップショットを上書き（非推奨）")
    s.add_argument("--artifact-id")
    s.add_argument("--item")
    s.add_argument("--text")
    s.set_defaults(func=cmd_adopt)

    s = sub.add_parser("view", help="機読源 .md → 人向け HTML（中文ビュー）")
    s.add_argument("source")
    s.add_argument("-o", "--out")
    s.set_defaults(func=cmd_view)

    s = sub.add_parser("md", help="機読源 YAML → 人読 Markdown（readable/ に生成）")
    s.add_argument("--module")
    s.add_argument("--case")
    s.add_argument("--html", action="store_true",
                   help="人読 MD から中国語ビュー .zh.html も生成する")
    s.set_defaults(func=cmd_md)

    s = sub.add_parser("handoff", help="SESSION_HANDOFF.md（新セッションへの交接単）")
    s.add_argument("--module", required=True)
    s.add_argument("--write", action="store_true")
    s.add_argument("--session")
    s.set_defaults(func=cmd_handoff)

    return p


def main(argv: list[str] | None = None) -> int:
    _utf8()
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

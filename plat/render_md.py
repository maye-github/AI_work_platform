# -*- coding: utf-8 -*-
"""機読源 YAML → 人読 Markdown（生成物）。

**位置づけ**
- 正は YAML。`readable/**/*.md` は `plat md` が生成する**閲覧用**で、手で編集しない。
- `readable/` は `model.load_module()` の skip_dirs に入れてあるため、門番の対象外。
- 文章は日本語（`.md` は日本語、という媒体規約に合わせる）。
"""
from __future__ import annotations

import datetime as dt

from . import model, paths


def _val(v) -> str:
    if v is None or v == [] or v == "":
        return "—"
    if isinstance(v, list):
        return " / ".join(str(x) for x in v)
    return str(v)


def _table(headers: list[str], rows: list[list]) -> str:
    if not rows:
        return "（なし）\n"
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        cells = []
        for c in row:
            s = _val(c).replace("|", "\\|").replace("\n", "<br>")
            cells.append(s)
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def _kv(pairs: list[tuple[str, object]]) -> str:
    return _table(["項目", "内容"], [[k, v] for k, v in pairs])


def _header(a: model.Artifact) -> str:
    d = a.data
    lines = [f"# {d.get('title') or a.id}", "",
             f"> **生成物**：`plat md` が機読源 `{a.rel}` から生成。手で編集しない。"
             f"修正は YAML に入れて再生成する。",
             f"> 生成日：{dt.date.today().isoformat()}", ""]
    lines.append(_kv([
        ("id", d.get("id")), ("type", d.get("type")), ("status", d.get("status")),
        ("version", d.get("version")), ("owner", d.get("owner")),
        ("updated_at", d.get("updated_at")), ("sensitivity", d.get("sensitivity")),
    ]))
    return "\n".join(lines) + "\n"


def _r(a: model.Artifact) -> str:
    out = ["## 要件一覧\n"]
    for it in a.data.get("requirements", []):
        out.append(f"### {it.get('id')}　{it.get('title', '')}\n")
        out.append(f"**要求**：{it.get('statement', '')}\n")
        out.append(_kv([
            ("入力", it.get("inputs")), ("出力", it.get("outputs")),
            ("受入条件", it.get("acceptance")), ("出所", it.get("source_ref")),
            ("関連", it.get("related_ids")),
        ]))
    return "\n".join(out)


def _q(a: model.Artifact) -> str:
    out = ["## 確認事項\n"]
    for it in a.data.get("questions", []):
        out.append(f"### {it.get('id')}　{it.get('question', '')}\n")
        out.append(_kv([
            ("なぜ聞くか", it.get("why")), ("選択肢", it.get("options")),
            ("影響", it.get("impact")), ("状態", it.get("status")),
            ("回答", it.get("answer")),
        ]))
    return "\n".join(out)


def _asm(a: model.Artifact) -> str:
    out = ["## 前提・仮定\n"]
    for it in a.data.get("assumptions", []):
        out.append(f"### {it.get('id')}\n")
        out.append(_kv([
            ("前提", it.get("text")), ("根拠", it.get("basis")),
            ("前提が崩れたら", it.get("if_wrong")), ("関連", it.get("related_ids")),
        ]))
    return "\n".join(out)


def _iss(a: model.Artifact) -> str:
    out = ["## 未決事項\n"]
    for it in a.data.get("issues", []):
        out.append(f"### {it.get('id')}\n")
        out.append(_kv([
            ("内容", it.get("text")), ("ブロック", it.get("block")),
            ("対象工程", it.get("blocks_stage")), ("解決", it.get("resolution")),
            ("提案", it.get("proposal")), ("根拠", it.get("rationale")),
            ("顧客確認", it.get("customer_confirmed")), ("関連", it.get("related_ids")),
        ]))
    return "\n".join(out)


def _f(a: model.Artifact) -> str:
    out = ["## 機能一覧\n"]
    for it in a.data.get("functions", []):
        out.append(f"### {it.get('id')}　{it.get('title', '')}\n")
        out.append(_kv([
            ("目的", it.get("purpose")), ("由来要件", it.get("req_ids")),
            ("トリガー", it.get("trigger")), ("前提", it.get("preconditions")),
            ("事後", it.get("postconditions")), ("入力", it.get("inputs")),
            ("出力", it.get("outputs")), ("補足", it.get("spec")),
            ("関連", it.get("related_ids")),
        ]))
    return "\n".join(out)


def _i(a: model.Artifact) -> str:
    rows = []
    for it in a.data.get("items", []):
        rows.append([it.get("id"), it.get("title"), it.get("kind"), it.get("data_type"),
                     it.get("length"), it.get("required"), it.get("source_req"),
                     it.get("spec")])
    return "## 画面項目\n\n" + _table(
        ["ID", "項目", "種別", "型", "桁", "必須", "由来要件", "補足"], rows)


def _d(a: model.Artifact) -> str:
    out = ["## データモデル\n"]
    for it in a.data.get("models", []):
        out.append(f"### {it.get('id')}　{it.get('title', '')}\n")
        out.append(_kv([
            ("物理名", it.get("table_name")), ("論理名", it.get("entity")),
            ("主キー", it.get("key")), ("注記", it.get("note")),
        ]))
        rows = [[c.get("name"), c.get("logical"), c.get("type"), c.get("length"),
                 c.get("required"), c.get("note")] for c in it.get("columns", [])]
        out.append(_table(["物理名", "論理名", "型", "桁", "必須", "注記"], rows))
    return "\n".join(out)


def _l(a: model.Artifact) -> str:
    out = ["## 業務ロジック\n"]
    for it in a.data.get("logic", []):
        out.append(f"### {it.get('id')}　{it.get('title', '')}\n")
        out.append(_kv([
            ("対応機能", it.get("belongs_to")), ("入力", it.get("inputs")),
            ("出力", it.get("outputs")), ("エラー", it.get("errors")),
            ("注記", it.get("note")),
        ]))
        steps = [[s.get("no"), s.get("do"), s.get("cond"), s.get("else")]
                 for s in it.get("steps", [])]
        out.append("**手順**\n\n" + _table(["#", "やること", "条件", "条件不成立時"], steps))
        bounds = [[b.get("item"), b.get("value"), b.get("expect")]
                  for b in it.get("boundaries", [])]
        if bounds:
            out.append("**境界値**\n\n" + _table(["項目", "値", "期待"], bounds))
    return "\n".join(out)


def _e(a: model.Artifact) -> str:
    rows = []
    for it in a.data.get("messages", []):
        rows.append([it.get("id"), it.get("title"), it.get("condition"),
                     it.get("message_id"), it.get("message"), it.get("action"),
                     it.get("severity")])
    return "## エラー・メッセージ\n\n" + _table(
        ["ID", "名称", "条件", "message_id", "メッセージ", "対処", "重要度"], rows)


def _tc(a: model.Artifact) -> str:
    rows = []
    for it in a.data.get("cases", []):
        rows.append([it.get("id"), it.get("title"), it.get("kind"), it.get("viewpoint"),
                     it.get("design_id"), it.get("input"), it.get("expected"),
                     it.get("result")])
    return "## 単体テストケース\n\n" + _table(
        ["ID", "タイトル", "区分", "観点", "設計", "入力", "期待", "結果"], rows)


def _it(a: model.Artifact) -> str:
    out = ["## シナリオ\n"]
    for it in a.data.get("scenarios", []):
        out.append(f"### {it.get('id')}　{it.get('title', '')}\n")
        out.append(f"**目的**：{it.get('goal', '')}\n")
        steps = [[s.get("no"), s.get("do"), s.get("expect")] for s in it.get("steps", [])]
        out.append(_table(["#", "操作", "期待"], steps))
        out.append(_kv([
            ("担保する要件", it.get("covers")), ("結果", it.get("result")),
            ("エビデンス", it.get("evidence")),
        ]))
    amap = a.data.get("acceptance_map", [])
    if amap:
        out.append("## 受入条件との対応\n")
        out.append(_table(["要件", "受入条件", "カバー", "未カバー理由"],
                          [[x.get("req_id"), x.get("acceptance"), x.get("covered_by"),
                            x.get("not_covered_reason")] for x in amap]))
    nf = a.data.get("non_functional_observations", [])
    if nf:
        out.append("## 非機能の観測点\n")
        out.append(_table(["観点", "目標", "観測"],
                          [[x.get("viewpoint"), x.get("target"), x.get("observed_by")]
                           for x in nf]))
    return "\n".join(out)


def _rel(a: model.Artifact) -> str:
    out = ["## リリース\n"]
    for it in a.data.get("release", []):
        out.append(_kv([
            ("バージョン", it.get("version")), ("環境", it.get("environment")),
            ("対象 ID", it.get("scope_ids")), ("変更点", it.get("notes")),
        ]))
        out.append("### 手順\n")
        out.append(_table(["#", "手順", "確認"],
                          [[s.get("no"), s.get("do"), s.get("check")]
                           for s in it.get("procedure", [])]))
        out.append("### 切戻し\n")
        out.append(_table(["#", "手順"],
                          [[s.get("no"), s.get("do")] for s in it.get("rollback", [])]))
        out.append(_kv([
            ("切戻し目標（分）", it.get("rollback_target_minutes")),
            ("切戻し演練", it.get("drilled")),
        ]))
        out.append("### 監視\n")
        out.append(_table(["指標", "閾値", "担当"],
                          [[m.get("metric"), m.get("threshold"), m.get("owner")]
                           for m in it.get("monitoring", [])]))
        out.append("### 判定条件の現状\n")
        out.append(_table(["条件", "状態", "根拠"],
                          [[c.get("condition"), c.get("state"), c.get("evidence")]
                           for c in it.get("criteria", [])]))
    return "\n".join(out)


def _doc(a: model.Artifact) -> str:
    doc = a.data.get("doc")
    if doc == "TECH_STACK":
        out = ["## 技術スタック\n"]
        stack = a.data.get("stack") or {}
        rows = []
        for k, v in stack.items():
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    rows.append([f"{k}.{k2}", v2])
            else:
                rows.append([k, v])
        out.append(_table(["項目", "内容"], rows))
        dec = a.data.get("decisions") or []
        if dec:
            out.append("## 選定理由\n")
            out.append(_table(["論点", "選択", "理由"],
                              [[d.get("topic"), d.get("choice"), d.get("why")]
                               for d in dec]))
        return "\n".join(out)
    if doc == "COMPONENTS":
        out = ["## 共通部品\n"]
        out.append(_table(["キー", "目的", "利用機能"],
                          [[c.get("key"), c.get("purpose"), c.get("used_by")]
                           for c in a.data.get("components", [])]))
        return "\n".join(out)
    if doc == "TRACEABILITY":
        out = ["## 設計-コード対応\n"]
        out.append(_table(["設計", "ロジック", "テスト観点", "ソース"],
                          [[t.get("design_id"), t.get("logic_ids"),
                            t.get("test_viewpoints"), t.get("source_files")]
                           for t in a.data.get("traces", [])]))
        out.append("## 未実装\n")
        out.append(_table(["ID", "理由"],
                          [[u.get("id"), u.get("reason")]
                           for u in a.data.get("unimplemented", [])]))
        out.append("## 設計外の実装\n")
        out.append(_table(["ファイル", "理由"],
                          [[e.get("file"), e.get("reason")]
                           for e in a.data.get("extra", [])]))
        return "\n".join(out)
    return _kv([(k, v) for k, v in a.data.items() if not isinstance(v, list)])


RENDERERS = {
    "R": _r, "Q": _q, "ASM": _asm, "ISS": _iss,
    "F": _f, "I": _i, "D": _d, "L": _l, "E": _e,
    "TC": _tc, "IT": _it, "REL": _rel,
}


def render_artifact(a: model.Artifact) -> str:
    body = _header(a)
    if a.data.get("doc"):
        body += "\n" + _doc(a)
    else:
        fn = RENDERERS.get(a.type)
        body += "\n" + (fn(a) if fn else _kv([(k, v) for k, v in a.data.items()]))
    return body + "\n"


def render(module: str | None = None, case: str | None = None, html: bool = False) -> int:
    arts = model.load_all()
    count = 0
    for a in arts:
        if a.error or not a.data:
            continue
        if module and a.module != module:
            continue
        if case and a.case != case:
            continue
        if not a.path.is_file() or a.path.suffix.lower() not in (".yaml", ".yml"):
            continue
        mod_root = paths.module_dir(a.case, a.module)
        rel = a.path.relative_to(mod_root)
        out = mod_root / "readable" / rel.with_suffix(".md")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_artifact(a), encoding="utf-8", newline="\n")
        if html:
            from . import view
            view.convert(out)
        count += 1
    return count

# -*- coding: utf-8 -*-
"""脱敏 —— 明文 ↔ 代号 の対照表。

**なぜ「置換スクリプト」ではなく「対照表」か**
対照表（`registry/MASK_MAP.yaml`）が唯一の写像であり、成果物には**代号しか書かない**。
こうすると「どの成果物に何が漏れているか」を機械で判定でき、対外版の作り直しも 1 コマンドで済む。
対照表そのものが機密なので `.gitignore` 済み（コミット禁止）。

使い方:
    plat mask assign --plain "<顧客名>" --code "<客户A>"     # 対照を登録
    plat mask apply  [--write]                              # 成果物の明文を代号へ置換
    plat mask check                                         # 残留明文 / 未登録代号を検査（gate6 の一部）
    plat mask list [--safe]                                 # 対照一覧（--safe は明文を伏せる）
"""
from __future__ import annotations

from pathlib import Path

import yaml

from . import model, paths


def load_map() -> list[dict]:
    p = paths.mask_map_file()
    if not p.is_file():
        return []
    try:
        d = model.load_yaml_doc(p)
    except Exception:
        return []
    return list(d.get("entries") or [])


def save_map(entries: list[dict]) -> None:
    p = paths.mask_map_file()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        yaml.dump({"entries": entries}, allow_unicode=True, sort_keys=False,
                  default_flow_style=False, width=4096),
        encoding="utf-8",
    )


def assign(plain: str, code: str, category: str = "customer") -> dict:
    entries = load_map()
    for e in entries:
        if e.get("plain") == plain:
            raise SystemExit(f"既に登録済みです: {plain} → {e.get('code')}")
        if e.get("code") == code:
            raise SystemExit(f"代号が重複しています: {code}")
    if not (code.startswith("<") and code.endswith(">")):
        code = f"<{code}>"
    e = {"code": code, "plain": plain, "category": category}
    entries.append(e)
    save_map(entries)
    return e


def _artifact_texts() -> list[Path]:
    """検査対象は成果物のみ。`raw/`（素材）と生成物は対象外。

    `raw/` は原文のままであり、`<host>:<port>` のような**書き方のための山括弧**を
    正当に含む。ここを検査対象にすると誤検出で門番が使えなくなる。
    """
    out: list[Path] = []
    for _case, _module, mod in paths.modules():
        for p in mod.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in (".yaml", ".yml", ".md"):
                continue
            if "raw" in p.relative_to(mod).parts:
                continue
            if p.name == "module.yaml":
                continue
            out.append(p)
    return out


def apply(write: bool = False) -> list[tuple[Path, int]]:
    entries = load_map()
    changed: list[tuple[Path, int]] = []
    for p in _artifact_texts():
        text = p.read_text(encoding="utf-8")
        new, n = text, 0
        for e in entries:
            plain = str(e.get("plain") or "")
            if not plain:
                continue
            n += new.count(plain)
            new = new.replace(plain, str(e.get("code")))
        if n:
            changed.append((p, n))
            if write:
                p.write_text(new, encoding="utf-8")
    return changed


import re

# 代号の形：`<客户A>` のような短い山括弧。HTML タグと紛れないよう長さと字種を絞る。
_CODE_LIKE = re.compile(r"<([A-Za-z0-9_぀-ヿ一-鿿]{1,10})>")
_HTML_TAGS = {
    "br", "b", "i", "u", "p", "em", "strong", "code", "pre", "ul", "ol", "li",
    "table", "tr", "td", "th", "h1", "h2", "h3", "h4", "div", "span", "a", "hr",
}
# 書き方のための山括弧（プレースホルダ）。代号ではないので指摘しない。
_TEMPLATE_PLACEHOLDERS = {
    "host", "port", "scheme", "path", "name", "value", "id", "n", "x",
    "案件", "模块", "人", "条目", "成果物ID", "案件名", "模块名", "例", "…",
}


def check() -> list[str]:
    """成果物に残る明文 / 未登録の代号を返す。空リスト = きれい。"""
    err: list[str] = []
    entries = load_map()
    codes = {str(e.get("code")) for e in entries}
    for p in _artifact_texts():
        text = p.read_text(encoding="utf-8")
        for e in entries:
            plain = str(e.get("plain") or "")
            if plain and plain in text:
                err.append(f"{paths.rel(p)}: 明文が残っています（{e.get('code')}）")
        for m in _CODE_LIKE.finditer(text):
            tok = m.group(0)
            inner = m.group(1)
            if (tok in codes or inner.lower() in _HTML_TAGS
                    or inner.lower() in _TEMPLATE_PLACEHOLDERS):
                continue
            err.append(f"{paths.rel(p)}: 未登録の代号 {tok}")
    return err

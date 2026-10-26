# -*- coding: utf-8 -*-
"""成果物与台账的读取层。

**成果物的两种形态（唯一真源在此）**
- `.yaml` … 单文档。开头可有 1 个 `---`，**不许有第二个**（否则 safe_load 会炸）。
            必填字段与业务字段同级。
- `.md`   … `---` 包住 front-matter，后面是正文。

位置的三个要素（case / module / stage）**一律由路径推出**，不从字段里读 —— 避免两处定义。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import paths, rules_data as R

ID_RE = re.compile(r"^([A-Z]{1,3})-(\d{3})$")


# =============================================================================
# front matter
# =============================================================================
def split_front(text: str) -> tuple[dict, str]:
    """`.md` の front-matter を分離する。無ければ空 dict と全文を返す。"""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines(keepends=True)
    if lines and lines[0].strip() != "---":
        return {}, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            head = "".join(lines[1:i])
            body = "".join(lines[i + 1:])
            try:
                d = yaml.safe_load(head) or {}
            except yaml.YAMLError:
                return {}, text
            return (d if isinstance(d, dict) else {}), body
    return {}, text


def load_yaml_doc(path: Path) -> dict:
    """`.yaml` を 1 ドキュメントとして読む。2 ドキュメントなら例外（規則違反）。"""
    text = path.read_text(encoding="utf-8")
    docs = list(yaml.safe_load_all(text))
    if len(docs) > 1:
        raise ValueError(
            f"{path}: YAML が {len(docs)} ドキュメントあります。"
            "本プラットフォームは単一ドキュメントのみ許可します"
            "（2 つ目の `---` を削除してください）"
        )
    d = docs[0] if docs else {}
    if not isinstance(d, dict):
        raise ValueError(f"{path}: YAML の最上位が mapping ではありません")
    return d


# =============================================================================
# 成果物
# =============================================================================
@dataclass
class Artifact:
    path: Path
    rel: str
    case: str
    module: str
    stage: int | None          # 1..8、判定できなければ None
    data: dict
    body: str = ""
    error: str | None = None

    # --- 便捷访问 ---
    @property
    def id(self) -> str:
        return str(self.data.get("id") or "")

    @property
    def type(self) -> str:
        return str(self.data.get("type") or "")

    @property
    def status(self) -> str:
        return str(self.data.get("status") or "")

    @property
    def related(self) -> list[str]:
        v = self.data.get("related_ids") or []
        return [str(x) for x in v] if isinstance(v, list) else []

    @property
    def key(self) -> str:
        """台帳のキー：`<case>/<module>/<ID>`。"""
        return f"{self.case}/{self.module}/{self.id}"

    @property
    def suffix_yaml(self) -> bool:
        return self.path.suffix.lower() in (".yaml", ".yml")

    def items(self) -> list[dict]:
        """成果物が持つ条目（`id` と `related_ids` を持つ dict）の一覧。

        集約ファイル（1 ファイルに複数の ID を収める）では、追溯は条目単位で張られる。
        条目が無い成果物（管理文書など）は front-matter 自体を 1 条目として扱う。
        """
        out: list[dict] = []
        if isinstance(self.data, dict):
            for _k, v in self.data.items():
                if isinstance(v, list):
                    for x in v:
                        if isinstance(x, dict) and x.get("id"):
                            rel = x.get("related_ids") or []
                            out.append({
                                "id": str(x["id"]),
                                "related_ids": [str(r) for r in rel] if isinstance(rel, list) else [],
                                "raw": x,
                            })
        if out:
            return out
        if self.id:
            return [{"id": self.id, "related_ids": self.related, "raw": self.data}]
        return []

    @property
    def all_ids(self) -> list[str]:
        return [x["id"] for x in self.items()]


def _stage_from_rel(rel_in_module: str) -> int | None:
    for s in R.STAGES:
        d = s.artifact_dir.replace("\\", "/").strip("/")
        if rel_in_module == d or rel_in_module.startswith(d + "/"):
            return s.no
    return None


def load_module(case: str, module: str, mod_path: Path) -> list[Artifact]:
    """1 モジュール配下の成果物を全部読む。`module.yaml` と README は成果物ではない。"""
    out: list[Artifact] = []
    skip_dirs = {"node_modules", "__pycache__", ".venv", "venv", "dist", ".git", "raw"}
    for p in sorted(mod_path.rglob("*")):
        if not p.is_file():
            continue
        if any(part in skip_dirs for part in p.relative_to(mod_path).parts):
            continue
        if p.name in ("module.yaml", "README.md", "README.zh.html"):
            continue
        suffix = p.suffix.lower()
        if suffix not in (".yaml", ".yml", ".md"):
            continue
        rel_in_mod = p.relative_to(mod_path).as_posix()
        art = Artifact(
            path=p, rel=paths.rel(p), case=case, module=module,
            stage=_stage_from_rel(rel_in_mod), data={},
        )
        try:
            if suffix == ".md":
                fm, body = split_front(p.read_text(encoding="utf-8"))
                art.data, art.body = fm, body
            else:
                art.data = load_yaml_doc(p)
        except Exception as e:  # 読めない成果物も「報告対象」にする（黙って飛ばさない）
            art.error = str(e)
        out.append(art)
    return out


def load_all() -> list[Artifact]:
    out: list[Artifact] = []
    for case, module, path in paths.modules():
        out.extend(load_module(case, module, path))
    return out


# =============================================================================
# 台帳
# =============================================================================
EMPTY_LEDGER: dict = {
    "schema": "1",
    "updated_at": "",
    "cases": {},
    "ids": {},
    "management_docs": [],
    "changes": [],
}


def load_ledger() -> dict:
    p = paths.registry_file()
    if not p.is_file():
        return dict(EMPTY_LEDGER)
    d = load_yaml_doc(p)
    for k, v in EMPTY_LEDGER.items():
        d.setdefault(k, v)
    return d


def ledger_ids(ledger: dict) -> dict[str, dict]:
    """`<case>/<module>/<ID>` → 条目。"""
    v = ledger.get("ids") or {}
    return v if isinstance(v, dict) else {}


def split_key(key: str) -> tuple[str, str, str]:
    parts = key.split("/")
    if len(parts) != 3:
        return "", "", key
    return parts[0], parts[1], parts[2]


def id_type(id_str: str) -> str:
    m = ID_RE.match(id_str or "")
    return m.group(1) if m else ""


def id_num(id_str: str) -> int | None:
    m = ID_RE.match(id_str or "")
    return int(m.group(2)) if m else None


def block_of(ledger: dict, case: str, module: str) -> int | None:
    node = ((ledger.get("cases") or {}).get(case) or {}).get("modules") or {}
    m = node.get(module) or {}
    b = m.get("block")
    return int(b) if isinstance(b, (int, str)) and str(b).isdigit() else None

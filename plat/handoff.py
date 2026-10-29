# -*- coding: utf-8 -*-
"""SESSION_HANDOFF.md —— 新セッションに状態を引き継ぐための**交接単**（成果物ではない）。

**なぜチャットではなくファイルか**
新セッションは前の会話を自動では読まない。成果物から現算した状態と、
AI が残した「なぜ」だけを 1 ページにまとめ、`SessionStart` と `CLAUDE.md` で読ませる。

- 生成物の状態・门禁・次工程は**成果物から現算**する（手書きしない）
- `AI-NOTES` 区間だけは AI/人が書く。再生成しても保持する
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

from . import gate, model, paths, status

_NOTES_BEGIN = "<!-- AI-NOTES:BEGIN -->"
_NOTES_END = "<!-- AI-NOTES:END -->"


def _existing_notes(path: Path) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    if _NOTES_BEGIN in text and _NOTES_END in text:
        a = text.index(_NOTES_BEGIN) + len(_NOTES_BEGIN)
        b = text.index(_NOTES_END)
        return text[a:b].strip("\n")
    return ""


def _module_yaml(case: str, module: str) -> dict:
    p = paths.module_dir(case, module) / "module.yaml"
    if not p.is_file():
        return {}
    try:
        return model.load_yaml_doc(p)
    except Exception:
        return {}


def build(case: str, module: str, session_id: str | None = None) -> str:
    arts = [a for a in model.load_all() if a.case == case and a.module == module]
    mod = paths.module_dir(case, module)
    meta = _module_yaml(case, module)
    st = status.render(case, module, arts)
    res = gate.run()
    gate_line = gate.format_line(res)

    rows = status.module_status(case, module, arts)
    cmd, _ = status.next_command(rows)

    out = [
        f"# SESSION_HANDOFF — {case}/{module}",
        "",
        f"> 生成: {dt.date.today().isoformat()} ／ 本ファイルは**交接単**（成果物ではない。門番対象外）。",
        f"> 原文は `raw/` にあり、AI は直接読まない。脱敏副本は `requirements/ai_input/`。",
    ]
    if session_id:
        out.append(f"> 前回セッション: `{session_id}`")
    out += ["", "## 現在地", "", "```", st, "```", "", "## 門番", "", "```", gate_line, "```", ""]

    known = meta.get("known_issues") or []
    simulated = meta.get("simulated_decisions") or []
    if known:
        out += ["## 既知の遺留", ""] + [f"- {x}" for x in known] + [""]
    if simulated:
        out += ["## 模拟決定", ""] + [f"- {x}" for x in simulated] + [""]

    out += ["## 次の 1 歩", ""]
    out.append(f"- {cmd}" if cmd else "- （全工程 承認済）")
    out += ["", "## 次セッション必読", ""]
    out.append("- `module.yaml`（known_issues / simulated_decisions）")
    for a in sorted(arts, key=lambda x: x.rel):
        out.append(f"- `{a.rel}`")
    out += [
        "- `backlog/backlog.yaml`（未排期）",
        "- `knowledge/traps.md`（踩坑）",
        "",
        "## AI-NOTES（今回決めたこと・なぜ／3〜5 条）",
        "",
        _NOTES_BEGIN,
        _existing_notes(mod / "SESSION_HANDOFF.md") or "（未記入）",
        _NOTES_END,
        "",
    ]
    return "\n".join(out)


def write(case: str, module: str, session_id: str | None = None) -> Path:
    mod = paths.module_dir(case, module)
    out = mod / "SESSION_HANDOFF.md"
    out.write_text(build(case, module, session_id), encoding="utf-8", newline="\n")
    return out

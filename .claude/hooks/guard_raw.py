#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PreToolUse 钩子 —— AI 不得直接读 `raw/`。

**允许**：`python -m plat mask prep ...`（这个脚本替 AI 读 raw、写脱敏副本）。
**阻断**：Read / Grep / Glob / Bash 只要碰到 `raw/` 目录，就 exit 2。
"""
from __future__ import annotations

import json
import re
import sys

_RAW = re.compile(r"(^|[/\\])raw(?=$|[/\\\"'\s])")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    tool = str(payload.get("tool_name") or "")
    if tool not in ("Read", "Grep", "Glob", "Bash"):
        return 0
    text = json.dumps(payload.get("tool_input") or {}, ensure_ascii=False)

    # 脱敏スクリプトは raw を読む唯一の正規ルート。AI が実行してもよい。
    if "plat mask prep" in text:
        return 0

    # 正規化済みの raw_requirements.md は脱敏後の成果物。読み書きしてよい。
    if "raw_requirements.md" in text:
        return 0

    if _RAW.search(text):
        print(
            "[guard_raw] raw/ は AI が直接読めません。"
            "`python -m plat mask prep --module <模块>` を実行し、"
            "`requirements/ai_input/` を読んでください。",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PostToolUse 钩子 —— 成果物落盘后自动跑门禁，把问题**立刻**摆到 AI 面前。

**故意不阻断（始终 exit 0）**：
先写成果物、后补台账是正常的作业顺序。阻断会让人没法干活。
真正的闸门是 `/approve` 前的 `plat gate`。

只有当检查出 ERROR 时才输出内容；无问题时保持安静，避免刷屏。
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _utf8() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main() -> int:
    _utf8()
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    fp = ((payload.get("tool_input") or {}).get("file_path")
          or (payload.get("tool_input") or {}).get("notebook_path") or "")
    if not fp:
        return 0
    p = Path(fp)
    if p.suffix.lower() not in (".yaml", ".yml", ".md"):
        return 0
    try:
        rel = p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return 0
    if not rel.startswith("cases/"):
        return 0
    if p.name in ("module.yaml", "README.md"):
        return 0

    try:
        r = subprocess.run(
            [sys.executable, "-m", "plat", "gate", "--json"],
            cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", timeout=60,
        )
        res = json.loads(r.stdout or "{}")
    except Exception as e:  # フックは絶対に作業を止めない
        print(f"[hook] 門番を実行できませんでした: {e}", file=sys.stderr)
        return 0

    # 初稿スナップショット（採用率の測定用）。初回の書き込みだけ記録する。
    try:
        sys.path.insert(0, str(ROOT))
        from plat import adoption, model
        for art in model.load_all():
            if art.path.resolve() == p.resolve():
                adoption.snapshot(art)
                break
    except Exception as e:  # 計測できなくても作業は止めない
        print(f"[hook] スナップショットを取りませんでした: {e}", file=sys.stderr)

    hits = []
    for name, g in (res.get("gates") or {}).items():
        for e in g.get("error") or []:
            if rel in e or p.name in e:
                hits.append(f"{name}: {e}")
    if hits:
        print(f"[hook] {rel} を書いた直後の門番エラー（{len(hits)} 件）:")
        for h in hits[:10]:
            print("  " + h)
        print("[hook] 直すか、直せないなら止まって人に返してください（規約 §12）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

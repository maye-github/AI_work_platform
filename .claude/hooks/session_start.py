#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SessionStart フック —— 新セッションの冒頭に交接単・現在地・門番を出す。

- 最新の `SESSION_HANDOFF.md` を 1 つ選んで表示（5000 文字まで）
- `plat status` と `plat gate` の要約を表示
- 出力は新セッションのコンテキストに載る（載らない環境でも `CLAUDE.md` が読ませる）
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def main() -> int:
    _utf8()
    try:
        from plat import gate, paths, status

        handoffs = []
        for _case, _module, mod in paths.modules():
            p = mod / "SESSION_HANDOFF.md"
            if p.is_file():
                handoffs.append((p.stat().st_mtime, p))
        if handoffs:
            p = max(handoffs, key=lambda x: x[0])[1]
            print(f"[session-start] 交接单: {paths.rel(p)}")
            print(p.read_text(encoding="utf-8")[:5000])
            print()
        else:
            print("[session-start] SESSION_HANDOFF.md がありません。")
            print("  `python -m plat handoff --module <模块> --write` を実行してください。")
            print()

        print("[session-start] 現在地:")
        print(status.render_all())
        print("[session-start] 門番:")
        print(gate.format_line(gate.run()))
    except Exception as e:  # フックは絶対にセッションを止めない
        print(f"[session-start] 読み込みに失敗: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

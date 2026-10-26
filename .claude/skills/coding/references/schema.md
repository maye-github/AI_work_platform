# 工程5 成果物スキーマ（管理文書）

## src/TRACEABILITY.yaml
```yaml
doc: TRACEABILITY
title: コード-設計 追溯対照表
status: draft
version: 0.1
owner: <人>
created_at: 2026-01-01
updated_at: 2026-01-01
scope: <どの機能までを対象にしたか>
traces:
  - design_id: D-101
    logic_ids: [L-101, L-102]
    test_viewpoints: [TC-101]          # 工程6 で埋まる。それまでは空でよい
    source_files:
      - src/backend/.../xxx.py
unimplemented:                          # 設計にあるが未実装
  - id: L-103
    reason: <なぜ>
extra:                                  # 設計にないが実装した
  - file: src/backend/.../yyy.py
    reason: <なぜ>
```

> **`unimplemented` と `extra` を空にしないことが誠実さの証拠**。どちらも空なら
> 「本当に一致した」か「調べていない」かを人が確かめる。

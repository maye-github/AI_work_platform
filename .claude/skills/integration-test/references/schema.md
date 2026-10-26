# 工程7 成果物スキーマ

## IT.yaml ── 結合・総合テスト
```yaml
scenarios:
  - id: IT-101
    title: <シナリオ名>
    goal: <利用者が達成したいこと>
    steps:
      - no: 1
        do: <操作>
        expect: <期待>
    covers: [R-101, F-101]           # このシナリオが担保する要件
    result: pass | fail | manual | not_run
    evidence: <ログ・画面・コマンドのどこで確かめたか>
    related_ids: [R-101, F-101]
acceptance_map:                       # 受入条件 ↔ シナリオ
  - req_id: R-101
    acceptance: <受入条件の該当行>
    covered_by: [IT-101]
  - req_id: R-102
    acceptance: <受入条件>
    covered_by: []
    not_covered_reason: <なぜ今回はやらないか>   # 空にしない（静默未覆盖の禁止）
```

> **`covered_by: []` は許されるが、`not_covered_reason` は必須。**
> 空欄のまま残すと G2（網羅性）が FAIL する。

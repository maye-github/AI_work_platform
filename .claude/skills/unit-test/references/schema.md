# 工程6 成果物スキーマ

## TC.yaml ── 単体テストケース
```yaml
cases:
  - id: TC-101
    title: <用例名>
    kind: normal | boundary | error
    viewpoint: 同値分割 | 境界値 | デシジョンテーブル
    design_id: L-101                 # どの設計を検証するか（必須）
    error_id: E-101                  # 異常系なら必須
    preconditions: <前提>
    input: <入力>
    expected: <期待>
    result: pass | fail | skipped    # 実行後に埋める（空欄は「未実施」）
    actual: <実測（fail のとき必須）>
    related_ids: [L-101, E-101, R-101]
```

**比率の下限**：1 ロジックあたり `normal 3 / boundary 2 / error 3`。

## BUG.yaml ── 障害
```yaml
bugs:
  - id: BUG-101
    title: <事象>
    found_by: TC-101
    layer: design | implementation | test      # 責任層（人が決める）
    severity: high | medium | low
    reproduce: <再現手順>
    related_ids: [TC-101]
```

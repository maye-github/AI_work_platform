# 工程8 成果物スキーマ

## REL.yaml
```yaml
release:
  - id: REL-101
    version: v1.0.0
    environment: <本番 | 検証>
    scope_ids: [F-101, L-101]        # この版に含むもの
    notes: <変更点（ID から集約した結果）>
    procedure:
      - no: 1
        do: <手順>
        check: <次へ進む前に何を見るか>
    rollback:
      - no: 1
        do: <切戻し手順>
      target_minutes: <目標時間>
      drilled: false                 # 演練したか。していないなら false のまま
    monitoring:
      - metric: <見る指標>
        threshold: <閾値（決めていないなら null）>
        owner: <誰が見るか>
    criteria:                        # リリース判定条件の現状（事実のみ）
      - condition: <条件>
        state: met | unmet
        evidence: <根拠>
    related_ids: [F-101, L-101]
```

> **禁止**：「リリース可」「GO」と書くこと。判定は人が行う。本ファイルは**材料**である。

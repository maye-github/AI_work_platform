# 工程3 成果物スキーマ

## DSN.yaml ── データモデル（D）
```yaml
models:
  - id: D-101
    title: <モデル名>
    table_name: <物理名>
    entity: <論理名>
    key: [<主キー項目>]
    columns:
      - name: <物理名>
        logical: <論理名>
        type: string | number | date
        length: <桁>
        required: true | false
        note: <排他項目・既定値など>
    related_ids: [F-101]
```

## LGC.yaml ── 業務ロジック（L）
```yaml
logic:
  - id: L-101
    title: <ロジック名>
    belongs_to: F-101
    inputs: [I-101]
    outputs: [I-102]
    steps:
      - no: 1
        do: <やること>
        cond: <条件（あれば）>
        else: <そうでないとき（あれば）>
    boundaries:
      - item: <項目>
        value: <境界のちょうど>
        expect: <期待>
    errors: [E-101]
    related_ids: [F-101, D-101, E-101]
```

## ERR.yaml ── エラー／メッセージ（E）
```yaml
messages:
  - id: E-101
    condition: <どういうときに出すか>
    message: <利用者に見せる文（業務の言葉）>
    action: <利用者が次にすること>
    severity: error | warning | info
    related_ids: [L-101]
```

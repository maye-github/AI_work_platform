# 工程2 成果物スキーマ

## FNC.yaml ── 機能一覧
```yaml
functions:
  - id: F-101
    title: <機能名（体言止め）>
    purpose: <何のためにあるか 1 文>
    req_ids: [R-101]              # 由来の要件。空は創作
    trigger: <いつ動くか>
    preconditions: [<前提>]
    postconditions: [<事後状態>]
    inputs: [I-101, I-102]
    outputs: [I-103]
    related_ids: [R-101, I-101, I-102, I-103]
```

## SCR.yaml ── 画面項目（I）
```yaml
items:
  - id: I-101
    title: <項目名>
    screen: <画面名>
    kind: input | display | button | label
    data_type: string | number | date | code
    length: <桁（不明なら null）>
    required: true | false
    source_req: R-101             # この項目が要る理由（必須）
    related_ids: [R-101, F-101]
```

> **`source_req` が書けない項目は作らない。** 「あると便利」は要件ではない。

## IF.yaml ── 外部接口（任意）
```yaml
interfaces:
  - code: IF-101                  # 接口は独立 ID を持たない（所属機能に従う）
    belongs_to: F-101
    direction: inbound | outbound
    protocol: REST | file | batch
    endpoint: "GET /api/..."
    related_ids: [F-101]
```

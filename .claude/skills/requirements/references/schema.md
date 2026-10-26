# 工程1 成果物スキーマ

> 共通の必填項目は `.claude/rules/00-platform.md` §5。ここは**工程1 固有**の形だけ。

## 共通ヘッダ（4 ファイルとも同じ）

```yaml
---
id: R-101                 # plat ids alloc で発番したもの。手書き禁止
type: R                   # R / Q / ASM / ISS
title: <一覧の見出し>
status: draft
version: 0.1
related_ids: []           # 関連する ID（後から追記してよい）
owner: <人の識別子>
created_at: 2026-01-01
updated_at: 2026-01-01
sensitivity: internal
```

**注意**：`---` は先頭の 1 本だけ。**2 本目を書くとパーサが壊れる**（`plat gate` G3 が FAIL する）。

---

## REQ.yaml ── 要件一覧

```yaml
requirements:
  - id: R-101
    title: 短い名前（体言止め）
    statement: >
      誰が・何を・どうできる。1 文で。形容詞で終わらせない。
    inputs: [<何を入れるか>]
    outputs: [<何が出るか>]
    acceptance: [<どうなっていれば合格か。検証可能な形で>]
    source_ref: "raw/raw_requirements.md#<見出し>"
    related_ids: [Q-101]        # 紐づく確認事項・前提
```

| 字段 | 必須 | 意味 |
|---|---|---|
| `statement` | ○ | 1 文。**「〜できる」**の形にする |
| `acceptance` | ○ | 検証可能（数値・状態・画面のいずれかで判定できる） |
| `source_ref` | ○ | 出所。**無い要件は創作**（規約違反） |
| `inputs` / `outputs` | ○ | 空でも項目は置く |

---

## QST.yaml ── 日方确认事项

```yaml
questions:
  - id: Q-101
    question: <日方に聞く 1 文>
    why: <なぜ聞かないと決められないか>
    options: [<選択肢A>, <選択肢B>]     # 我方の案があれば書く（聞きっぱなしにしない）
    impact: <答えが変わると何が変わるか>
    status: open                        # open / answered
    answer: null                        # 日方の回答（人はこれを埋める）
```

> **我方が案を作れるものを Q にしない。** 運用の決め事は提案（案＋根拠）にして承認を求める。

---

## ASM.yaml ── 前提・仮定

```yaml
assumptions:
  - id: ASM-101
    text: <前提>
    basis: <なぜそう置けるか（出所 or 判断根拠）>
    if_wrong: <この前提が崩れたら何が壊れるか>
```

---

## ISS.yaml ── 未決事项

```yaml
issues:
  - id: ISS-101
    text: <未決の内容>
    block: true                 # true = これが解けないと次工程へ進めない
    blocks_stage: 1             # どの工程を止めるか
    owner: <解く人（人）>
    resolution: null
```

> `block: true` が残っている限り、`/approve` しても次工程へ進めない（`plat gate` G4 が止める）。

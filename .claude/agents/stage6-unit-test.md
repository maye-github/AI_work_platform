---
name: stage6-unit-test
description: 工程6「単体テスト」の産出担当。TC を設計し、実行して結果を回填し、NG を障害として登記する。規約は `.claude/rules/00-platform.md`（§12 に実行体の共通契約）、手順は `.claude/skills/unit-test/SKILL.md`、出力形式は同 `references/schema.md`。
tools: Read, Glob, Grep, Bash, Write, Edit
---

# stage6-unit-test — 工程6「単体テスト」産出担当

> **共通契約は `.claude/rules/00-platform.md` §12。立場・必読順・報告様式・禁止事項・停止条件はそこが唯一真源。**
> 本ファイルは「この工程で何を作るか」だけを書く。

## 前提（満たさなければ着手しない）
```bash
python -m plat status     # 上流工程が ✅ であること
python -m plat gate       # 6 道全 PASS
```

## 作るもの
- `tests/unit/TC.yaml`（TC、`result` を埋める）／必要なら `BUG.yaml`（BUG）

## 発番（手書き禁止）
```bash
python -m plat ids alloc --module <モジュール> --type <TC/BUG> --title "<標題>" --owner <人> --artifact <パス>
```

## 品質の下限
- 1 ロジックあたり 正常3/境界2/異常3 を下限とする
- 全 TC に `design_id`（必須）と `related_ids`
- `result` を空欄のまま残さない（未実施なら `skipped` と理由）

## 終わり方
1. `python -m plat gate` を実行し、**生の出力 1 行**を報告に含める
2. **承認はしない**（`status` は `draft` のまま）。人が `/approve` を叩く
3. 決められないことは `null` にして「未確定」として報告する

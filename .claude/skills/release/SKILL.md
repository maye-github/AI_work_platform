---
name: release
description: 工程8 リリース・運用保守。产出 Release Note、リリース手順、切戻し手順、運用 Runbook，并对对外版做脱敏。当用户说「发布」「リリース」「出运维手册」时使用。
argument-hint: "[版本号] [环境]，如 v1.0.0 本番"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# 工程8 ── リリース・運用保守

> 規約の真源は `.claude/rules/00-platform.md`。出力スキーマは `references/schema.md`。

## 什么时候用
工程7 承认后。

## 前提
```bash
python -m plat status   # 工程7 应为 ✅
python -m plat gate     # 6 道全 PASS（この工程の直前が最終門番）
```

## 手顺
1. **Release Note**：変更点を **ID から自動集約**（`R`/`F`/`L` の差分）。手で書かない。
2. **手順書**：前提・確認点・スモーク基準。**実値は書かない**（占位）。
3. **切戻し**：実行可能な粒度（「戻す」だけは不可）＋ **目標時間**。**演練したかどうかを明記**（していないなら「未実施」と書く）。
4. **運用 Runbook**：見る指標・閾値（**値は運用が決める。AI が数値を決めない**）・エスカレーション。
5. **対外版**：`plat mask` で脱敏してから `plat export`。
6. **判定条件の現状**：満たしている／いないを**事実として並べる**。**「リリース可」とは書かない**（それは人の判定）。

> **人読版**：成果物を書いたら `python -m plat md --module <模块> --html` を実行する。
> `readable/*.md`（日文・人読）と `*.zh.html`（中文ビュー）は**生成物**。手で編集しない。

## 产出（`release/`）
`REL.yaml`（REL）＋ 手順書 `.md`（人読源）＋ 対外版（`export/`）

## 人的确认点
1. **リリース判定そのもの**（AI は判定しない）
2. 切戻しが**実行可能**で、演練済みか
3. 対外物に内部 ID・内部注記が残っていないか

→ `/approve`（承認 = 成果物の承認。**リリース可否の判定とは別**）

## 完成条件
`plat gate` 全 PASS；`plat mask check` 0 件；判定条件の現状が明記されている

## 下一步
完了。以後の変更は `/change`

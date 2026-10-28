---
name: detail-design
description: 工程3 詳細設計。把基本設計下沉到「可编码」的精度：数据模型 D、业务逻辑 L、错误消息 E。当用户说「做详细设计」「詳細設計」「细化到能写代码」时使用。
argument-hint: "[案件/模块；省略则用唯一的模块]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# 工程3 ── 詳細設計

> 規約の真源は `.claude/rules/00-platform.md`。出力スキーマは `references/schema.md`。

## 前提
```bash
python -m plat status   # 工程2 应为 ✅
python -m plat gate
```

## 输入
`designs/basic/FNC.yaml`・`SCR.yaml`・`IF.yaml`

## 手顺
1. **データモデル（D）**：表・項目・型・桁・主キー・排他項目。**物理名と論理名の両方**を書く。
2. **ロジック（L）**：1 機能を 1〜3 個のロジックに分ける。各ロジックは **入力・分岐・出力・異常** を持つ。
3. **エラー（E）**：条件・消息・対処。**同じ条件で違うメッセージを出さない**。
4. **境界値**：L の中に境界値を明記（テストはここから機械的に作られる）。
5. **発番** → 書く（`status: draft`）→ `python -m plat gate`。

> **人読版**：成果物を書いたら `python -m plat md --module <模块> --html` を実行する。
> `readable/*.md`（日文・人読）と `*.zh.html`（中文ビュー）は**生成物**。手で編集しない。

## 产出（`designs/detail/`）
`DSN.yaml`（D）／`LGC.yaml`（L）／`ERR.yaml`（E）

## 人的确认点
1. **排他制御・更新日時**の取り扱い（後で直せない類の決定）
2. **異常系の網羅**：入力不正・対象なし・重複・権限・外部障害
3. **E のメッセージが業務の言葉になっているか**（技術用語を利用者に見せない）

→ `/approve`

## 完成条件
`plat gate` 6 道 PASS ＋ 本工程成果物 `confirmed`

## 下一步
`/framework` 与 `/coding`（**可以并行**：框架定了技术栈，编码按设计写字）

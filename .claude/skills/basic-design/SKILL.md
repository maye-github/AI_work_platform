---
name: basic-design
description: 工程2 基本設計。从已承认的要件 YAML 生成機能一覧（F）与画面項目（I），并给出每个机能的初步构成。当用户说「做基本设计」「基本設計」「把要件落成系统结构」时使用。
argument-hint: "[案件/模块；省略则用唯一的模块]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# 工程2 ── 基本設計

> 規約の真源は `.claude/rules/00-platform.md`。出力スキーマは `references/schema.md`。

## 什么时候用
工程1 的成果物全部 `confirmed` 之后。

## 前提（自己查，不满足就停）
```bash
python -m plat status     # 工程1 应为 ✅ 承認済
python -m plat gate       # 必须 6 道全 PASS
```
要件里还有 `block: true` 未决 → **不开始**，先回去问人。

## 输入
`requirements/REQ.yaml`（必须）、`QST.yaml` / `ASM.yaml`（作为限定条件的来源）

## 手顺
1. **機能（F）を切る**：1 つの `R` を 2〜5 個の機能に分ける。分けすぎたら 1 機能が小さすぎる合図。
2. **画面項目（I）を起こす**：画面に出す／入れるものを 1 項目 1 ID で。**I は「利用者が見る／触るもの」だけ**。
3. **来源を必ず張る**：`related_ids` に上流 `R` を書く。書けない F/I は**要件に無い＝創作**。
4. **発番**：`python -m plat ids alloc --module <模块> --type F|I --title ... --owner ... --artifact ...`
5. **書く** → `references/schema.md`。`status: draft`。
6. **自查**：`python -m plat gate`。

> **人読版**：成果物を書いたら `python -m plat md --module <模块> --html` を実行する。
> `readable/*.md`（日文・人読）と `*.zh.html`（中文ビュー）は**生成物**。手で編集しない。

## 产出（`designs/basic/`）
`FNC.yaml`（機能一覧 F）／`SCR.yaml`（画面項目 I）／必要なら `IF.yaml`（外部接口，附着在 F 上）

## 人的确认点
1. **F 的切分**是不是一条条能独立开发·测试的单位
2. **I 有没有多出来**（要件里没有的字段＝擅自扩范围）
3. **画面项目的粒度**（1 项目 1 ID，不要把一组当一个）

→ `/approve`

## 完成条件
`plat gate` 6 道 PASS ＋ 本工程成果物 `confirmed`

## 下一步
`/detail-design`

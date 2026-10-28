---
name: integration-test
description: 工程7 結合・総合テスト。梳理业务场景，产出结合测试仕样书（IT）与受入条件对照表，不允许出现静默未覆盖。当用户说「结合测试」「結合テスト」「端到端场景」时使用。
argument-hint: "[案件/模块；省略则全量]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# 工程7 ── 結合・総合テスト

> 規約の真源は `.claude/rules/00-platform.md`。出力スキーマは `references/schema.md`。

## 什么时候用
工程6 承认后。

## 前提
```bash
python -m plat status   # 工程6 应为 ✅
python -m plat gate
```

## 输入
`tests/unit/TC.yaml`・`designs/basic/`・`requirements/REQ.yaml`（受入条件）

## 手顺
1. **从业务场景出发**，不从模块出发：利用者が何をしたくて、どこまで到達するか。
2. **每个 R 的受入条件必须被至少 1 个 IT 覆盖**。覆盖不了的，**显式写成「不覆盖 + 理由」**（禁止静默遗漏）。
3. **发番**：`--type IT`（与单测的 TC 分开，便于区分责任层与阶段）
4. **写受入条件对照表**：R ↔ IT。
5. **执行**：能自动化的写脚本；不能的在 `result` 里写 `manual` 并记实测。
6. **自查**：`python -m plat gate`。

> **人読版**：成果物を書いたら `python -m plat md --module <模块> --html` を実行する。
> `readable/*.md`（日文・人読）と `*.zh.html`（中文ビュー）は**生成物**。手で編集しない。

## 产出（`tests/integration/`）
`IT.yaml`（IT）＋ 受入条件对照（同文件 `acceptance_map:` 段）

## 人的确认点
1. **场景是否覆盖了业务的主线**（不是接口的排列组合）
2. **不覆盖的部分和理由**——这是给客户的诚实清单
3. **非功能（性能・并发・排他）**：本工程至少要列出**观测点**，跑不跑由人决定

→ `/approve`

## 完成条件
`plat gate` 全 PASS；每条 R 要么被覆盖，要么在不覆盖清单里写明理由

## 下一步
`/release`

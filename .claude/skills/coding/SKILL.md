---
name: coding
description: 工程5 製造（コーディング）。严格按详细设计 YAML 产出源码与单元测试代码，并生成「设计-代码对应表」。当用户说「写代码」「実装」「按设计书实现」时使用。
argument-hint: "[案件/模块；省略则用唯一的模块]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# 工程5 ── 製造（コーディング）

> 規約の真源は `.claude/rules/00-platform.md`。出力スキーマは `references/schema.md`。

## 什么时候用
工程4 承认后。

## 前提
```bash
python -m plat status   # 工程4 应为 ✅（技术栈已承认——**不得擅改**）
python -m plat gate
```

## 输入
`designs/detail/DSN.yaml`・`LGC.yaml`・`ERR.yaml`、`framework/TECH_STACK.yaml`・`COMPONENTS.yaml`

## 手顺
1. **分层实现**：按 `TECH_STACK.commands` 定的栈与目录写。**逻辑一个 L 一个函数**，便于追溯。
2. **不让实现跑在设计前面**：设计里没有的分支不写；写了就在 TRACEABILITY 里标 `extra` 并告诉人。
3. **同时写单元测试代码**（用例本身在工程6 定；这里只保证可测：依赖可注入、外部调用可替身）。
4. **写对应表**：`src/TRACEABILITY.yaml` —— `design_id → logic_ids → test_viewpoints → source_files`。
5. **自查**：`python -m plat gate`（G5 查键名分区；G2 查追溯）。

## 产出（`src/`）
源码（后端/前端）＋ `src/TRACEABILITY.yaml`（管理文書）

## 人的确认点
1. **设计没写、代码里却有的东西**（`extra`）——补设计还是删代码？
2. **设计写了、代码里没有的东西**（`unimplemented`）——本期不做，还是漏了？
3. **异常处理的落点**：错误码在哪一层转成用户消息

→ `/approve`

## 完成条件
`plat gate` 全 PASS；`TRACEABILITY.yaml` 覆盖本模块所有 L

## 下一步
`/unit-test`

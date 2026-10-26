---
name: framework
description: 工程4 フレームワーク・環境構築。确定技术栈（人承认）、定共通部品与目录骨架、给出构建与检查命令。当用户说「定技术栈」「框架构筑」「搭项目骨架」时使用。
argument-hint: "[案件/模块；省略则用唯一的模块]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# 工程4 ── フレームワーク・環境構築

> 規約の真源は `.claude/rules/00-platform.md`。出力スキーマは `references/schema.md`。

## 什么时候用
工程3 承认后。**这是「技术选型」唯一被允许做决定的工程**——之后的工程不得擅自换栈。

## 前提
```bash
python -m plat status   # 工程3 应为 ✅
python -m plat gate
```

## 输入
`designs/detail/` 全量（D 决定 DB，L 决定运行时形态）

## 手顺
1. **提案技术栈**：语言・框架・DB・测试・构建。**每项给理由与替代案**，由人承认（`confidential` 案件要写清闭域要求）。
2. **定共通部品**：错误码体系・响应包装・日期时区・分页・权限。**共通部品是这批源码里唯一的复用层。**
3. **定目录骨架**：后端/前端的分层（api / service / logic / repository / model）。
4. **定命令**：build / test / lint / run。**写进 `TECH_STACK.yaml`，后面所有工程照着跑。**
5. **写管理文書**：`TECH_STACK`（栈）与 `COMPONENTS`（共通部品）。**它们是管理文档，不占 ID 号段**，登记到台账 `management_docs`。

## 产出（`framework/`）
`TECH_STACK.yaml`／`COMPONENTS.yaml`（**都没有 ID**，靠 `doc:` 字段标识）

## 人的确认点
1. **技术栈**——这是本工程唯一真正要拍板的事（承认后不得擅改）
2. **闭域/机密要求**是否满足（能不能把代码和样本送出网络）
3. **共通部品的边界**（哪些进共通、哪些留在业务里）

→ `/approve`（**注意：本工程无 ID 成果物，承认记录写在 `module.yaml` 的 `approved_stages` 里**）

## 完成条件
`TECH_STACK.yaml` 存在且 `status: confirmed`；`plat gate` 全 PASS

## 下一步
`/coding`

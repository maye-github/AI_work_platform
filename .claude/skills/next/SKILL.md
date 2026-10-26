---
name: next
description: 问路。判定当前进度、列出阻塞项、给出下一步该敲哪个命令。只读，不改任何东西。当用户问「现在到哪了」「下一步做什么」「卡在哪」「有哪些阻塞」时使用。
argument-hint: "[案件/模块；省略则全部]"
allowed-tools: Read, Glob, Grep, Bash
---

# 问路（只读）

## 手顺
```bash
python -m plat status      # 8 工程进度 + 下一步命令 + 阻塞项
python -m plat gate        # 6 道门现状
python -m plat kpi         # 六维指标（可选）
```

## 输出什么
1. 现在在哪个模块的哪个工程
2. 下一步的那一条命令
3. 阻塞项（`block: true` 的 ISS、门禁 ERROR）
4. 未承认的成果物件数

## 禁止
- **不要顺手改状态。** 问路就是问路。
- 不要在门禁 FAIL 的情况下说「可以继续」。

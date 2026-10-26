---
name: change
description: 变更管理。登记变更并顺着追溯链算出受影响的下游成果物，经人确认范围后标记失效、定向重做。当用户说「日方改需求了」「要件错了要改」「返工」「这条要重做」时使用。
argument-hint: "<变更的 ID>，如 R-101；可多个"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Edit
---

# 变更管理

> **変更は必ず上流から入れる。** 設計を直さずコードだけ直すのは、追跡を切る行為（紅線）。

## 手顺

1. **看影响面**（只读，不是承认）：
   ```bash
   python -m plat impact <ID> --module <模块>
   ```
   输出「下游（要重做）」「上游（要复核）」「起点工程（候选）」。

2. **起票**：`registry` 的 `changes:` 追加 1 条（`plat` 不代劳——**编号与退回工程由人定**）
   ```yaml
   changes:
     - id: CR-101              # 人发号
       target: R-101
       reason: <なぜ>
       raised_by: <顧客 | QA | 社内>
       raised_at: 2026-01-01
       reenter_stage: 1        # 人が決める
       state: raised           # raised → fixing → closed
   ```

3. **人确认重做范围**：下游全部要重做吗？有没有可以先放着的？

4. **标失效并重做**：受影响的下游改成 `draft`（不是删除），从 `reenter_stage` 重新走阶段命令。

5. **收货**：重做完成后跑 `plat gate`；人复核后再 `/approve`。

## 禁止
- AI 自己决定退回到哪个工程
- 直接删掉旧成果物（保留能看出「改了什么」）

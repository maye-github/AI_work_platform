---
name: approve
description: 阶段承认。汇总指定范围内成果物的条目统计与疑点清单供人判断，确认后一次性把 ID 台账与成果物 front matter 的 status 改为 confirmed。当用户说「承认」「批准这个阶段」「过」「承认节点N」时使用。
argument-hint: "<阶段名或范围，如 requirements / 工程1 / designs/basic/>"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Edit
---

# 阶段承认

> **承认是人的行为。** 本 skill 只做两件事：把材料摆到人面前、把人说的结论落到文件里。
> **AI 不得代替人下结论**——那等于自己批自己。

## 手顺

1. **摆材料**（不做判断）：
   ```bash
   python -m plat status                        # 现在到哪
   python -m plat gate                          # 6 道门现状
   python -m plat ids list --module <模块>      # 本阶段有哪些 ID、什么状态
   ```
   再列出**疑点**：未填的 `expected`/`actual`、`block: true` 的 ISS、`extra`/`unimplemented`、`not_covered_reason` 空着的项。

2. **问人**：把上面整理成一张表，问「哪些承认、哪些打回」。

3. **按人的结论落盘**（**必须带 `--by`，且是人的标识符**）：
   ```bash
   python -m plat ids set-status --module <模块> --stage <N> --status confirmed --by <人>
   ```
   - 打回的项：`--id <ID> --status draft`（退回）或 `--status deprecated --note "<理由>"`（废掉）

4. **（任意）改动过的条目写一句理由** —— 不强制，但它能把「AI 错在哪一类」变成可统计的：
   ```bash
   python -m plat adopt note --artifact-id <成果物ID> --item "<条目>" --text "<为什么改>"
   ```
   先看哪些条目被改了：`python -m plat adopt --module <模块>`（承认后自动有数）

5. **复验**：
   ```bash
   python -m plat gate
   ```

## 禁止
- `--by` 写 AI 的名字或留空
- 人没说「承认」就改成 `confirmed`
- 把「审查未做」记成「已承认」（未做就写「未做」）

## 下一步
`python -m plat status` 看下一个命令。

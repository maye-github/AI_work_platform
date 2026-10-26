---
name: requirements
description: 工程1 要件理解（含需求取込）。把日方给的 docx/xlsx/pdf/口头素材归一成带来源锚点的原始需求，再结构化成要件 YAML（R / Q / ASM / ISS）。当用户说「做需求」「要件定義」「整理日方资料」「把这份需求书吃进来」时使用。
argument-hint: "[案件/模块，如 PRJ01/ModuleA；省略则用唯一的模块]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# 工程1 ── 要件理解（含需求取込）

> 規約の真源は `.claude/rules/00-platform.md`。ここは**手順**だけ。
> 出力スキーマは `references/schema.md`。

## 什么时候用
拿到日方素材、要开始一个新模块时。**这是唯一允许「无中生有」的工程**——之后的工程都必须有上游。

## 前提（自己查，不满足就停下告诉人）

```bash
python -m plat status          # 该模块应当还没有工程1 的成果物
python -m plat gate            # 现有内容必须是 6 道全 PASS
```

## 输入
- `cases/<案件>/<模块>/raw/` 下的素材（docx / xlsx / pdf / png / txt）
- 或用户在对话里直接贴的口头需求
- 上一模块的同类成果物（**只当作写法参考，不当事实来源**）

## 手顺

1. **取込**：把每个素材读成 `raw/raw_requirements.md`。每条一段，**必须有来源锚点**：
   `> 出典: <文件名> / <页・sheet・行> / <摘录>`。读不了的（旧 .doc/.xls、扫描件）→ 记进“未取込”清单，不要猜。
2. **抽争议点**：曖昧・矛盾・前提不足 → 写成 `Q`（对日方确认事项），**不要自己定**。
3. **抽前提**：素材里没说但必须成立的东西 → `ASM`（前提假设），写明“若此前提不成立会怎样”。
4. **抽阻塞**：需要日方回答才能继续的 → `ISS` 且 `block: true`。
5. **结构化**：业务要求 → `R`。每条要能独立验收（含输入・处理・结果）。
6. **发号**：**先登台账再引用**。
   ```bash
   python -m plat ids alloc --module <模块> --type R --title "<标题>" --owner <人> --artifact requirements/REQ.yaml
   ```
   `Q` / `ASM` / `ISS` 同理（`--type Q` / `ASM` / `ISS`）。
7. **写成果物** → `references/schema.md` の形。`status: draft`、`related_ids` 必填。
8. **自查**：`python -m plat gate` 全 PASS。

## 产出（`cases/<案件>/<模块>/requirements/`）
| 文件 | 内容 | 类型 |
|---|---|---|
| `raw/raw_requirements.md` | 归一后的原始需求（带来源锚点） | 非成果物（不入 ID） |
| `REQ.yaml` | 要件一覧 | R |
| `QST.yaml` | 对日方确认事项 | Q |
| `ASM.yaml` | 前提・假设 | ASM |
| `ISS.yaml` | 未决事项（`block: true` 会挡住下一步） | ISS |

## 人的确认点（写完必须停下来问）
1. **R 的切分粒度**：一条 R 是不是「一个可独立验收的业务要求」？
2. **Q 是不是真该问日方**：能从素材里读出来的，不该变成 Q。
3. **ASM 能不能当默认值**：说明「若前提错了会怎样」。
4. **ISS 的 block 判定**：阻塞的是本工程，还是只阻塞后面某个工程？

→ 人确认后跑 `/approve`。

## 完成条件
- `plat gate` 6 道全 PASS
- 本工程成果物 `status: confirmed`（由 `/approve` 写入）
- 未决的 `block: true` 为 0

## 下一步
`/basic-design`

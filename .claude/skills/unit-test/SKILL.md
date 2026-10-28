---
name: unit-test
description: 工程6 単体テスト。先出单体测试仕样书（TC），再执行并回填实测值与覆盖率，NG 用例登记障害并判定责任层。当用户说「单测」「単体テスト」「跑单元测试」时使用。
argument-hint: "[案件/模块；省略则全量]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# 工程6 ── 単体テスト

> 規約の真源は `.claude/rules/00-platform.md`。出力スキーマは `references/schema.md`。

## 什么时候用
工程5 承认后。

## 前提
```bash
python -m plat status   # 工程5 应为 ✅
python -m plat gate
```

## 输入
`designs/detail/LGC.yaml`（分岐と境界値）・`ERR.yaml`（異常系）・`src/`

## 手顺
1. **先设计后执行**（设计没承认前不写测试代码）：
   每个 L 至少 **正常 3 / 境界 2 / 异常 3**。少于此比例即「设计未完成」。
2. **用例必须有出处**：`design_id`（L 或 E）＋ `related_ids`（含 `R`）。**出处が無い TC は廃品。**
3. **发番**：`python -m plat ids alloc --module <模块> --type TC ...`（**工程7 的 IT 另起类型**）
4. **执行**：按 `TECH_STACK.commands.test` 跑。结果回填 `result`（pass/fail）与实测值。
5. **NG → 障害**：`type: BUG` 的成果物（`bugs:` 段），写 `layer`（设计错 / 实现错 / 测试错）。
6. **覆盖**：把 `TRACEABILITY.yaml` 的 `test_viewpoints` 补上。
7. **自查**：`python -m plat gate`。

> **人読版**：成果物を書いたら `python -m plat md --module <模块> --html` を実行する。
> `readable/*.md`（日文・人読）と `*.zh.html`（中文ビュー）は**生成物**。手で編集しない。

## 产出（`tests/unit/`）
`TC.yaml`（TC）＋ 执行结果（附在 TC 每一项的 `result`）＋ 必要なら `BUG.yaml`

## 人的确认点
1. **观点的妥当性**（3/2/3 是下限，不是目标）
2. **NG 的责任层判定**——「测试错」是最容易被滥用的选项
3. **覆盖率不足的部分是不是真的不重要**

→ `/approve`

## 完成条件
`plat gate` 全 PASS；每个 L 至少 1 个 TC；`result` 全部填了（没有空白）

## 下一步
`/integration-test`

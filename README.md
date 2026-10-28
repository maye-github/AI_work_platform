# AI 全链路软件工程平台

对日软件开发的 **8 工程全链路流水线**。人敲命令、AI 干活、机械检查自动跑。
**平台本体不含任何业务**——客户案件全部在 `cases/` 下，由平台生成。

```
要件理解 → 基本設計 → 詳細設計 → 框架構築 → 製造 → 単体テスト → 結合测试 → リリース
   ↑ 每一步都必须人承认，AI 不能自己往下走
```

## 从哪开始

**第一次用 → 读 [`使用手册.md`](使用手册.md)**。

日常只用两件事：

```bash
python -m plat status        # 现在到哪、下一步敲什么、卡在哪
python -m plat gate          # 六道门：一条命令全查
```

阶段命令（**只有人能敲**，AI 推不动）：

`/requirements` 要件理解（含需求取込）· `/basic-design` 基本設計 · `/detail-design` 詳細設計
`/framework` 框架構築 · `/coding` 製造 · `/unit-test` 単体テスト
`/integration-test` 結合测试 · `/release` リリース

横切命令：`/approve` 承认 · `/change` 变更 · `/next` 问路

## 怎么跑起来

源码不集中到一个 `src/`：每个模块自带 `src/`，可独立构建/部署。根目录的 `Makefile` / `docker-compose.yml` 提供“一条命令”的体验。

```bash
# 本地开发（R60Login）
make dev-login-backend     # 后端 :8080
make dev-login-frontend    # 前端 :5173

# Docker（前后端一起起）
make up                    # 前端 http://localhost:8081 / 后端 http://localhost:8080/docs
make down
```

代码索引见 [`CODE_INDEX.md`](CODE_INDEX.md)。

## 三条硬约束（机制，不是口号）

1. **推进只能靠人敲命令** —— 11 个 skill 全部设了 `disable-model-invocation: true`。
2. **承认只能由人做** —— `/approve` 必须带人的标识符；AI 写承认栏 = 自己批自己。
3. **机检查不通过就不许往下走** —— `plat gate` 六道门，ERROR 一条都不许留。

## 目录

```
plat/          核心 CLI（发号・门禁・度量・导出・脱敏・视图）—— 唯一入口
.claude/       rules 2 份 / skills 11 个 / agents 9 个 / hooks 1 个
templates/     8 个阶段的输入模板（人填）
registry/      ID 台账（唯一发号口，只许脚本写）
knowledge/     踩坑记录（进化的起点）
cases/         客户案件成果（每个模块自带 requirements/designs/src/tests/release）
backlog/       待办池（未排期，不进 ID 台账）
presentation/  给领导演示的 PPT 稿 + HTML
export/        生成的 Excel / Word（gitignore）
CODE_INDEX.md  模块 → 代码路径 → 启动命令
Makefile       一条命令 gate / status / md / test / dev / up
docker-compose.yml  前端 + 后端一键启动
env.example    环境变量样例（复制成 .env）
```

## 需要装什么

Python 3.10+、`pyyaml`、`openpyxl`（Excel 导出）。Word 导出另需 `python-docx`（可选）。

```bash
pip install pyyaml openpyxl python-docx
```

> Windows 上如果 `python` 指向 Microsoft Store 的占位程序，改用 `py -3 -m plat ...`。

## 一句话

**命令是人敲的，活是 AI 干的，检查是机器做的，责任是人担的。**

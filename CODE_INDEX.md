# 代码索引

> **源码不集中到一个 `src/`。** 每个模块自带 `src/`，便于独立构建、独立部署、独立追溯。
> 一条命令启动见根目录 `Makefile` / `docker-compose.yml`；文件位置不变。

## 模块 → 代码

| 模块 | 后端 | 前端 | 本地启动 | 状态 |
|---|---|---|---|---|
| **R60Login** | [src/backend](cases/R60/R60Login/src/backend) | [src/frontend](cases/R60/R60Login/src/frontend) | `make dev-login-backend` / `make dev-login-frontend` | **可运行** |
| **R60Maker** | [src/backend](cases/R60/R60Maker/src/backend) | 无 | — | 后端骨架（缺 `main.py` / `pyproject.toml`），不能直接启动 |

## 常用命令

| 想做什么 | 命令 |
|---|---|
| 6 道门 | `make gate` 或 `python -m plat gate` |
| 8 工程进度 | `make status` 或 `python -m plat status` |
| 生成人读版 | `make md` 或 `python -m plat md --module R60Login --html` |
| 后端单测 | `make test` |
| 前端构建 | `make build` |
| 本地起后端 | `make dev-login-backend` → `http://localhost:8080/docs` |
| 本地起前端 | `make dev-login-frontend` → `http://localhost:5173` |
| Docker 起全部 | `make up` → 前端 `http://localhost:8081` |
| 停掉 Docker | `make down` |

## 部署单位

| 服务 | 构建 | 端口 | 说明 |
|---|---|---|---|
| `login-backend` | `src/backend/Dockerfile` | 8080 | FastAPI |
| `login-frontend` | `src/frontend/Dockerfile` | 8081 → 80 | Nginx；`/R60Login` 反代到 backend |

> **C: 盘满时**：npm 默认把缓存/临时文件写到 C:。安装前把 `npm_config_cache`、`TEMP`、`TMP` 指到 D: 盘（例如 `D:\AI_work_platform_dev\.npm-cache`、`.tmp`）。

## 配置

- `env.example`：本地开发的环境变量样例；复制成 `.env` 后按需修改（`.env` 已被 gitignore）。

## 相关设计

- 技术栈：`cases/R60/R60Login/framework/TECH_STACK.yaml`
- 共通部品：`cases/R60/R60Login/framework/COMPONENTS.yaml`
- 设计-代码对照：`cases/R60/R60Login/src/TRACEABILITY.yaml`
- 人读版：`cases/R60/R60Login/readable/`（生成物，不手改）

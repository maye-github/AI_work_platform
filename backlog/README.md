# backlog/ —— 待办池

> 这里放「要做但还没排期」的候选。**不是成果物，不占平台 ID 号段，不参与 `plat gate`。**

## 为什么单独放

- `ISS`：当前未决、会挡路的问题（工程内）。
- `CR`：已确认要改的变更（走 `/change`）。
- **Backlog**：想做、但还没决定做不做/什么时候做的候选池。

一条 backlog 只有在**人确认要做**之后，才升格为 `CR` 或正式任务；不要直接拿 BL 编号当成果物 ID 引用。

## 字段

| 字段 | 含义 |
|---|---|
| `id` | `BL-xxx`，backlog 本地编号 |
| `title` | 一句话 |
| `ppt_refs` | 对应 PPT 的页码/章节 |
| `why` | 为什么值得做 |
| `acceptance` | 怎样算做完（可验证） |
| `priority` | P0 先做 / P1 重要 / P2 以后 |
| `size` | S / M / L（粗略） |
| `depends_on` | 前置项 |
| `status` | not_started / in_progress / done |

## 使用方式

```bash
# 看全部（按优先级）
python - <<'PY'
import yaml
d = yaml.safe_load(open("backlog/backlog.yaml", encoding="utf-8"))
for it in sorted(d["items"], key=lambda x: (x["priority"], x["id"])):
    print(it["priority"], it["id"], it["status"], it["title"])
PY
```

## 升格规则

1. 人确认某条要做 → 在 `registry/ids.yaml` 走 `plat ids alloc --type CR`（或作为正式任务），写 `changes:`。
2. 把 backlog 条目的 `status` 改为 `done`，并注明对应的 CR / 任务 ID。
3. 不要在成果物里直接引用 `BL-xxx`。

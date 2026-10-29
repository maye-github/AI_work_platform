# 项目入口（每次会话先读）

1. 先读当前模块的 `cases/<案件>/<模块>/SESSION_HANDOFF.md`。
2. 跑 `python -m plat status` 和 `python -m plat gate`。
3. 规则真源：`.claude/rules/00-platform.md` / `01-security.md`。
4. **AI 不得直接读 `raw/`**：先 `python -m plat mask prep --module <模块>`，只读 `requirements/ai_input/`。
5. 一次只做一个工程；做完由人 `/approve`。
6. 会话结束前：`python -m plat handoff --module <模块> --write`，并在 `AI-NOTES` 补 3〜5 条“这次定了什么、为什么”。

> 当前模块：R60/R60Login（8 工程承認済）、R60/R60Maker（8 工程承認済）。
> **交接单是跨会话的唯一入口；聊天记录不会自动带过去。**

# presentation/img_src

`presentation/img/*.png` の生成元。

## 8 张图

| 图片 | 生成方式 |
|---|---|
| `fig_ui.png` | 实际运行截图：R60Login 后端 8080 + 前端 `dist` 8081（裁剪 580×630） |
| `fig_api.png` | 实际运行截图：`http://localhost:8080/docs`（裁剪 1440×520） |
| `fig_gate.png` | `gate.html` を Chrome headless で撮影（裁剪 1400×870） |
| `fig_tree.png` | `tree.html` を Chrome headless で撮影（裁剪 1400×420） |
| `fig_trace.png` | `trace.html`（`TRACEABILITY.yaml` から生成、裁剪 1400×760） |
| `fig_excel.png` | `excel.html`（`TC.yaml` から生成、Excel 風、裁剪 1400×720） |
| `fig_readable.png` | `readable_focus.html`（`REQ.yaml` の R-101/R-102、裁剪 1400×870） |
| `fig_project_tree.png` | `project_tree.html`（目录 + 作用 + 备注、裁剪 1400×760） |
| `fig_mask.png` | `mask.html`（脱敏流程 + 前后对照 + 终端、裁剪 1400×540） |
| `fig_demo.png` | 实际运行：`presentation/demo.html` 封面（1440×900；本稿未引用） |

> 部分图片截取后用 Pillow 裁掉了空白区域，以便在 PPT 里放大后仍看得清。

## 再生成

```bash
# 后端 / 前端（fig_ui / fig_api 用）
cd cases/R60/R60Login/src/backend && uvicorn app.main:app --port 8080
cd cases/R60/R60Login/src/frontend/dist && python -m http.server 8081

# Chrome headless
CHROME="C:/Program Files/Google/Chrome/Application/chrome.exe"
"$CHROME" --headless=new --disable-gpu --window-size=1440,900 \
  --screenshot=presentation/img/fig_ui.png http://localhost:8081
"$CHROME" --headless=new --disable-gpu --window-size=1440,900 \
  --screenshot=presentation/img/fig_api.png http://localhost:8080/docs
"$CHROME" --headless=new --disable-gpu --window-size=1400,900 \
  --screenshot=presentation/img/fig_gate.png file:///D:/AI_work_platform_dev/presentation/img_src/gate.html
"$CHROME" --headless=new --disable-gpu --window-size=1400,900 \
  --screenshot=presentation/img/fig_tree.png file:///D:/AI_work_platform_dev/presentation/img_src/tree.html
"$CHROME" --headless=new --disable-gpu --window-size=1400,1000 \
  --screenshot=presentation/img/fig_trace.png file:///D:/AI_work_platform_dev/presentation/img_src/trace.html
"$CHROME" --headless=new --disable-gpu --window-size=1400,900 \
  --screenshot=presentation/img/fig_excel.png file:///D:/AI_work_platform_dev/presentation/img_src/excel.html
"$CHROME" --headless=new --disable-gpu --window-size=1400,1500 \
  --screenshot=presentation/img/fig_readable.png file:///D:/AI_work_platform_dev/cases/R60/R60Login/readable/requirements/REQ.zh.html
"$CHROME" --headless=new --disable-gpu --window-size=1440,900 \
  --screenshot=presentation/img/fig_demo.png file:///D:/AI_work_platform_dev/presentation/demo.html
```

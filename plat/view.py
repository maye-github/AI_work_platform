# -*- coding: utf-8 -*-
"""機読源 `.md` → 人向け HTML（単一ファイル）。

**媒体規約**（本プラットフォームの唯一の規約）
- `.md` は**日本語のみ**（機読源）
- 人向けビューは**同名の `.zh.html`（中文のみ）**
- 日本語の `.html` は作らない。`.zh.md` は生成後に削除する。
- 生成物は**手で編集しない**（次回生成で消える）

chrome（`lang` / 目次 / 警告帯 / フッタ）は中文ビューでは中文にする。
**本文は翻訳しない** —— 翻訳は書く人の仕事であり、本ツールは描画だけを行う。
"""
from __future__ import annotations

import datetime as dt
import html
import re
from pathlib import Path

CSS = """
:root{--fg:#1f2937;--muted:#6b7280;--line:#e5e7eb;--bg:#ffffff;--accent:#2563eb;
--th:#eef2ff;--warn-bg:#fff7ed;--warn-bd:#fdba74}
*{box-sizing:border-box}
body{margin:0;padding:32px 20px 60px;background:#f8fafc;color:var(--fg);
font-family:-apple-system,"Segoe UI","Microsoft YaHei","Hiragino Sans",Meiryo,sans-serif;
font-size:15px;line-height:1.75}
.wrap{max-width:1080px;margin:0 auto;background:var(--bg);padding:36px 44px 44px;
border:1px solid var(--line);border-radius:10px}
h1{font-size:26px;margin:0 0 10px;letter-spacing:.01em}
h2{font-size:20px;margin:34px 0 12px;padding-bottom:6px;border-bottom:2px solid var(--accent)}
h3{font-size:17px;margin:24px 0 8px}
h4{font-size:15px;margin:18px 0 6px;color:#374151}
.meta{color:var(--muted);font-size:12.5px}
.warn-note{margin:14px 0 0;padding:10px 14px;background:var(--warn-bg);
border:1px solid var(--warn-bd);border-radius:8px;font-size:12.5px;color:#7c2d12}
nav.toc{margin:22px 0 8px;padding:12px 16px;background:#f9fafb;border:1px solid var(--line);border-radius:8px}
nav.toc .toc-title{font-weight:700;font-size:13px;color:var(--muted);margin-bottom:6px}
nav.toc ol{margin:0;padding-left:20px;columns:2;column-gap:28px}
nav.toc li{font-size:13.5px;margin:2px 0}
table{border-collapse:collapse;width:100%;margin:12px 0 18px;font-size:13.5px}
th,td{border:1px solid var(--line);padding:7px 10px;vertical-align:top;text-align:left}
th{background:var(--th);font-weight:700}
tbody tr:nth-child(even){background:#fcfcfd}
code{background:#f3f4f6;padding:1px 5px;border-radius:4px;font-size:12.5px;
font-family:Consolas,Menlo,monospace}
pre{background:#111827;color:#e5e7eb;padding:14px 16px;border-radius:8px;overflow:auto;
font-size:12.5px;line-height:1.6}
pre code{background:none;color:inherit;padding:0}
blockquote{margin:12px 0;padding:10px 16px;border-left:4px solid var(--warn-bd);
background:var(--warn-bg);border-radius:0 8px 8px 0}
blockquote p{margin:4px 0}
.foot{margin-top:34px;padding-top:14px;border-top:1px solid var(--line);
color:var(--muted);font-size:12px}
@media print{body{padding:0;background:#fff;font-size:10.5pt}.wrap{border:0;padding:0}
.noprint{display:none!important}nav.toc ol{columns:2}tr,li{break-inside:avoid}}
"""

UI = {
    "ja": {
        "toc": "目次", "src": "機読源", "gen": "生成", "sec": "セクション", "tbl": "表",
        "warn": ("⚠️ 本ページは機読源 (<code>{n}</code>) から自動生成された<strong>閲覧専用ビュー</strong>です。"
                 "この HTML を直接編集しないでください。修正は必ず機読源に入れ、再生成してください。"),
        "print": "印刷 (Ctrl+P) で PDF 化できます。",
        "foot": "このビューは <code>plat view</code> が生成しました。機読源は <code>{n}</code> です。",
    },
    "zh": {
        "toc": "目录", "src": "机读源", "gen": "生成", "sec": "节", "tbl": "表",
        "warn": ("⚠️ 本页由机读源 (<code>{n}</code>) 自动生成，是<strong>仅供阅读的视图</strong>。"
                 "请勿直接修改本 HTML。修改一律写回机读源后重新生成。"),
        "print": "按 Ctrl+P 可存为 PDF。",
        "foot": "本视图由 <code>plat view</code> 生成，机读源是 <code>{n}</code>。",
    },
}


def _inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def _slug(s: str, used: dict) -> str:
    base = re.sub(r"[^0-9A-Za-z぀-ヿ一-鿿]+", "-", s).strip("-") or "sec"
    n = used.get(base, 0) + 1
    used[base] = n
    return base if n == 1 else f"{base}-{n}"


def render_markdown(text: str) -> tuple[str, list[tuple[str, str]]]:
    lines = text.splitlines()
    out: list[str] = []
    toc: list[tuple[str, str]] = []
    used: dict[str, int] = {}
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            lang = ln[3:].strip()
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            body = html.escape("\n".join(buf))
            out.append(f'<pre><code class="lang-{lang}">{body}</code></pre>')
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            lvl, txt = len(m.group(1)), m.group(2).strip()
            sid = _slug(txt, used)
            if lvl == 2:
                toc.append((sid, txt))
            out.append(f'<h{lvl} id="{sid}">{_inline(txt)}</h{lvl}>')
            i += 1
            continue
        if ln.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ["<table><thead><tr>"] + [f"<th>{_inline(h)}</th>" for h in head] + ["</tr></thead><tbody>"]
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue
        if re.match(r"^\s*[-*]\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]))
                i += 1
            out.append("<ul>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + "</ul>")
            continue
        if re.match(r"^\s*\d+\.\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]))
                i += 1
            out.append("<ol>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + "</ol>")
            continue
        if ln.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip(">").strip())
                i += 1
            out.append("<blockquote>" + "".join(f"<p>{_inline(x)}</p>" for x in buf if x) + "</blockquote>")
            continue
        if not ln.strip() or ln.strip() == "---":
            i += 1
            continue
        out.append(f"<p>{_inline(ln.strip())}</p>")
        i += 1
    return "\n".join(out), toc


def build(text: str, source: Path, title: str | None = None, lang: str | None = None) -> str:
    body, toc = render_markdown(text)
    if lang is None:
        lang = "zh" if source.stem.endswith(".zh") else "ja"
    ui = UI.get(lang, UI["ja"])
    name = html.escape(source.name)
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    nav = ""
    if toc:
        items = "".join(f'<li><a href="#{a}">{html.escape(t)}</a></li>' for a, t in toc)
        nav = f'<nav class="toc noprint"><div class="toc-title">{ui["toc"]}</div><ol>{items}</ol></nav>'
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title or source.stem)}</title>
<style>{CSS}</style></head>
<body><div class="wrap">
<header>
<h1>{html.escape(title or source.stem)}</h1>
<div class="meta">{ui["src"]}: <code>{name}</code> ／ {ui["gen"]}: {stamp}</div>
<div class="warn-note">{ui["warn"].format(n=name)}
<span class="noprint">{ui["print"]}</span></div>
</header>
{nav}
{body}
<div class="foot">{ui["foot"].format(n=name)}</div>
</div></body></html>
"""


def convert(md_path: Path, out_path: Path | None = None) -> Path:
    text = md_path.read_text(encoding="utf-8")
    from .model import split_front
    fm, body = split_front(text)
    src = body if fm else text
    out = out_path or md_path.with_suffix(".zh.html")
    # 中文ビューの判定は「出力名が *.zh.html」か「入力名が *.zh.md」のどちらでも成立させる
    lang = "zh" if out.name.endswith(".zh.html") or md_path.stem.endswith(".zh") else "ja"
    out.write_text(build(src, md_path, lang=lang), encoding="utf-8")
    return out

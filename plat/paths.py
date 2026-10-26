# -*- coding: utf-8 -*-
"""路径解析 —— 平台根 / 案件 / 模块 / 成果物。

**单一定义**：本模块是「东西放哪里」的唯一真源。其它模块不得自己拼路径。
"""
from __future__ import annotations

import os
from pathlib import Path

# 允许用环境变量覆盖根（测试、CI、从别处调用时用）
ENV_ROOT = "AIP_ROOT"


def root() -> Path:
    """平台根目录。默认 = 本包所在目录的父目录。"""
    v = os.environ.get(ENV_ROOT)
    if v:
        return Path(v).resolve()
    return Path(__file__).resolve().parent.parent


def rel(p: Path) -> str:
    """把绝对路径转成相对平台根的 posix 路径（台账、报告里统一用这个写法）。"""
    try:
        return p.resolve().relative_to(root()).as_posix()
    except ValueError:
        return p.as_posix()


def registry_file() -> Path:
    return root() / "registry" / "ids.yaml"


def mask_map_file() -> Path:
    return root() / "registry" / "MASK_MAP.yaml"


def cases_dir() -> Path:
    return root() / "cases"


def templates_dir() -> Path:
    return root() / "templates"


def knowledge_dir() -> Path:
    return root() / "knowledge"


def modules() -> list[tuple[str, str, Path]]:
    """[(case, module, path)] —— 按 cases/<case>/<module>/ 扫描。

    模块的判定标准是「目录下存在 module.yaml」，避免把临时目录当成模块。
    """
    out: list[tuple[str, str, Path]] = []
    base = cases_dir()
    if not base.is_dir():
        return out
    for case_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        for mod_dir in sorted(p for p in case_dir.iterdir() if p.is_dir()):
            if (mod_dir / "module.yaml").is_file():
                out.append((case_dir.name, mod_dir.name, mod_dir))
    return out


def module_dir(case: str, module: str) -> Path:
    return cases_dir() / case / module


def find_module(name: str) -> tuple[str, str, Path] | None:
    """按模块名找（模块名在案件内唯一；跨案件同名时要求带 case 前缀 `case/module`）。"""
    if "/" in name:
        c, m = name.split("/", 1)
        p = module_dir(c, m)
        return (c, m, p) if (p / "module.yaml").is_file() else None
    hits = [t for t in modules() if t[1] == name]
    return hits[0] if len(hits) == 1 else None

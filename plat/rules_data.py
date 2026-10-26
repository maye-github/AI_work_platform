# -*- coding: utf-8 -*-
"""规则的**数据化**定义 —— 阶段表 / ID 类型 / 必填字段 / 状态机 / 追溯链。

**为什么单列一个文件**：这些东西既要被脚本读（gate / ids / status），
又要被人读（`使用手册.md` 与 `.claude/rules/00-platform.md` 引用同一张表）。
放在代码里当常量，避免「文档写一套、脚本跑另一套」。
"""
from __future__ import annotations

from typing import NamedTuple

# =============================================================================
# 1. 八工程（规格书 §4.4 的落地口径）
# =============================================================================
class Stage(NamedTuple):
    no: int
    key: str          # 命令名片段：/requirements
    name_ja: str      # 对外日文
    name_zh: str      # 中文（视图用）
    produces: tuple[str, ...]   # 该阶段产出的 ID 类型（空 = 只产管理文档/源码）
    artifact_dir: str           # 该阶段成果物在模块目录下的子目录


STAGES: tuple[Stage, ...] = (
    Stage(1, "requirements",    "要件理解",         "需求理解",       ("R", "Q", "ASM", "ISS"), "requirements"),
    Stage(2, "basic-design",    "基本設計",         "基本设计",       ("F", "I"),               "designs/basic"),
    Stage(3, "detail-design",   "詳細設計",         "详细设计",       ("D", "L", "E"),          "designs/detail"),
    Stage(4, "framework",       "フレームワーク・環境構築", "框架环境构筑", (),                 "framework"),
    Stage(5, "coding",          "製造（コーディング）", "制造（编码）",  (),                    "src"),
    Stage(6, "unit-test",       "単体テスト",       "单元测试",       ("TC",),                  "tests/unit"),
    Stage(7, "integration-test","結合・総合テスト",  "结合·综合测试",  ("IT",),                  "tests/integration"),
    Stage(8, "release",         "リリース・運用保守","发布·运维",      ("REL",),                 "release"),
)

STAGE_BY_KEY = {s.key: s for s in STAGES}
STAGE_BY_NO = {s.no: s for s in STAGES}


def stage_of_type(t: str) -> int | None:
    for s in STAGES:
        if t in s.produces:
            return s.no
    return None


# =============================================================================
# 2. ID 类型（号段制）
# =============================================================================
# 格式：<类型码>-<3 位号>，例 R-101。
# 号段由台账给每个模块分配：模块的号段基数 100 → 101..199，200 → 201..299。
# 「类型码」在这里是**唯一真源**；增加类型必须先改这张表，再改 .claude/rules。
ID_TYPES: dict[str, str] = {
    "R":   "要件（要求）",
    "F":   "機能（功能）",
    "I":   "画面項目（画面/接口项目）",
    "D":   "データモデル（数据模型）",
    "L":   "ロジック（业务逻辑）",
    "E":   "エラー（错误/消息）",
    "TC":  "単体テストケース",
    "IT":  "結合テストケース",      # 规格书未列，本平台追加（§9.2 只举了 TC）
    "Q":   "確認事項（对日方确认）",
    "ASM": "前提・仮定",
    "ISS": "未決事項（阻塞项）",
    "CR":  "変更要求",
    "BUG": "不具合",
    "REL": "リリース成果物",
}

# 追溯链的**允许边**：上游类型 → 下游类型。
# gate2 用它判断「这条链走不走得通」，也用它判断有没有反向引用的野边。
TRACE_EDGES: dict[str, tuple[str, ...]] = {
    "R":   ("F", "I", "D", "L", "E", "TC", "IT"),
    "F":   ("I", "D", "L", "TC", "IT"),
    "I":   ("D", "TC", "IT"),
    "D":   ("L", "E", "TC", "IT"),
    "L":   ("E", "TC", "IT"),
    "E":   ("TC", "IT"),
    "TC":  ("REL",),
    "IT":  ("REL",),
    "Q":   ("R", "F", "I", "D", "L", "E"),
    "ASM": ("R", "F", "D"),
    "ISS": ("R", "F", "I", "D", "L", "E", "TC", "IT"),
    "CR":  ("R", "F", "I", "D", "L", "E", "TC", "IT"),
    "BUG": ("L", "E", "TC", "IT"),
    "REL": (),
}

# 终端类型：不再往下游引
TERMINAL_TYPES = ("TC", "IT", "REL")

# 允许不挂 related_ids 的类型（确认事项/不具合/发布物天然可以没有上游）
RELATED_OPTIONAL = ("Q", "BUG", "REL", "ASM", "ISS")

# 管理文档（不占 ID 号段，登记在台账 management_docs 里）
MANAGEMENT_DOCS = ("TECH_STACK", "TRACEABILITY", "COMPONENTS")


# =============================================================================
# 3. 成果物必填字段与状态机
# =============================================================================
# 位置信息（case / module / stage）**不从字段取**，一律由目录推出 —— 单一真源。
REQUIRED_FIELDS = (
    "id", "type", "title", "status", "version",
    "related_ids", "owner", "created_at", "updated_at", "sensitivity",
)

STATUS_FLOW: dict[str, tuple[str, ...]] = {
    "draft":      ("reviewed", "deprecated"),
    "reviewed":   ("confirmed", "draft", "deprecated"),
    "confirmed":  ("frozen", "deprecated"),
    "frozen":     ("deprecated",),
    "deprecated": (),
}
STATUS_VALUES = tuple(STATUS_FLOW)
# 「已承认」= 可以据此进入下一阶段
APPROVED_STATUS = ("confirmed", "frozen")

SENSITIVITY_VALUES = ("public", "internal", "confidential")

# 承认记录字段（由 /approve 写入，人填标识符）
APPROVAL_FIELDS = ("approved_by", "approved_at")


# =============================================================================
# 4. 命名分区（gate5）
# =============================================================================
# 定义层（YAML/MD/Python）用 snake_case；接口层（TS/Vue）用 camelCase。
SNAKE_SUFFIXES = (".yaml", ".yml", ".py")
CAMEL_SUFFIXES = (".ts", ".vue")


# =============================================================================
# 5. 机密（gate6）
# =============================================================================
# 只检测「机密の形」，不维护实值清单。实值清单位于 registry/MASK_MAP.yaml（gitignore）。
SECRET_PATTERNS: tuple[tuple[str, str], ...] = (
    ("内部IP(RFC1918)",   r"\b(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
    ("连接串(ユーザ:パス)", r"\b[A-Za-z_][\w$]*:[^\s@/'\"]{3,}@[A-Za-z0-9_.-]+"),
    ("社内メール",        r"\b[\w.+-]+@(?!(?:example|test)\.)[\w-]+(?:\.[\w-]+)+\b"),
    ("AWSアクセスキー",    r"\bAKIA[0-9A-Z]{16}\b"),
    ("秘密鍵ブロック",     r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("Bearer トークン",   r"\bBearer\s+[A-Za-z0-9\-._~+/]{20,}"),
    ("パスワード代入",     r"(?i)\b(?:password|passwd|pwd|secret|token|api[_-]?key)\s*[:=]\s*['\"]?[^\s'\"$<]{6,}"),
    ("復号関数の実引数",   r"\b[A-Z0-9_]{2,}_FNC\s*\(\s*['\"]?[A-Za-z0-9]", ),
    ("緊急配信トリガー式", r"(?i)IF\s+[A-Z_]{2,}\s*=\s*['\"]?[0-9]['\"]?\s+THEN"),
)

# gate6 的豁免文件：规则本身写着「什么算机密」，不能自己把自己判成机密。
SECRET_EXEMPT = (
    ".claude/rules/01-security.md",
    "plat/rules_data.py",
    "registry/MASK_MAP.yaml",
)

# 占位记号：出现这些就说明已经脱敏，不算泄露
PLACEHOLDER_TOKENS = (
    "PWD_", "IP_", "TBL_", "COL_", "VAL_", "EMP_", "NAME_", "DOM_",
    "KEY_", "MAIL_", "SID_", "BUCKET_", "PROFILE_", "TRG_", "<客户",
    "example.com", "xxxx", "****",
)

# 工程4 成果物スキーマ（管理文書）

管理文書は**業務 ID を持たない**。代わりに `doc:` で識別し、台帳の `management_docs` に登録する。

## TECH_STACK.yaml
```yaml
doc: TECH_STACK
title: 技術スタック宣言
status: draft            # /approve で confirmed に
version: 0.1
owner: <人>
created_at: 2026-01-01
updated_at: 2026-01-01
stack:
  backend:
    language: <例 Python 3.12>
    framework: <例 FastAPI>
    db: <例 PostgreSQL 16>
    orm: <例 SQLAlchemy 2>
    test: <例 pytest>
  frontend:
    language: <例 TypeScript 5>
    framework: <例 Vue 3>
    state: <例 Pinia>
    test: <例 vitest>
  conventions:
    timezone: <例 Asia/Tokyo>
    naming_definition_layer: snake_case
    naming_interface_layer: camelCase
  commands:
    build: <コマンド>
    test: <コマンド>
    lint: <コマンド>
    run: <コマンド>
```

## COMPONENTS.yaml
```yaml
doc: COMPONENTS
title: 共通部品一覧
status: draft
version: 0.1
owner: <人>
created_at: 2026-01-01
updated_at: 2026-01-01
components:
  - key: <部品キー（snake_case）>
    purpose: <何のため>
    interface: <署名・入出力>
    used_by: [F-101]
```

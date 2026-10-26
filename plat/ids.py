# -*- coding: utf-8 -*-
"""ID 台帳（`registry/ids.yaml`）の操作 —— **台帳の唯一の書き込み口**。

台帳を手で編集してはいけない。理由は「号が飛ぶ／重複する」だけでなく、
**成果物の status と台帳の status が食い違う**ことにある。
`set-status` は両方を同時に更新して、その食い違いを作らない。
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

import yaml

from . import model, paths, rules_data as R


def _today() -> str:
    return dt.date.today().isoformat()


# =============================================================================
# 台帳の読み書き
# =============================================================================
def save(ledger: dict) -> None:
    ledger["updated_at"] = _today()
    p = paths.registry_file()
    p.parent.mkdir(parents=True, exist_ok=True)

    class D(yaml.SafeDumper):
        pass

    def _str(rep, data):
        if "\n" in data:
            return rep.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return rep.represent_scalar("tag:yaml.org,2002:str", data)

    D.add_representer(str, _str)
    p.write_text(
        yaml.dump(ledger, Dumper=D, allow_unicode=True, sort_keys=False,
                  default_flow_style=False, width=4096),
        encoding="utf-8",
    )


def ensure_module(ledger: dict, case: str, module: str, block: int | None = None) -> dict:
    cases = ledger.setdefault("cases", {})
    c = cases.setdefault(case, {})
    mods = c.setdefault("modules", {})
    m = mods.setdefault(module, {})
    if block is not None:
        m["block"] = int(block)
    m.setdefault("block", 100)
    return m


# =============================================================================
# 発番
# =============================================================================
def alloc(ledger: dict, case: str, module: str, type_code: str,
          title: str, owner: str, artifact: str,
          count: int = 1) -> list[str]:
    """号段の次の番号を払い出す。飛ばさない・再利用しない。"""
    if type_code not in R.ID_TYPES:
        raise SystemExit(f"未知の種別コード: {type_code}（{'/'.join(R.ID_TYPES)}）")
    m = ensure_module(ledger, case, module)
    block = int(m.get("block", 100))
    ids = ledger.setdefault("ids", {})

    used = [
        model.id_num(k.split("/")[-1]) or 0
        for k in ids
        if k.startswith(f"{case}/{module}/")
        and model.id_type(k.split("/")[-1]) == type_code
    ]
    nxt = max(used + [block]) + 1
    out: list[str] = []
    for i in range(count):
        num = nxt + i
        if num > block + 99:
            raise SystemExit(
                f"{module} の号段 {block}xx を使い切ります（次は {num}）。"
                "号段の拡張は人が決めてください（plat ids block）。"
            )
        new_id = f"{type_code}-{num}"
        key = f"{case}/{module}/{new_id}"
        if key in ids:
            raise SystemExit(f"既に存在します: {key}")
        ids[key] = {
            "type": type_code,
            "title": title if count == 1 else f"{title} ({i + 1})",
            "status": "draft",
            "version": "0.1",
            "artifact": artifact,
            "owner": owner,
            "created_at": _today(),
            "updated_at": _today(),
            "note": "",
        }
        out.append(new_id)
    save(ledger)
    return out


def set_status(ledger: dict, keys: list[str], status: str, by: str | None = None) -> list[str]:
    """台帳と成果物の status を**同時に**更新する。"""
    if status not in R.STATUS_VALUES:
        raise SystemExit(f"状態が不正: {status}（{'/'.join(R.STATUS_VALUES)}）")
    ids = model.ledger_ids(ledger)
    touched: list[str] = []
    # 承認の瞬間に「初稿 → 承認版」の修正量を記録する（status を書き換える前に測る）
    arts = {a.key: a for a in model.load_all() if a.id}
    for key in keys:
        e = ids.get(key)
        if not e:
            raise SystemExit(f"台帳にありません: {key}")
        if status in R.APPROVED_STATUS and key in arts:
            from . import adoption
            adoption.record(arts[key])
        e["status"] = status
        e["updated_at"] = _today()
        art = Path(paths.root()) / str(e.get("artifact") or "")
        if art.is_file():
            _rewrite_front(art, status, by)
        touched.append(key)
    save(ledger)
    return touched


def deprecate(ledger: dict, keys: list[str], note: str, by: str | None = None) -> list[str]:
    if not note.strip():
        raise SystemExit("廃止には理由（--note）が必要です（跡を残すため）")
    ids = model.ledger_ids(ledger)
    out = []
    for key in keys:
        e = ids.get(key)
        if not e:
            raise SystemExit(f"台帳にありません: {key}")
        e["status"] = "deprecated"
        e["note"] = note
        e["updated_at"] = _today()
        out.append(key)
    save(ledger)
    return out


# =============================================================================
# 成果物ファイルの書き換え（status / 承認欄だけ・本文には触れない）
# =============================================================================
_STATUS_LINE = re.compile(r"^status:\s*.*$", re.M)
# `approved_by` はインライン列表（["SE-001"]）にもブロック列表（"\n- SE-001"）にもなる。
# 行だけ置換するとブロックの `- ` 行が残って YAML が壊れるので、値の全体を食う。
_APPROVED_LINE = re.compile(r"^approved_by:.*(?:\n[ \t]*- [^\n]*)*", re.M)
_APPROVED_AT_LINE = re.compile(r"^approved_at:.*$", re.M)


def _rewrite_front(path: Path, status: str, by: str | None) -> None:
    # 改行コードを LF に正規化してから編集する。Windows の write_text は CRLF を書き、
    # 行末アンカーの正規表現が期待どおりに当たらないことがある。書き戻しも LF に固定する。
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    new, n = _STATUS_LINE.subn(f"status: {status}", text, count=1)
    if n == 0:
        raise SystemExit(f"{path}: status 行が見つかりません（成果物の形式を確認してください）")
    # 承認欄：既にあれば置換、無ければ status 行の直後に挿入
    stamp = _today()
    by_val = f"[" + ", ".join(f'"{b}"' for b in ([by] if by else [])) + "]"
    if _APPROVED_LINE.search(new):
        new = _APPROVED_LINE.sub(f"approved_by: {by_val}", new, count=1)
    else:
        new = new.replace(f"status: {status}", f"status: {status}\napproved_by: {by_val}", 1)
    if _APPROVED_AT_LINE.search(new):
        at_val = f'"{stamp}"' if by else "null"
        new = _APPROVED_AT_LINE.sub(f"approved_at: {at_val}", new, count=1)
    else:
        at_val = f'"{stamp}"' if by else "null"
        new = new.replace(f"approved_by: {by_val}", f"approved_by: {by_val}\napproved_at: {at_val}", 1)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)


# =============================================================================
# 検証
# =============================================================================
def verify(ledger: dict, arts: list[model.Artifact]) -> tuple[list[str], list[str]]:
    """(ERROR, WARN) を返す。E1〜E8／E11〜E13 相当。"""
    err: list[str] = []
    warn: list[str] = []
    ids = model.ledger_ids(ledger)

    # --- 台帳側 ---
    for key, e in ids.items():
        case, module, id_str = model.split_key(key)
        t = model.id_type(id_str)
        n = model.id_num(id_str)
        if not t or n is None:
            err.append(f"E1 形式不正: {key}")
            continue
        if t not in R.ID_TYPES:
            err.append(f"E2 未知の種別: {key}")
        block = model.block_of(ledger, case, module)
        if block is None:
            err.append(f"E2 モジュール未登録（号段なし）: {case}/{module}")
        elif not (block + 1 <= n <= block + 99):
            err.append(f"E4 号段外: {key}（号段 {block}xx）")
        if str(e.get("type")) != t:
            err.append(f"E2 type フィールド不一致: {key}（{e.get('type')} vs {t}）")
        for k in ("type", "title", "status", "version", "artifact", "owner",
                  "created_at", "updated_at"):
            if not e.get(k):
                err.append(f"E11 必須項目が空: {key}.{k}")
        if e.get("status") not in R.STATUS_VALUES:
            err.append(f"E9 状態が不正: {key}（{e.get('status')}）")
        a = str(e.get("artifact") or "")
        if a and not (paths.root() / a).is_file():
            err.append(f"E12 artifact が存在しません: {key} → {a}")

    # --- 号段の連続性（同一モジュール・同一種別）---
    from collections import defaultdict
    nums: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    for key in ids:
        case, module, id_str = model.split_key(key)
        t, n = model.id_type(id_str), model.id_num(id_str)
        if t and n is not None:
            nums[(case, module, t)].append(n)
    for (case, module, t), lst in nums.items():
        block = model.block_of(ledger, case, module)
        if block is None:
            continue
        want = list(range(block + 1, max(lst) + 1))
        missing = [x for x in want if x not in lst]
        if missing:
            err.append(f"E5 番号に飛びがあります: {module} {t} → {missing[:5]}")

    # --- 成果物側 ---
    seen: dict[str, str] = {}
    for art in arts:
        if art.error:
            err.append(f"E13 読めません: {art.rel}（{art.error}）")
            continue
        if not art.id:
            err.append(f"E13 id がありません: {art.rel}")
            continue
        # 集約ファイルは条目ごとに登録されている。先頭の id だけで判定しない。
        for item_id in (art.all_ids or [art.id]):
            key = f"{art.case}/{art.module}/{item_id}"
            if key in seen:
                err.append(f"E3 ID 重複: {key}（{seen[key]} と {art.rel}）")
            seen[key] = art.rel
            if key not in ids:
                err.append(f"E7 台帳未登録: {key}（{art.rel}）")
                continue
            e = ids[key]
            if str(e.get("artifact")) != art.rel:
                warn.append(f"E12 artifact パス不一致: {key}（台帳 {e.get('artifact')} / 実体 {art.rel}）")
            if art.status != e.get("status"):
                err.append(f"E13 status 不一致: {key}（成果物 {art.status} / 台帳 {e.get('status')}）")
            if e.get("status") == "deprecated":
                err.append(f"E8 廃止 ID を参照しています: {art.rel}")

    # --- 孤立（台帳にあるが成果物がない）---
    for key, e in ids.items():
        if key not in seen and e.get("status") != "deprecated":
            warn.append(f"W1 孤立 ID: {key}（成果物がありません）")
    return err, warn


# =============================================================================
# CLI から使う補助
# =============================================================================
def register_doc(ledger: dict, doc: str, path: str, title: str, owner: str) -> dict:
    """管理文書を台帳へ登録する（業務 ID は発番しない）。

    **キーはパス**。`doc` 名で引くと、同じ種類の管理文書をモジュールごとに持つとき
    （例: 各モジュールの TECH_STACK）に**上書きし合って**、片方の登録が消える。
    """
    docs = ledger.setdefault("management_docs", [])
    for d in docs:
        if isinstance(d, dict) and d.get("path") == path:
            d.update({"doc": doc, "title": title, "owner": owner,
                      "updated_at": _today()})
            save(ledger)
            return d
    e = {"doc": doc, "path": path, "title": title, "status": "draft",
         "version": "0.1", "owner": owner,
         "created_at": _today(), "updated_at": _today()}
    docs.append(e)
    save(ledger)
    return e


def set_doc_status(ledger: dict, doc: str, status: str, by: str | None = None,
                   path: str | None = None, module: str | None = None) -> str:
    """管理文書の status を、台帳とファイルの両方で更新する。

    `path` か `module`（`<案件>/<モジュール>`）で**対象を特定する**。
    どちらも無く同名の管理文書が複数ある場合は、取り違えを避けるためエラーにする。
    """
    if status not in R.STATUS_VALUES:
        raise SystemExit(f"状態が不正: {status}")
    docs = ledger.setdefault("management_docs", [])
    cands = [d for d in docs if isinstance(d, dict) and d.get("doc") == doc]
    if path:
        cands = [d for d in cands if str(d.get("path")) == path]
    elif module:
        cands = [d for d in cands if str(d.get("path", "")).startswith(f"cases/{module}/")]
    if len(cands) > 1:
        raise SystemExit(
            f"管理文書 `{doc}` が {len(cands)} 件あります。--module か --path で特定してください: "
            + ", ".join(str(d.get("path")) for d in cands))
    hit = cands[0] if cands else None
    if not hit:
        raise SystemExit(f"管理文書が台帳にありません: {doc}")
    hit["status"] = status
    hit["updated_at"] = _today()
    path = Path(paths.root()) / str(hit.get("path") or "")
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        new, n = _STATUS_LINE.subn(f"status: {status}", text, count=1)
        if n == 0:
            raise SystemExit(f"{path}: status 行が見つかりません")
        by_val = "[" + ", ".join(f'"{b}"' for b in ([by] if by else [])) + "]"
        at_val = f'"{_today()}"' if by else "null"
        if "approved_by:" in new:
            new = re.sub(r"^approved_by:.*$", f"approved_by: {by_val}", new, count=1, flags=re.M)
        else:
            new = new.replace(f"status: {status}", f"status: {status}\napproved_by: {by_val}", 1)
        if "approved_at:" in new:
            new = re.sub(r"^approved_at:.*$", f"approved_at: {at_val}", new, count=1, flags=re.M)
        else:
            new = new.replace(f"approved_by: {by_val}", f"approved_by: {by_val}\napproved_at: {at_val}", 1)
        path.write_text(new, encoding="utf-8")
    save(ledger)
    return doc


def keys_of_stage(ledger: dict, case: str, module: str, stage_no: int) -> list[str]:
    stage = R.STAGE_BY_NO.get(stage_no)
    if not stage:
        return []
    return [
        k for k in model.ledger_ids(ledger)
        if k.startswith(f"{case}/{module}/") and model.id_type(k.split("/")[-1]) in stage.produces
    ]

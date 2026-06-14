# Loose-Movement Phase 1 (Part B) — Inbox Proposal-Card Writer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the `lionwheel-route-invoices` skill turn each non-invoice exception task (return/exchange/sample/gift/check) into a `loose_movement_pending` proposal **card in Tom's Inbox** (`private_core.exceptions`) — moving **no stock** (Phase 2 commits).

**Architecture:** A new skill module `scripts/loose_cards.py` orchestrates the already-built+tested pure layer (`loose_classify` → `loose_notation` → `loose_items.Resolver` → `loose_movement.compute`). For each exception task it builds an `exceptions`-row dict (the card) whose `detail` is `compute()`'s `mv["detail"]` JSON. Two outputs: a **dry-run JSON preview** (no DB, default) and a **live INSERT** into `private_core.exceptions` (SELECT-before-insert dedup per §R7) via the pooled Postgres URL. Stock is never touched.

**Tech Stack:** Python 3.13, `psycopg[binary]` (pooled Postgres), the skill's existing pure modules. `pytest` for unit tests (no live DB in tests — the INSERT path is exercised against an in-memory fake cursor; the real INSERT is validated live in the dry-run runbook, Task 8).

**Design-of-record:** `PRODUCTION/docs/superpowers/specs/2026-06-14-loose-movement-stock-commit-design.md` + skill spec `SPEC_loose_movement_delivery_note_2026-06-13.md` (§6, §8, §R1, §R2, §R7, §16).

**Skill dir (all skill paths below are relative to it):** `C:/Users/tomw2/.claude/skills/lionwheel-route-invoices/`

---

## File Structure

| File | Responsibility |
|---|---|
| `scripts/loose_cards.py` (CREATE) | Build cards from a route manifest's exception tasks; preview to JSON; INSERT to Inbox with dedup; CLI. |
| `tests/test_loose_cards.py` (CREATE) | Unit tests: exception-task detection, ctx, card fields/severity/title/dedupe, full route fixture, dedup-select, preview. |
| `scripts/list_active_skus.py` (MODIFY if needed) | Ensure the snapshot emits Resolver fields incl. `aliases[]`, `status`, `item_type`, `unit`. |
| `SKILL.md` (MODIFY) | Document the Phase-1 step (preview → Tom OK → `--write`) in the FULL DAILY FILE pipeline. |

**Interfaces already built (do NOT modify — call them):**
- `loose_classify.classify(task) -> {"type","type_he","parsed"}` (`type` ∈ return/exchange/sample/gift/check/pickup/delivery/None; `parsed` is a ParsedNote or None).
- `loose_notation.parse(text) -> {"type","segments":[{verb,qty_actual,qty_expected,product_raw,flags}],"flags","raw"}`.
- `loose_items.Resolver(snapshot).resolve(product_raw) -> {"item_id","item_name","unit","resolved","reason",...}`; `snapshot` = list of `{item_id,item_name,status,item_type,unit,aliases[]}`.
- `loose_movement.compute(parsed, picker_status, ctx, resolve) -> mv` where `mv["detail"]` is the card detail JSON, `mv["commit_blocked"]` bool, `mv["flags"]` list, `mv["legs"]` list. `ctx` requires: `driver_id, delivery_date, task_id, recipient_name, wp_order_id, route_dir, skill_version, task_status_at_commit`.
- Inbox INSERT columns (from `api/src/integrations/lionwheel/poller.ts::emitException`): `category, severity, source, title, detail, dedupe_key, related_job_run_id, related_entity_type, related_entity_id`; `status` defaults to `'open'`; **dedup = SELECT an open row with same `dedupe_key`, skip if found**. `category` is free-text (no migration).

---

## Task 1: Active-SKU snapshot carries the Resolver fields

**Files:**
- Modify: `scripts/list_active_skus.py`
- Test: `tests/test_loose_cards.py`

The `Resolver` needs each snapshot item to have `item_id, item_name, status, item_type, unit, aliases[]`. Hebrew `aliases` are essential (§R6) or routine Hebrew returns never resolve.

- [ ] **Step 1: Read `scripts/list_active_skus.py`** and check what columns `_active_skus.json` currently emits. Confirm whether `status`, `item_type`, `unit`, and `aliases` are present per item.

- [ ] **Step 2: Write a failing test** that loads a fixture snapshot and asserts the Resolver resolves a Hebrew alias.

```python
# tests/test_loose_cards.py
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import loose_items

def test_resolver_resolves_hebrew_alias():
    snap = [{"item_id": "FG-DET-1L", "item_name": "DETOX 1L", "status": "ACTIVE",
             "item_type": "FG", "unit": "bottle", "aliases": ["דיטוקס", "DETOX 1000ml"]}]
    r = loose_items.Resolver(snap)
    assert r.resolve("דיטוקס")["item_id"] == "FG-DET-1L"
    assert r.resolve("DETOX 1000ml")["resolved"] is True
```

- [ ] **Step 3: Run it.** `cd "<skill>" && python -m pytest tests/test_loose_cards.py::test_resolver_resolves_hebrew_alias -v` — Expected: PASS (Resolver already handles aliases; this pins the snapshot contract).

- [ ] **Step 4: If `list_active_skus.py` does NOT emit `aliases`/`status`/`item_type`/`unit`,** extend its query/output so each item is `{item_id,item_name,status,item_type,unit,aliases}`. Source Hebrew aliases from `private_core.items` (e.g. an `aliases`/`name_he` column if present; else emit `aliases: []` and note it). Keep the file's existing pooled-DB pattern. If it already emits them, no change — record that in the commit message.

- [ ] **Step 5: Commit.** `git add scripts/list_active_skus.py tests/test_loose_cards.py` (skip list_active_skus if unchanged) `&& git commit -m "feat(loose-cards): pin active-SKU snapshot contract for Resolver"`

---

## Task 2: Exception-task detection + per-task context

**Files:**
- Create: `scripts/loose_cards.py`
- Test: `tests/test_loose_cards.py`

- [ ] **Step 1: Write failing tests.**

```python
# add to tests/test_loose_cards.py
import loose_cards

def test_is_exception_task():
    assert loose_cards.is_exception_task({"invoice_line_items": []}) is True
    assert loose_cards.is_exception_task({"invoice_line_items": [{"description": "X"}]}) is False

def test_task_ctx_pulls_required_fields():
    manifest = {"driver_id": 28174, "delivery_date": "2026-06-14", "_route_dir": "/r"}
    task = {"task_id": 25253384, "recipient_name": "שי קדוש", "wp_order_id": None,
            "pick_state": "picked"}
    ctx = loose_cards.task_ctx(task, manifest, skill_version="t1")
    assert ctx["driver_id"] == 28174 and ctx["delivery_date"] == "2026-06-14"
    assert ctx["task_id"] == "25253384" and ctx["route_dir"] == "/r"
    assert ctx["recipient_name"] == "שי קדוש" and ctx["wp_order_id"] is None
    assert ctx["skill_version"] == "t1" and ctx["task_status_at_commit"] == "picked"
```

- [ ] **Step 2: Run, verify FAIL** (`ModuleNotFoundError: loose_cards`). `python -m pytest tests/test_loose_cards.py -k "exception_task or task_ctx" -v`

- [ ] **Step 3: Create `scripts/loose_cards.py` with the minimal code.**

```python
# -*- coding: utf-8 -*-
"""Phase 1 / Part B — build loose_movement_pending Inbox proposal cards from a
route manifest's exception (non-invoice) tasks. Computes movements via the pure
layer (loose_classify -> loose_notation -> loose_items -> loose_movement) and
emits exceptions-card rows. Two outputs: a dry-run JSON preview (no DB, default)
and a live INSERT into private_core.exceptions (SELECT-before-insert dedup, R7).
MOVES NO STOCK — Phase 2 (approve handler) commits."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import loose_classify
import loose_movement

SOURCE = "lionwheel-route-invoices-skill"
MOVEMENT_TYPES = {"return", "exchange", "sample", "gift", "check"}


def is_exception_task(task):
    """A non-invoice task = no GI invoice lines. These are the loose-movement
    candidates (returns/exchanges/samples/gifts/check pickups)."""
    return not (task.get("invoice_line_items"))


def task_ctx(task, manifest, skill_version):
    return {
        "driver_id": manifest.get("driver_id"),
        "delivery_date": manifest.get("delivery_date"),
        "task_id": str(task.get("task_id")),
        "recipient_name": task.get("recipient_name"),
        "wp_order_id": task.get("wp_order_id"),
        "route_dir": manifest.get("_route_dir") or "",
        "skill_version": skill_version,
        "task_status_at_commit": task.get("pick_state") or task.get("lw_status"),
    }
```

- [ ] **Step 4: Run, verify PASS.** `python -m pytest tests/test_loose_cards.py -k "exception_task or task_ctx" -v`

- [ ] **Step 5: Commit.** `git add scripts/loose_cards.py tests/test_loose_cards.py && git commit -m "feat(loose-cards): exception-task detection + per-task ctx"`

---

## Task 3: Build one card from a task (the core)

**Files:**
- Modify: `scripts/loose_cards.py`
- Test: `tests/test_loose_cards.py`

A card = an `exceptions` row dict. `severity` = `warning` when `commit_blocked` or any flags, else `info`. `dedupe_key` = `loose_mv:<driver>:<date>:<task>`. `detail` = `json.dumps(mv["detail"], ensure_ascii=False)`. `title` = Hebrew one-liner. When a movement type is known but there is NO parsed notation, build a minimal blocked parsed so the card still surfaces (never silently drop a real exception).

- [ ] **Step 1: Write failing tests.**

```python
# add to tests/test_loose_cards.py
SNAP = [
    {"item_id": "FG-DET-1L", "item_name": "DETOX 1L", "status": "ACTIVE",
     "item_type": "FG", "unit": "bottle", "aliases": ["DETOX 1000ml", "דיטוקס"]},
    {"item_id": "FG-FRE-1L", "item_name": "FRESH 1L", "status": "ACTIVE",
     "item_type": "FG", "unit": "bottle", "aliases": ["FRESH 1000ml"]},
]
MANIFEST = {"driver_id": 1, "delivery_date": "2026-06-14", "_route_dir": "/r"}

def _resolver():
    return loose_items.Resolver(SNAP)

def test_return_card_basic():
    task = {"task_id": "t1", "route_order": 2, "recipient_name": "קפה X",
            "wp_order_id": None, "pick_state": "FULLY_PICKED",
            "notes": "החזרה: 6 DETOX 1000ml"}
    card = loose_cards.build_card(task, MANIFEST, _resolver(), skill_version="v")
    assert card["category"] == "loose_movement_pending"
    assert card["source"] == loose_cards.SOURCE
    assert card["dedupe_key"] == "loose_mv:1:2026-06-14:t1"
    assert card["related_entity_type"] == "lionwheel_task"
    assert card["related_entity_id"] == "t1"
    d = json.loads(card["detail"])
    assert d["type"] == "return" and d["commit_blocked"] is False
    assert d["legs"][0]["direction"] == "INBOUND"
    assert d["legs"][0]["lines"][0]["item_id"] == "FG-DET-1L"
    assert d["legs"][0]["lines"][0]["quantity"] == 6
    assert card["severity"] == "info"

def test_unresolved_line_makes_card_warning_and_blocked():
    task = {"task_id": "t2", "recipient_name": "X", "wp_order_id": None,
            "pick_state": "FULLY_PICKED", "notes": "החזרה: 6 WIDGET 9000"}
    card = loose_cards.build_card(task, MANIFEST, _resolver(), skill_version="v")
    d = json.loads(card["detail"])
    assert d["commit_blocked"] is True
    assert card["severity"] == "warning"

def test_non_movement_task_returns_none():
    # a plain label-send / delivery with no movement type -> no card
    task = {"task_id": "t3", "recipient_name": "X", "wp_order_id": None,
            "notes": "לשלוח תוויות כשר לפסח - 12 יח'"}
    assert loose_cards.build_card(task, MANIFEST, _resolver(), skill_version="v") is None

def test_check_task_card_no_movement():
    task = {"task_id": "t4", "recipient_name": "בנק - איסוף צ'ק", "wp_order_id": None,
            "notes": "צ'ק"}
    card = loose_cards.build_card(task, MANIFEST, _resolver(), skill_version="v")
    d = json.loads(card["detail"])
    assert d["type"] == "check" and d["legs"] == [] and d["note"] == "check_no_goods"
```

- [ ] **Step 2: Run, verify FAIL.** `python -m pytest tests/test_loose_cards.py -k "card" -v`

- [ ] **Step 3: Implement `build_card` (+ helpers) in `scripts/loose_cards.py`.**

```python
def _title(detail):
    """Hebrew one-liner, e.g. 'תנועת מלאי לאישור — החזרה · קפה X · 6 DETOX 1L (IN)'."""
    type_he = {"return": "החזרה", "exchange": "החלפה", "sample": "טעימה",
               "gift": "מתנה", "check": "איסוף צ'ק"}.get(detail.get("type"), "חריג")
    who = detail.get("recipient_name") or ""
    if detail.get("note") == "check_no_goods":
        return f"תנועת מלאי לאישור — {type_he} · {who} · אין סחורה"
    bits = []
    for lg in detail.get("legs", []):
        arrow = "IN" if lg["direction"] == "INBOUND" else "OUT"
        for ln in lg["lines"]:
            qty = ln.get("quantity")
            name = ln.get("item_name") or ln.get("product_raw") or "?"
            bits.append(f"{qty if qty is not None else '?'} {name} ({arrow})")
    summary = " · ".join(bits) if bits else "ללא פריטים"
    return f"תנועת מלאי לאישור — {type_he} · {who} · {summary}"


def build_card(task, manifest, resolver, skill_version):
    """Return an exceptions-row dict, or None if the task carries no stock
    movement (plain delivery / unrelated). Never silently drops a real
    exception: a movement type with no parsed notation yields a blocked card."""
    cls = loose_classify.classify(task)
    mtype = cls.get("type")
    if mtype not in MOVEMENT_TYPES:
        return None  # pickup-of-nothing / delivery / None -> not a stock movement
    parsed = cls.get("parsed")
    if parsed is None:
        # type known (heuristic) but no structured notation -> surface for Tom
        parsed = {"type": mtype, "segments": [], "flags": ["no_notation"],
                  "raw": task.get("notes") or ""}
    ctx = task_ctx(task, manifest, skill_version)
    mv = loose_movement.compute(parsed, task.get("pick_state"), ctx, resolver.resolve)
    detail = mv["detail"]
    blocked = bool(mv.get("commit_blocked"))
    any_flags = bool(mv.get("flags")) or any(
        l.get("flags") for lg in mv.get("legs", []) for l in lg["lines"])
    severity = "warning" if (blocked or any_flags) else "info"
    return {
        "category": "loose_movement_pending",
        "severity": severity,
        "source": SOURCE,
        "title": _title(detail),
        "detail": json.dumps(detail, ensure_ascii=False),
        "dedupe_key": f"loose_mv:{ctx['driver_id']}:{ctx['delivery_date']}:{ctx['task_id']}",
        "related_entity_type": "lionwheel_task",
        "related_entity_id": ctx["task_id"],
        "recommended_action": "אשר/דחה — באישור המלאי יזוז",
    }
```

Also add `import loose_items` at the top of `loose_cards.py` (used by callers/tests) and ensure `import loose_movement` is present.

- [ ] **Step 4: Run, verify PASS.** `python -m pytest tests/test_loose_cards.py -k "card" -v`

- [ ] **Step 5: Commit.** `git add scripts/loose_cards.py tests/test_loose_cards.py && git commit -m "feat(loose-cards): build one loose_movement_pending card from a task"`

---

## Task 4: Build all cards for a route

**Files:**
- Modify: `scripts/loose_cards.py`
- Test: `tests/test_loose_cards.py`

- [ ] **Step 1: Write failing test** with a fixture manifest of mixed exceptions.

```python
def test_build_cards_for_route(tmp_path):
    manifest = {"driver_id": 1, "delivery_date": "2026-06-14", "_route_dir": str(tmp_path),
                "tasks": [
                    {"task_id": "inv", "invoice_line_items": [{"description": "DETOX 1000ml", "quantity": 6}]},
                    {"task_id": "ret", "recipient_name": "A", "wp_order_id": None,
                     "pick_state": "FULLY_PICKED", "notes": "החזרה: 6 DETOX 1000ml"},
                    {"task_id": "exc", "recipient_name": "B", "wp_order_id": None,
                     "pick_state": "FULLY_PICKED",
                     "notes": "החלפה: מוסר 3 FRESH 1000ml | אוסף 3 DETOX 1000ml"},
                    {"task_id": "lbl", "recipient_name": "C", "wp_order_id": None,
                     "notes": "לשלוח תוויות - 12"},
                ]}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    cards = loose_cards.build_cards(str(tmp_path), SNAP, skill_version="v")
    ids = {c["related_entity_id"] for c in cards}
    assert ids == {"ret", "exc"}  # invoice task skipped; label task = no card
    exc = next(c for c in cards if c["related_entity_id"] == "exc")
    assert len(json.loads(exc["detail"])["legs"]) == 2  # exchange = 2 legs
```

- [ ] **Step 2: Run, verify FAIL.** `python -m pytest tests/test_loose_cards.py -k build_cards -v`

- [ ] **Step 3: Implement `build_cards`.**

```python
def build_cards(route_dir, snapshot, skill_version):
    """Read <route_dir>/manifest.json, build a card for every exception task
    that carries a stock movement. Returns a list of card dicts."""
    route_dir = Path(route_dir)
    manifest = json.loads((route_dir / "manifest.json").read_text(encoding="utf-8"))
    manifest.setdefault("_route_dir", str(route_dir))
    resolver = loose_items.Resolver(snapshot)
    cards = []
    for task in manifest.get("tasks", []):
        if not is_exception_task(task):
            continue
        card = build_card(task, manifest, resolver, skill_version)
        if card is not None:
            cards.append(card)
    return cards
```

- [ ] **Step 4: Run, verify PASS.** `python -m pytest tests/test_loose_cards.py -k build_cards -v`

- [ ] **Step 5: Commit.** `git add scripts/loose_cards.py tests/test_loose_cards.py && git commit -m "feat(loose-cards): build all cards for a route manifest"`

---

## Task 5: Dry-run preview writer (no DB)

**Files:**
- Modify: `scripts/loose_cards.py`
- Test: `tests/test_loose_cards.py`

- [ ] **Step 1: Write failing test.**

```python
def test_write_preview(tmp_path):
    cards = [{"category": "loose_movement_pending", "title": "t", "detail": "{}",
              "dedupe_key": "k", "severity": "info", "source": "s",
              "related_entity_type": "lionwheel_task", "related_entity_id": "ret",
              "recommended_action": "x"}]
    out = loose_cards.write_preview(str(tmp_path), cards)
    assert Path(out).exists()
    data = json.loads(Path(out).read_text(encoding="utf-8"))
    assert data["count"] == 1 and data["cards"][0]["dedupe_key"] == "k"
```

- [ ] **Step 2: Run, verify FAIL.** `python -m pytest tests/test_loose_cards.py -k write_preview -v`

- [ ] **Step 3: Implement.**

```python
def write_preview(route_dir, cards):
    """Write the proposed cards to <route_dir>/loose_movement_cards.json for Tom
    to review. No DB write. Returns the path."""
    out = Path(route_dir) / "loose_movement_cards.json"
    out.write_text(json.dumps({"count": len(cards), "cards": cards},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    return str(out)
```

- [ ] **Step 4: Run, verify PASS.** `python -m pytest tests/test_loose_cards.py -k write_preview -v`

- [ ] **Step 5: Commit.** `git add scripts/loose_cards.py tests/test_loose_cards.py && git commit -m "feat(loose-cards): dry-run JSON preview writer"`

---

## Task 6: Live Inbox writer with SELECT-before-insert dedup

**Files:**
- Modify: `scripts/loose_cards.py`
- Test: `tests/test_loose_cards.py`

Mirror `emitException`: for each card, SELECT an open row with the same `dedupe_key`; if found, skip; else INSERT the 9 columns. The function takes an open DB cursor so it is unit-testable with a fake cursor (no live DB in tests).

- [ ] **Step 1: Write failing test using a fake cursor.**

```python
class _FakeCur:
    def __init__(self, existing_keys=()):
        self.existing = set(existing_keys); self.inserted = []
        self._last = None
    def execute(self, sql, params=None):
        self._last = (sql, params)
        if sql.strip().upper().startswith("SELECT"):
            self._rows = [("x",)] if (params and params[0] in self.existing) else []
        else:
            self.inserted.append(params)
    def fetchall(self): return getattr(self, "_rows", [])
    def fetchone(self): return (self._rows[0] if getattr(self, "_rows", []) else None)

def test_write_cards_inserts_new_skips_existing():
    cards = [
        {"category":"loose_movement_pending","severity":"info","source":"s","title":"t1",
         "detail":"{}","dedupe_key":"k1","related_entity_type":"lionwheel_task",
         "related_entity_id":"a","recommended_action":"x"},
        {"category":"loose_movement_pending","severity":"info","source":"s","title":"t2",
         "detail":"{}","dedupe_key":"k2","related_entity_type":"lionwheel_task",
         "related_entity_id":"b","recommended_action":"x"},
    ]
    cur = _FakeCur(existing_keys=["k1"])  # k1 already open -> skip
    res = loose_cards.write_cards(cur, cards)
    assert res == {"inserted": 1, "skipped": 1}
    assert len(cur.inserted) == 1 and cur.inserted[0][5] == "k2"  # dedupe_key is param index 5
```

- [ ] **Step 2: Run, verify FAIL.** `python -m pytest tests/test_loose_cards.py -k write_cards -v`

- [ ] **Step 3: Implement `write_cards(cur, cards)`.**

```python
def write_cards(cur, cards):
    """INSERT each card into private_core.exceptions, skipping any whose
    dedupe_key already has an OPEN row (mirrors emitException). `cur` is a DB
    cursor. Returns {'inserted': n, 'skipped': m}. Caller owns the
    connection/transaction. NEVER moves stock — only writes a proposal row."""
    inserted = skipped = 0
    for c in cards:
        cur.execute(
            "SELECT exception_id FROM private_core.exceptions "
            "WHERE dedupe_key = %s AND status = 'open' LIMIT 1",
            (c["dedupe_key"],))
        if cur.fetchall():
            skipped += 1
            continue
        cur.execute(
            "INSERT INTO private_core.exceptions ("
            "category, severity, source, title, detail, dedupe_key, "
            "related_job_run_id, related_entity_type, related_entity_id"
            ") VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (c["category"], c["severity"], c["source"], c["title"], c["detail"],
             c["dedupe_key"], None, c["related_entity_type"], c["related_entity_id"]))
        inserted += 1
    return {"inserted": inserted, "skipped": skipped}
```

Note: `recommended_action` is carried in the card dict for the preview/title but is NOT a column in the INSERT (emitException doesn't write it). Keep it in the preview only.

- [ ] **Step 4: Run, verify PASS.** `python -m pytest tests/test_loose_cards.py -k write_cards -v`

- [ ] **Step 5: Commit.** `git add scripts/loose_cards.py tests/test_loose_cards.py && git commit -m "feat(loose-cards): live Inbox writer with SELECT-before-insert dedup"`

---

## Task 7: CLI entry + pooled-DB connection + SKILL.md wiring

**Files:**
- Modify: `scripts/loose_cards.py`
- Modify: `SKILL.md`
- Test: `tests/test_loose_cards.py`

CLI: `python scripts/loose_cards.py <route_dir> [--write]`. Default = preview only (writes `loose_movement_cards.json`, no DB). `--write` = preview AND INSERT to the Inbox via the pooled URL. The snapshot is read from `<route_dir>/_active_skus.json` (produced by `list_active_skus.py`); if absent, run that first.

- [ ] **Step 1: Write a failing test for `main` in preview mode** (no DB).

```python
def test_main_preview_only(tmp_path, monkeypatch, capsys):
    (tmp_path / "_active_skus.json").write_text(json.dumps(SNAP), encoding="utf-8")
    manifest = {"driver_id": 1, "delivery_date": "2026-06-14", "_route_dir": str(tmp_path),
                "tasks": [{"task_id": "ret", "recipient_name": "A", "wp_order_id": None,
                           "pick_state": "FULLY_PICKED", "notes": "החזרה: 6 DETOX 1000ml"}]}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    rc = loose_cards.main([str(tmp_path)])  # no --write
    assert rc == 0
    assert (tmp_path / "loose_movement_cards.json").exists()
```

- [ ] **Step 2: Run, verify FAIL.** `python -m pytest tests/test_loose_cards.py -k main_preview -v`

- [ ] **Step 3: Implement the pooled connection + `main`.**

```python
def _skill_version():
    """Best-effort version stamp for the card detail/audit. Uses the skill dir
    name + a static tag; refine if a VERSION file is added later."""
    return "lionwheel-route-invoices/phase1-partB"


def _connect_pooled():
    """Connect to Postgres via DATABASE_URL_POOLED (the direct Supabase host is
    DNS-dead — see reference_lionwheel_skill_db_pooler_shim). Read from
    gt-factory-os/.env. Returns a psycopg connection."""
    import re
    env_path = Path(r"C:/Users/tomw2/Projects/gt-factory-os/.env")
    url = None
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*DATABASE_URL_POOLED\s*=\s*(.*)$", raw)
        if m:
            url = m.group(1).strip().strip('"').strip("'"); break
    if not url:
        raise RuntimeError("DATABASE_URL_POOLED missing in gt-factory-os/.env")
    import psycopg
    return psycopg.connect(url)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Phase 1 loose-movement Inbox cards (preview by default)")
    ap.add_argument("route_dir")
    ap.add_argument("--write", action="store_true",
                    help="ALSO INSERT the cards into the Inbox (default: preview only, no DB)")
    args = ap.parse_args(argv)
    route_dir = Path(args.route_dir)
    snap_path = route_dir / "_active_skus.json"
    if not snap_path.exists():
        sys.stderr.write(f"missing {snap_path} — run list_active_skus.py first\n")
        return 1
    snapshot = json.loads(snap_path.read_text(encoding="utf-8"))
    cards = build_cards(str(route_dir), snapshot, _skill_version())
    out = write_preview(str(route_dir), cards)
    print(f"preview: {out}  ({len(cards)} card(s))")
    for c in cards:
        print(f"  [{c['severity']}] {c['title']}")
    if args.write:
        conn = _connect_pooled()
        try:
            with conn, conn.cursor() as cur:
                res = write_cards(cur, cards)
            print(f"inbox: inserted {res['inserted']}, skipped {res['skipped']}")
        finally:
            conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run, verify PASS.** `python -m pytest tests/test_loose_cards.py -k main_preview -v`

- [ ] **Step 5: Run the FULL suite** to confirm no regressions. `cd "<skill>" && python -m pytest -q` — Expected: all PASS (104 prior + the new loose_cards tests).

- [ ] **Step 6: Wire into SKILL.md.** In the FULL DAILY FILE pipeline section, after Step 6 (merge) / before Step 7 (open), add a Phase-1 step:

```markdown
8. **Loose-movement proposal cards (Phase 1 — no commit).** For exception tasks, run
   `python scripts/loose_cards.py <route_dir>` → writes `loose_movement_cards.json` (preview, **no DB**).
   Review the proposals with Tom. On Tom's OK, run `python scripts/loose_cards.py <route_dir> --write`
   to create the `loose_movement_pending` cards in the Inbox (`private_core.exceptions`). **This moves NO stock** —
   Tom approves each card in the portal (Phase 2 / Parts C+D) to actually commit. Same-SKU exchanges are flagged
   `commit_blocked` and handled manually until the Phase-2 disambiguator ships.
```

- [ ] **Step 7: Commit.** `git add scripts/loose_cards.py tests/test_loose_cards.py SKILL.md && git commit -m "feat(loose-cards): CLI + pooled DB writer + SKILL.md Phase-1 wiring"`

---

## Task 8: Dry-run runbook (live validation, no stock)

**Files:**
- Create: `docs/superpowers/plans/2026-06-14-loose-movement-phase1-dryrun-runbook.md` (in PRODUCTION)

This task is a written runbook (no code) for the live dry-run with Tom. It is the Phase-1 acceptance gate.

- [ ] **Step 1: Write the runbook** with these exact steps:
  1. Run a normal route build for a route that has at least one exception task (or use the day's real route).
  2. Ensure `_active_skus.json` is fresh: `python scripts/list_active_skus.py <route_dir>`.
  3. Preview: `python scripts/loose_cards.py <route_dir>` → open `loose_movement_cards.json`; with Tom, confirm each proposed movement (type, direction, item_id, qty, flags). **Resolve the probe here:** confirm the `task_status_at_commit` value real return tasks carry (returns lack `לוקט/חלקית/חדש`) — if a return shows `unknown_status`+`commit_blocked`, that's correct gating; note the real signal for Phase 2.
  4. Only after Tom approves the previews: `python scripts/loose_cards.py <route_dir> --write`.
  5. Verify in DB (read-only): `SELECT exception_id, category, severity, title, status FROM private_core.exceptions WHERE category='loose_movement_pending' AND status='open' ORDER BY created_at DESC LIMIT 20;` — confirm one open card per exception task, correct severity, no duplicates on re-run (dedup).
  6. Re-run `--write` once more → confirm `inserted 0, skipped N` (dedup works).
  7. **Acceptance:** cards exist with correct `detail.legs`, no stock moved (there is no commit path yet), dedup holds. Phase 1 done → proceed to Phase 2 plan (Parts C+D) under the governance wrap.

- [ ] **Step 2: Commit.** `git add docs/superpowers/plans/2026-06-14-loose-movement-phase1-dryrun-runbook.md && git commit -m "docs(plan): Phase-1 loose-movement dry-run runbook"`

---

## Self-Review (completed)

- **Spec coverage:** §6 Part B steps 1-6 → Tasks 2-7; §8 card contract + §R1 detail fields → Task 3 (uses `compute()`'s `detail`); §R7 store-in-`detail` + SELECT-before-insert dedup → Tasks 3 & 6; §R2 idempotency → already in `compute()` (carried in `detail.legs[].idempotency_key`); §R6 bilingual resolve → Task 1; §16 same-SKU gate → `compute()` sets `commit_blocked` → Task 3 severity=warning. Dry-run milestone → Task 8.
- **No stock movement:** confirmed — no task calls the loose-shipment endpoint; `write_cards` only INSERTs a proposal row. Stock commit is Phase 2.
- **Placeholder scan:** none — every code step is complete; `_skill_version` is a real (if simple) stamp, not a TODO.
- **Type consistency:** `build_card`→dict with keys reused verbatim by `write_cards`/`write_preview`/`main`; `task_ctx` keys match `compute()`'s required `ctx`; `dedupe_key` format identical in Task 3 and the runbook query.
- **No migration needed:** `exceptions.category` is free-text (verified migration 0010 E4).

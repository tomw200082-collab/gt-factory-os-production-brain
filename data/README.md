# PRODUCTION/data/ — Operational Reference Files

These files are **operational references only**. None of them are canonical runtime code or source of truth unless explicitly stated in `CURRENT_STATE.md` or `WORKSPACE_MAP.md`.

Runtime truth lives in `gt-factory-os/` (backend) and `tomw200082-collab/gt-factory-os-portal` (frontend portal).

---

## Structure

### `excel/active/`
Current operational Excel workbooks (GT_Factory_OS, GT_Master_Data, purchase plans, forecasts, product lists).  
These are **transitional reference files** — not editable by the system, not canonical truth.  
The system reads from Postgres, not from these files.

### `excel/backups/`
Historical Excel backups named with a `.bak-*` suffix.  
Created before significant data operations as safety snapshots.  
Do not use as source of truth. Do not edit.

### `excel/temp-locks/`
Excel temporary lock files (`~$*.xlsx`).  
Created by Excel when a workbook is open. These were stale (Excel not open) at time of move.  
Do not delete — they are evidence artifacts.  
If a fresh lock file appears at PRODUCTION root, leave it in place until the workbook is closed.

### `json/shopify/`
Shopify export/reference dumps (e.g. `shopify-products-full.json`).  
Used for one-off reference and import planning only.  
Shopify live truth comes through the integration API, not these files.

### `invoices/suppliers/`
Scanned supplier invoices and operational invoice references; not runtime code and not canonical accounting source unless explicitly stated.  
Subdirectories:
- `unprocessed/` — scanned invoices awaiting entry into Green Invoice / the system
- `processed/` — invoices confirmed as entered into the system (auto-routing here is a future GI pipeline enhancement)

Current files landed in `unprocessed/` as a conservative default pending explicit classification by Tom.  
Migrated from `PRODUCTION/חשבוניות ספקים/` on 2026-05-08. Original archived at `PRODUCTION/archive/migrated-to-data/`.

---

## What never lives here
- Source code (TypeScript, Python, SQL)
- Migration files
- Agent configurations
- Governance documents (those live at PRODUCTION root or in `.claude/`)

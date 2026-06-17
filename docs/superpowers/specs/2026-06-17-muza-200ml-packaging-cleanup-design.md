# Muza 200ML Packaging Cleanup — Design Decision Record

> **Status:** APPROVED by Tom 2026-06-17 — design locked, proceeding to the implementation plan.
> **Owner:** Tom · **Author:** Claude · **Touches STOCK TRUTH** (boot-kernel non-negotiable #1 — opening-stock anchors).
> **Scope:** the 5 Muza 200ML cocktails' packaging components, in `gt-factory-os` Postgres (`private_core`). Master data + opening stock only. **No price work** (deferred per Tom), no BOM-recipe change, no ledger movements.

## Goal
Make the Muza 200ML packaging reflect how GT **actually buys** it, so procurement planning is correct: stop sourcing bottle/cap/carton as one bundle from the brand (`SUP-041 "Muza Cocktails"`), point each at its real packaging supplier (like the gold-standard 1L mixer line), and give every packaging component an opening on-hand so the planner nets against real stock.

## Current state (verified read-only this session)
The 5 cocktails — `FG-MUZ-{HER,JAS,NEG,PSC,QUE}-200ML` — are all ACTIVE with ACTIVE PACK BOMs. Their packaging already exists as **separate** `private_core.components` lines (bottle / cap / label / carton), so the *line structure* is fine. The gaps:

- **Bottle, cap, carton are all sourced from `SUP-041 "Muza Cocktails"`** — the brand itself (`supplier_type EXTERNAL`), not a packaging supplier. These three are the **only** bottle/cap/carton in the whole catalog still pointed at the brand (every other points at a real packaging supplier). This is the "written-as-one / bought-as-a-bundle" anomaly. (`SUP-041` correctly remains the supplier of the Muza **mixer/cocktail FGs** — untouched.)
- **The 5 labels are already correct** — distinct per flavor, `primary_supplier_id = SUP-022` (Miki Madbekot), Sagol (`SUP-042`) as approved ALTERNATE, cost 0.43, re-pointed to Miki 2026-06-01. **No master-data change needed.**
- **None of the 8 packaging components has any `current_balances` row** — completely untracked (vs the 1L mixer's bottle/cap/carton at 161/271/60). This is why "set 1000 of each label" is needed.
- `label_size_id` is null on all (matches "no sizes yet"); the `label_sizes` table has no 200ml size. **Left null.**

**Gold standard (1L mixer, Tom-endorsed as fully correct):** bottle+cap → Arizot 2100 (`SUP-002`), carton → Eliran Kartonim (`SUP-020`), real costs, stock tracked. The 200ML target below makes the line match this exactly.

## Locked decisions (2026-06-17)

| Decision | Chosen | Rationale / rejected |
|---|---|---|
| **What "as one" means** | Bottle/cap/carton bundled under brand `SUP-041`; **split each onto its real packaging supplier.** | Only genuine anomaly in the data; labels were already cleaned up. |
| **Labels per bottle** | **One** label component per flavor (current model is right). | Tom confirmed; not a front/back split (unlike Matcha). |
| **Bottle + cap supplier** | **Arizot 2100 (`SUP-002`)** — both. | Tom-named. Matches the 1L mixer bottle/cap. |
| **Carton supplier** | **Eliran Kartonim (`SUP-020`)**. | Eliran is "default for ALL cartons"; matches 1L mixer. |
| **Labels supplier** | **No change** — already Miki (`SUP-022`) + Sagol alternate. | Already correct. |
| **Label opening stock** | **1000 each** (5 labels). | Tom-specified. |
| **Bottle/cap/carton opening stock** | **0 each** (explicit baseline, real count later). | Tom chose truth-first; planner will recommend buying. |
| **Stock mechanism** | `balance_anchors_current` row, `anchor_source='COUNT_APPROVAL'`, approved by Tom, `anchor_at`=2026-06-17 — **never a direct `current_balances` edit**. | Matches how the other label anchors were seeded 2026-05-12; `current_balances` is a rebuilt projection. |
| **Costs & names** | **Deferred** — keep the existing est. supplier_item costs (1.10 / 0.25 / 1.40) as placeholders; no rename. | Tom: "details like price later." Component-level `std_cost` + physical-spec names belong with the price pass. |
| **BOM recipe & ledger** | **Untouched.** | Out of scope; append-only ledger gets no fabricated movements. |

## The exact change

**A · Master data — re-point 3 components off `SUP-041`** (update both `components.primary_supplier_id` **and** the existing PRIMARY `supplier_items` row's `supplier_id`; keep the placeholder cost; update `notes`/`source_basis` to record the 2026-06-17 split):

| Component | `primary_supplier_id`: from → to | placeholder cost kept |
|---|---|---|
| `PKG-BOTTLE-200ML` | `SUP-041` → **`SUP-002`** (Arizot 2100) | 1.10 |
| `PKG-CAP-200ML` | `SUP-041` → **`SUP-002`** (Arizot 2100) | 0.25 |
| `PKG-CARTON-200ML` | `SUP-041` → **`SUP-020`** (Eliran Kartonim) | 1.40 |

**B · Stock — 8 opening anchors** (`site_id='GT-MAIN'`, `item_type='PKG'`, `batch_id_or_empty=''`, `anchor_source='COUNT_APPROVAL'`, `anchor_at='2026-06-17'`, `approved_by_user_id` = Tom `0db008a9-05e3-4521-8b30-42e5d444818d`, note = "opening baseline, Muza 200ML packaging setup 2026-06-17"):

| Components | `anchor_qty` |
|---|---|
| `PKG-LABEL-MUZ-{HER,JAS,NEG,PSC,QUE}-200ML` (5) | **1000** |
| `PKG-BOTTLE-200ML`, `PKG-CAP-200ML`, `PKG-CARTON-200ML` (3) | **0** |

## Execution approach
A single **numbered SQL migration** in `gt-factory-os/db/migrations`, authored in a **git worktree cut from `origin/main`** (migration number taken from origin/main's highest, not the drifted local ledger). Idempotent: `UPDATE` guards on the supplier re-points; anchors via `INSERT … ON CONFLICT (site_id,item_type,item_id,batch_id_or_empty) DO UPDATE` (pre-checked that the 8 components have no existing anchor). Applied to prod via the documented manual path (`MIGRATION_ALLOW_PRODUCTION=confirmed node scripts/_apply_migration.mjs <file>`). After insert, the **balance projection is rebuilt** (identify the rebuild fn/job; don't rely on the nightly run for verification). **Adversarial review pass** on the migration before the prod apply (append-only respected · anchors not balance-edits · supplier IDs valid/ACTIVE · projection rebuild handled · idempotent on re-run).

## Governance
Opening-stock anchors are **stock-truth production work** → decision packet → `factory-os-governor` verdict → `release-verifier` before the prod apply (per boot-kernel stop condition: halt on stock-truth-impacting ops, route to governor). The anchor rows themselves encode Tom's approval (`approved_by_user_id`). Master-data re-points are reversible `UPDATE`s. No frozen flags, no external-system writes, no destructive ops. Mission-scoped git/deploy authority applies (commit/push/PR/apply with evidence).

## Verification / evidence (read-only; shadow DB is dead)
1. `components.primary_supplier_id` = SUP-002 / SUP-002 / SUP-020 for bottle/cap/carton; matching PRIMARY `supplier_items.supplier_id`; no remaining packaging component on `SUP-041`.
2. `balance_anchors_current` has 8 new rows with the right `anchor_qty` and Tom approval stamp.
3. After rebuild, `current_balances` shows on-hand **1000** for each of the 5 labels and **0** for bottle/cap/carton.
4. No `stock_ledger` rows were written; BOM lines unchanged.
5. A planning dry-run nets the 5 labels against 1000 on-hand and recommends buying bottle/cap/carton (from Arizot 2100 / Eliran).

## Deliberately NOT touched
Label supplier (already Miki) · BOM recipe lines · `stock_ledger` · component names · component/supplier costs (placeholders kept) · `label_size_id` (null) · `SUP-041`'s relationships to the Muza FG items.

## Open flags (Tom-Tax — confirm when convenient, not blocking)
- **Carton ratio** is `1/12` (12 bottles/carton) in the BOM; the 1L is `1/6`. Left as-is — confirm 12-per-carton is physically right.
- **Component-level `std_cost`** is null on bottle/cap/carton (cost only on the supplier_item), unlike the gold-standard 1L. Fold into the later price pass.
- **PSC** (`FG-MUZ-PSC-200ML`) reads ACTIVE in prod, though an older memory note flagged it "draft-stuck" — treated as a normal active flavor here.

# Forecast findings log — daily-ops-guardian

Append-only. date | item | signal | evidence (live SQL, run date) | direction. Log only — forecast edits via weekly/monthly proposals (V6).

## 2026-07-03 (first guardian run; forecast version 369f5cb1 published 2026-06-08, 25d old 🟡)

| item | signal | evidence (14d window) | direction |
|---|---|---|---|
| FG-MAT-30G | committed > forecast | committed 300 vs forecast 177.3 | forecast under-estimates matcha B2B demand; raise |
| GTCC-MUZ-SMAR-1L | committed > forecast ×2.4 | committed 14 vs forecast 5.9 | Muza spicy margarita under-forecast |
| ADD-MUZ-HER-1L | committed ≈ forecast, zero stock | committed 4, forecast 5.9, on-hand 0 | confirm Muza line status (parked) — real orders exist |
| FG-CON-1L | forecast demand w/o supply plan | forecast 175 /14d, on-hand 105, planned 0 | not a forecast miss — planning gap; handed to Thursday ritual |
| FG-SAN-WHI-750ML | forecast w/o production | forecast 40.9, on-hand 12, planned 0 | check if sangria forecast still realistic (summer) |

Data-quality flags (not forecast): negative on-hand — FG-SAN-RED-3850ML −1, FG-SAN-BAB-RED/WHI-750ML −6/−6, ADD-GAR-ORA-DRY −16, EXCLUDED-NONSTOCK −346. rebuild_verifier=0 ∴ ledger-consistent negatives = unrecorded production/receipt events.

## 2026-07-05 (second guardian run; manual, morning trigger produced no evidence — see run notes below; forecast version 369f5cb1 published 2026-06-08, unchanged, now 27d old 🟡)

| item | signal | evidence (14d window) | direction |
|---|---|---|---|
| FG-DET-STR-500ML | no forecast coverage at all | committed backlog 1,250 units / 7 open orders (oldest 2026-06-08, 27d) vs forecast_14d = 0 (item absent from `fn_forecast_daily_demand` output entirely) | confirm this B2B/Elita-Ofek line is intentionally forecast-exempt (custom account), or add forecast coverage |
| FG-DES-1L | committed ≈ forecast, zero firmed batch found | committed 51 (3 orders, oldest 2026-06-24, 11d) vs forecast 60.45; no `production_plan` row (item- or base-level) in next 14d | needs a Thursday-ritual production slot, or confirm this item is intentionally parked like the Muza line |
| ADD-MUZ-PNMM-1L | committed persists, oldest unfulfilled order now 42 days | committed 25 (5 orders, oldest 2026-05-24) vs forecast 83.64; still no firmed batch (Muza line parked per 2026-07-03 finding) | Muza line status decision is more urgent now — oldest unfulfilled order has aged from unknown to 42 days |
| FG-ENE-1L / FG-ENE-500ML | committed backlog keeps growing against a known, deliberate no-batch decision | committed 27+24=51 units (10 open orders) vs forecast 157.7+72.7; base deprioritized vs CON-REG per Tom's 2026-07-04 delegated tradeoff (plan-production-14d) | re-confirm the ENE vs CON tradeoff at the next Thursday ritual now that backlog is still accumulating |

Data-quality / engine-contract flag (not forecast): `fn_compute_daily_fg_projection`'s `incoming_supply_qty` nets only `purchase_order_lines` receipts, not firmed `production_plan` output — so its raw FG shortfall read this run (41/79 active items, ~₪22,994 material margin "at risk" over 14d) is a *zero-further-production* baseline, not netted against this week's already-firmed, Tom-approved 2026-07-04 batches. Cross-checked manually against `production_plan`: most flagged items already have a scheduled batch inside the window. Recommend the engine eventually nets firmed production as "incoming supply" the same way it nets PO receipts — flagged here for awareness, not actioned (out of guardian's write scope).

Run note: today's 06:30 IDT scheduled trigger fired (per trigger logs) but produced no completion evidence (no commit here, presumably no email) — leading hypothesis is the fresh/headless trigger session lacked live Supabase access. This run is a manual make-up executed from an interactive session with confirmed live Supabase + Gmail access, to isolate "skill bug" from "trigger infrastructure gap."

## 2026-07-06 (manual run, Tom asked explicitly for a forecast-improvement suggestion; forecast version 369f5cb1 published 2026-06-08, now 28d old 🟡 — first run past the 14d staleness threshold)

Stage 1b two-window persistence test (day −28..−15 vs −14..0) run read-only against `fn_forecast_daily_demand` + `stock_ledger` FG_OUT_PICK, per plan-production-14d §1b. 18 items passed the >15%/>15% same-direction filter.

**Routine correction candidates (not stock/backlog-censored, factor inside [0.5, 2.0] clamp — proposed to Tom in chat this run, none written without approval, per V6):**

| item | actual_b (14d rate) | forecast_b | dev | proposed_factor |
|---|---|---|---|---|
| FG-REV-500ML | 7.57/day | 3.92/day | +93.0% | 1.47 |
| FG-FRE-500ML | 7.36/day | 5.95/day | +23.6% | 1.12 |
| FG-DES-1L | 4.14/day | 3.50/day | +18.4% | 1.09 |
| FG-DET-500ML | 11.21/day | 20.84/day | −46.2% | 0.77 |
| ADD-GAR-ROSE-DRY | 0.29/day | 0.52/day | −45.0% | 0.77 |

**Structural (factor outside clamp — flagged for Tom's judgment, NOT a routine proposal):**

| item | dev | implied factor |
|---|---|---|
| FG-SAN-WHI-1L | +560.0% | 3.80 |
| FG-MAT-18G | +294.6% | 2.47 |

**Stock/backlog-censored (real signal exists, cannot be trusted yet — low actuals reflect empty shelf or unpicked backlog, not low demand):** FG-FRE-500ML-NS, FG-MAT-500G, GTCC-MUZ-APPZ-1L, FG-NM-3850ML, FG-FRE-1L, FG-NM-1L, FG-DET-1L, FG-REV-1L, FG-NAM-1L, FG-DET-1L-NS, FG-CAL-1L.

**Separate finding — forecast staleness itself:** published version `369f5cb1` is now 28 days old, past the 14d Stage-0 threshold for the first time since this skill started tracking (was 25d on 2026-07-03, 27d on 2026-07-05). Horizon (`2026-06-01` + 9 weeks = through `2026-08-03`) still covers the planning window, so this is a freshness/quality flag, not a coverage gap — but the correction-factor drift above (5 routine + 2 structural candidates, mostly this run) is consistent with a forecast that is due for a full republish rather than one-off factor patches. Recommend: republish the forecast at the next monthly cycle (guardian is 2026-07 first-of-month proposal per §Monthly) rather than accumulating more per-item factors.

**RM/PKG gaps found in Stage 2 (latest planning run 2026-06-23, 13d stale — read-back only, not re-run):** `RAW-LEMON-JUICE` (11.36 on hand) and `RAW-MERLOT-GRAPES` (1.73 on hand) both feed multiple Muza batches marked `ready_if_purchase_executes` in that run but have **no line in the current open purchase session** (`2026-07-04`) — a real procurement gap, not yet actioned (handed to procurement-planning skill scope, not written here). `PKG-LABEL-MUZ-JASM-1L` has `needs_purchase_missing_supplier` (zero supplier mapping) blocking the entire Muza Jasmine line at every recommended batch size — needs a new supplier before it can even enter a purchase session. `ADD-MUZ-BZSM-1L` still `blocked_missing_bom` (no active BOM version) — same as prior runs, unresolved.

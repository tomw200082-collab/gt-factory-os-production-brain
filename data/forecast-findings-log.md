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

## 2026-07-10 (third guardian run; rebuild_verifier=0 live; forecast version 369f5cb1 published 2026-06-08, unchanged, now 32d old 🟡 — third consecutive run flagging this same stale version)

| item | signal | evidence (live SQL this run) | direction |
|---|---|---|---|
| PKG-CAP-PLASTIC-28 / PKG-BOTTLE-500ML | component gap blocks firmed production in 2 days, session PO already drafted but never actioned | 31d net position −6,275 / −2,756; first demand day 2026-07-12; both components sit in purchase_session (session_id 23dea385, dated 2026-07-04, still `open`) as session_po `ec4db7d9…` status=`skipped` since creation | not a forecast issue — an actioning gap; recommend Tom/Doreen review the skipped session PO before Sunday |
| FG-MAT-30G | zero coverage, any horizon — no production_plan row for this item has ever existed | on-hand 0, committed backlog 300 (1 order, oldest 2026-06-29 → 11d old), forecast_14d 177.3, no repack batch scheduled (BOM-REPACK-MAT-30G) | needs an explicit Thursday-ritual decision — this is not a forecast-accuracy issue, it's an unscheduled line |
| ADD-MUZ-PNMM-1L | committed backlog aging continues past last run's flag | oldest unfulfilled order now 47 days (2026-05-24→2026-07-10, up from 42d on 2026-07-05); production_plan already has 80 units planned 2026-07-21 against 132 backlog (Tom-approved 2026-07-09, notes flag "132 (46 יום!)") | partial coverage exists and is Tom-aware; re-confirm remaining-52-units completion timing at Thursday ritual |
| all 71 active FG items | `demand_lionwheel_qty` (dated committed) = 0 for every single item this run — third consecutive confirmation the engine sees zero committed demand | `orders_mirror`: 35/35 open orders (all `UNASSIGNED/ASSIGNED/ACTIVE`) still have `pickup_at IS NULL`; `fn_compute_daily_fg_projection` committed_dated_14d summed to 0.00 across all 71 FG rows | not a forecast miss — confirms the known engine-contract gap persists unresolved; committed demand is only visible via the manual dateless-backlog overlay |

Data-quality / engine-contract flag (not forecast, recurring from 2026-07-05): raw `fn_compute_daily_fg_projection` 14d shortfall read this run = 43/71 active FG items (zero-further-production baseline). Manually netted against firmed `production_plan` (item_id or base_bom_head_id match, status in planned/draft, plan_date in window): 19 of those 43 already have a Tom-approved covering batch inside the 14d window (e.g. all core DETOX/FRESH/CALM/ENERGY/REVIVE/NAMASTEA/CONSCIOUSNESS 1L+500ML SKUs, approved 2026-07-09) — false alarms once netted. Real uncovered-in-14d count: 24 items, concentrated in Sangria/Nonomimi (FG-SAN-RED-3850ML, FG-SAN-WHI-750ML, FG-SAN-BAB-RED/WHI-750ML, FG-NM-1L, FG-NM-3850ML), Muza 200ml cocktails (JAS/NEG/HER/QUE — covered only 2026-08-02, outside this window), Muza 1L cocktails (APPZ/PSSP/SMAR), and the Matcha line (FG-MAT-30G, FG-MAT-500G, GT-MAT-KIT). Recommend the engine eventually nets firmed production the same way it nets PO receipts (flagged twice now, still out of guardian's write scope).

Data-quality flags (persisting, not forecast): negative on-hand still present on ADD-GAR-ORA-DRY and a few others (rebuild_verifier=0 ∴ ledger-consistent, same unrecorded-event pattern as 2026-07-03/07-05). PKG-BOTTLE-1L has an `expected_receive_date` of 2026-07-05 (5 days overdue) still `OPEN`/unreceived for 32,999 units — not yet a shortage (net position still +28,480 over 31d) but worth a receiving-desk check.

Run note: this run executed live end-to-end (Stage 0 rebuild_verifier re-verified = 0 live, not assumed) from an interactive session per Tom's request to make today's 06:30 delivery land after the 2026-07-05 trigger-infrastructure gap. No new `production_plan` or purchase-session drafts were written this run — the two candidate FG-level gaps (FG-MAT-30G repack batch parameters; Muza-200ml plan-date-vs-backlog mismatch) both lacked enough precedent/context to draft with confidence, and the component-level gaps already have an existing (if un-actioned) purchase-session draft — so per the 2026-07-05 judgment (surface hard findings, leave engine calls to Tom), this run is read-only + log-append only.

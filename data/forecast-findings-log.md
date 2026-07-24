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

## 2026-07-24 (restoration-verification run; manual, Friday; forecast c7e9db2a published 2026-07-23, age 0 🟢; rebuild_verifier=0 🟢)

Verdict 🟡 לעקוב (WATCH): stock truth clean, **zero committed (dated) orders at risk**, watch items are forecast-driven production + procurement (open weekly session) + a data-quality cluster.

| item | signal | evidence (live SQL 2026-07-24, 14d window 07-24..08-06) | direction |
|---|---|---|---|
| FG (38 of 67 items) | forecast shortfall, committed = 0 | `fn_compute_daily_fg_projection`: 38 items project a stockout; `demand_lionwheel_qty`=0 for every one; largest DETOX 1L −86.4, FRESH 1L −58.6, DETOX 1L NS −35.5, DETOX 0.5L −32.7 | not committed-driven — production-planning coverage. Summer DETOX/FRESH forecast looks high vs on-hand; confirm realism at Thursday retro |
| FG-MAT-30G | forecast shortfall persists | −17.7 / 14d vs forecast 88.6 | matcha demand still strong (consistent w/ 2026-07-03 finding); forecast holding |
| ADD-MUZ-PNMM-1L | reported yesterday, still short forward | 71 planned + 93 total reported 07-23; forward −8.4 / 14d | Muza Pink Mama now in production (was parked per 07-03/07-05) — good; keep on plan |
| (procurement, not forecast) PO-2026-00216 | overdue receipt 18d | PKG-BOTTLE-1L 32,999 u, expected 2026-07-05, still OPEN; projection counts it as arrived → suppresses reorder | chase supplier / update expected date / close line |
| (data-quality) RM/PKG counts | 15 of 25 in-scope components stale or never-counted, oldest 73d | purchase_session 62179ce9 `input_integrity.counts` | schedule counts before next purchase placement |

Delivery / run evidence (V4, observed this session — no fabrication): rebuild_verifier=**0**; FG via `fn_compute_daily_fg_projection`; RM via `planning_run_component_netting` (run 2ad307b8, 90/141 components net-positive, ₪38,990 across 10 draft POs in open session 62179ce9); email POSTed to Make webhook → **HTTP 200 "Accepted"**; Make execution `b987cb5a` status=success (2 ops, 27,873 B, 06:05:52Z); email confirmed delivered to tom@gteveryday.com (thread `19f92baf5228748a`, 06:05:53Z). Yesterday production report present (2/2 batches, 93 of 101 u; plan rows not linked-closed — `completed_submission_id` null — minor data note, not a missing-report red).

Root-cause of the 2026-07-05 → 07-24 log gap: fresh scheduled-session runs were not completing the full loop (live-SQL → fill → send → **commit findings-log** → chat). The Make→Gmail delivery leg itself continued to fire on some days (executions on 07-21/07-23), so delivery infra was not the failure — the full guardian loop was. Mitigation this session: skill hardened with a **connector pre-flight** (V9) so a connector-less session fails *loudly* (chat/push + Gmail-draft note + a FAILURE log row) instead of silently no-op'ing.

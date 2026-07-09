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

## 2026-07-09 (third guardian run; manual, Thursday — plan-production-14d ritual day; forecast version 369f5cb1 published 2026-06-08, unchanged, now 31d old 🟡; rebuild_verifier=0, last planning run 2026-06-23)

| item | signal | evidence (14d window) | direction |
|---|---|---|---|
| FG-DET-STR-500ML | improving — not a new alarm | committed backlog now 850 units / 5 open orders (oldest 2026-06-09, 30d), down from 1,250/7 on 2026-07-05; 500L batch firmed for 2026-07-14 (Tom-approved 2026-07-04 note references the tranche plan) | system already handling this correctly via the tranche plan; keep scheduling next tranche, no new action |
| ADD-MUZ-PNMM-1L | Muza line status decision now overdue 46 days | committed 132 units / 3 orders, oldest 2026-05-24 (46d); still zero production_plan row; 6 more Muza SKUs (FG-MUZ-JAS-200ML, ADD-MUZ-PRPL-1L, ADD-MUZ-TRIL-1L, FG-MUZ-NEG-200ML, ADD-MUZ-JASM-1L, FG-MUZ-HER-200ML, FG-MUZ-QUE-200ML) share the same zero-plan pattern, committed gaps 24–144 units each | this has recurred in every guardian run since 2026-07-03; escalating to a direct ask in today's report rather than another silent log line |
| FG-FRE-1L (base FRE-REG) | new — base fully unscheduled | on-hand 26, committed backlog 97/13 orders, gap 71 units, ~₪1,764/day material margin at risk; base_bom_head_id BOM-BASE-FRE-REG has zero `production_plan` rows (planned or draft) anywhere in the 14d window, while sibling bases (DET-REG, DET-STR, NAM-REG, FRE-NS, CAL-REG) all have at least a draft or planned batch | flagged for today's Thursday ritual — highest-margin unscheduled gap found this run |
| FG-MAT-30G / FG-MAT-500G | persists — still zero repack batch | FG-MAT-30G: 0 on-hand vs 300 committed (1 order, since 2026-06-29, 10d); FG-MAT-500G: 3 on-hand vs 8 committed, ~₪2,822/day material margin at risk | same gap as 2026-07-03 finding, still unaddressed 6 days later; needs a matcha-repack slot in today's ritual |
| RM/PKG procurement-approval backlog (not forecast, engine-contract adjacent) | 4 draft purchase-session POs (~₪14,223 total, session opened 2026-07-04) have sat `proposed`/unapproved since their `order_by_date` (2026-06-24–2026-06-27, 12–15d overdue): PKG-CAP-PLASTIC-28+PKG-BOTTLE-500ML (session_po ec4db7d9, ₪6,940.73), RAW-APPLE-DRY (ba71c749, ₪2,316.00), RAW-LYCHEE-PUREE (21965b83, ₪4,574.20), PKG-LABEL-CON-500ML (731e0f79, ₪392.04). PKG-CAP-PLASTIC-28 and PKG-BOTTLE-500ML block the firmed 2026-07-12 DET-REG batch in 3 days | approval, not sourcing, is the bottleneck — surfaced as today's #1 action, not a new draft (drafts already exist) |
| PKG-BOTTLE-1L | overdue receipt, separate from the approval backlog above | PO-2026-00216: 32,999 units ordered 2026-05-13, `expected_receive_date` 2026-07-05 (4d past due), still `OPEN`/not received; blocks the firmed 2026-07-12 DET-REG batch | chase the supplier directly — quantity is not the issue, the shipment is |

Data-quality flags (not forecast): negative on-hand — EXCLUDED-NONSTOCK −354 (accounting bucket, not a real FG), FG-CAL-1L −136 (has a firmed 500L batch 2026-07-20; likely unposted production/receipt event), FG-MAT-100G −10, GT-MAT-KIT −8, FG-NM-3850ML −7, FG-SAN-BAB-RED/WHI-750ML −6/−6, ADD-UBE-500G −5, GTCC-MUZ-APPZ-1L −3, AP-DRI-PIN-1KG −1, FG-SAN-RED-3850ML −1. rebuild_verifier=0 ∴ ledger-consistent negatives = unrecorded production/receipt events, same pattern as 2026-07-03.

Double-order-trap (Stage 0 gate, not forecast): 15 open PO lines across 9 POs (PO-2026-00256/257/258/259/260/261/263/264, ordered 2026-07-03–2026-07-06) still have no `expected_receive_date`. Two of them (RAW-LIME-PUREE 80 units on PO-2026-00258, PKG-LABEL-NAM-500ML 1,000 units on PO-2026-00260) would fully cover this run's Stage-2 shortages on those components once a supplier ETA is confirmed — flagged in today's report as a quick win, not a new order.

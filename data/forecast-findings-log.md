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

## 2026-07-17 (Tom asked "למה זה לא עובד?" — root-cause + manual run; forecast version 369f5cb1 published 2026-06-08, still unchanged, now 39d old 🟡)

**Root cause of the 12-day silence (2026-07-05 → 2026-07-17), found this run:** there was never a recurring cron trigger for this skill. `list_triggers` shows the account's entire trigger store is one-shot `send_later` PR-babysitting check-ins (re-arming hourly) for unrelated PRs — none targets `daily-ops-guardian`. The 2026-07-05 hypothesis ("fresh/headless session lacked live Supabase access") was the wrong diagnosis: a live check this run (`rebuild_verifier()`) succeeded fine from a fresh-context session. Separately, the Make delivery pipe (scenario `6439326`) is healthy and fired successfully on 07-06, 07-09, 07-10 and 07-15 (real 27–38KB payloads, HTTP 200) — meaning the skill *did* run and email Tom on at least those four days via manual/ad-hoc fires, but none of those runs committed a findings-log entry, so this log under-represents actual run history. Fixed this run: real cron trigger created (`30 3 * * *` UTC, fresh session per fire, see repo commit). Process gap also flagged: findings-log commit should not be optional on days the report sends — folding into the Stage 4/5 checklist going forward.

| item | signal | evidence (14d window) | direction |
|---|---|---|---|
| PKG-BOTTLE-1L | engine-contract mask hides a real PKG shortage | PO-2026-00216 (32,999u) is 11 days overdue (expected 2026-07-05); projection still counts it as arriving today, netting the component to "healthy". Real position: 816 on-hand vs 4,957 firmed 14d demand = **-4,141 deficit**, first-blocked 2026-07-19. No draft session line exists for it yet (the generator that produced session `00802e4a` on 07-16 was fooled by the same mask). | not a forecast miss — data-quality/engine-contract gap (same class as the 07-05 `incoming_supply_qty` flag). Chase the supplier or correct the PO status before the engine can see this; flagged as today's #1 procurement action regardless. |
| ADD-MUZ-PNMM-1L | committed backlog keeps aging, Muza line status still undecided | 72 units unpicked (2 orders), oldest now **54 days** (was 42d on 07-05, 25-ish implied on 07-03) — +12 days aged with zero progress since the last guardian run that flagged it | third consecutive flagged run with no movement; this is no longer a forecast question, it's a stalled Tom decision (line status) blocking a real customer promise |
| FG-MUZ-JAS-200ML / FG-MUZ-NEG-200ML | same Muza-line blocker, two more SKUs | 24 units unpicked each (2 orders each), oldest 33 days; no firmed `production_plan` row for either in the next 30 days | same root cause as above — bundling under one Tom decision, not two separate asks |
| FG-CAL-500ML / FG-CAL-1L | committed backlog with no firmed coverage, **not previously logged** | 22u (500ML) + 16u (1L) unpicked, no firmed batch in next 30 days | unlike ENE (explicitly deprioritized per Tom's 2026-07-04 tradeoff), CAL's exclusion doesn't trace to a documented decision — flagging as new, needs Tom confirmation whether this is deliberate or an oversight |
| — (systemic) | committed-demand blind spot, still 100%, third run running | Every open LionWheel order with backlog_units > 0 checked this run (31 items) had `backlog_units_dateless = backlog_units` — i.e. **zero** committed demand is currently visible to `fn_compute_daily_fg_projection`'s own internal calculation; every committed-shortage number in this run came from a direct mirror read, not the engine | unchanged since 07-03; the engine-contract fix recommended on 07-05 (net firmed production + dateless-aware committed demand) has not landed — re-flagging, still out of guardian's write scope |

Data-quality flags (not forecast): 6 open PO lines still missing `expected_receive_date` (RAW-LUISA 48u, RAW-LIME-PUREE 80u, PKG-LABEL-DET-1L-NS 1000u, PKG-LABEL-NAM-500ML 1000u, RAW-ROSE-DRY-GARNISH 10u, RAW-DRIED-ORANGE 5u) — 3 of these (LUISA, LIME-PUREE, LABEL-NAM-500ML) are the exact components showing as short in Stage 2's RM/PKG coverage, i.e. already on order, just needs a date set. Physical-count staleness (from session `00802e4a`'s own `input_integrity`): only 4/33 session-scoped targets fresh, 19 stale, 10 never counted, oldest 66 days — caveats the confidence of every RM/PKG on-hand number this run, surfaced but not gate-blocking (`rebuild_verifier=0`).

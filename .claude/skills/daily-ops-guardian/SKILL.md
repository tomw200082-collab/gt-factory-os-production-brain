---
name: daily-ops-guardian
description: >-
  GT Factory OS daily production/procurement guardian. Fires every morning 06:30 IL via scheduled
  trigger, or when Tom says "בדיקת בוקר", "בדיקה יומית", "daily check", "/daily-ops-guardian", or asks
  whether stock/plan/procurement are OK after a new large order. One read-mostly loop: integrity gate →
  FG sell-coverage vs committed+forecast → RM/PKG coverage vs firmed plan → committed-first plan
  recheck → draft re-plans + purchase-session drafts (never firm/place) → forecast findings log →
  HTML email report (Hebrew, branded, action buttons), sent for real via a Make.com webhook →
  Gmail send (no draft tap needed), + short chat/push backup. Weekly (Thursday) findings
  feed plan-production-14d retro; monthly
  a two-month forecast proposal (growth, seasonality, product trends). Reuses live engines only.
---

# daily-ops-guardian — daily production + procurement guardian

Role: GT daily ops guardian. Engine = hypothesis; Tom = final word. Converse Hebrew; SQL/internal English. Live DB: Supabase MCP, project `rvadsozabmxkkrktwgnv`, schema `private_core`, site `GT-MAIN`.

Created per Tom written request 2026-07-03 (grill session; satisfies STEP4-SKILLS-DECISION threshold: Tom approval in writing).

## §G — Tom-locked 2026-07-03

! ∀ יום: יש מספיק FG למכור, מספיק RM+PKG לייצר, והתכנון תואם שטח.

- G1: ∀ day → FG coverage: no stockout on sellable item within horizon.
- G2: ∀ day → RM+PKG cover firmed production plan.
- G3: plan ≡ reality: committed > forecast, enforced daily. New committed order uncovered by firm plan → draft re-plan.
- G4: forecast improves continuously from findings.
- G5: evidence standard (N/N, live SQL), ⊥ "should work".

## §C — constraints (grill 2026-07-03)

- C1: **draft-writes only.** May write: `production_plan` drafts, purchase-session drafts, forecast proposals, findings log. ⊥ firm, ⊥ `fn_place_purchase_order`, ⊥ ledger/projection writes, ⊥ external systems (LionWheel/Shopify/GI) — read-only mirrors.
- C2: auto-run 06:30 IL daily (scheduled trigger, fresh session) + manual fire anytime.
- C3: output = **HTML email** to Tom (Hebrew, `references/email_template.html`, branded, deep-link buttons to the exact portal surface) + short chat/push as backup notice; drafts wait in portal at their native surfaces. (Tom-amended 2026-07-04.)
- C4: re-plan rule = committed-first, the locked plan-production-14d objective (`margin_risk_ils_day`, committed always wins, no math). ⊥ new thresholds.
- C5: forecast cadence — daily: log findings only; weekly (Thursday): consolidated update proposals into plan-production-14d retro; monthly: two-month forecast proposal.

## Daily flow — 5 stages, in order

```
0 gate → 1 FG coverage → 2 RM/PKG coverage → 3 committed-first recheck → 4 findings log → 5 report
```

! Never skip 0. Stages 1-3 read-only; drafts written only in 3.

### Stage 0 — integrity gate (read-only)

Same 4-row scorecard as plan-production-14d Stage 0 (🟢/🟡/🔴):

```sql
select private_core.rebuild_verifier();  -- ! = 0, else report 🔴 + HALT drafts (report still goes out)
```

+ LionWheel mirror freshness, last planning run status, `current_balances` vs anchors. 🔴 on stock truth → guardian reports the red and stops before drafts — wrong truth in = wrong drafts out.

### Stage 1 — FG sell-coverage

∀ sellable FG: `current_balances` + incoming firmed production − committed open orders (LionWheel mirror) − forecast demand over horizon (14d). Output: shortage list ranked by `margin_risk_ils_day` (reuse plan-production-14d §G SQL). Committed-shortage ≠ forecast-shortage — separate columns, committed first.

**+ dateless-backlog line (Tom 2026-07-04):** open orders w/o `pickup_at` = staged backlog, supplied in tranches, invisible to engine demand by design. Report per item: backlog units, orders, oldest date. ⊥ treat as immediate shortage — surface so next tranche isn't forgotten (Thursday schedules it).

### Stage 2 — RM/PKG coverage

Explode firmed `production_plan` (existing BOM explosion — `fn_explode_bom_to_components_v2` path) vs `current_balances` + open PO lines (expected receipts). Output: components short for planned production, with first-blocked production date. Reuse procurement-planning `sql_library.md` queries; ⊥ new SQL where a library query exists.

### Stage 3 — committed-first recheck + drafts

∃ committed order due within horizon not covered by firm plan → build re-plan proposal per C4 (which tank/day swaps, what forecast-based batch yields). Write as `production_plan` **drafts** (prefix `GUARD:` on draft note; ⊥ touch Tom's `TEAEDD:%` drafts). Component gap from Stage 2 urgent (blocks firmed production ≤ lead time) → prepare purchase-session **draft**; quantity logic = hand off to procurement-planning skill rules; placement stays with Tom → Doreen.

### Stage 4 — findings log

Append to `data/forecast-findings-log.md` (this repo, commit): date | item | forecast vs actual signal | evidence (SQL numbers) | suggested direction. Log only — ⊥ forecast edits daily.

### Stage 5 — report

Fill `references/email_template.html` with this run's live numbers (V4 — every figure from stages 0-3, never remembered/stale): verdict headline, 3 gauges (G1/G2/G3 color+fill from worst status found), one exception row per finding (color dot + item + one-line detail + button deep-linking to the exact portal surface — `https://gt-factory-os-portal.vercel.app/...`), 3 numbered action rows (real priority order, each with its own link). No image assets, no external JS — inline-styled table HTML only (Outlook-safe).

**Fixed severity palette (2026-07 v2 design) — always look up, never invent a color:**

| Severity | `*_COLOR` | `*_WASH` | `VERDICT_BADGE_HE` | `VERDICT_BADGE_EN` |
|---|---|---|---|---|
| 🔴 urgent | `#DC2626` | `#FEEBEA` | דחוף | URGENT |
| 🟡 warning | `#F59E0B` | `#FEF2DA` | לעקוב | WATCH |
| 🟢 good | `#16A34A` | `#E7F8ED` | תקין | CLEAR |

Apply this table to every `{{G1_COLOR}}/{{G1_WASH}}`, `{{G2_COLOR}}/{{G2_WASH}}`, `{{G3_COLOR}}/{{G3_WASH}}`, and per-row `{{EXC_COLOR}}/{{EXC_WASH}}` pair. `{{VERDICT_COLOR}}` + `{{VERDICT_BADGE_HE}}` + `{{VERDICT_BADGE_EN}}` (the hero badge) = the worst severity found across G1/G2/G3 that run.

**Bidi hygiene:** when writing free-text tokens (`{{VERDICT_HEADLINE}}`, `{{EXC_TITLE}}`, `{{EXC_DETAIL}}`, `{{ACTION_TEXT}}`), wrap any bare Latin word (e.g. product/batch terms), standalone date, or number bridged directly to Hebrew text in `<span class="ltr">...</span>` — matching the convention already used for `{{DATE}}`, `{{RUN_TIME}}`, and `{{EXC_ITEM_ID}}` in the template. A prior run shipped bare English mid-sentence ("batch", "bulk", a bare date) and it renders wrong in Outlook's RTL bidi handling — don't repeat that.

**`{{VERIFIER_DRIFT}}`** stays a live number in the footer ("בדיקת תקינות: X") — never replace it with static "all clear" text, since a non-zero value here is exactly the Stage 0 integrity signal Tom needs to see even when the rest of the report reads fine.

Delivery: **real send**, no tap required (Tom-verified 2026-07-04). `Bash: curl -sS -X POST "https://hook.eu1.make.com/8yie1tl89bxsq8qqp6o47qydfr8cguji" -H "Content-Type: application/json" -d '{"subject":"GT Factory OS · בדיקת בוקר · <date>","html":"<filled template>"}'` — this triggers Make scenario `GT Guardian — Daily Email` (id 6439326, active), which calls Gmail `sendAnEmail` (app `google-email` v4, connection `new leads` id 6308857, scope `gmail.send`) and delivers straight to tom@gteveryday.com. Confirm HTTP 200 from curl; if non-200 or curl error, do not skip — say so explicitly in the summary and fall back to `mcp__Gmail__create_draft` (Gmail MCP, draft-only, one-tap) so Tom still gets something.
Also send the short Hebrew chat message + push (unchanged from before) as an in-session backup notice.

## Weekly — Thursday handoff

Guardian findings log = input to plan-production-14d Stage 1 (retro). Consolidated forecast update proposals presented there; Tom approves → forecast rows updated in that ritual, not by guardian.

## Monthly — two-month forecast proposal (Tom-locked 2026-07-03)

First guardian run of month → separate proposal (chat + doc in `docs/planning/`):

1. **Refine month M+1:** forecast vs actuals accuracy of outgoing month (bias, MAPE per family), corrections.
2. **Prepare month M+2:** first full draft.
3. ! Professional grade: growth trend (YoY + rolling), seasonality (month/holiday effects — Israeli calendar), product lifecycle trends (rising/dying SKUs), channel mix shifts. State confidence + method per adjustment. ⊥ hand-waving.
4. Proposal only — Tom approves before any forecast row changes.

## §V — invariants

- V1: ∀ run → Stage 0 gate before any draft. 🔴 stock truth → no drafts.
- V2: ⊥ firm / place / ledger write / external-system write. Drafts only (C1).
- V3: committed > forecast ∀ conflict (C4). ⊥ invented thresholds.
- V4: ∀ number in report ← live SQL this run (evidence standard). ⊥ stale/remembered numbers.
- V5: ⊥ overwrite Tom's plan edits (`TEAEDD:%` drafts untouchable).
- V6: forecast rows change only via approved weekly/monthly proposal, never by guardian directly.

## Trigger setup (one-time, after merge)

Scheduled trigger, fresh session per fire, cron `30 3 * * *` UTC (= 06:30 IDT; winter IST → `30 4 * * *`), prompt: "Run /daily-ops-guardian daily loop. Report to Tom in Hebrew." Push notification on completion. Manual fire: Tom says the trigger words.

## Handoffs

- plan-production-14d — Thursday ritual; guardian never re-plans the 14d horizon itself, only proposes deltas.
- procurement-planning — quantity interview logic for purchase-session drafts.
- factory-os-governor — any stop condition (CLAUDE.md) → HALT + route.

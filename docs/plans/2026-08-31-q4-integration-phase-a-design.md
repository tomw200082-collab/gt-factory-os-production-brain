# Phase A design — the Q4 plan becomes the work in the portal

**Status: AWAITING TOM'S WRITTEN APPROVAL.** No schema, no migration, no portal code was
written. Phase B does not start until Tom answers Q1–Q7 in writing (masterprompt §8).

Answers the masterprompt `2026-08-31 sales system integration`, §4 steps A-1…A-6.
Companion plan: `docs/plans/2026-08-31-existing-customers-q4-masterprompt.md`.

Everything below was measured on 2026-08-31 between 16:10Z and 17:00Z. Nothing is from
memory, and where live measurement contradicts the masterprompt, §1 says so.

---

## 1. A-1 — re-verification, and four corrections

§2.6 run in full. Supabase `rvadsozabmxkkrktwgnv`, and both scoreboard paths.

### Confirmed exactly

| Fact | Measured |
|---|---|
| `lead` / `lead_event` / `org` | 200 · 360 · 197 |
| `lead.status` | `new` 142 · `lost` 43 · `working` 12 · `won` 3 |
| Today queue by `item_type` | `new_lead` 132 · `returning_customer` 10 · `due_follow_up` 8 |
| `org` carrying `shopify_customer_id` | **13 of 197** |
| Avi's `lead_event` rows | 113 of 360; Tom 16; `system*` 231 |
| Avi's last event | 2026-08-31 15:31 Asia/Jerusalem |
| `q4_scoreboard.py --selfcheck` | **16/16 PASS** — 153 accounts, 716 tasks, 84 days |
| `q4_scoreboard.py --since 2026-09-01` | ran clean; 642 planned touches, 0 outcomes, 0 orders (Q4 has not begun) |

Both scoreboard paths were exercised, per landmine §7.3.

### C-1 — Avi is live, but the evidence is one working day, not a week

§2.1 reads Avi's 113 events as "he started this week … a live daily user". The daily shape:

```
2026-08-30   108 events across 52 leads      <- one backlog-triage sprint
2026-08-31     5 events across  1 lead       <- today, last at 15:31
```

He is genuinely in the tool today, and the design's premise holds — the growth work must
arrive where he already is. But "daily user" rests on one sprint plus a light day. The
premise to protect is *he is in the tool*, not *he clears a queue every morning*.

### C-2 — the daily cap already exists, is set, and is visible

§3.4, §6.C and Q4 all treat the cap as an unbuilt thing Tom must decide. It is built:

```
sales_core.app_setting('queue') = {"order": "newest_first", "daily_cap": 15}
```

- Tom edits it on the settings screen — `gt-factory-os-portal` `_components/SettingsForm.tsx`.
- The API returns the full row set plus the cap, deliberately, "so the 'X more waiting'
  line can tell the truth" — `api/src/sales/queries_handler.ts`.
- `_components/TodayQueue.tsx` spends the cap as a budget down `SECTION_ORDER` and renders
  `today-daily-cap-rule` when it bites.

**D8 is therefore already satisfied by code that ships today.** A growth item inherits the
cap by being one more entry in `SECTION_ORDER`. Tom has no new decision to make here —
only where growth sits in that order (§3, Q4).

### C-3 — the overflow is not the growth plan. It is 142 unassigned leads.

Measured daily load from the shipped CSV, customer touches only:

| Owner | Accounts | Days | Touches | Max/day |
|---|---|---|---|---|
| אבי (T2 + 2×T1) | 24 | 49 | 133 | **4** |
| אלכס+אבי (T1) | 13 | 15 | 15 | **1** |
| תום (T3) | 116 | 52 | 494 | **10** |

Avi's growth load peaks at 4 a day against his stated 3–4 calls. **The plan does not
overflow him.** What does: `handleSalesToday` scopes to `assignee = me OR assignee is
null`, and 142 of 200 leads are unassigned — so Avi's Today already carries 149 items of
which 7 are actually his. That is `U-011`/`U-012`, an assignment gap, and it is not this
work's to fix. It is worth saying plainly because §3.4 attributes the crowding to the
growth plan, and fixing the wrong thing here would cap Avi's 4 real tasks while leaving
the 142 in place.

### C-4 — the plan is built and verified, but it is not merged

§1.1 calls the plan "shipped". Neither the CSV nor the scoreboard is on `main`:

| Artifact | Lives on |
|---|---|
| `evidence/2026-08-31-q4-daily-plan.csv` | Sales-Machine PR **#22**, draft, branch `claude/caveman-ponytale-fh8gpv` |
| `scripts/sales-report/q4_scoreboard.py`, `q4_penetration.py`, `q4_plan_v3.py` | gt-factory-os PR **#254**, draft, same branch |
| `docs/plans/2026-08-31-existing-customers-q4-masterprompt.md` | brain, same branch |

D1 and D5 both compare against that CSV. **Phase B cannot start until those three PRs
merge**, or it will build against an artifact that can still change. Opened as `U-032`.

---

## 2. A-3 — the win rules, as SQL

Written first, because Q1 and Q2 are decided by what these rules need.

### 2.1 The classifier already exists — reuse it, do not re-derive it

`scripts/sales-report/q4_penetration.py` maps SKU → family in thirteen lines, and **that
exact function produced the penetration figures the plan is priced from.** A second
classifier is a second truth waiting to drift. Transcribe it to SQL once:

```sql
-- sales_core.fn_sku_family(text) -> text | null
-- Transcribed verbatim from q4_penetration.py's fam(); pgTAP asserts the two agree
-- on every SKU present in the plan CSV.
--   GT-HIB-* פרש · GT-LUI-* דיטוקס · GT-LEM-* אנרג'י  · GT-CHA-* קאלם
--   GT-JAS-* קונשסנס · GT-SEN-* ריווייב · GT-INF-* דזרטי · GT-MAS-* נמסטיאה
--   ^GT-SHI-CER|^GT-MAT-KIT  מאצ'ה      ^UBE-POWDER  אובה     ^GT-ODK  מחית ODK
--   ^GTCC|^GTMX|^GTEL  סנגריה/קוקטייל   ^AP-|^GT-GLA|^GT-MAT-BTL  ציוד
```

### 2.2 The frozen baseline (W2)

One row per account per family, over `2025-09-01 … 2026-08-31`, written once and never
updated — a dated evidence snapshot in the `Sales-Machine` sense (truth rule 2).

```sql
create table sales_core.play_baseline (
  shopify_customer_id text        not null,
  family              text        not null,
  first_seen_at       timestamptz not null,
  last_seen_at        timestamptz not null,
  max_qty             integer     not null,   -- largest quantity on ONE order
  total_ils           numeric     not null,
  window_start        date        not null,   -- 2025-09-01
  window_end          date        not null,   -- 2026-08-31
  frozen_at           timestamptz not null,
  primary key (shopify_customer_id, family)
);
```

**The absence of a row is the load-bearing fact.** "First-ever matcha" is `not exists
(… family = 'מאצ''ה')`. That is why the table is keyed by `shopify_customer_id` and not by
display name: a name-matched baseline that silently misses an account would read as
"never bought matcha" and hand back a false win on their next routine order — exactly D4.

### 2.3 One predicate per motion

Given `l` = the play's `lead` row, `b` = `play_baseline` for its account, and `line` = the
line items of **one** non-cancelled order placed at or after the play's first touch:

```sql
-- sales_core.fn_play_win(p_lead_id uuid, p_lines jsonb) -> text | null
-- Returns the evidence kind, or null when the order proves nothing. STABLE, no writes.
with line as (
  select sales_core.fn_sku_family(x->>'sku') as fam,
         (x->>'quantity')::int               as qty
    from jsonb_array_elements(p_lines) x
   where sales_core.fn_sku_family(x->>'sku') is not null
)
select case play.motion

  -- E1 · מאצ'ה — קו חדש (73 accounts)
  when 'מאצ''ה — קו חדש' then (
    select 'first_matcha' where exists (select 1 from line where fam = 'מאצ''ה')
      and not exists (select 1 from b where b.family = 'מאצ''ה'))

  -- E3 · מחית פרי — קו חדש (21)
  when 'מחית פרי — קו חדש' then (
    select 'first_puree' where exists (select 1 from line where fam = 'מחית ODK')
      and not exists (select 1 from b where b.family = 'מחית ODK'))

  -- E4 · אובה — הרחבה על מאצ'ה (8)
  when 'אובה — הרחבה על מאצ''ה' then (
    select 'first_ube' where exists (select 1 from line where fam = 'אובה')
      and not exists (select 1 from b where b.family = 'אובה'))

  -- E5 · תה — עומק ורוחב (11): a tea flavour never bought before
  when 'תה — עומק ורוחב' then (
    select 'new_tea_flavour' where exists (
      select 1 from line where fam in (select * from sales_core.tea_families())
        and not exists (select 1 from b where b.family = line.fam)))

  -- E2 · מאצ'ה — עומק (35): deeper than they have ever gone in one order
  when 'מאצ''ה — עומק' then (
    select 'matcha_depth' where exists (
      select 1 from line join b on b.family = 'מאצ''ה'
       where line.fam = 'מאצ''ה' and line.qty > b.max_qty))

  -- W · החזרה (5): a dormant account ordered anything at all
  when 'החזרה' then (
    select 'reactivated' where exists (select 1 from line))

end
```

**Every rule is decidable from one order.** No window to wait out, no ₪ threshold, and
none of them can fire on a reorder of what the account already buys — which is what makes
D4 structural rather than merely avoided.

### 2.4 The one motion that resisted, and what it cost

`מאצ'ה — עומק` is the only rule with a judgement call in it (A-3: surface, do not invent).
Depth has no natural single-order signal — an account that already buys matcha ordering
matcha again is Tuesday.

Rejected: *matcha spend over a rolling window ≥ some multiple of baseline*. It needs a
multiple nobody can defend, it needs a window (60? 90 days?), and it cannot be decided
until the window closes — so the scoreboard reads zero for a quarter of the plan for two
months.

Recommended: **`quantity > the largest matcha quantity they have ever put on one order`.**
It defends itself (a routine reorder is by definition not larger than their largest), it
decides on the day, and it invents no number.

**What it misses, stated:** an account that deepens by ordering *more often* at the same
size never trips it. That is a real 35-account blind spot, and the honest mitigation is
that the scoreboard's money section already counts their spend — the win flag is
conservative, the revenue is not lost. If Tom would rather catch cadence too, that is a
window rule and it costs the two-month reporting delay above. **Q2 is where he chooses.**

---

## 3. A-2 — the seven questions, answered

### Q1 — where does a growth play live? → **a `lead` row, not a new `play` table**

*This reverses the masterprompt's own recommendation.* §3.1's argument is that `lead` is
terminal and singular while a play is neither. Measured against the shipped plan, **for Q4
a play is both**: `q4_scoreboard.py --selfcheck` asserts one lead motion per account, and
the six motions partition the 153 exactly (73+35+21+11+8+5). One account, one motion, one
quarter, one terminal answer.

Cost of the recommended path — one migration:

- `lead.source = 'q4_existing_2026'` marks the 153, and one added column
  `lead.play jsonb` carries `{motion, sku, family, touches[]}`.
- `v_sales_today` gains **one** `WHEN` branch at the top of its existing `CASE`.
- `SECTION_ORDER` in `TodayQueue.tsx` gains one entry. The cap, the outcome loop, the
  assignment, the SLA, the append-only event log and `⌘K` all work unchanged.

Cost of the rejected path — `sales_core.play`: `v_sales_today` is `FROM sales_core.lead
JOIN sales_core.org`, single-table, and every consumer downstream reads `lead_id` as
non-null. A second work object turns that view into a `UNION ALL`, and drags a new API
query, a new card component, a new mutation set and a new test suite behind it. That is
weeks of surface for a distinction Q4 does not make.

**What the lazy answer gives up, and when to pay it back:** the moment an account carries
two live motions at once, or a motion outlives its quarter, `lead` stops fitting. That is
Q7's question, and the answer there is *build `play` then, from a quarter of real usage* —
not now, from a guess about what next quarter needs.

The one thing that must not be inherited is `lead`'s `won` semantics — which is Q2, and
which §2.3 above already fixes at the source rather than by exclusion.

### Q2 — what is a win? → **§2.3's six predicates, against the frozen baseline**

Recommended as written. The open decision inside it is the depth threshold (§2.4):
**single-order quantity** (recommended, decides same-day, blind to cadence) versus a
**windowed spend rule** (catches cadence, needs an invented multiple, reports nothing for
two months). Tom picks.

Cost either way: `ORDERS_Q` in `sales-leads-poll/index.ts` must fetch line items, which it
does not today. See `U-033` and `U-034` — two live bugs in that path found while designing
this, both of which bite before any of it works.

### Q3 — CSV or database as source of truth? → **agreed, no change**

The masterprompt's answer is right and needs nothing added: the CSV stays the immutable
dated snapshot of the plan as designed, the database becomes live state, and D5 (the
scoreboard reproducing the CSV exactly on day zero) is what stops them drifting silently.

One correction from C-4: the CSV is not merged yet. It must be, before it can be the
immutable thing everything compares against.

### Q4 — the daily cap → **already decided, and already 15**

See C-2. Not Tom's decision to make; it is made, live, and editable. Two things do remain,
and they are small:

1. **Where growth sits in `SECTION_ORDER`.** Recommended: `conversion` ·
   **`growth_play`** · `returning_customer` · `due_follow_up` · `new_lead`. A dated task
   an owner accepted outranks backlog; it sits under `conversion` because a closed loop is
   worth seeing first.
2. **Whether growth gets a floor.** Recommended: **no floor.** Avi's peak is 4 against a
   cap of 15, so the cap cannot bite him this quarter. Adding reserved slots is machinery
   for a collision the measurements say will not happen.

### Q5 — which agents? → **agreed, and Phase B should ship neither**

The masterprompt recommends exactly two read-only agents. Agreed on the shape. Recommended
change: **write both declarations in Phase B, run neither.**

`retention-radar` proposes wins — but §2.3's rules are deterministic and already run in the
conversion job, so an agent proposing what a function decides is a second opinion with no
authority. `brief-composer` writes the Sunday brief — but `U-020` (nothing to send) and
`U-021` (nowhere to escalate) are both still open on Tom, so its output would reference
material that does not exist. Both declarations satisfy D6 and cost nothing. Running them
buys nothing this quarter. `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` stays `false`; D7 holds
because no code sends.

### Q6 — where does the beautiful surface live? → **agreed**

Portal is the system of record and the daily surface; the published artifact stays a
read-only board for Tom and Alex, regenerated from the database, never holding state.
Nothing to add.

### Q7 — 2027-01-01 → **the structure is quarter-specific on purpose**

The masterprompt recommends building a general shape that outlives the plan. Recommended
instead: **ship Q4's shape, and let the general one be paid for by evidence.**

Quarter-specific by design, and say so out loud: `source = 'q4_existing_2026'`, the
`play_baseline` window frozen at 2026-08-31, and the six motion strings. Reusable as-is: the
family classifier, the baseline table shape, the win-predicate pattern, and the Today
surface. On 2027-01-01 the honest move is to look at what actually happened — how many
accounts carried a second motion, how many outlived the quarter — and build `play` then, if
the answer says to. A general work object designed today is designed from a guess.

---

## 4. A-4 — the human load, re-derived

§3.3's ~100 is a design target with no source. Re-derived from the shipped CSV, from the
principle that **a person types only what no order can ever show** (§3.3):

| Channel | Accounts | Typed entries | Why |
|---|---|---|---|
| T1 · Alex + Avi, meeting | 15 | ≤ 15 | a refusal is heard in the room |
| T2 · Avi, call | 22 | ≤ 22 | same |
| T3 · Tom, WhatsApp | 116 | **0** | silence is the default; the order stream closes the win |
| | **153** | **≤ 37** | |

Two rules make that number hold:

1. **One terminal outcome per account, never per touch.** 642 touches, at most 37 entries.
   A play that gets a "no" is finished and its remaining touches disappear.
2. **"No answer" is typed by nobody.** The touch date passed, no order arrived, no outcome
   was recorded — the system already knows all three and can render it. Requiring a human
   to type "no answer" 400 times is how a system becomes a spreadsheet nobody fills, which
   §2.4 already measured: 642 planned, 0 recorded.

Plus **74 done-taps** on the internal tasks (Tom 32 · Avi 24 · Alex 18) — a checkbox, no
typing.

**≤ 37 typed entries across the quarter. A3's ceiling is 150.** Expected is lower: at the
plan's own conversion assumptions ~32 of 153 convert, and only accounts that actively
refuse produce an entry at all.

---

## 5. A-5 — the two surfaces

Described to build-precision in the artifact (the one visual A-5 permits; it is a mock):

**https://claude.ai/code/artifact/0dcfef23-aba4-4701-a3db-e224d97864c4** — private, not link-shared.

- **Avi at 09:00** — one Today list, the growth cards inline among the lead cards, ordered
  by `SECTION_ORDER`, capped at 15 with the existing overflow line. A growth card carries:
  account, motion, lead product + SKU, why-today, the opening line, and one control —
  *not now* / *refused* / *wrong contact*. There is no `won` button, by design and by CHECK
  constraint.
- **Tom on Sunday** — the scoreboard, reading the database rather than the CSV: touches
  planned vs. outcomes recorded per owner, wins by motion against the plan's own assumed
  rate, signals-without-outcome flagged, and run-rate against ₪262,661. Every figure names
  its source and its date.

---

## 6. New unknowns — `U-032` … `U-035`

Allocated after checking both `main` (through `U-021`) and the unmerged plan branch
(`U-022`–`U-031`), per landmine §7.2.

`U-032` — **the plan is not merged.** The CSV, the scoreboard and the companion plan live
on three unmerged draft PRs (Sales-Machine #22, gt-factory-os #254, brain, all on
`claude/caveman-ponytale-fh8gpv`). D1 and D5 compare against an artifact that can still
change. **Blocks Phase B.** → Tom, or whoever owns those PRs.

`U-033` — **`ORDERS_Q` fetches the twenty *oldest* orders.**
`supabase/functions/sales-leads-poll/index.ts:321` — `orders(first:20, sortKey:CREATED_AT,
reverse:false)`. For a new lead with little history that is fine. The 153 plan accounts
averaged ~26 orders in the last twelve months alone (`q4_penetration.py`: 3,872 orders
across 151 matched accounts), so their twenty oldest orders are all older than the play,
`pickConversionOrder` returns null forever, and **no play would ever convert.** Note this
cuts against `U-029`'s reading: for high-volume accounts the failure is silence, not a
false win; the false win hits only the accounts with fewer than twenty lifetime orders.
Both are wrong, differently. Fix: `reverse:true`, or a `created_at:>=` filter.

`U-034` — **`routeDaily()` truncates at `limit 200`.** Same file, line 665, ordered
`by l.created_at` ascending. 153 plays plus 142 open leads is 295 candidates. The plays are
created last, so they sort last, so they are the ones cut. Silent. Fix: raise the limit, or
paginate, or run plays as their own pass.

`U-035` — **`play_baseline` needs `shopify_customer_id` for all 153, and 13 of 197 `org`
rows have one.** The existing loader matches on `o.display_name = <plan name>` exactly,
which will match almost none of them: org names come from Meta lead forms, plan names from
Shopify `displayName`. W1 must resolve the 153 to Shopify customer ids directly — the
scoreboard's `match()` tokeniser is the tested tool for it, and every unmatched account
must halt rather than default, because a missing baseline row reads as "never bought this"
and hands back a false win (D4).

---

## 7. What is Tom's

**A. Approve this design in writing, naming his answer to Q1–Q7.** Q1 (a `lead` row, not a
new table) and Q2's depth threshold are the two that change the build. — 20 minutes.

**B. `U-021` — one contact detail for Alexander.** Unchanged, still open, still dead-ends
17 escalation rules.

**C. ~~The daily cap~~ — withdrawn.** It exists and is 15 (C-2). What is left is where
growth sits in the queue order, recommended in Q4, and it is a one-line answer.

**D. `U-020` — the materials to send.** Unchanged. Blocks `brief-composer` ever running.

**E. `U-030` — 80 matcha bags against 74 target accounts.** Unchanged, and the plan's first
task is dated 2026-09-01. This design puts it on the Sunday surface rather than letting it
be discovered account by account.

**F. `U-032` — merge the three plan PRs, or say who does.** New. Blocks Phase B outright.

---

## 8. Condition check — A1…A4

| # | Condition | |
|---|---|---|
| A1 | Every §5 question has a recommendation, its reasoning, its cost, its rejected alternative | ✅ §3 |
| A2 | The win rule is specified per motion as a query | ✅ §2.3 — six predicates, one per motion, all decidable on one order |
| A3 | The design names what a human must type, and the count is under 150 | ✅ §4 — **≤ 37** |
| A4 | Tom has approved it in writing, with each §5 answer recorded | ❌ **not yet** — this document is the thing being put to him |

A4 is the gate. **Phase B does not start until it is ✅.**

# Ice Dream Handoff Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the price book, the customer book and the Ice Dream package (Hebrew Excel + printed binder) exactly as specified in `docs/superpowers/specs/2026-09-24-icedream-handoff-design.md`, gated so nothing leaves GT until every check passes.

**Architecture:** Three new `sales_core` tables and one resolving view in Postgres hold the truth (migration 0352). A small Python pipeline in `gt-factory-os/scripts/distributor-handoff/` pulls Shopify, Green Invoice and LionWheel read-only, seeds the book, runs the gates, and renders the package from the database. Pure logic lives in small modules with unit tests on synthetic data; live runs are controller-only.

**Tech Stack:** Postgres 17 (Supabase) + pgTAP · Python 3.11 stdlib (`unittest`, `urllib`, `json`, `decimal`) · `openpyxl` 3.1.5 · `psycopg[binary]` 3.3.6 · `pypdf` 6.19.0 · headless Chromium (`/opt/pw-browsers/chromium-1194/chrome-linux/chrome`) for HTML → PDF.

## Global Constraints

- Prices are stored **before VAT**; VAT is 18% (`× 1.18`), rounded to agorot, half up.
- Customer data and prices **never enter git**. `raw/` and `out/` are gitignored; the package goes to a private Google Drive folder.
- Shopify, Green Invoice and LionWheel are **read-only**. No external writes anywhere in this plan.
- The customer message is sent **by a person** (Doreen or Alex); `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` stays `false`.
- Migrations: list `db/migrations/` immediately before and after writing a numbered file; a new file appearing in between → HALT (`contract_failure`). No `DROP`. No stock-ledger or projection object is touched.
- Never print a secret or token. Never run `env | grep`. Check env vars with `[ -n "$VAR" ] && echo set`.
- Unit tests use **synthetic data only** — no real customer, price or phone in any committed file.
- Hebrew copy: short, clear, the key word first; every customer-facing string lives in `handoff/copy_he.py`. Addressing a business: plural ("שלכם"). No gendered wording about unknown people.
- Visual: GT brand DNA (Tom-approved 2026-08-06): Rubik (display) + Heebo (body), embedded from `gt-factory-os-production-brain/docs/pricing/pricelist_pdf/fonts/`; palette paper `#EFE6D6` · ink `#241C15` · green `#263B18` · coral `#FA6E4D` · line `#D8CCB4` · muted `#7C6E58`. RTL, A4. The Excel uses Arial (Excel cannot embed fonts; Arial renders Hebrew on every Windows PC).
- Controller-only steps (live Postgres, live APIs, prod migration apply, anything sent to Tom) are marked **CONTROLLER** and are never delegated to a subagent.
- Git: branch `claude/shopify-customer-identifier-cwm1j1` in every repo. Stage files by name — never `git add -A` / `git add .`. After opening any PR, call `unsubscribe_pr_activity` at once (Tom did not ask for watching).

## File Structure

```
gt-factory-os/
  db/migrations/0352_sales_core_price_book.sql          # tables, append-only trigger, view, grants
  db/tests/0352_sales_core_price_book.test.sql          # 21 pgTAP assertions
  scripts/distributor-handoff/
    README.md                 # how to run, data policy
    requirements.txt
    .gitignore                # raw/ out/ .venv/
    run.py                    # CLI: pull · seed · gates · review · decide · messages · import-form · package · update
    handoff/
      __init__.py
      config.py               # paths + constants (families, VAT, windows)
      model.py                # Line, ListPrice, Proposal, Flag, CustomerRow
      brand.py                # palette + embedded fonts CSS
      copy_he.py              # every Hebrew string
      catalog.py              # catalog-truth + TSV → list prices (+ C1 flags)
      prices.py               # seeding rules + E1–E4
      customers.py            # customer-book rules, GT numbers, gaps (+ K2)
      shopify.py              # read-only pulls + parsers
      gi.py                   # read-only Green Invoice pulls + parsers
      lionwheel.py            # read-only LionWheel pull + parser
      db.py                   # sales_core I/O
      gates.py                # G1–G4
      review.py               # Tom's exception page
      messages.py             # WhatsApp links for the switch message
      forms.py                # Google Form responses → answers
      package.py              # PackageData from the database
      render_excel.py         # the workbook + CSVs
      render_pdf.py           # the binder (HTML → PDF)
      updates.py              # weekly diff
    tests/
      __init__.py
      test_catalog.py test_prices.py test_customers.py test_shopify.py test_gi.py
      test_lionwheel.py test_gates.py test_review.py test_messages.py test_forms.py
      test_package.py test_render_excel.py test_render_pdf.py test_updates.py
gt-factory-os-production-brain/docs/decisions/modules/sales-declaration.md   # Amendment B
Sales-Machine/doctrine/decisions.md                                          # D-025 … D-027
```

Test command (used by every task below):

```bash
cd /home/user/gt-factory-os/scripts/distributor-handoff && .venv/bin/python -m unittest discover -s tests -t . -v
```

---

### Task 1: Governance records

Records Tom's decisions where the repos keep them. Docs only.

**Files:**
- Modify: `Sales-Machine/doctrine/decisions.md` (append three rows to the table)
- Modify: `gt-factory-os-production-brain/docs/decisions/modules/sales-declaration.md` (insert Amendment B after the A.6 paragraph)

**Interfaces:** none.

- [ ] **Step 1: Append the decisions**

Append these rows at the end of the decisions table in `Sales-Machine/doctrine/decisions.md` (keep the existing column order `| ID | Decision | Status | Date | Context |`):

```markdown
| D-025 | **Tea extracts have one fixed price per customer per size.** If a customer bought any 1L tea extract at X, every 1L flavor is X for them; the same for 500 ml. | **CONFIRMED** (Tom) | 2026-09-24 | Tom, session 2026-09-24: "המחירים של תמציות תה ליטר וחצי ליטר תמיד קבועים — אם לקוח הזמין בעבר תה ליטר מסוג מסוים ב־X גם סוג אחר הוא יקבל ב־X, ואותו דבר גם בחצי ליטר." Holds for 95% of customers in 24 months of orders (30 exceptions go to Tom). Spec: PRODUCTION `docs/superpowers/specs/2026-09-24-icedream-handoff-design.md`. |
| D-026 | **A brand-new customer buys at full list price.** An existing customer buying a product for the first time also pays list price. | **CONFIRMED** (Tom) | 2026-09-24 | Tom, session 2026-09-24: "לקוחות חדשים לגמרי נעשה כברירת מחדל במחיר מלא." The extension to a first-time product for an existing customer was stated in the approved design ("stop me if not"). |
| D-027 | **One price book in `sales_core` is the single price truth from go-live.** The last price paid only seeds it; later changes are explicit, dated rows with an approver. Ice Dream, the future order page and GT's own order entry all read it. | **CONFIRMED** (Tom) | 2026-09-24 | Tom approved the approach and the design in session 2026-09-24 ("מאשר"). Replaces the implicit last-paid rule of 2026-06-25 as the source of truth; last-paid remains the seeding method. |
```

- [ ] **Step 2: Add Amendment B to the module declaration**

In `gt-factory-os-production-brain/docs/decisions/modules/sales-declaration.md`, insert after the paragraph that starts `**A.6 — New Tom decisions required**`:

```markdown
## Amendment B — customer price book (proposed 2026-09-24 · approach APPROVED by Tom in session 2026-09-24; this text awaits Tom's merge)

**B.1 — Supersedes A.4 for customer-specific prices.** A customer-specific price list is now modeled: `sales_core.customer_price` (append-only) resolved through `sales_core.v_customer_price`, with `sales_core.list_price` as the general list and `sales_core.customer_book` as the per-branch record. Public Shopify pricing remains what sales agents quote to prospects.

**B.2 — Why.** GT is moving almost all business customers to the distributor Ice Dream, which invoices them at GT's prices. On 2026-09-24, 75% of tea customers paid below list and the legacy `custom.price_list` field matched the price actually paid for only 202 of 455. A distributor cannot invoice from that.

**B.3 — Rules** (Sales-Machine D-025 … D-027): tea 1L / 0.5L fixed per customer per size; new customer or first-time product = list price; the book is the truth from go-live.

**B.4 — Boundaries unchanged.** No foreign key leaves `sales_core`; nothing reads or writes the ledger, balances, items or BOMs. Customer-facing sends stay behind `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED`; the switch announcement is sent by a person.

Spec: `docs/superpowers/specs/2026-09-24-icedream-handoff-design.md` · plan: `docs/superpowers/plans/2026-09-24-icedream-handoff.md`.
```

- [ ] **Step 3: Commit both repos**

```bash
cd /home/user/Sales-Machine && git add doctrine/decisions.md && git commit -m "docs(doctrine): D-025–D-027 — tea fixed per size, new customer at list, price book is truth"
cd /home/user/gt-factory-os-production-brain && git add docs/decisions/modules/sales-declaration.md && git commit -m "docs(sales-declaration): Amendment B — customer price book supersedes A.4"
```

Every commit message in this plan ends with the two attribution lines from the session's system reminder (`Co-Authored-By: …` and `Claude-Session: …`).

---

### Task 2: Migration 0352 — price book, customer book, resolving view

**Files:**
- Create: `gt-factory-os/db/migrations/0352_sales_core_price_book.sql`
- Test: `gt-factory-os/db/tests/0352_sales_core_price_book.test.sql`

**Interfaces:**
- Produces: tables `sales_core.list_price`, `sales_core.customer_price`, `sales_core.customer_book`; view `sales_core.v_customer_price` with columns `shopify_customer_id, gt_customer_no, sku, name_he, size_label, barcode, family, general, price_ex_vat, price_inc_vat, list_price_ex_vat, basis, evidence`.

- [ ] **Step 1: Slot check (FR1)**

```bash
cd /home/user/gt-factory-os && ls db/migrations | sort | tail -3
```
Expected: the highest is `0351_…`. If a file `0352_*` already exists → HALT, report `contract_failure`.

- [ ] **Step 2: Write the failing test**

Create `db/tests/0352_sales_core_price_book.test.sql`:

```sql
-- ===========================================================================
-- 0352_sales_core_price_book.test.sql
-- ===========================================================================
-- pgTAP tests for 0352_sales_core_price_book.sql. Self-contained: fixtures
-- inlined, everything inside begin/rollback.
--
-- Before apply (migration inside the same rolled-back transaction):
--   printf 'begin;\n\\i db/migrations/0352_sales_core_price_book.sql\n\\i db/tests/0352_sales_core_price_book.test.sql\n' > /tmp/t0352.sql
--   psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f /tmp/t0352.sql
-- After apply:
--   psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/tests/0352_sales_core_price_book.test.sql
-- ===========================================================================

begin;

create extension if not exists pgtap;

select plan(21);

-- ---------------------------------------------------------------- structural
select has_table('sales_core'::name, 'list_price'::name);
select has_table('sales_core'::name, 'customer_price'::name);
select has_table('sales_core'::name, 'customer_book'::name);
select has_view('sales_core'::name, 'v_customer_price'::name, 'sales_core.v_customer_price exists');

-- ---------------------------------------------------------------- fixtures
insert into sales_core.list_price (sku, name_he, size_label, family, price_ex_vat, general, source, verified_on) values
  ('T-FRESH-1L', 'FRESH',   '1 ליטר', 'TEA_1L', 65,   true,  'test', '2026-09-24'),
  ('T-DETOX-1L', 'DETOX',   '1 ליטר', 'TEA_1L', 65,   true,  'test', '2026-09-24'),
  ('T-MATCHA',   'מאצ''ה',  '',       null,     590,  true,  'test', '2026-09-24'),
  ('T-PUREE',    'מחית',    '',       null,     60,   true,  'test', '2026-09-24'),
  ('T-PRIVATE',  'תה פרטי', '',       null,     null, false, 'test', '2026-09-24'),
  ('T-GONE',     'לא נמכר', '',       null,     10,   true,  'test', '2026-09-24');
update sales_core.list_price set active = false where sku = 'T-GONE';

insert into sales_core.customer_book (shopify_customer_id, gt_customer_no, place_name) values
  ('gid://shopify/Customer/9000000001', 9001, 'בית קפה א'),
  ('gid://shopify/Customer/9000000002', 9002, 'בית קפה ב');

insert into sales_core.customer_price (shopify_customer_id, price_key, price_ex_vat, basis, evidence, effective_from, recorded_by) values
  ('gid://shopify/Customer/9000000001', 'TEA_1L',    58.50, 'family_last_paid', '#GT1 2026-09-01', '2026-09-01', 'test'),
  ('gid://shopify/Customer/9000000001', 'T-MATCHA',  450,   'last_paid',        '#GT1 2026-09-01', '2026-09-01', 'test'),
  ('gid://shopify/Customer/9000000001', 'T-PRIVATE', 24,    'last_paid',        '#GT1 2026-09-01', '2026-09-01', 'test');
insert into sales_core.customer_price (shopify_customer_id, price_key, price_ex_vat, basis, evidence, effective_from, recorded_by) values
  ('gid://shopify/Customer/9000000001', 'TEA_1L',    55.00, 'tom_decision',     'Tom 2026-09-24',  '2026-09-24', 'test');

-- ---------------------------------------------------------------- resolution
select is((select price_ex_vat from sales_core.v_customer_price where gt_customer_no = 9001 and sku = 'T-FRESH-1L'),
          55.00::numeric, 'R1: the latest row wins for the family');
select is((select basis from sales_core.v_customer_price where gt_customer_no = 9001 and sku = 'T-DETOX-1L'),
          'tom_decision', 'R2: the family price applies to every flavor');
select is((select price_ex_vat from sales_core.v_customer_price where gt_customer_no = 9001 and sku = 'T-MATCHA'),
          450.00::numeric, 'R3: a SKU price wins over the list');
select is((select price_inc_vat from sales_core.v_customer_price where gt_customer_no = 9001 and sku = 'T-MATCHA'),
          531.00::numeric, 'R4: VAT 18% is added');
select is((select basis from sales_core.v_customer_price where gt_customer_no = 9001 and sku = 'T-PUREE'),
          'list', 'R5: no history falls through to the list');
select is((select price_ex_vat from sales_core.v_customer_price where gt_customer_no = 9001 and sku = 'T-PRIVATE'),
          24.00::numeric, 'R6: a customer-specific product is shown to its customer');
select is((select count(*)::int from sales_core.v_customer_price where gt_customer_no = 9002 and sku = 'T-PRIVATE'),
          0, 'R7: a customer-specific product is hidden from others');
select is((select count(*)::int from sales_core.v_customer_price where sku = 'T-GONE'),
          0, 'R8: an inactive product is excluded');
select is((select count(*)::int from sales_core.v_customer_price where gt_customer_no = 9002 and sku like 'T-%'),
          4, 'R9: customer B sees the four general test products');
select is((select count(*)::int from sales_core.v_customer_price where price_ex_vat is null),
          0, 'R10: never a null price');

-- ---------------------------------------------------------------- invariants
select throws_ok($$update sales_core.customer_price set price_ex_vat = 1$$,
                 'P0001', null, 'I1: customer_price rejects UPDATE');
select throws_ok($$delete from sales_core.customer_price$$,
                 'P0001', null, 'I2: customer_price rejects DELETE');
select throws_ok($$insert into sales_core.list_price (sku, name_he, general, source, verified_on)
                   values ('X', 'x', true, 't', '2026-09-24')$$,
                 '23514', null, 'I3: a general product needs a list price');
select throws_ok($$insert into sales_core.customer_price (shopify_customer_id, price_key, price_ex_vat, basis, evidence, effective_from, recorded_by)
                   values ('gid://shopify/Customer/1', 'X', 1, 'guess', 'e', '2026-09-24', 't')$$,
                 '23514', null, 'I4: basis is a closed list');
select throws_ok($$insert into sales_core.customer_book (shopify_customer_id, gt_customer_no, place_name)
                   values ('gid://shopify/Customer/3', 999, 'x')$$,
                 '23514', null, 'I5: the customer number has 4 digits');
select throws_ok($$insert into sales_core.customer_book (shopify_customer_id, gt_customer_no, place_name)
                   values ('gid://shopify/Customer/4', 9001, 'x')$$,
                 '23505', null, 'I6: the customer number is unique');
select is((select count(*)::int
             from information_schema.table_constraints tc
             join information_schema.constraint_column_usage ccu
               on ccu.constraint_name = tc.constraint_name and ccu.constraint_schema = tc.constraint_schema
            where tc.table_schema = 'sales_core'
              and tc.table_name in ('list_price', 'customer_price', 'customer_book')
              and tc.constraint_type = 'FOREIGN KEY'
              and ccu.table_schema <> 'sales_core'),
          0, 'I7: no foreign key leaves sales_core');

select * from finish();

rollback;
```

- [ ] **Step 3: Run it to verify it fails** — **CONTROLLER**

```bash
cd /home/user/gt-factory-os && psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/tests/0352_sales_core_price_book.test.sql
```
Expected: FAIL (`relation "sales_core.list_price" does not exist`). Nothing persists (rollback).

- [ ] **Step 4: Write the migration**

Create `db/migrations/0352_sales_core_price_book.sql` (no `begin`/`commit` inside — the apply wraps it; the pre-apply test wraps it in a rolled-back transaction):

```sql
-- 0352_sales_core_price_book.sql
--
-- WHY
--
-- GT is moving almost all of its business customers to the distributor Ice
-- Dream, which invoices them at GT's prices. Until now a customer's price lived
-- nowhere: it was whatever they paid last time, recomputed from Shopify order
-- history by every caller, while a free-text metafield (178 spellings) and
-- pricing tags disagreed with what customers actually paid. A distributor
-- cannot invoice from that. This migration gives prices one home.
--
-- Spec: gt-factory-os-production-brain/docs/superpowers/specs/2026-09-24-icedream-handoff-design.md
--
-- SHAPE
--
--   list_price       -- what GT sells (catalog-truth) at list price, plus
--                       customer-specific products (general = false, no list price).
--   customer_price   -- append-only. One row = one price decision for
--                       (customer, key); key is a SKU or a tea family (TEA_1L /
--                       TEA_05L). The current price is the row with the highest seq.
--   customer_book    -- one row per branch (Shopify customer): what a distributor
--                       needs to invoice and deliver, each field with its source.
--   v_customer_price -- the resolved matrix: customer SKU row, else customer
--                       family row, else list price. Never a null price.
--
-- Isolated by construction: no foreign key leaves sales_core; nothing here reads
-- or writes the ledger, balances, items or BOMs. Prices are before VAT; the view
-- adds Israel's 18%.

create table if not exists sales_core.list_price (
  sku           text primary key,
  name_he       text not null,
  size_label    text not null default '',
  family        text check (family in ('TEA_1L', 'TEA_05L')),
  barcode       text,
  price_ex_vat  numeric(10,2) check (price_ex_vat > 0),
  general       boolean not null default true,
  active        boolean not null default true,
  source        text not null,
  verified_on   date not null,
  updated_at    timestamptz not null default now(),
  constraint list_price_general_has_price check (not general or price_ex_vat is not null)
);

create table if not exists sales_core.customer_price (
  id                   uuid primary key default gen_random_uuid(),
  seq                  bigint generated always as identity unique,
  shopify_customer_id  text not null check (shopify_customer_id like 'gid://shopify/Customer/%'),
  price_key            text not null,
  price_ex_vat         numeric(10,2) not null check (price_ex_vat > 0),
  basis                text not null check (basis in ('last_paid', 'family_last_paid', 'discontinued_map', 'tom_decision')),
  evidence             text not null check (length(evidence) > 0),
  effective_from       date not null,
  recorded_at          timestamptz not null default clock_timestamp(),
  recorded_by          text not null
);

create index if not exists customer_price_current_idx
  on sales_core.customer_price (shopify_customer_id, price_key, seq desc);

create or replace function sales_core.tg_customer_price_append_only()
returns trigger
language plpgsql
as $fn$
begin
  raise exception 'sales_core.customer_price is append-only: % is not permitted', tg_op
    using errcode = 'P0001';
end;
$fn$;

drop trigger if exists customer_price_no_update on sales_core.customer_price;
create trigger customer_price_no_update
  before update on sales_core.customer_price
  for each row execute function sales_core.tg_customer_price_append_only();

drop trigger if exists customer_price_no_delete on sales_core.customer_price;
create trigger customer_price_no_delete
  before delete on sales_core.customer_price
  for each row execute function sales_core.tg_customer_price_append_only();

create table if not exists sales_core.customer_book (
  shopify_customer_id     text primary key check (shopify_customer_id like 'gid://shopify/Customer/%'),
  gt_customer_no          integer not null unique check (gt_customer_no between 1001 and 9999),
  place_name              text not null,
  legal_name              text,
  tax_id                  text,
  chain                   text,
  business_type           text,
  invoice_address         text,
  accounting_email        text,
  payment_terms_code      integer,
  payment_terms_he        text,
  street                  text,
  house_number            text,
  city                    text,
  delivery_notes          text,
  region                  text check (region in ('center', 'north', 'south')),
  delivery_days_he        text,
  onsite_contact_name     text,
  onsite_contact_phone    text,
  receiving_restrictions  text,
  kashrut                 text check (kashrut in ('not_kosher', 'rabbinate', 'badatz')),
  last_order_on           date,
  orders_per_month        numeric(5,1),
  field_sources           jsonb not null default '{}'::jsonb,
  active                  boolean not null default true,
  created_at              timestamptz not null default now(),
  updated_at              timestamptz not null default now()
);

create or replace view sales_core.v_customer_price as
with cur as (
  select distinct on (cp.shopify_customer_id, cp.price_key)
         cp.shopify_customer_id, cp.price_key, cp.price_ex_vat, cp.basis, cp.evidence
    from sales_core.customer_price cp
   order by cp.shopify_customer_id, cp.price_key, cp.seq desc
)
select b.shopify_customer_id,
       b.gt_customer_no,
       lp.sku,
       lp.name_he,
       lp.size_label,
       lp.barcode,
       lp.family,
       lp.general,
       coalesce(s.price_ex_vat, f.price_ex_vat, lp.price_ex_vat)                  as price_ex_vat,
       round(coalesce(s.price_ex_vat, f.price_ex_vat, lp.price_ex_vat) * 1.18, 2) as price_inc_vat,
       lp.price_ex_vat                                                            as list_price_ex_vat,
       case when s.price_key is not null then s.basis
            when f.price_key is not null then f.basis
            else 'list' end                                                       as basis,
       coalesce(s.evidence, f.evidence)                                           as evidence
  from sales_core.customer_book b
  cross join sales_core.list_price lp
  left join cur s on s.shopify_customer_id = b.shopify_customer_id and s.price_key = lp.sku
  left join cur f on f.shopify_customer_id = b.shopify_customer_id and f.price_key = lp.family
 where b.active
   and lp.active
   and (lp.general or s.price_key is not null);

-- grants: service_role ONLY (customer contacts are PII) ---------------------
do $$
begin
  if exists (select 1 from pg_roles where rolname = 'service_role') then
    grant usage on schema sales_core to service_role;
    grant select, insert, update on sales_core.list_price to service_role;
    grant select, insert on sales_core.customer_price to service_role;
    grant select, insert, update on sales_core.customer_book to service_role;
    grant select on sales_core.v_customer_price to service_role;
  end if;
end $$;
```

- [ ] **Step 5: Run the test with the migration inside a rolled-back transaction** — **CONTROLLER**

```bash
cd /home/user/gt-factory-os
printf 'begin;\n\\i db/migrations/0352_sales_core_price_book.sql\n\\i db/tests/0352_sales_core_price_book.test.sql\n' > /tmp/t0352.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f /tmp/t0352.sql | grep -E "^(ok|not ok|1\.\.)" 
psql "$DATABASE_URL" -Atc "select to_regclass('sales_core.list_price')"
```
Expected: `1..21`, 21 lines `ok`, zero `not ok`; the second command prints an empty line (nothing persisted).

- [ ] **Step 6: Slot check again (FR2) and commit**

```bash
cd /home/user/gt-factory-os && ls db/migrations | sort | tail -3
git add db/migrations/0352_sales_core_price_book.sql db/tests/0352_sales_core_price_book.test.sql
git commit -m "feat(sales_core): 0352 price book, customer book, resolving view"
```
Expected: `0352_sales_core_price_book.sql` is the highest; no other new file.

---

### Task 3: Pipeline scaffold, brand, Hebrew copy, general price list

**Files:**
- Create: `scripts/distributor-handoff/{README.md,requirements.txt,.gitignore}`
- Create: `scripts/distributor-handoff/handoff/{__init__.py,config.py,model.py,brand.py,copy_he.py,catalog.py}`
- Test: `scripts/distributor-handoff/tests/{__init__.py,test_catalog.py}`

**Interfaces:**
- Produces: `config` constants (`FAMILIES`, `DISCONTINUED_EQUIV`, `VAT`, `WINDOW_DAYS`, `E2_DROP`, paths); dataclasses `Line`, `ListPrice`, `Proposal`, `Flag` (with `.id`), `CustomerRow`; `brand.font_face_css() -> str`, `brand.tokens_css() -> str`; `copy_he` constants; `catalog.read_tsv(path) -> dict[str, tuple[str, str, Decimal]]`, `catalog.read_catalog_truth(path) -> tuple[list[tuple[str, str, str, Decimal | None]], set[str]]`, `catalog.build_list_prices(tsv, truth, negative, barcodes, sold_recently, verified_on) -> tuple[list[ListPrice], list[Flag]]`.

- [ ] **Step 1: Scaffold files and virtualenv**

`requirements.txt`:
```
openpyxl==3.1.5
psycopg[binary]==3.3.6
pypdf==6.19.0
```

`.gitignore`:
```
raw/
out/
.venv/
__pycache__/
```

`README.md`:
```markdown
# distributor-handoff — חבילת ההעברה לאייס דרים

Spec: `gt-factory-os-production-brain/docs/superpowers/specs/2026-09-24-icedream-handoff-design.md`.
Plan: `gt-factory-os-production-brain/docs/superpowers/plans/2026-09-24-icedream-handoff.md`.

    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/python -m unittest discover -s tests -t . -v
    .venv/bin/python run.py --help

- Shopify, Green Invoice, LionWheel: read-only.
- `raw/` and `out/` hold customer data and prices: never committed.
- Env: SHOPIFY_STORE_DOMAIN, SHOPIFY_ADMIN_API_TOKEN, GREENINVOICE_API_BASE_URL, GREENINVOICE_KEY_ID,
  GREENINVOICE_SECRET, LIONWHEEL_BASE_URL, LIONWHEEL_API_KEY, DATABASE_URL. Never printed.
```

`handoff/__init__.py`:
```python
"""Ice Dream handoff pipeline (spec: docs/superpowers/specs/2026-09-24-icedream-handoff-design.md, brain repo)."""
```

`tests/__init__.py`: empty file.

```bash
cd /home/user/gt-factory-os/scripts/distributor-handoff && python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt
```

- [ ] **Step 2: Write `config.py`, `model.py`, `brand.py`, `copy_he.py`**

`handoff/config.py`:
```python
"""Paths and constants for the Ice Dream handoff pipeline. Secrets come only from the environment."""
from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # scripts/distributor-handoff
RAW = ROOT / "raw"  # gitignored — pulled source data
OUT = ROOT / "out"  # gitignored — packages, reports, decisions
BRAIN = Path(os.environ.get("GT_BRAIN_PATH", str(ROOT.parents[2] / "gt-factory-os-production-brain")))
PRICING_TSV = BRAIN / "docs/pricing/2026-08-05_shopify_products_exvat.tsv"
CATALOG_TRUTH = BRAIN / "docs/warehouses/catalog-truth.md"
ZONES = BRAIN / ".claude/skills/daily-delivery-dispatch/zones.json"
ROUTE_CALENDAR = BRAIN / ".claude/skills/daily-delivery-dispatch/route_calendar.json"
FONTS = BRAIN / "docs/pricing/pricelist_pdf/fonts"
CHROME = os.environ.get("CHROME_BIN", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")

SHOPIFY_API_VERSION = "2025-07"
VAT = Decimal("1.18")  # Israel VAT 18%
WINDOW_DAYS = 365  # "active" = ordered within this many days
E2_DROP = Decimal("0.10")  # E2 fires when the last price is ≥10% below the previous one
RECORDED_BY = "system:distributor-handoff"

TEA_FLAVORS = (
    "GT-HIB-LOW", "GT-HIB-FRE", "GT-LUI-LOW", "GT-LUI-FRE", "GT-LEM-LOW", "GT-CHA-LOW",
    "GT-JAS-LOW", "GT-SEN-LOW", "GT-INF-DES", "GT-MAS-CHA", "GT-AME-LOW",
)
FAMILIES = {
    "TEA_1L": frozenset(f"{f}-1L" for f in TEA_FLAVORS),
    "TEA_05L": frozenset(f"{f}-0.5L" for f in TEA_FLAVORS),
}
# Old matcha SKUs carry their price to the current Shizuoka SKU
# (same map as .claude/skills/shopify-draft-order-from-po/scripts/lookup.mjs).
DISCONTINUED_EQUIV = {
    "GT-MAR-CER-500": "GT-SHI-CER-500", "GT-KOG-ORG-500": "GT-SHI-CER-500", "GT-MAR-XP-500": "GT-SHI-CER-500",
    "GT-MAR-CER-18*22": "GT-SHI-CER-18*22", "GT-KOG-ORG-18*22": "GT-SHI-CER-18*22",
}
```

`handoff/model.py`:
```python
"""Records shared by every stage. Plain dataclasses, no I/O."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True)
class Line:
    """One purchased order line — not test, not cancelled, price and quantity > 0."""
    customer_id: str
    sku: str
    order_name: str
    ordered_at: datetime
    qty: int
    net_unit: Decimal


@dataclass(frozen=True)
class ListPrice:
    sku: str
    name_he: str
    size_label: str
    family: str | None
    barcode: str | None
    price_ex_vat: Decimal | None
    general: bool
    source: str
    verified_on: date


@dataclass(frozen=True)
class Proposal:
    customer_id: str
    price_key: str
    price_ex_vat: Decimal
    basis: str
    evidence: str
    effective_from: date


@dataclass(frozen=True)
class Flag:
    code: str  # E1–E5 prices · C1 catalog · K2/K3 customer book
    customer_id: str  # '' for catalog-level flags
    key: str  # price key, SKU, field or invoice reference
    proposed: Decimal | None
    detail_he: str
    weight_ils: Decimal = Decimal("0")

    @property
    def id(self) -> str:
        return f"{self.code}:{self.customer_id}:{self.key}"


@dataclass
class CustomerRow:
    shopify_customer_id: str
    gt_customer_no: int | None = None
    place_name: str | None = None
    legal_name: str | None = None
    tax_id: str | None = None
    chain: str | None = None
    business_type: str | None = None
    invoice_address: str | None = None
    accounting_email: str | None = None
    payment_terms_code: int | None = None
    payment_terms_he: str | None = None
    street: str | None = None
    house_number: str | None = None
    city: str | None = None
    delivery_notes: str | None = None
    region: str | None = None
    delivery_days_he: str | None = None
    onsite_contact_name: str | None = None
    onsite_contact_phone: str | None = None
    receiving_restrictions: str | None = None
    kashrut: str | None = None
    last_order_on: date | None = None
    orders_per_month: Decimal | None = None
    field_sources: dict[str, str] = field(default_factory=dict)
    active: bool = True
```

`handoff/brand.py`:
```python
"""GT brand DNA (Tom-approved 2026-08-06, docs/warehouses/marketing-assets.md): palette + embedded fonts."""
from __future__ import annotations

import base64
from functools import lru_cache

from .config import FONTS

PAPER, INK, GREEN, CORAL, LINE, MUTED, WASH = "#EFE6D6", "#241C15", "#263B18", "#FA6E4D", "#D8CCB4", "#7C6E58", "#F7F2E9"

_FACES = (
    ("Heebo", 400, "heebo-400.woff"), ("Heebo", 500, "heebo-500.woff"), ("Heebo", 700, "heebo-700.woff"),
    ("Rubik", 500, "rubik-500.woff"), ("Rubik", 600, "rubik-600.woff"), ("Rubik", 700, "rubik-700.woff"),
)


@lru_cache(maxsize=1)
def font_face_css() -> str:
    """@font-face rules with the WOFF files inlined — the PDF renders identically offline."""
    rules = []
    for family, weight, file in _FACES:
        data = base64.b64encode((FONTS / file).read_bytes()).decode()
        rules.append(f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:normal;"
                     f"src:url(data:font/woff;base64,{data}) format('woff')}}")
    return "".join(rules)


def tokens_css() -> str:
    return (f":root{{--paper:{PAPER};--ink:{INK};--green:{GREEN};--coral:{CORAL};"
            f"--line:{LINE};--muted:{MUTED};--wash:{WASH}}}")
```

`handoff/copy_he.py`:
```python
"""Every Hebrew string the package shows, in one place. Short, clear, the key word first."""
from __future__ import annotations

PACKAGE_TITLE = "לקוחות ומחירים"
PACKAGE_FOR = "חבילת העברה לאייס דרים"
CONFIDENTIAL = "סודי · לשימוש אייס דרים בלבד"
VERSION_LINE = "גרסה {version} · {date_he}"

REGION_HE = {"center": "מרכז", "north": "צפון", "south": "דרום"}
NO_REGION = "ללא אזור"
KASHRUT_HE = {"not_kosher": "לא כשר", "rabbinate": "כשר — רבנות", "badatz": "כשר — בד״ץ"}
FAMILY_HE = {"TEA_1L": "תמציות תה 1 ליטר", "TEA_05L": "תמציות תה 500 מ״ל"}
ALL_FLAVORS = "כל הטעמים"
PRODUCTS_KASHRUT = "כל המוצרים כשרים בד״ץ בית יוסף, בהשגחת הרבנות חולון."
MISSING = "—"

# ---------------------------------------------------------------- workbook
SHEET_README = "קרא אותי"
SHEET_CUSTOMERS = "לקוחות"
SHEET_SPECIALS = "מחירים מיוחדים ללקוח"
SHEET_GENERAL = "מחירון כללי"
SHEET_DAYS = "ימי חלוקה"


def readme_rules(meta: dict) -> list[tuple[str, str]]:
    return [
        ("המחירים", "לפני מע״מ. ליד כל מחיר מופיע גם המחיר כולל מע״מ (18%)."),
        ("תמציות תה", "ללקוח יש מחיר אחד לכל הטעמים באותו גודל: 1 ליטר או 500 מ״ל."),
        ("מוצר שלא מופיע אצל הלקוח", "נמכר לו לפי המחירון הכללי."),
        ("לקוח חדש", "נמכר לפי המחירון הכללי."),
        ("מספר לקוח", "4 ספרות. כך נזהה את הלקוח בכל הזמנה שנעביר אליכם."),
        ("ימי חלוקה", meta["days_summary_he"]),
        ("כשרות המוצרים", PRODUCTS_KASHRUT),
        ("חשבוניות", f"החל מ־{meta['switch_date_he']} החשבונית ללקוח יוצאת מאייס דרים."),
        ("שאלות", f"{meta['contact_name']} · {meta['contact_phone']}"),
    ]


CUSTOMER_GROUPS = [("זיהוי", 6), ("חשבונית", 3), ("משלוח", 6), ("בסניף", 3), ("כשרות", 1), ("לתכנון", 2), ("מערכת", 1)]
CUSTOMER_HEADERS = [
    "מספר לקוח", "שם העסק", "שם משפטי", "ח.פ / ע.מ", "רשת", "סוג עסק",
    "מייל להנהלת חשבונות", "כתובת לחשבונית", "תנאי תשלום היום ב־GT",
    "רחוב", "מספר", "עיר", "אזור", "ימי חלוקה", "הערות למשלוח",
    "מי מקבל את הסחורה", "טלפון", "הגבלות קבלה",
    "כשרות",
    "הזמנה אחרונה", "הזמנות בחודש",
    "מזהה במערכת GT",
]
SPECIAL_HEADERS = ["מספר לקוח", "שם העסק", "מוצר", "גודל", "ברקוד", "מק״ט", "לפני מע״מ", "כולל מע״מ", "מחירון כללי", "הערה"]
GENERAL_HEADERS = ["מוצר", "גודל", "ברקוד", "מק״ט", "לפני מע״מ", "כולל מע״מ"]
DAYS_HEADERS = ["עיר", "אזור", "ימי חלוקה"]
FAMILY_NOTE = "מחיר קבוע לכל הטעמים בגודל הזה"
PRIVATE_NOTE = "מוצר ייעודי ללקוח"

# ---------------------------------------------------------------- binder
B_GUIDE = "איך משתמשים בקלסר"
B_INDEX = "רשימת הלקוחות"
B_INDEX_HEADERS = ["מספר", "שם העסק", "עיר", "אזור", "עמוד"]
B_CUSTOMER_NO = "מספר לקוח"
B_DELIVERY = "משלוח"
B_SITE = "בסניף"
B_INVOICE = "חשבונית"
B_KASHRUT = "כשרות"
B_DAYS = "ימי חלוקה"
B_PRICES = "המחירים של הלקוח"
B_PRICE_HEADERS = ["מוצר", "גודל", "לפני מע״מ", "כולל מע״מ"]
B_REST = "כל שאר המוצרים — לפי המחירון הכללי, עמוד {page}."
B_ONLY_GENERAL = "הלקוח קונה לפי המחירון הכללי, עמוד {page}."
B_CONTINUED = "המשך"
B_GENERAL = "המחירון הכללי"
B_CATALOG = "המוצרים"
B_CUSTOMERS_IN_REGION = "{n} לקוחות"
B_TAX_ID = "ח.פ"

# ---------------------------------------------------------------- review page (Tom)
REVIEW_TITLE = "חריגים לאישור — ספר המחירים"
REVIEW_HOW = "כל שורה היא הצעה. ענה בצ׳אט: ״מאשר הכל״, או כתוב רק את מה שמשתנה."
REVIEW_HEADERS = ["לקוח", "מוצר / שדה", "מוצע", "פירוט", "מחזור בשנה"]
REVIEW_GAPS = "פרטים חסרים בכרטיסי הלקוחות (ייאספו בטופס)"
FLAG_TITLES = {
    "E1": "מחירי תה שונים בין טעמים",
    "E2": "ירידה חדה במחיר בקנייה האחרונה",
    "E3": "משלם יותר מהמחירון הכללי",
    "E4": "סניפים של אותה חברה — מחירים שונים",
    "E5": "לא תואם לחשבונית האחרונה",
    "C1": "נמכר ולא מופיע בקטלוג",
    "K2": "ח.פ שונה בין Green Invoice לשופיפיי",
    "K3": "לקוח פעיל בלי קישור ל־Green Invoice",
}
FLAG_WHY = {
    "E1": "הלקוח שילם מחירים שונים על טעמים שונים באותו גודל. הכלל: מחיר אחד לכל הטעמים. מוצע: המחיר האחרון.",
    "E2": "הקנייה האחרונה זולה ב־10% או יותר מהקודמת. אולי הנחה חד־פעמית — האם זה המחיר הקבוע?",
    "E3": "הלקוח משלם יותר מהמחירון הכללי.",
    "E4": "סניפים של אותה חברה משלמים מחירים שונים על אותו מוצר.",
    "E5": "המחיר בספר שונה מהמחיר בחשבונית האחרונה ב־Green Invoice.",
    "C1": "המוצר נמכר בשנה האחרונה ולא מופיע בקטלוג: מחירון כללי, מוצר ייעודי, או לא נמכר עוד?",
    "K2": "ח.פ שונה בין Green Invoice לשופיפיי. איזה נכון?",
    "K3": "הלקוח הזמין השנה ואין לו קישור ל־Green Invoice.",
}

# ---------------------------------------------------------------- customer message + form (Tom approves before use)
CUSTOMER_MESSAGE = (
    "שלום {place_name},\n"
    "עדכון קצר מ־GT Everyday: החל מ־{switch_date_he} ההפצה והחשבוניות שלנו עוברות לאייס דרים, המפיץ שלנו.\n"
    "המחירים שלכם לא משתנים, וההזמנות ממשיכות להגיע אלינו כרגיל.\n"
    "כדי שהמשלוח הראשון יגיע בדיוק — טופס של 30 שניות: {form_link}\n"
    "ייתכן שדנה מאייס דרים תיצור קשר לגבי תנאי התשלום.\n"
    "תודה, {sender}"
)
FORM_TITLE = "GT Everyday — פרטים למשלוח"
FORM_INTRO = "30 שניות, ואנחנו מוכנים למעבר לאייס דרים. תודה!"
FORM_QUESTIONS = {
    "gt_no": "מספר לקוח (ממולא מראש)",
    "place_name": "שם העסק, כמו על השלט",
    "street": "רחוב",
    "house_number": "מספר בית",
    "city": "עיר",
    "onsite_contact_name": "מי מקבל את הסחורה בסניף? (שם)",
    "onsite_contact_phone": "טלפון של מי שמקבל את הסחורה",
    "accounting_email": "מייל להנהלת חשבונות (לחשבוניות)",
    "kashrut": "כשרות העסק",
    "receiving_restrictions": "יש שעות שבהן אי אפשר לקבל סחורה? (לא חובה)",
}
FORM_KASHRUT_OPTIONS = {"לא כשר": "not_kosher", "כשר — רבנות": "rabbinate", "כשר — בד״ץ": "badatz"}
MESSAGES_TITLE = "הודעות ללקוחות — שליחה ידנית"
MESSAGES_HOW = "לחיצה על ״שליחה״ פותחת וואטסאפ עם ההודעה מוכנה. קוראים — ושולחים."
MESSAGES_SEND = "שליחה"
MESSAGES_NO_PHONE = "אין מספר וואטסאפ"

# ---------------------------------------------------------------- weekly update
UPDATE_SHEET = "עדכון שבועי"
UPDATE_HEADERS = ["מספר לקוח", "שם העסק", "מה השתנה", "היה", "עכשיו"]
CHANGE_NEW_CUSTOMER = "לקוח חדש"
CHANGE_REMOVED = "לא בחבילה יותר"
CHANGE_PRICE = "מחיר: {product}"
CHANGE_PRICE_NEW = "מחיר מיוחד חדש: {product}"
CHANGE_PRICE_GONE = "מחיר מיוחד בוטל: {product}"
GENERAL_LIST = "מחירון כללי"
```

- [ ] **Step 3: Write the failing test**

`tests/test_catalog.py`:
```python
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from handoff.catalog import build_list_prices, read_catalog_truth, read_tsv

TSV = (
    "# comment line\n"
    "sku\ttitle\ttype\tprice_ils_exvat\n"
    "GT-HIB-LOW-1L\tFRESH 1000ml\tTea 1 l\t65.00\n"
    "GT-HIB-LOW-0.5L\tFRESH 500ml\tTea 0.5 l\t33.00\n"
    "GT-SHI-CER-500\tShizuoka 500g\tMatcha\t590.00\n"
    "GTCC-MUZ-ANBL-1L\tMuza Anise Bliss 1000ml\tCocktail\t88.00\n"
)
TRUTH = """# title

## תמציות תה — ליטר ₪65

| מוצר | SKU ליטר | SKU 500 מ"ל | מקור |
|---|---|---|---|
| FRESH | GT-HIB-LOW-1L | GT-HIB-LOW-0.5L | TSV |

## מאצ'ה ואבקות

| מוצר | SKU | ₪ ללא מע"מ | מקור |
|---|---|---|---|
| מאצ'ה שיזואוקה 500 גרם | GT-SHI-CER-500 | 590 | TSV |
| HOJICHA 500 גרם | GT-HOJ-BLK-500 | 375 | live |

## רשומות-שלילה — לא נמכר

| מוצר | SKU | קביעה |
|---|---|---|
| מאצ'ה 50 גרם | GT-SHI-CER-50 | לא מוכרים |
"""
TODAY = date(2026, 9, 24)


class CatalogTest(unittest.TestCase):
    def setUp(self):
        d = Path(tempfile.mkdtemp())
        (d / "p.tsv").write_text(TSV, encoding="utf-8")
        (d / "c.md").write_text(TRUTH, encoding="utf-8")
        self.tsv = read_tsv(d / "p.tsv")
        self.truth, self.negative = read_catalog_truth(d / "c.md")

    def test_tsv(self):
        self.assertEqual(self.tsv["GT-HIB-LOW-1L"], ("FRESH 1000ml", "Tea 1 l", Decimal("65.00")))

    def test_truth_rows_sizes_and_negative_section(self):
        self.assertEqual([r[0] for r in self.truth], ["GT-HIB-LOW-1L", "GT-HIB-LOW-0.5L", "GT-SHI-CER-500", "GT-HOJ-BLK-500"])
        self.assertEqual((self.truth[0][2], self.truth[1][2]), ("1 ליטר", "500 מ״ל"))
        self.assertEqual(self.truth[3][3], Decimal("375"))
        self.assertEqual(self.negative, {"GT-SHI-CER-50"})

    def test_build_general_specific_and_flags(self):
        rows, flags = build_list_prices(self.tsv, self.truth, self.negative, {"GT-HIB-LOW-1L": "7290000000011"},
                                        {"GTCC-MUZ-ANBL-1L": "Muza", "GT-SHI-CER-50": "old"}, TODAY)
        by = {r.sku: r for r in rows}
        self.assertEqual((by["GT-HIB-LOW-1L"].family, by["GT-HIB-LOW-1L"].barcode), ("TEA_1L", "7290000000011"))
        self.assertEqual(by["GT-HOJ-BLK-500"].price_ex_vat, Decimal("375"))
        self.assertFalse(by["GTCC-MUZ-ANBL-1L"].general)
        self.assertIsNone(by["GTCC-MUZ-ANBL-1L"].price_ex_vat)
        self.assertNotIn("GT-SHI-CER-50", by)
        self.assertEqual([f.code for f in flags], ["C1"])

    def test_price_conflict_halts(self):
        with self.assertRaises(ValueError):
            build_list_prices(self.tsv, [("GT-SHI-CER-500", "x", "", Decimal("600"))], set(), {}, {}, TODAY)
```

- [ ] **Step 4: Run to verify it fails**

Run the test command. Expected: `ModuleNotFoundError: No module named 'handoff.catalog'`.

- [ ] **Step 5: Implement `catalog.py`**

```python
"""General price list (spec §5.1): catalog-truth decides WHAT we sell; the price TSV decides the price."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from .config import FAMILIES
from .model import Flag, ListPrice

NEGATIVE_SECTION = "רשומות-שלילה"
SIZE_FROM_TSV_TYPE = {"Tea 1 l": "1 ליטר", "Tea 0.5 l": "500 מ״ל", "Tea 0.3 l": "300 מ״ל"}
FAMILY_OF = {sku: fam for fam, skus in FAMILIES.items() for sku in skus}


def read_tsv(path: Path) -> dict[str, tuple[str, str, Decimal]]:
    """sku -> (title, type, price ex VAT). Lines starting with '#' are comments."""
    rows = [ln.split("\t") for ln in path.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    header = rows[0]
    i_sku, i_title, i_type, i_price = (header.index(c) for c in ("sku", "title", "type", "price_ils_exvat"))
    return {r[i_sku].strip(): (r[i_title].strip(), r[i_type].strip(), Decimal(r[i_price].strip()))
            for r in rows[1:] if len(r) > i_price and r[i_sku].strip()}


def read_catalog_truth(path: Path) -> tuple[list[tuple[str, str, str, Decimal | None]], set[str]]:
    """([(sku, name_he, size_label, price_or_None)], negative SKUs). The negative section lists what is NOT sold."""
    sold: list[tuple[str, str, str, Decimal | None]] = []
    negative: set[str] = set()
    in_negative = False
    header: list[str] | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("## "):
            in_negative = NEGATIVE_SECTION in line
            header = None
            continue
        if not line.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if header is None:
            header = cells
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        row = dict(zip(header, cells))
        name = row.get("מוצר", "")
        price_col = next((h for h in header if h.startswith("₪")), None)
        price_txt = row.get(price_col, "") if price_col else ""
        price = Decimal(price_txt.replace(",", "")) if price_txt else None
        for col in (h for h in header if "SKU" in h):
            sku = row.get(col, "")
            if not sku:
                continue
            if in_negative:
                negative.add(sku)
                continue
            size = "500 מ״ל" if "500" in col else ("1 ליטר" if "ליטר" in col else "")
            sold.append((sku, name, size, price))
    return sold, negative


def build_list_prices(
    tsv: dict[str, tuple[str, str, Decimal]],
    truth: list[tuple[str, str, str, Decimal | None]],
    negative: set[str],
    barcodes: dict[str, str],
    sold_recently: dict[str, str],
    verified_on: date,
) -> tuple[list[ListPrice], list[Flag]]:
    """General list from catalog-truth, plus customer-specific rows (C1) for other SKUs sold recently."""
    out: list[ListPrice] = []
    flags: list[Flag] = []
    seen: set[str] = set()
    for sku, name, size, truth_price in truth:
        if sku in seen:
            continue
        t = tsv.get(sku)
        tsv_price = t[2] if t else None
        if tsv_price is not None and truth_price is not None and tsv_price != truth_price:
            raise ValueError(f"{sku}: TSV {tsv_price} ≠ catalog-truth {truth_price}")
        price = tsv_price if tsv_price is not None else truth_price
        if price is None:
            raise ValueError(f"{sku}: no list price in the TSV or in catalog-truth")
        if not size and t:
            size = SIZE_FROM_TSV_TYPE.get(t[1], "")
        out.append(ListPrice(sku, name, size, FAMILY_OF.get(sku), barcodes.get(sku), price, True, "catalog-truth", verified_on))
        seen.add(sku)
    for sku, title in sorted(sold_recently.items()):
        if sku in seen or sku in negative:
            continue
        t = tsv.get(sku)
        name = t[0] if t else title
        size = SIZE_FROM_TSV_TYPE.get(t[1], "") if t else ""
        out.append(ListPrice(sku, name, size, None, barcodes.get(sku), None, False, "sold, not in catalog-truth", verified_on))
        flags.append(Flag("C1", "", sku, None,
                          f"{name} ({sku}) נמכר בשנה האחרונה ולא מופיע בקטלוג. כרגע: מוצר ייעודי ללקוחות שקנו אותו."))
    return out, flags
```

- [ ] **Step 6: Run to verify it passes**

Run the test command. Expected: `Ran 4 tests … OK`. Also check the fonts resolve:
```bash
cd /home/user/gt-factory-os/scripts/distributor-handoff && .venv/bin/python -c "from handoff.brand import font_face_css; print(len(font_face_css()) > 100000)"
```
Expected: `True`.

- [ ] **Step 7: Commit**

```bash
cd /home/user/gt-factory-os && git add scripts/distributor-handoff/README.md scripts/distributor-handoff/requirements.txt scripts/distributor-handoff/.gitignore scripts/distributor-handoff/handoff/__init__.py scripts/distributor-handoff/handoff/config.py scripts/distributor-handoff/handoff/model.py scripts/distributor-handoff/handoff/brand.py scripts/distributor-handoff/handoff/copy_he.py scripts/distributor-handoff/handoff/catalog.py scripts/distributor-handoff/tests/__init__.py scripts/distributor-handoff/tests/test_catalog.py
git commit -m "feat(distributor-handoff): scaffold, brand, Hebrew copy, general price list"
```

---

### Task 4: Price seeding rules and exceptions E1–E4

**Files:**
- Create: `scripts/distributor-handoff/handoff/prices.py`
- Test: `scripts/distributor-handoff/tests/test_prices.py`

**Interfaces:**
- Consumes: `Line`, `ListPrice`, `Proposal`, `Flag`; `config.FAMILIES`, `DISCONTINUED_EQUIV`, `WINDOW_DAYS`, `E2_DROP`.
- Produces: `money(x: Decimal) -> Decimal`; `canonical_sku(sku, list_prices) -> tuple[str | None, bool]`; `seed_prices(lines, list_prices: dict[str, ListPrice], today: date) -> tuple[list[Proposal], list[Flag], dict[str, int]]`; `chain_flags(proposals, tax_id_by_customer: dict[str, str]) -> list[Flag]`.

- [ ] **Step 1: Write the failing test**

`tests/test_prices.py`:
```python
import unittest
from datetime import date, datetime, timezone
from decimal import Decimal

from handoff.model import Line, ListPrice, Proposal
from handoff.prices import chain_flags, money, seed_prices

TODAY = date(2026, 9, 24)


def at(m, d, y=2026):
    return datetime(y, m, d, 10, tzinfo=timezone.utc)


def lp(sku, price, family=None, general=True):
    return ListPrice(sku, sku, "", family, None, None if price is None else Decimal(price), general, "test", TODAY)


LIST = {x.sku: x for x in [
    lp("GT-HIB-LOW-1L", "65", "TEA_1L"), lp("GT-LUI-LOW-1L", "65", "TEA_1L"),
    lp("GT-SHI-CER-500", "590"), lp("GT-ODK-MAN-1", "60"), lp("GTCC-MUZ-ANBL-1L", None, general=False),
]}


def line(cust, sku, order, when, price, qty=1):
    return Line(cust, sku, order, when, qty, Decimal(price))


class SeedTest(unittest.TestCase):
    def seed(self, lines):
        return seed_prices(lines, LIST, TODAY)

    def test_family_uses_latest_purchase_across_flavors(self):
        props, flags, _ = self.seed([line("c1", "GT-HIB-LOW-1L", "#GT1", at(9, 1), "58.50"),
                                     line("c1", "GT-LUI-LOW-1L", "#GT2", at(9, 10), "58.50")])
        self.assertEqual(len(props), 1)
        p = props[0]
        self.assertEqual((p.price_key, p.price_ex_vat, p.basis, p.evidence),
                         ("TEA_1L", Decimal("58.50"), "family_last_paid", "#GT2 2026-09-10"))
        self.assertEqual(flags, [])

    def test_e1_when_flavors_disagree(self):
        props, flags, _ = self.seed([line("c1", "GT-HIB-LOW-1L", "#GT1", at(9, 1), "58.50"),
                                     line("c1", "GT-LUI-LOW-1L", "#GT2", at(9, 10), "61")])
        self.assertEqual(props[0].price_ex_vat, Decimal("61.00"))
        self.assertEqual([f.code for f in flags], ["E1"])

    def test_discontinued_matcha_maps_to_shizuoka(self):
        props, _, _ = self.seed([line("c1", "GT-MAR-CER-500", "#GT3", at(9, 5), "450")])
        self.assertEqual((props[0].price_key, props[0].basis), ("GT-SHI-CER-500", "discontinued_map"))

    def test_not_sold_is_dropped(self):
        props, _, stats = self.seed([line("c1", "OLD-SKU", "#GT4", at(9, 5), "10")])
        self.assertEqual(props, [])
        self.assertEqual(stats["dropped_not_sold"], 1)

    def test_e2_sharp_drop(self):
        _, flags, _ = self.seed([line("c1", "GT-ODK-MAN-1", "#GT5", at(8, 1), "60"),
                                 line("c1", "GT-ODK-MAN-1", "#GT6", at(9, 1), "50")])
        self.assertEqual([f.code for f in flags], ["E2"])

    def test_no_e2_for_a_small_drop(self):
        _, flags, _ = self.seed([line("c1", "GT-ODK-MAN-1", "#GT5", at(8, 1), "60"),
                                 line("c1", "GT-ODK-MAN-1", "#GT6", at(9, 1), "55")])
        self.assertEqual(flags, [])

    def test_e3_above_list(self):
        _, flags, _ = self.seed([line("c1", "GT-ODK-MAN-1", "#GT7", at(9, 1), "70")])
        self.assertEqual([f.code for f in flags], ["E3"])

    def test_customer_specific_product_is_priced_without_e3(self):
        props, flags, _ = self.seed([line("c1", "GTCC-MUZ-ANBL-1L", "#GT8", at(9, 1), "88")])
        self.assertEqual((props[0].price_key, props[0].basis), ("GTCC-MUZ-ANBL-1L", "last_paid"))
        self.assertEqual(flags, [])

    def test_latest_wins_even_outside_the_window(self):
        props, _, _ = self.seed([line("c1", "GT-ODK-MAN-1", "#GT9", at(1, 1, 2025), "52")])
        self.assertEqual((props[0].price_ex_vat, props[0].effective_from), (Decimal("52.00"), date(2025, 1, 1)))

    def test_money_rounds_half_up(self):
        self.assertEqual(money(Decimal("58.505")), Decimal("58.51"))


class ChainTest(unittest.TestCase):
    def test_e4_only_when_branches_disagree(self):
        def p(cust, v):
            return Proposal(cust, "TEA_1L", Decimal(v), "family_last_paid", "e", TODAY)
        flags = chain_flags([p("a", "58.50"), p("b", "61.00"), p("c", "58.50")],
                            {"a": "000000018", "b": "000000018", "c": "000000026"})
        self.assertEqual(sorted(f.customer_id for f in flags), ["a", "b"])
        self.assertEqual({f.code for f in flags}, {"E4"})
```

- [ ] **Step 2: Run to verify it fails**

Expected: `ModuleNotFoundError: No module named 'handoff.prices'`.

- [ ] **Step 3: Implement `prices.py`**

```python
"""Seeding rules for the price book (spec §5.2) and the exceptions Tom reviews (§5.3)."""
from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from .config import DISCONTINUED_EQUIV, E2_DROP, FAMILIES, WINDOW_DAYS
from .model import Flag, Line, ListPrice, Proposal

CENT = Decimal("0.01")
FAMILY_OF = {sku: fam for fam, skus in FAMILIES.items() for sku in skus}


def money(x: Decimal) -> Decimal:
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


def canonical_sku(sku: str, list_prices: dict[str, ListPrice]) -> tuple[str | None, bool]:
    """(SKU to price under, mapped from a discontinued SKU?). None = no longer sold."""
    if sku in list_prices:
        return sku, False
    target = DISCONTINUED_EQUIV.get(sku)
    if target and target in list_prices:
        return target, True
    return None, False


def _list_price_for_key(key: str, list_prices: dict[str, ListPrice]) -> Decimal | None:
    if key in FAMILIES:
        found = [lp.price_ex_vat for sku, lp in list_prices.items()
                 if sku in FAMILIES[key] and lp.general and lp.price_ex_vat is not None]
        return max(found) if found else None
    lp = list_prices.get(key)
    return lp.price_ex_vat if lp and lp.general else None


def seed_prices(lines: list[Line], list_prices: dict[str, ListPrice], today: date
                ) -> tuple[list[Proposal], list[Flag], dict[str, int]]:
    window_start = today - timedelta(days=WINDOW_DAYS)
    stats: dict[str, int] = defaultdict(int)
    groups: dict[tuple[str, str], list[tuple[Line, str, bool]]] = defaultdict(list)
    for ln in lines:
        sku, mapped = canonical_sku(ln.sku, list_prices)
        if sku is None:
            stats["dropped_not_sold"] += 1
            continue
        groups[(ln.customer_id, FAMILY_OF.get(sku, sku))].append((ln, sku, mapped))

    proposals: list[Proposal] = []
    flags: list[Flag] = []
    for (cust, key), items in sorted(groups.items()):
        items.sort(key=lambda t: (t[0].ordered_at, t[0].order_name), reverse=True)
        latest, _, mapped = items[0]
        price = money(latest.net_unit)
        is_family = key in FAMILIES
        basis = "family_last_paid" if is_family else ("discontinued_map" if mapped else "last_paid")
        proposals.append(Proposal(cust, key, price, basis,
                                  f"{latest.order_name} {latest.ordered_at:%Y-%m-%d}", latest.ordered_at.date()))
        recent = [t for t in items if t[0].ordered_at.date() >= window_start]
        weight = money(sum((t[0].net_unit * t[0].qty for t in recent), Decimal("0")))

        if is_family:  # E1 — flavors of one size disagree within the window
            per_sku: dict[str, Decimal] = {}
            for ln, sku, _ in recent:  # newest first → first seen = latest per SKU
                per_sku.setdefault(sku, money(ln.net_unit))
            if len(set(per_sku.values())) > 1:
                spread = ", ".join(f"{s}: ₪{p}" for s, p in sorted(per_sku.items()))
                flags.append(Flag("E1", cust, key, price, f"מחירים שונים בין הטעמים ({spread}). מוצע: ₪{price}.", weight))

        earlier = [t for t in items[1:]
                   if window_start <= t[0].ordered_at.date() < latest.ordered_at.date()]
        if earlier:  # E2 — sharp drop on the last purchase
            prev = money(earlier[0][0].net_unit)
            if price < prev * (1 - E2_DROP):
                drop = int((1 - price / prev) * 100)
                flags.append(Flag("E2", cust, key, price, f"₪{price} — נמוך ב־{drop}% מהקנייה הקודמת (₪{prev}).", weight))

        list_ref = _list_price_for_key(key, list_prices)
        if list_ref is not None and price > list_ref:  # E3 — above the general list
            flags.append(Flag("E3", cust, key, price, f"משלם ₪{price}, המחירון הכללי ₪{list_ref}.", weight))
    return proposals, flags, dict(stats)


def chain_flags(proposals: list[Proposal], tax_id_by_customer: dict[str, str]) -> list[Flag]:
    """E4 — branches of one company (same ח.פ) pay different prices for the same key."""
    by: dict[tuple[str, str], list[Proposal]] = defaultdict(list)
    for p in proposals:
        tid = tax_id_by_customer.get(p.customer_id)
        if tid:
            by[(tid, p.price_key)].append(p)
    flags: list[Flag] = []
    for (tid, key), group in sorted(by.items()):
        if len({p.price_ex_vat for p in group}) > 1:
            listing = ", ".join(sorted(f"₪{p.price_ex_vat}" for p in group))
            for p in group:
                flags.append(Flag("E4", p.customer_id, key, p.price_ex_vat, f"סניפים עם ח.פ {tid}: {listing}."))
    return flags
```

- [ ] **Step 4: Run to verify it passes**

Expected: `Ran 15 tests … OK` (4 catalog + 11 prices).

- [ ] **Step 5: Commit**

```bash
cd /home/user/gt-factory-os && git add scripts/distributor-handoff/handoff/prices.py scripts/distributor-handoff/tests/test_prices.py
git commit -m "feat(distributor-handoff): price seeding rules and exceptions E1–E4"
```

---

### Task 5: Customer book rules

**Files:**
- Create: `scripts/distributor-handoff/handoff/customers.py`
- Test: `scripts/distributor-handoff/tests/test_customers.py`

**Interfaces:**
- Consumes: `CustomerRow`, `Flag`.
- Produces: `REGION_ORDER: dict[str, int]`; `normalize_city(s) -> str`; `region_for_city(city, zones) -> str | None`; `delivery_days_he(region, calendar) -> str | None`; `split_street_house(address1) -> tuple[str | None, str | None]`; `place_name_from_shopify(last_name) -> str | None`; `chain_and_type(client_type) -> tuple[str | None, str | None]`; `valid_tax_id(v) -> str | None`; `terms_he(code, semantics) -> str | None`; `assign_gt_numbers(rows, existing: dict[str, int]) -> None`; `build_customer_rows(active_ids, shopify, gi, lw, stats, zones, calendar, terms_semantics, form, existing) -> tuple[list[CustomerRow], list[Flag]]`; `gaps(row) -> list[str]`.

- [ ] **Step 1: Write the failing test**

`tests/test_customers.py`:
```python
import unittest
from datetime import date
from decimal import Decimal

from handoff import customers as C
from handoff.model import CustomerRow

ZONES = {"_comment": "x", "Center": ["תל אביב", "tel aviv", "רמת גן"], "North": ["חיפה"], "South": ["באר שבע"]}
CAL = {"calendar": {"sunday": "center", "monday": "center", "tuesday": "north", "wednesday": "south",
                    "thursday": "center", "friday": None, "saturday": None}}
SEM = {"30": {"kind": "eom_plus", "days": 30}, "0": {"kind": "immediate"}}


class ParsingTest(unittest.TestCase):
    def test_split_street_house(self):
        self.assertEqual(C.split_street_house("השיקמה 1"), ("השיקמה", "1"))
        self.assertEqual(C.split_street_house("דרך מנחם בגין 132"), ("דרך מנחם בגין", "132"))
        self.assertEqual(C.split_street_house("הרצל 12א"), ("הרצל", "12א"))
        self.assertEqual(C.split_street_house("קניון רמת אביב"), ("קניון רמת אביב", None))
        self.assertEqual(C.split_street_house(""), (None, None))

    def test_place_name(self):
        self.assertEqual(C.place_name_from_shopify('(קופי פוינט) גור את אפשטיין בע"מ'), "קופי פוינט")
        self.assertEqual(C.place_name_from_shopify('צייט פור ברוט בע"מ (קניון רמת אביב)'), "צייט פור ברוט — קניון רמת אביב")
        self.assertEqual(C.place_name_from_shopify('סאמר קפה בע"מ'), "סאמר קפה")

    def test_region_and_days(self):
        self.assertEqual(C.region_for_city("  Tel Aviv ", ZONES), "center")
        self.assertIsNone(C.region_for_city("אילת", ZONES))
        self.assertEqual(C.delivery_days_he("center", CAL), "ראשון · שני · חמישי")

    def test_tax_id(self):
        self.assertEqual(C.valid_tax_id("18"), "000000018")
        self.assertIsNone(C.valid_tax_id("000000019"))
        self.assertIsNone(C.valid_tax_id(None))

    def test_terms(self):
        self.assertEqual(C.terms_he(30, SEM), "שוטף + 30")
        self.assertEqual(C.terms_he(0, SEM), "מיידי")
        self.assertIsNone(C.terms_he(-1, SEM))


class NumbersTest(unittest.TestCase):
    def test_existing_kept_and_new_sorted_by_region_city_name(self):
        rows = [CustomerRow("c", region="north", city="חיפה", place_name="א"),
                CustomerRow("a", region="center", city="תל אביב", place_name="ב"),
                CustomerRow("b", region="center", city="רמת גן", place_name="ג")]
        C.assign_gt_numbers(rows, {"c": 1005})
        self.assertEqual({r.shopify_customer_id: r.gt_customer_no for r in rows}, {"c": 1005, "b": 1006, "a": 1007})


class BuildTest(unittest.TestCase):
    def test_precedence_sources_and_flags(self):
        shop = {"c1": {"lastName": '(קפה א) חברה בע"מ',
                       "defaultAddress": {"address1": "הרצל 5", "city": "תל אביב", "phone": "0501111111"},
                       "idn": {"value": "000000026"}, "ct": {"value": "בית קפה"}}}
        gi = {"c1": {"name": 'חברה בע"מ', "taxId": "000000018", "emails": ["acc@example.co.il"], "paymentTerms": 30,
                     "address": "הרצל 5", "city": "תל אביב", "contactPerson": "דנה", "phone": "0502222222"}}
        lw = {"c1": {"recipient_name": "יוסי", "phone": "0503333333", "notes": "כניסה אחורית"}}
        form = {"c1": {"kashrut": "badatz", "onsite_contact_name": "רון"}}
        existing = {"c1": CustomerRow("c1", gt_customer_no=1001, accounting_email="fixed@example.co.il",
                                      field_sources={"accounting_email": "manual"})}
        stats = {"c1": {"last_order_on": date(2026, 9, 1), "orders_per_month": Decimal("2.5")}}
        rows, flags = C.build_customer_rows(["c1"], shop, gi, lw, stats, ZONES, CAL, SEM, form, existing)
        r = rows[0]
        self.assertEqual(r.place_name, "קפה א")
        self.assertEqual((r.tax_id, r.field_sources["tax_id"]), ("000000018", "green_invoice"))
        self.assertEqual((r.accounting_email, r.field_sources["accounting_email"]), ("fixed@example.co.il", "manual"))
        self.assertEqual((r.onsite_contact_name, r.field_sources["onsite_contact_name"]), ("רון", "form"))
        self.assertEqual((r.onsite_contact_phone, r.field_sources["onsite_contact_phone"]), ("0503333333", "lionwheel"))
        self.assertEqual((r.region, r.delivery_days_he, r.payment_terms_he), ("center", "ראשון · שני · חמישי", "שוטף + 30"))
        self.assertEqual((r.street, r.house_number, r.business_type), ("הרצל", "5", "בית קפה"))
        self.assertEqual([f.code for f in flags], ["K2"])
        self.assertEqual(C.gaps(r), [])

    def test_gaps_name_missing_fields_and_unverified_terms(self):
        r = CustomerRow("c9", place_name="x", payment_terms_code=-1)
        g = C.gaps(r)
        self.assertIn("כשרות", g)
        self.assertIn("תנאי תשלום (קוד לא מאומת)", g)
```

- [ ] **Step 2: Run to verify it fails**

Expected: `ModuleNotFoundError: No module named 'handoff.customers'`.

- [ ] **Step 3: Implement `customers.py`**

```python
"""Customer book rules (spec §6): one row per branch, every field with its source."""
from __future__ import annotations

import re

from .model import CustomerRow, Flag

REGION_ORDER = {"center": 0, "north": 1, "south": 2}
DAY_HE = {"sunday": "ראשון", "monday": "שני", "tuesday": "שלישי", "wednesday": "רביעי",
          "thursday": "חמישי", "friday": "שישי", "saturday": "שבת"}
MANUAL_SOURCES = {"form", "manual"}
REQUIRED = {
    "place_name": "שם העסק", "legal_name": "שם משפטי", "tax_id": "ח.פ תקין", "invoice_address": "כתובת לחשבונית",
    "accounting_email": "מייל להנהלת חשבונות", "street": "רחוב", "house_number": "מספר בית", "city": "עיר",
    "region": "אזור חלוקה", "onsite_contact_name": "מי מקבל את הסחורה", "onsite_contact_phone": "טלפון בסניף",
    "kashrut": "כשרות",
}

_HOUSE = re.compile(r"(?<![\d/])(\d{1,4}[א-ת]?)(?![\d/])")
_PREFIX = re.compile(r"^\((?P<nick>[^)]+)\)\s*(?P<rest>.+)$")
_SUFFIX = re.compile(r"^(?P<rest>.+?)\s*\((?P<branch>[^)]+)\)$")
_LEGAL = re.compile(r'\s*בע["״]?מ\s*')


def normalize_city(s: str | None) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("־", "-")).strip().lower()


def region_for_city(city: str | None, zones: dict) -> str | None:
    c = normalize_city(city)
    if not c:
        return None
    for zone, cities in zones.items():
        if zone.startswith("_"):
            continue
        if c in {normalize_city(x) for x in cities}:
            return zone.lower()
    return None


def delivery_days_he(region: str | None, calendar: dict) -> str | None:
    days = [DAY_HE[d] for d, z in calendar["calendar"].items() if z and z == region]
    return " · ".join(days) or None


def split_street_house(address1: str | None) -> tuple[str | None, str | None]:
    if not address1 or not address1.strip():
        return None, None
    a = address1.strip()
    m = _HOUSE.search(a)
    if not m:
        return a, None
    street = a[:m.start()].strip(" ,-")
    return (street or a), m.group(1)


def place_name_from_shopify(last_name: str | None) -> str | None:
    """Store convention: '(nickname) legal name' or 'legal name (branch)'."""
    if not last_name or not last_name.strip():
        return None
    s = last_name.strip()
    if m := _PREFIX.match(s):
        return m.group("nick").strip()
    if m := _SUFFIX.match(s):
        return f"{_LEGAL.sub(' ', m.group('rest')).strip()} — {m.group('branch').strip()}"
    return _LEGAL.sub(" ", s).strip() or s


def chain_and_type(client_type: str | None) -> tuple[str | None, str | None]:
    if not client_type or not client_type.strip():
        return None, None
    ct = client_type.strip()
    return (ct[4:].strip(), None) if ct.startswith("רשת ") else (None, ct)


def valid_tax_id(v) -> str | None:
    """Israeli ח.פ / ע.מ check digit. Returns the 9-digit form, or None."""
    d = re.sub(r"\D", "", str(v or ""))
    if not d or len(d) > 9:
        return None
    d = d.zfill(9)
    total = 0
    for i, ch in enumerate(d):
        x = int(ch) * (1 if i % 2 == 0 else 2)
        total += x - 9 if x > 9 else x
    return d if total % 10 == 0 else None


def terms_he(code: int | None, semantics: dict[str, dict]) -> str | None:
    """Green Invoice payment-term code in words — only when its meaning was verified from invoices."""
    if code is None:
        return None
    s = semantics.get(str(code))
    if not s:
        return None
    days = s.get("days", 0)
    return {"immediate": "מיידי", "eom": "שוטף", "eom_plus": f"שוטף + {days}", "net": f"{days} יום"}[s["kind"]]


def _join_address(street: str | None, city: str | None) -> str | None:
    parts = [p.strip() for p in (street, city) if p and p.strip()]
    return ", ".join(parts) or None


def build_customer_rows(active_ids, shopify: dict, gi: dict, lw: dict, stats: dict, zones: dict, calendar: dict,
                        terms_semantics: dict, form: dict, existing: dict[str, CustomerRow]
                        ) -> tuple[list[CustomerRow], list[Flag]]:
    rows: list[CustomerRow] = []
    flags: list[Flag] = []
    for cid in sorted(active_ids):
        s, g, l, f, prev = shopify.get(cid, {}), gi.get(cid, {}), lw.get(cid, {}), form.get(cid, {}), existing.get(cid)
        r = CustomerRow(cid, gt_customer_no=prev.gt_customer_no if prev else None)

        def put(field: str, candidates: list[tuple[object, str]]) -> None:
            if prev and prev.field_sources.get(field) in MANUAL_SOURCES and getattr(prev, field) not in (None, ""):
                setattr(r, field, getattr(prev, field))
                r.field_sources[field] = prev.field_sources[field]
                return
            for value, source in candidates:
                if value not in (None, ""):
                    setattr(r, field, value)
                    r.field_sources[field] = source
                    return

        addr = s.get("defaultAddress") or {}
        street, house = split_street_house(addr.get("address1"))
        chain, btype = chain_and_type((s.get("ct") or {}).get("value"))
        gi_tax = valid_tax_id(g.get("taxId"))
        shop_tax = valid_tax_id((s.get("idn") or {}).get("value"))
        if gi_tax and shop_tax and gi_tax != shop_tax:
            flags.append(Flag("K2", cid, "tax_id", None, f"Green Invoice: {gi_tax} · שופיפיי: {shop_tax}"))

        put("place_name", [(f.get("place_name"), "form"),
                           (place_name_from_shopify(s.get("lastName") or s.get("displayName")), "shopify")])
        put("legal_name", [(g.get("name"), "green_invoice"), (s.get("lastName"), "shopify")])
        put("tax_id", [(gi_tax, "green_invoice"), (shop_tax, "shopify")])
        put("chain", [(chain, "shopify")])
        put("business_type", [(btype, "shopify")])
        put("invoice_address", [(_join_address(g.get("address"), g.get("city")), "green_invoice")])
        put("accounting_email", [(f.get("accounting_email"), "form"), ((g.get("emails") or [None])[0], "green_invoice")])
        put("payment_terms_code", [(g.get("paymentTerms"), "green_invoice")])
        r.payment_terms_he = terms_he(r.payment_terms_code, terms_semantics)
        put("street", [(f.get("street"), "form"), (street, "shopify")])
        put("house_number", [(f.get("house_number"), "form"), (house, "shopify")])
        put("city", [(f.get("city"), "form"), (addr.get("city"), "shopify")])
        put("delivery_notes", [(f.get("delivery_notes"), "form"), (l.get("notes"), "lionwheel")])
        put("onsite_contact_name", [(f.get("onsite_contact_name"), "form"), (l.get("recipient_name"), "lionwheel"),
                                    (g.get("contactPerson"), "green_invoice")])
        put("onsite_contact_phone", [(f.get("onsite_contact_phone"), "form"), (l.get("phone"), "lionwheel"),
                                     (g.get("phone"), "green_invoice"), (addr.get("phone"), "shopify")])
        put("receiving_restrictions", [(f.get("receiving_restrictions"), "form")])
        put("kashrut", [(f.get("kashrut"), "form")])
        r.region = region_for_city(r.city, zones)
        r.delivery_days_he = delivery_days_he(r.region, calendar) if r.region else None
        st = stats.get(cid, {})
        r.last_order_on, r.orders_per_month = st.get("last_order_on"), st.get("orders_per_month")
        rows.append(r)
    return rows, flags


def assign_gt_numbers(rows: list[CustomerRow], existing: dict[str, int]) -> None:
    """Existing numbers never change; new customers continue after the highest, sorted region → city → name."""
    taken = {n for n in existing.values() if n}
    for r in rows:
        if existing.get(r.shopify_customer_id):
            r.gt_customer_no = existing[r.shopify_customer_id]
    new = sorted((r for r in rows if r.gt_customer_no is None),
                 key=lambda r: (REGION_ORDER.get(r.region or "", 9), r.city or "", r.place_name or "", r.shopify_customer_id))
    nxt = max(taken | {1000}) + 1
    for r in new:
        while nxt in taken:
            nxt += 1
        if nxt > 9999:
            raise ValueError("GT customer numbers exhausted (4 digits)")
        r.gt_customer_no = nxt
        taken.add(nxt)
        nxt += 1


def gaps(r: CustomerRow) -> list[str]:
    missing = [label for f, label in REQUIRED.items() if getattr(r, f) in (None, "")]
    if r.payment_terms_code is not None and not r.payment_terms_he:
        missing.append("תנאי תשלום (קוד לא מאומת)")
    return missing
```

- [ ] **Step 4: Run to verify it passes**

Expected: `Ran 23 tests … OK`.

- [ ] **Step 5: Commit**

```bash
cd /home/user/gt-factory-os && git add scripts/distributor-handoff/handoff/customers.py scripts/distributor-handoff/tests/test_customers.py
git commit -m "feat(distributor-handoff): customer book rules, GT numbers, gaps"
```

---

### Task 6: Read-only source pulls — Shopify, Green Invoice, LionWheel

**Files:**
- Create: `scripts/distributor-handoff/handoff/{shopify.py,gi.py,lionwheel.py}`
- Test: `scripts/distributor-handoff/tests/{test_shopify.py,test_gi.py,test_lionwheel.py}`

**Interfaces:**
- Consumes: `Line`, `config.SHOPIFY_API_VERSION`.
- Produces:
  - `shopify.gql(query, variables) -> dict`; `pull_customers(dest) -> int`; `pull_variants(dest) -> int`; `run_bulk_orders(since: date, dest) -> int`; `parse_bulk_orders(path) -> tuple[list[Line], dict[str, dict], dict[str, int]]`; `order_stats(orders, today) -> dict[str, dict]`; `active_customer_ids(orders, customers, today, window_days) -> tuple[set[str], set[str]]`; `barcode_maps(variants) -> tuple[dict[str, str], dict[str, set[str]], dict[str, str]]`.
  - `gi.GreenInvoice().client(id) / .documents(client_id, from_date, to_date)`; `gi.TAX_INVOICE_TYPES`; `latest_tax_invoice(docs) -> dict | None`; `has_doc_discount(doc) -> bool`; `invoice_record(doc) -> dict`; `terms_semantics(samples: dict[str, list[tuple[date, date]]]) -> dict[str, dict]`.
  - `lionwheel.pull_tasks() -> list[dict]`; `by_customer(tasks, order_customer: dict[str, str]) -> dict[str, dict]`.

Observed live on 2026-09-24 (do not change without re-inspecting): Green Invoice `documents/search` returns `items` with `type` (305 tax invoice, 330 credit, 400 receipt), `documentDate`, `dueDate`, `number`, `client.id`, `income[] {catalogNum, price, quantity, vatType}`, `discount {type, amount, total}` — `total` alone is agorot rounding, a real discount has `amount > 0`. LionWheel `GET /api/v1/tasks.json?limit=300` returns `{tasks: [...]}` with `wp_order_id` = Shopify order name (`#GT…`), `destination_recipient_name`, `destination_phone`, `destination_floor`; `GET /api/v1/tasks/show/<id>.json` adds `notes`, `driver_note`.

- [ ] **Step 1: Write the failing tests**

`tests/test_shopify.py`:
```python
import json
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from handoff import shopify

ROWS = [
    {"id": "gid://shopify/Order/1", "name": "#GT1", "createdAt": "2026-09-01T08:00:00Z", "test": False,
     "cancelledAt": None, "customer": {"id": "C1"}},
    {"id": "gid://shopify/LineItem/11", "__parentId": "gid://shopify/Order/1", "sku": "GT-HIB-LOW-1L", "quantity": 6,
     "variant": {"id": "V1", "sku": "GT-HIB-LOW-1L", "barcode": "729001"},
     "discountedUnitPriceAfterAllDiscountsSet": {"shopMoney": {"amount": "58.5"}}},
    {"id": "gid://shopify/LineItem/12", "__parentId": "gid://shopify/Order/1", "sku": "SAMPLE", "quantity": 1,
     "variant": None, "discountedUnitPriceAfterAllDiscountsSet": {"shopMoney": {"amount": "0.0"}}},
    {"id": "gid://shopify/Order/2", "name": "#GT2", "createdAt": "2026-09-02T08:00:00Z", "test": False,
     "cancelledAt": "2026-09-02T09:00:00Z", "customer": {"id": "C1"}},
    {"id": "gid://shopify/LineItem/21", "__parentId": "gid://shopify/Order/2", "sku": "GT-HIB-LOW-1L", "quantity": 1,
     "variant": {"sku": "GT-HIB-LOW-1L"}, "discountedUnitPriceAfterAllDiscountsSet": {"shopMoney": {"amount": "65"}}},
    {"id": "gid://shopify/Order/3", "name": "#GT3", "createdAt": "2024-01-02T08:00:00Z", "test": False,
     "cancelledAt": None, "customer": {"id": "C2"}},
]


class ShopifyParseTest(unittest.TestCase):
    def setUp(self):
        self.path = Path(tempfile.mkdtemp()) / "orders.jsonl"
        self.path.write_text("\n".join(json.dumps(r) for r in ROWS), encoding="utf-8")

    def test_parse_bulk_orders(self):
        lines, orders, stats = shopify.parse_bulk_orders(self.path)
        self.assertEqual(len(lines), 1)
        ln = lines[0]
        self.assertEqual((ln.customer_id, ln.sku, ln.order_name, ln.qty, ln.net_unit), ("C1", "GT-HIB-LOW-1L", "#GT1", 6, Decimal("58.5")))
        self.assertEqual(stats, {"zero_price_or_qty": 1, "excluded_order": 1})
        self.assertEqual(len(orders), 3)

    def test_order_stats_and_active(self):
        _, orders, _ = shopify.parse_bulk_orders(self.path)
        st = shopify.order_stats(orders, date(2026, 9, 24))
        self.assertEqual((st["C1"]["last_order_on"], st["C1"]["orders_per_month"]), (date(2026, 9, 1), Decimal("0.2")))
        customers = [{"id": "C1", "ck": {"value": "uuid-1"}}, {"id": "C2", "ck": None}]
        active, unlinked = shopify.active_customer_ids(orders, customers, date(2026, 9, 24), 365)
        self.assertEqual((active, unlinked), ({"C1"}, set()))

    def test_barcode_maps(self):
        variants = [{"sku": "A", "barcode": "1", "product": {"featuredMedia": {"preview": {"image": {"url": "https://cdn/a.jpg"}}}}},
                    {"sku": "B", "barcode": "1", "product": {}}, {"sku": "", "barcode": "9"}]
        sku_bc, bc_skus, img = shopify.barcode_maps(variants)
        self.assertEqual((sku_bc, bc_skus, img), ({"A": "1", "B": "1"}, {"1": {"A", "B"}}, {"A": "https://cdn/a.jpg"}))
```

`tests/test_gi.py`:
```python
import unittest
from datetime import date, timedelta

from handoff import gi


class TermsTest(unittest.TestCase):
    def test_net_30(self):
        pairs = [(date(2026, 9, d), date(2026, 9, d) + timedelta(days=30)) for d in (3, 10, 17)]
        self.assertEqual(gi.terms_semantics({"30": pairs}), {"30": {"kind": "net", "days": 30}})

    def test_end_of_month_plus_30(self):
        pairs = [(date(2026, 9, d), date(2026, 10, 30)) for d in (3, 10, 17)]
        self.assertEqual(gi.terms_semantics({"30": pairs}), {"30": {"kind": "eom_plus", "days": 30}})

    def test_immediate(self):
        pairs = [(date(2026, 9, d), date(2026, 9, d)) for d in (3, 10, 17)]
        self.assertEqual(gi.terms_semantics({"0": pairs}), {"0": {"kind": "immediate"}})

    def test_too_little_evidence_stays_unmapped(self):
        self.assertEqual(gi.terms_semantics({"45": [(date(2026, 9, 3), date(2026, 10, 18))]}), {})


class DocumentTest(unittest.TestCase):
    def test_latest_tax_invoice_and_record(self):
        docs = [{"type": 400, "documentDate": "2026-09-20", "number": 9},
                {"type": 305, "documentDate": "2026-09-09", "number": 101, "discount": {"type": "sum", "amount": 0, "total": 0.2},
                 "income": [{"catalogNum": "729001", "price": 58.5, "quantity": 6}]},
                {"type": 305, "documentDate": "2026-09-01", "number": 90}]
        inv = gi.latest_tax_invoice(docs)
        self.assertEqual(inv["number"], 101)
        self.assertEqual(gi.invoice_record(inv), {"number": 101, "date": "2026-09-09", "discounted": False,
                                                  "lines": [{"code": "729001", "price": 58.5, "qty": 6}]})

    def test_real_discount_detected(self):
        self.assertTrue(gi.has_doc_discount({"discount": {"type": "sum", "amount": 50, "total": 50}}))
        self.assertFalse(gi.has_doc_discount({"discount": None}))
```

`tests/test_lionwheel.py`:
```python
import unittest

from handoff.lionwheel import by_customer


class LionWheelTest(unittest.TestCase):
    def test_newest_task_wins_and_notes_join(self):
        tasks = [
            {"id": 5, "wp_order_id": "#GT1", "destination_recipient_name": "יוסי", "destination_phone": "0501",
             "destination_floor": "2", "driver_note": "כניסה אחורית", "notes": None},
            {"id": 9, "wp_order_id": "#GT2", "destination_recipient_name": "רון", "destination_phone": "0502",
             "destination_floor": "", "driver_note": None, "notes": "להתקשר"},
            {"id": 7, "wp_order_id": "#GT3", "destination_recipient_name": "x"},
        ]
        got = by_customer(tasks, {"#GT1": "C2", "#GT2": "C1", "#GT3": None})
        self.assertEqual(got["C1"], {"recipient_name": "רון", "phone": "0502", "notes": "להתקשר"})
        self.assertEqual(got["C2"], {"recipient_name": "יוסי", "phone": "0501", "notes": "כניסה אחורית · קומה 2"})
        self.assertEqual(set(got), {"C1", "C2"})
```

- [ ] **Step 2: Run to verify they fail**

Expected: `ModuleNotFoundError` for `handoff.shopify`, `handoff.gi`, `handoff.lionwheel`.

- [ ] **Step 3: Implement `shopify.py`**

```python
"""Read-only Shopify pulls (Admin GraphQL) and pure parsers for them."""
from __future__ import annotations

import json
import os
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from .config import SHOPIFY_API_VERSION
from .model import Line

BULK_ORDERS = """{ orders(query: "created_at:>=%s") { edges { node { id name createdAt test cancelledAt customer { id }
  lineItems { edges { node { id sku quantity variant { id sku barcode }
  discountedUnitPriceAfterAllDiscountsSet { shopMoney { amount } } } } } } } } }"""

CUSTOMERS = """query($after: String) { customers(first: 100, after: $after, sortKey: ID) { pageInfo { hasNextPage endCursor }
  nodes { id displayName lastName tags note numberOfOrders createdAt
  defaultAddress { address1 address2 city zip phone company }
  idn: metafield(namespace: "custom", key: "id_nomber") { value }
  ck: metafield(namespace: "custom", key: "client_key") { value }
  ct: metafield(namespace: "custom", key: "client_type") { value } } } }"""

VARIANTS = """query($after: String) { productVariants(first: 250, after: $after) { pageInfo { hasNextPage endCursor }
  nodes { id sku barcode title price product { id title status featuredMedia { preview { image { url } } } } } } }"""

POLL = "{ currentBulkOperation(type: QUERY) { id status errorCode objectCount url } }"


def gql(query: str, variables: dict | None = None) -> dict:
    url = f"https://{os.environ['SHOPIFY_STORE_DOMAIN']}/admin/api/{SHOPIFY_API_VERSION}/graphql.json"
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    for _ in range(8):
        req = urllib.request.Request(url, data=body, headers={
            "Content-Type": "application/json", "X-Shopify-Access-Token": os.environ["SHOPIFY_ADMIN_API_TOKEN"]})
        with urllib.request.urlopen(req, timeout=120) as resp:
            j = json.load(resp)
        if any((e.get("extensions") or {}).get("code") == "THROTTLED" for e in j.get("errors") or []):
            time.sleep(2)
            continue
        if j.get("errors"):
            raise RuntimeError(json.dumps(j["errors"], ensure_ascii=False)[:400])
        return j["data"]
    raise RuntimeError("Shopify: throttled 8 times in a row")


def _paged(query: str, root: str) -> list[dict]:
    out: list[dict] = []
    after = None
    while True:
        data = gql(query, {"after": after})[root]
        out.extend(data["nodes"])
        if not data["pageInfo"]["hasNextPage"]:
            return out
        after = data["pageInfo"]["endCursor"]


def pull_customers(dest: Path) -> int:
    rows = _paged(CUSTOMERS, "customers")
    dest.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return len(rows)


def pull_variants(dest: Path) -> int:
    rows = _paged(VARIANTS, "productVariants")
    dest.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return len(rows)


def run_bulk_orders(since: date, dest: Path) -> int:
    """One bulk export of orders created since `since`; waits for any running bulk query first."""
    cur = gql(POLL)["currentBulkOperation"]
    while cur and cur["status"] in ("CREATED", "RUNNING"):
        time.sleep(15)
        cur = gql(POLL)["currentBulkOperation"]
    res = gql("mutation($q: String!) { bulkOperationRunQuery(query: $q) { bulkOperation { id } userErrors { message } } }",
              {"q": BULK_ORDERS % since.isoformat()})["bulkOperationRunQuery"]
    if res["userErrors"]:
        raise RuntimeError(json.dumps(res["userErrors"], ensure_ascii=False))
    while True:
        time.sleep(15)
        cur = gql(POLL)["currentBulkOperation"]
        if cur["status"] not in ("CREATED", "RUNNING"):
            break
    if cur["status"] != "COMPLETED" or not cur.get("url"):
        raise RuntimeError(f"bulk operation ended {cur['status']} {cur.get('errorCode')}")
    with urllib.request.urlopen(cur["url"], timeout=300) as resp:
        dest.write_bytes(resp.read())
    return int(cur["objectCount"])


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def parse_bulk_orders(path: Path) -> tuple[list[Line], dict[str, dict], dict[str, int]]:
    """(purchased lines, orders by id, exclusion counts). Drops test/cancelled/no-customer, empty SKU, price or qty ≤ 0."""
    orders: dict[str, dict] = {}
    items: list[dict] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        obj = json.loads(raw)
        if "/Order/" in obj["id"]:
            orders[obj["id"]] = obj
        elif "/LineItem/" in obj["id"]:
            items.append(obj)
    stats: Counter = Counter()
    lines: list[Line] = []
    for li in items:
        o = orders.get(li.get("__parentId", ""))
        if not o or o.get("test") or o.get("cancelledAt") or not (o.get("customer") or {}).get("id"):
            stats["excluded_order"] += 1
            continue
        sku = ((li.get("variant") or {}).get("sku") or li.get("sku") or "").strip()
        amount = ((li.get("discountedUnitPriceAfterAllDiscountsSet") or {}).get("shopMoney") or {}).get("amount")
        price = Decimal(str(amount)) if amount is not None else Decimal("0")
        qty = int(li.get("quantity") or 0)
        if price <= 0 or qty <= 0:
            stats["zero_price_or_qty"] += 1
            continue
        if not sku:
            stats["no_sku"] += 1
            continue
        lines.append(Line(o["customer"]["id"], sku, o["name"], _ts(o["createdAt"]), qty, price))
    return lines, orders, dict(stats)


def _live(o: dict) -> str | None:
    cid = (o.get("customer") or {}).get("id")
    return cid if cid and not o.get("test") and not o.get("cancelledAt") else None


def order_stats(orders: dict[str, dict], today: date) -> dict[str, dict]:
    """customer_id -> {'last_order_on', 'orders_per_month' (last 183 days / 6, one decimal)}."""
    per: dict[str, list[date]] = defaultdict(list)
    for o in orders.values():
        cid = _live(o)
        if cid:
            per[cid].append(_ts(o["createdAt"]).date())
    since = today - timedelta(days=183)
    return {cid: {"last_order_on": max(ds),
                  "orders_per_month": (Decimal(sum(1 for d in ds if d >= since)) / 6).quantize(Decimal("0.1"))}
            for cid, ds in per.items()}


def active_customer_ids(orders: dict[str, dict], customers: list[dict], today: date, window_days: int
                        ) -> tuple[set[str], set[str]]:
    """(active customers linked to Green Invoice, active customers without the link)."""
    since = today - timedelta(days=window_days)
    ordered = {_live(o) for o in orders.values() if _live(o) and _ts(o["createdAt"]).date() >= since}
    linked = {c["id"] for c in customers if ((c.get("ck") or {}).get("value") or "").strip()}
    return ordered & linked, ordered - linked


def barcode_maps(variants: list[dict]) -> tuple[dict[str, str], dict[str, set[str]], dict[str, str]]:
    """(sku -> barcode, barcode -> {skus}, sku -> product image URL)."""
    sku_bc: dict[str, str] = {}
    bc_skus: dict[str, set[str]] = defaultdict(set)
    img: dict[str, str] = {}
    for v in variants:
        sku, bc = (v.get("sku") or "").strip(), (v.get("barcode") or "").strip()
        if not sku:
            continue
        if bc:
            sku_bc.setdefault(sku, bc)
            bc_skus[bc].add(sku)
        url = (((((v.get("product") or {}).get("featuredMedia") or {}).get("preview") or {}).get("image") or {}).get("url"))
        if url:
            img.setdefault(sku, url)
    return sku_bc, dict(bc_skus), img
```

- [ ] **Step 4: Implement `gi.py`**

```python
"""Read-only Green Invoice pulls. Never prints the secret or the token."""
from __future__ import annotations

import calendar
import json
import os
import urllib.request
from collections import Counter
from datetime import date

TAX_INVOICE_TYPES = {305, 320}


class GreenInvoice:
    def __init__(self) -> None:
        self.base = os.environ.get("GREENINVOICE_API_BASE_URL", "https://api.greeninvoice.co.il/api/v1/").rstrip("/") + "/"
        self._token: str | None = None

    def _call(self, method: str, path: str, body: dict | None = None, auth: bool = True) -> dict:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if auth:
            headers["Authorization"] = f"Bearer {self.token()}"
        req = urllib.request.Request(self.base + path, method=method, headers=headers,
                                     data=json.dumps(body).encode() if body is not None else None)
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)

    def token(self) -> str:
        if not self._token:
            self._token = self._call("POST", "account/token", {"id": os.environ["GREENINVOICE_KEY_ID"],
                                                               "secret": os.environ["GREENINVOICE_SECRET"]}, auth=False)["token"]
        return self._token

    def client(self, client_id: str) -> dict:
        return self._call("GET", f"clients/{client_id}")

    def documents(self, client_id: str, from_date: date, to_date: date) -> list[dict]:
        res = self._call("POST", "documents/search", {"clientId": client_id, "fromDate": from_date.isoformat(),
                                                      "toDate": to_date.isoformat(), "pageSize": 50})
        return [d for d in res.get("items", []) if (d.get("client") or {}).get("id") == client_id]


def latest_tax_invoice(docs: list[dict]) -> dict | None:
    invoices = [d for d in docs if d.get("type") in TAX_INVOICE_TYPES]
    return max(invoices, key=lambda d: (d.get("documentDate") or "", d.get("number") or 0)) if invoices else None


def has_doc_discount(doc: dict) -> bool:
    """A real document-level discount. discount.total alone is agorot rounding (observed 2026-09-24)."""
    disc = doc.get("discount")
    return isinstance(disc, dict) and float(disc.get("amount") or 0) > 0


def invoice_record(doc: dict) -> dict:
    return {"number": doc.get("number"), "date": doc.get("documentDate"), "discounted": has_doc_discount(doc),
            "lines": [{"code": str(it.get("catalogNum") or "").strip(), "price": it.get("price"), "qty": it.get("quantity")}
                      for it in doc.get("income") or []]}


def _end_of_month(d: date) -> date:
    return d.replace(day=calendar.monthrange(d.year, d.month)[1])


def terms_semantics(samples: dict[str, list[tuple[date, date]]]) -> dict[str, dict]:
    """code -> verified meaning from (document date, due date) pairs. Needs ≥3 invoices, ≥80% agreement, no tie."""
    out: dict[str, dict] = {}
    for code, pairs in samples.items():
        if len(pairs) < 3:
            continue
        cands: Counter = Counter()
        for d, due in pairs:
            cands[("net", (due - d).days)] += 1
            eom = _end_of_month(d)
            if due >= eom:
                cands[("eom_plus", (due - eom).days)] += 1
        ranked = cands.most_common(2)
        (kind, days), n = ranked[0]
        if n / len(pairs) < 0.8 or (len(ranked) > 1 and ranked[1][1] == n):
            continue
        if kind == "net" and days == 0:
            out[code] = {"kind": "immediate"}
        elif kind == "eom_plus" and days == 0:
            out[code] = {"kind": "eom"}
        else:
            out[code] = {"kind": kind, "days": days}
    return out
```

- [ ] **Step 5: Implement `lionwheel.py`**

```python
"""Read-only LionWheel pull: open delivery tasks (the documented list endpoint) + task detail for notes."""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request


def _get(path: str, **params) -> dict:
    base = os.environ.get("LIONWHEEL_BASE_URL", "https://members.lionwheel.com")
    query = urllib.parse.urlencode({"key": os.environ["LIONWHEEL_API_KEY"], **params})
    with urllib.request.urlopen(f"{base}{path}?{query}", timeout=60) as resp:
        return json.load(resp)


def pull_tasks() -> list[dict]:
    tasks = _get("/api/v1/tasks.json", limit="300").get("tasks", [])
    for t in tasks:
        detail = _get(f"/api/v1/tasks/show/{t['id']}.json")
        d = detail.get("task", detail)
        t["notes"], t["driver_note"] = d.get("notes"), d.get("driver_note")
    return tasks


def by_customer(tasks: list[dict], order_customer: dict[str, str | None]) -> dict[str, dict]:
    """customer_id -> newest task's recipient, phone and delivery notes (tasks link by Shopify order name)."""
    out: dict[str, dict] = {}
    for t in sorted(tasks, key=lambda t: t.get("id") or 0, reverse=True):
        cid = order_customer.get((t.get("wp_order_id") or "").strip())
        if not cid or cid in out:
            continue
        notes = [str(n).strip() for n in (t.get("driver_note"), t.get("notes")) if n and str(n).strip()]
        floor = str(t.get("destination_floor") or "").strip()
        if floor:
            notes.append(f"קומה {floor}")
        out[cid] = {"recipient_name": (t.get("destination_recipient_name") or "").strip() or None,
                    "phone": (t.get("destination_phone") or "").strip() or None,
                    "notes": " · ".join(dict.fromkeys(notes)) or None}
    return out
```

- [ ] **Step 6: Run to verify they pass**

Expected: `Ran 33 tests … OK`.

- [ ] **Step 7: Commit**

```bash
cd /home/user/gt-factory-os && git add scripts/distributor-handoff/handoff/shopify.py scripts/distributor-handoff/handoff/gi.py scripts/distributor-handoff/handoff/lionwheel.py scripts/distributor-handoff/tests/test_shopify.py scripts/distributor-handoff/tests/test_gi.py scripts/distributor-handoff/tests/test_lionwheel.py
git commit -m "feat(distributor-handoff): read-only Shopify, Green Invoice and LionWheel pulls"
```

---

### Task 7: Database I/O, gates, Tom's review page, CLI (pull · seed · gates · review · decide)

**Files:**
- Create: `scripts/distributor-handoff/handoff/{db.py,gates.py,review.py}`, `scripts/distributor-handoff/run.py`
- Test: `scripts/distributor-handoff/tests/{test_gates.py,test_review.py}`

**Interfaces:**
- Consumes: everything from Tasks 3–6.
- Produces:
  - `db.connect()`; `db.BOOK_COLUMNS`; `load_book(conn) -> dict[str, CustomerRow]`; `upsert_list_prices(conn, rows) -> int`; `upsert_customer_book(conn, rows) -> int`; `current_prices(conn) -> dict[tuple[str, str], Decimal]`; `insert_seed_prices(conn, proposals, recorded_by) -> int`; `record_decisions(conn, decisions, recorded_by, today) -> int`; `set_manual_fields(conn, items) -> int`; `price_matrix(conn) -> list[dict]`; `list_prices(conn) -> list[dict]`; `whatsapp_phones(conn) -> dict[str, str]`.
  - `gates.g1_invoice_match(prices, invoices, barcode_to_skus) -> tuple[int, list[Flag]]`; `g2_completeness(rows, general_counts, general_total) -> list[str]`; `g3_open(flags, decided_ids) -> list[Flag]`; `g4_integrity(db_ids, excel_ids, pdf_ids) -> list[str]`; `GATED_CODES`.
  - `review.review_html(flags, names, gap_counts) -> str`.
  - `run.py` helpers `load_flags(path) -> list[Flag]`, `save_flags(path, flags)`.

- [ ] **Step 1: Write the failing tests**

`tests/test_gates.py`:
```python
import unittest
from decimal import Decimal

from handoff import gates
from handoff.model import CustomerRow, Flag


class G1Test(unittest.TestCase):
    def test_match_mismatch_unknown_and_discounted(self):
        prices = {("c1", "GT-HIB-LOW-1L"): Decimal("58.50"), ("c1", "GT-ODK-MAN-1"): Decimal("52.00")}
        barcodes = {"729001": {"GT-HIB-LOW-1L"}, "8330": {"GT-ODK-MAN-1"}}
        invoices = {
            "c1": {"number": 101, "date": "2026-09-09", "discounted": False, "lines": [
                {"code": "729001", "price": 58.5, "qty": 6}, {"code": "8330", "price": 56, "qty": 3},
                {"code": "999", "price": 1, "qty": 1}]},
            "c2": {"number": 102, "date": "2026-09-09", "discounted": True, "lines": [{"code": "729001", "price": 50, "qty": 1}]},
        }
        checked, flags = gates.g1_invoice_match(prices, invoices, barcodes)
        self.assertEqual(checked, 2)
        self.assertEqual(sorted((f.customer_id, f.key) for f in flags),
                         [("c1", "999"), ("c1", "GT-ODK-MAN-1"), ("c2", "invoice-102")])
        self.assertEqual({f.code for f in flags}, {"E5"})


class G2G3G4Test(unittest.TestCase):
    def test_g2_names_gaps_and_short_price_rows(self):
        ok = CustomerRow("a", gt_customer_no=1001, place_name="א", legal_name="א", tax_id="000000018", invoice_address="x",
                         accounting_email="a@example.co.il", street="s", house_number="1", city="c", region="center",
                         onsite_contact_name="n", onsite_contact_phone="050", kashrut="badatz")
        bad = CustomerRow("b", gt_customer_no=1002, place_name="ב")
        problems = gates.g2_completeness([ok, bad], {"a": 40, "b": 39}, 40)
        self.assertEqual(len(problems), 2)
        self.assertTrue(all(p.startswith("1002") for p in problems))

    def test_g3_open_flags(self):
        f1 = Flag("E1", "a", "TEA_1L", Decimal("58.50"), "x")
        f2 = Flag("K1", "a", "kashrut", None, "x")
        self.assertEqual(gates.g3_open([f1, f2], set()), [f1])
        self.assertEqual(gates.g3_open([f1, f2], {f1.id}), [])

    def test_g4_duplicates_missing_extra(self):
        problems = gates.g4_integrity(["a", "b", "c"], ["a", "a", "b"], ["a", "b", "c", "d"])
        self.assertEqual(len(problems), 3)
```

`tests/test_review.py`:
```python
import unittest
from decimal import Decimal

from handoff.model import Flag
from handoff.review import review_html


class ReviewTest(unittest.TestCase):
    def test_sections_order_and_escaping(self):
        flags = [Flag("E3", "c1", "GT-ODK-MAN-1", Decimal("70.00"), "משלם ₪70", Decimal("840")),
                 Flag("E1", "c2", "TEA_1L", Decimal("61.00"), "<b>x</b>", Decimal("3000"))]
        html = review_html(flags, {"c1": "קפה <א>", "c2": "קפה ב"}, {"כשרות": 12})
        self.assertLess(html.index("מחירי תה שונים בין טעמים"), html.index("משלם יותר מהמחירון הכללי"))
        self.assertIn("קפה &lt;א&gt;", html)
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", html)
        self.assertNotIn("לא תואם לחשבונית האחרונה", html)
        self.assertIn("כשרות", html)
```

- [ ] **Step 2: Run to verify they fail**

Expected: `ModuleNotFoundError` for `handoff.gates` and `handoff.review`.

- [ ] **Step 3: Implement `gates.py`**

```python
"""Gates G1–G4 (spec §8). Nothing leaves GT until all pass."""
from __future__ import annotations

from collections import Counter
from decimal import Decimal

from .customers import gaps
from .model import CustomerRow, Flag

GATED_CODES = {"E1", "E2", "E3", "E4", "E5", "C1", "K2", "K3"}
TOLERANCE = Decimal("0.01")


def g1_invoice_match(prices: dict[tuple[str, str], Decimal], invoices: dict[str, dict],
                     barcode_to_skus: dict[str, set[str]]) -> tuple[int, list[Flag]]:
    """Every line on each customer's latest tax invoice must equal the book price (barcode → SKU)."""
    checked, flags = 0, []
    for cust, inv in sorted(invoices.items()):
        if inv.get("discounted"):
            flags.append(Flag("E5", cust, f"invoice-{inv['number']}", None,
                              f"בחשבונית {inv['number']} יש הנחה כללית — בודקים ידנית."))
            continue
        for ln in inv["lines"]:
            code = str(ln["code"]).strip()
            skus = barcode_to_skus.get(code) or {code}
            book = {s: prices[(cust, s)] for s in sorted(skus) if (cust, s) in prices}
            if not book:
                flags.append(Flag("E5", cust, code or "?", None,
                                  f"שורה בחשבונית {inv['number']} (קוד {code or 'ריק'}) לא מזוהה כמוצר בספר."))
                continue
            checked += 1
            inv_price = Decimal(str(ln["price"]))
            if not any(abs(p - inv_price) <= TOLERANCE for p in book.values()):
                sku, p = next(iter(book.items()))
                flags.append(Flag("E5", cust, sku, p, f"בספר ₪{p}, בחשבונית {inv['number']} מ־{inv['date']}: ₪{inv_price}."))
    return checked, flags


def g2_completeness(rows: list[CustomerRow], general_counts: dict[str, int], general_total: int) -> list[str]:
    problems = []
    for r in sorted(rows, key=lambda r: r.gt_customer_no or 0):
        missing = gaps(r)
        if missing:
            problems.append(f"{r.gt_customer_no} {r.place_name or ''}: חסר {', '.join(missing)}")
        have = general_counts.get(r.shopify_customer_id, 0)
        if have < general_total:
            problems.append(f"{r.gt_customer_no} {r.place_name or ''}: חסרים מחירים ({have}/{general_total})")
    return problems


def g3_open(flags: list[Flag], decided_ids: set[str]) -> list[Flag]:
    return [f for f in flags if f.code in GATED_CODES and f.id not in decided_ids]


def g4_integrity(db_ids: list[str], excel_ids: list[str], pdf_ids: list[str]) -> list[str]:
    problems = []
    for name, ids in (("Excel", excel_ids), ("PDF", pdf_ids)):
        dup = sorted(i for i, n in Counter(ids).items() if n > 1)
        if dup:
            problems.append(f"{name}: {len(dup)} לקוחות מופיעים יותר מפעם אחת")
        missing = set(db_ids) - set(ids)
        if missing:
            problems.append(f"{name}: חסרים {len(missing)} לקוחות")
        extra = set(ids) - set(db_ids)
        if extra:
            problems.append(f"{name}: {len(extra)} לקוחות שלא בספר")
    return problems
```

- [ ] **Step 4: Implement `review.py`**

```python
"""Tom's exception page — an HTML file sent to Tom, never published."""
from __future__ import annotations

import html

from . import copy_he as T
from .brand import font_face_css, tokens_css
from .model import Flag

ORDER = ["E1", "E2", "E3", "E4", "E5", "C1", "K2", "K3"]

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Heebo',sans-serif;color:var(--ink);background:var(--paper);padding:20px;line-height:1.5}
header{max-width:1100px;margin:0 auto 18px}
h1{font-family:'Rubik';font-weight:700;font-size:26px;color:var(--green)}
.how{margin-top:6px;font-size:16px;font-weight:500}
.gaps{margin-top:8px;color:var(--muted);font-size:14px}
section{max-width:1100px;margin:0 auto 22px;background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px;overflow-x:auto}
h2{font-family:'Rubik';font-weight:600;font-size:19px}
h2 small{display:inline-block;margin-right:8px;padding:0 9px;border-radius:12px;background:var(--coral);color:#fff;font-size:13px}
.why{color:var(--muted);margin:4px 0 10px;font-size:14px}
table{width:100%;border-collapse:collapse;font-size:14px}
th{text-align:right;color:var(--muted);font-weight:500;padding:6px;border-bottom:1px solid var(--line)}
td{padding:7px 6px;border-bottom:1px solid var(--line);vertical-align:top}
tr:nth-child(even) td{background:var(--wash)}
td.p{font-family:'Rubik';font-weight:600;white-space:nowrap}
td.w{color:var(--muted);white-space:nowrap}
"""


def _money(x) -> str:
    return "—" if x is None else f"₪{x}"


def review_html(flags: list[Flag], names: dict[str, str], gap_counts: dict[str, int]) -> str:
    esc = html.escape
    sections = []
    for code in ORDER:
        rows = sorted((f for f in flags if f.code == code), key=lambda f: (-f.weight_ils, names.get(f.customer_id, ""), f.key))
        if not rows:
            continue
        head = "".join(f"<th>{esc(h)}</th>" for h in T.REVIEW_HEADERS)
        body = "".join(
            f"<tr><td>{esc(names.get(f.customer_id, '—') if f.customer_id else '—')}</td><td dir='ltr'>{esc(f.key)}</td>"
            f"<td class='p'><span dir='ltr'>{esc(_money(f.proposed))}</span></td><td>{esc(f.detail_he)}</td>"
            f"<td class='w'><span dir='ltr'>{'—' if not f.weight_ils else f'₪{f.weight_ils:,.0f}'}</span></td></tr>"
            for f in rows)
        sections.append(f"<section><h2>{esc(T.FLAG_TITLES[code])}<small>{len(rows)}</small></h2>"
                        f"<p class='why'>{esc(T.FLAG_WHY[code])}</p><table><thead><tr>{head}</tr></thead>"
                        f"<tbody>{body}</tbody></table></section>")
    gaps = " · ".join(f"{esc(k)}: {v}" for k, v in sorted(gap_counts.items(), key=lambda kv: -kv[1]))
    return (f"<!doctype html><html lang='he' dir='rtl'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'><title>{esc(T.REVIEW_TITLE)}</title>"
            f"<style>{tokens_css()}{font_face_css()}{CSS}</style></head><body><header><h1>{esc(T.REVIEW_TITLE)}</h1>"
            f"<p class='how'>{esc(T.REVIEW_HOW)}</p><p class='gaps'>{esc(T.REVIEW_GAPS)}: {gaps or '0'}</p></header>"
            f"{''.join(sections)}</body></html>")
```

- [ ] **Step 5: Implement `db.py`**

```python
"""Postgres I/O for sales_core (spec §5–§6). Uses DATABASE_URL. Writes are idempotent; prices are append-only."""
from __future__ import annotations

import os
from datetime import date
from decimal import Decimal

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .model import CustomerRow, ListPrice, Proposal

BOOK_COLUMNS = ("shopify_customer_id", "gt_customer_no", "place_name", "legal_name", "tax_id", "chain", "business_type",
                "invoice_address", "accounting_email", "payment_terms_code", "payment_terms_he", "street", "house_number",
                "city", "delivery_notes", "region", "delivery_days_he", "onsite_contact_name", "onsite_contact_phone",
                "receiving_restrictions", "kashrut", "last_order_on", "orders_per_month", "field_sources", "active")
MANUAL_FIELDS = set(BOOK_COLUMNS) - {"shopify_customer_id", "gt_customer_no", "field_sources", "active"}


def connect() -> psycopg.Connection:
    return psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)


def load_book(conn) -> dict[str, CustomerRow]:
    with conn.cursor() as cur:
        cur.execute(f"select {', '.join(BOOK_COLUMNS)} from sales_core.customer_book")
        return {r["shopify_customer_id"]: CustomerRow(**r) for r in cur.fetchall()}


def upsert_list_prices(conn, rows: list[ListPrice]) -> int:
    with conn.cursor() as cur:
        cur.executemany(
            """insert into sales_core.list_price
                 (sku, name_he, size_label, family, barcode, price_ex_vat, general, active, source, verified_on, updated_at)
               values (%s, %s, %s, %s, %s, %s, %s, true, %s, %s, now())
               on conflict (sku) do update set name_he = excluded.name_he, size_label = excluded.size_label,
                 family = excluded.family, barcode = excluded.barcode, price_ex_vat = excluded.price_ex_vat,
                 general = excluded.general, active = true, source = excluded.source,
                 verified_on = excluded.verified_on, updated_at = now()""",
            [(r.sku, r.name_he, r.size_label, r.family, r.barcode, r.price_ex_vat, r.general, r.source, r.verified_on)
             for r in rows])
        cur.execute("update sales_core.list_price set active = false, updated_at = now() where not (sku = any(%s))",
                    ([r.sku for r in rows],))
    return len(rows)


def upsert_customer_book(conn, rows: list[CustomerRow]) -> int:
    cols = ", ".join(BOOK_COLUMNS)
    marks = ", ".join(["%s"] * len(BOOK_COLUMNS))
    updates = ", ".join(f"{c} = excluded.{c}" for c in BOOK_COLUMNS if c != "shopify_customer_id")
    with conn.cursor() as cur:
        cur.executemany(
            f"insert into sales_core.customer_book ({cols}, updated_at) values ({marks}, now()) "
            f"on conflict (shopify_customer_id) do update set {updates}, updated_at = now()",
            [tuple(Jsonb(r.field_sources) if c == "field_sources" else getattr(r, c) for c in BOOK_COLUMNS) for r in rows])
    return len(rows)


def current_prices(conn) -> dict[tuple[str, str], Decimal]:
    with conn.cursor() as cur:
        cur.execute("""select distinct on (shopify_customer_id, price_key) shopify_customer_id, price_key, price_ex_vat
                         from sales_core.customer_price order by shopify_customer_id, price_key, seq desc""")
        return {(r["shopify_customer_id"], r["price_key"]): r["price_ex_vat"] for r in cur.fetchall()}


def _insert_prices(conn, rows: list[Proposal], recorded_by: str) -> None:
    with conn.cursor() as cur:
        cur.executemany(
            """insert into sales_core.customer_price
                 (shopify_customer_id, price_key, price_ex_vat, basis, evidence, effective_from, recorded_by)
               values (%s, %s, %s, %s, %s, %s, %s)""",
            [(p.customer_id, p.price_key, p.price_ex_vat, p.basis, p.evidence, p.effective_from, recorded_by) for p in rows])


def insert_seed_prices(conn, proposals: list[Proposal], recorded_by: str) -> int:
    """First fill only (spec §5.2): a key that already has a price is never re-seeded."""
    existing = current_prices(conn)
    todo = [p for p in proposals if (p.customer_id, p.price_key) not in existing]
    _insert_prices(conn, todo, recorded_by)
    return len(todo)


def record_decisions(conn, decisions: list[dict], recorded_by: str, today: date) -> int:
    rows = [Proposal(d["customer_id"], d["price_key"], Decimal(str(d["price_ex_vat"])), "tom_decision", d["note"], today)
            for d in decisions]
    _insert_prices(conn, rows, recorded_by)
    return len(rows)


def set_manual_fields(conn, items: list[dict]) -> int:
    with conn.cursor() as cur:
        for it in items:
            field = it["field"]
            if field not in MANUAL_FIELDS:
                raise ValueError(f"not a manual field: {field}")
            cur.execute(f"update sales_core.customer_book set {field} = %s, "
                        f"field_sources = field_sources || jsonb_build_object(%s::text, 'manual'), updated_at = now() "
                        f"where shopify_customer_id = %s", (it["value"], field, it["customer_id"]))
    return len(items)


def price_matrix(conn) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("select * from sales_core.v_customer_price order by gt_customer_no, sku")
        return cur.fetchall()


def list_prices(conn) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("select * from sales_core.list_price order by sku")
        return cur.fetchall()


def whatsapp_phones(conn) -> dict[str, str]:
    """shopify_customer_id -> the WhatsApp number the customer orders from (newest mapping wins)."""
    with conn.cursor() as cur:
        cur.execute("""select shopify_customer_id, wa_phone from order_intake.wa_customer_map
                        where shopify_customer_id is not null and wa_phone is not null order by updated_at""")
        out = {}
        for r in cur.fetchall():
            cid = r["shopify_customer_id"]
            cid = cid if cid.startswith("gid://") else f"gid://shopify/Customer/{cid}"
            out[cid] = r["wa_phone"]
        return out
```

- [ ] **Step 6: Implement `run.py`**

```python
#!/usr/bin/env python3
"""Ice Dream handoff — command line. Run from scripts/distributor-handoff with .venv/bin/python.

  pull              Shopify + Green Invoice + LionWheel → raw/ (read-only)
  seed              list prices, customer book, first-fill prices → DB; flags → out/flags.json
  gates [--g1-only] G1–G3; E5 flags replace the previous ones; exit 1 on any failure
  review            out/review.html for Tom
  decide FILE       apply Tom's decisions (price rows, manual fields, acknowledgements)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from handoff import catalog, customers, db, gates, gi, lionwheel, prices, review, shopify
from handoff.config import (CATALOG_TRUTH, DISCONTINUED_EQUIV, OUT, PRICING_TSV, RAW, RECORDED_BY, ROUTE_CALENDAR,
                            WINDOW_DAYS, ZONES)
from handoff.model import Flag


def _j(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def load_flags(path: Path) -> list[Flag]:
    out = []
    for f in _j(path):
        out.append(Flag(f["code"], f["customer_id"], f["key"],
                        None if f["proposed"] in (None, "None") else Decimal(str(f["proposed"])),
                        f["detail_he"], Decimal(str(f.get("weight_ils") or "0"))))
    return out


def save_flags(path: Path, flags: list[Flag]) -> None:
    _dump(path, [asdict(f) | {"id": f.id} for f in flags])


def _decided_ids() -> set[str]:
    p = OUT / "decisions.json"
    return {d["id"] for d in _j(p)} if p.exists() else set()


def cmd_pull(args) -> int:
    RAW.mkdir(exist_ok=True)
    today = date.today()
    print(f"orders (bulk objects): {shopify.run_bulk_orders(today - timedelta(days=730), RAW / 'orders.jsonl')}")
    print(f"customers: {shopify.pull_customers(RAW / 'customers.json')}")
    print(f"variants: {shopify.pull_variants(RAW / 'variants.json')}")
    _, orders, _ = shopify.parse_bulk_orders(RAW / "orders.jsonl")
    custs = _j(RAW / "customers.json")
    active, _ = shopify.active_customer_ids(orders, custs, today, WINDOW_DAYS)
    links = {c["id"]: c["ck"]["value"].strip() for c in custs if c["id"] in active}
    client = gi.GreenInvoice()
    clients, invoices, samples = {}, {}, {}
    for cid, gid in sorted(links.items()):
        try:
            clients[cid] = client.client(gid)
            docs = client.documents(gid, today - timedelta(days=365), today)
        except Exception as e:  # recorded, never silent: becomes a K3 flag at seed
            clients[cid] = {"error": str(e)[:200]}
            continue
        inv = gi.latest_tax_invoice(docs)
        if inv:
            invoices[cid] = gi.invoice_record(inv)
        code = str(clients[cid].get("paymentTerms"))
        for d in docs:
            if d.get("type") in gi.TAX_INVOICE_TYPES and d.get("dueDate") and d.get("documentDate"):
                samples.setdefault(code, []).append((d["documentDate"], d["dueDate"]))
    semantics = gi.terms_semantics({k: [(date.fromisoformat(a), date.fromisoformat(b)) for a, b in v[:50]]
                                    for k, v in samples.items()})
    _dump(RAW / "gi_clients.json", clients)
    _dump(RAW / "gi_invoices.json", invoices)
    _dump(RAW / "gi_terms_semantics.json", semantics)
    errors = sum(1 for c in clients.values() if "error" in c)
    print(f"green invoice: {len(clients)} clients ({errors} errors), {len(invoices)} latest invoices, terms mapped {sorted(semantics)}")
    tasks = lionwheel.pull_tasks()
    _dump(RAW / "lw_tasks.json", tasks)
    print(f"lionwheel: {len(tasks)} open tasks")
    return 0


def cmd_seed(args) -> int:
    today = date.today()
    lines, orders, parse_stats = shopify.parse_bulk_orders(RAW / "orders.jsonl")
    custs = _j(RAW / "customers.json")
    variants = _j(RAW / "variants.json")
    active, unlinked = shopify.active_customer_ids(orders, custs, today, WINDOW_DAYS)
    sku_bc, _, _ = shopify.barcode_maps(variants)
    tsv = catalog.read_tsv(PRICING_TSV)
    truth, negative = catalog.read_catalog_truth(CATALOG_TRUTH)
    truth_skus = {row[0] for row in truth}
    titles = {v["sku"]: (v.get("product") or {}).get("title") or v["sku"] for v in variants if v.get("sku")}
    since = today - timedelta(days=WINDOW_DAYS)
    sold_recently: dict[str, str] = {}
    for ln in lines:
        if ln.customer_id in active and ln.ordered_at.date() >= since:
            sku = DISCONTINUED_EQUIV.get(ln.sku, ln.sku)
            if sku not in truth_skus:
                sold_recently.setdefault(sku, titles.get(sku, sku))
    list_rows, c_flags = catalog.build_list_prices(tsv, truth, negative, sku_bc, sold_recently, today)
    by_sku = {r.sku: r for r in list_rows}
    proposals, p_flags, seed_stats = prices.seed_prices([ln for ln in lines if ln.customer_id in active], by_sku, today)
    gi_all = _j(RAW / "gi_clients.json")
    gi_ok = {k: v for k, v in gi_all.items() if "error" not in v}
    order_customer = {o["name"]: o["customer"]["id"] for o in orders.values() if (o.get("customer") or {}).get("id")}
    lw = lionwheel.by_customer(_j(RAW / "lw_tasks.json"), order_customer)
    form_path = RAW / "form_answers.json"
    form = _j(form_path) if form_path.exists() else {}
    with db.connect() as conn:
        existing = db.load_book(conn)
        rows, k_flags = customers.build_customer_rows(sorted(active), {c["id"]: c for c in custs}, gi_ok, lw,
                                                      shopify.order_stats(orders, today), _j(ZONES), _j(ROUTE_CALENDAR),
                                                      _j(RAW / "gi_terms_semantics.json"), form, existing)
        customers.assign_gt_numbers(rows, {cid: r.gt_customer_no for cid, r in existing.items()})
        e4 = prices.chain_flags(proposals, {r.shopify_customer_id: r.tax_id for r in rows if r.tax_id})
        db.upsert_list_prices(conn, list_rows)
        db.upsert_customer_book(conn, rows)
        new_rows = db.insert_seed_prices(conn, proposals, RECORDED_BY)
        conn.commit()
    k3 = [Flag("K3", cid, "green_invoice_link", None, "הזמין בשנה האחרונה ואין לו קישור ל־Green Invoice.")
          for cid in sorted(unlinked)]
    k3 += [Flag("K3", cid, "green_invoice_error", None, f"הקישור ל־Green Invoice לא נפתח: {v['error'][:80]}")
           for cid, v in sorted(gi_all.items()) if "error" in v]
    previous_e5 = [f for f in load_flags(OUT / "flags.json") if f.code == "E5"] if (OUT / "flags.json").exists() else []
    save_flags(OUT / "flags.json", c_flags + p_flags + e4 + k_flags + k3 + previous_e5)
    print(f"active {len(active)} · list prices {len(list_rows)} · proposals {len(proposals)} (new rows {new_rows}) · "
          f"flags C1 {len(c_flags)} E1-3 {len(p_flags)} E4 {len(e4)} K2 {len(k_flags)} K3 {len(k3)} · "
          f"parse {parse_stats} · seed {seed_stats}")
    return 0


def cmd_gates(args) -> int:
    flags = load_flags(OUT / "flags.json")
    with db.connect() as conn:
        matrix = db.price_matrix(conn)
        book = [r for r in db.load_book(conn).values() if r.active]
        lrows = db.list_prices(conn)
    by = {(m["shopify_customer_id"], m["sku"]): m["price_ex_vat"] for m in matrix}
    _, bc_skus, _ = shopify.barcode_maps(_j(RAW / "variants.json"))
    checked, e5 = gates.g1_invoice_match(by, _j(RAW / "gi_invoices.json"), bc_skus)
    flags = [f for f in flags if f.code != "E5"] + e5
    save_flags(OUT / "flags.json", flags)
    print(f"G1: {checked} invoice lines checked, {len(e5)} to review (E5)")
    if args.g1_only:
        return 0
    general_total = sum(1 for r in lrows if r["general"] and r["active"])
    counts = Counter(m["shopify_customer_id"] for m in matrix if m["general"])
    g2 = gates.g2_completeness(book, counts, general_total)
    g3 = gates.g3_open(flags, _decided_ids())
    print(f"G2: {len(g2)} problems")
    for p in g2[:30]:
        print("  -", p)
    print(f"G3: {len(g3)} open exceptions {dict(Counter(f.code for f in g3))}")
    return 1 if (g2 or g3) else 0


def cmd_review(args) -> int:
    flags = load_flags(OUT / "flags.json")
    with db.connect() as conn:
        book = db.load_book(conn)
    names = {cid: f"{r.gt_customer_no} · {r.place_name}" for cid, r in book.items()}
    gap_counts = Counter(g for r in book.values() if r.active for g in customers.gaps(r))
    path = OUT / "review.html"
    path.write_text(review.review_html(flags, names, dict(gap_counts)), encoding="utf-8")
    print(f"review → {path} · {dict(Counter(f.code for f in flags))}")
    return 0


def cmd_decide(args) -> int:
    items = _j(Path(args.file))
    price_items = [d for d in items if d.get("price_key")]
    field_items = [d for d in items if d.get("field")]
    with db.connect() as conn:
        n_prices = db.record_decisions(conn, price_items, "tom", date.today())
        n_fields = db.set_manual_fields(conn, field_items)
        conn.commit()
    previous = _j(OUT / "decisions.json") if (OUT / "decisions.json").exists() else []
    _dump(OUT / "decisions.json", previous + items)
    print(f"decisions: {n_prices} prices · {n_fields} fields · {len(items) - n_prices - n_fields} acknowledgements")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pull").set_defaults(fn=cmd_pull)
    sub.add_parser("seed").set_defaults(fn=cmd_seed)
    g = sub.add_parser("gates")
    g.add_argument("--g1-only", action="store_true")
    g.set_defaults(fn=cmd_gates)
    sub.add_parser("review").set_defaults(fn=cmd_review)
    d = sub.add_parser("decide")
    d.add_argument("file")
    d.set_defaults(fn=cmd_decide)
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
```

Decisions file format (`decide FILE`), one item per decided flag — every item carries the flag `id`:
```json
[
  {"id": "E1:gid://shopify/Customer/1:TEA_1L", "customer_id": "gid://shopify/Customer/1", "price_key": "TEA_1L", "price_ex_vat": "58.50", "note": "Tom 2026-09-25: מאשר הצעה"},
  {"id": "K2:gid://shopify/Customer/2:tax_id", "customer_id": "gid://shopify/Customer/2", "field": "tax_id", "value": "000000018", "note": "Tom 2026-09-25"},
  {"id": "C1::GT-HIB-LOW-0.3L", "note": "Tom 2026-09-25: מחירון כללי — נוסף ל-catalog-truth"}
]
```

- [ ] **Step 7: Run to verify the tests pass and the CLI loads**

Run the test command. Expected: `Ran 38 tests … OK`. Then:
```bash
cd /home/user/gt-factory-os/scripts/distributor-handoff && .venv/bin/python run.py --help
```
Expected: usage text listing `pull seed gates review decide`.

- [ ] **Step 8: Commit**

```bash
cd /home/user/gt-factory-os && git add scripts/distributor-handoff/handoff/db.py scripts/distributor-handoff/handoff/gates.py scripts/distributor-handoff/handoff/review.py scripts/distributor-handoff/run.py scripts/distributor-handoff/tests/test_gates.py scripts/distributor-handoff/tests/test_review.py
git commit -m "feat(distributor-handoff): DB I/O, gates G1–G4, review page, CLI"
```

---

### Task 8: Switch message links and form import

**Files:**
- Create: `scripts/distributor-handoff/handoff/{messages.py,forms.py}`
- Modify: `scripts/distributor-handoff/run.py` (add `messages`, `import-form`)
- Test: `scripts/distributor-handoff/tests/{test_messages.py,test_forms.py}`

**Interfaces:**
- Consumes: `CustomerRow`, `copy_he.CUSTOMER_MESSAGE`, `FORM_QUESTIONS`, `FORM_KASHRUT_OPTIONS`, `db.whatsapp_phones`.
- Produces: `messages.wa_phone(raw) -> str | None`; `messages.message_rows(book, phones, form_link_template, sender, switch_date_he) -> list[dict]`; `messages.messages_html(rows) -> str`; `forms.parse_form_csv(path, customer_by_no: dict[int, str]) -> tuple[dict[str, dict], list[str]]`.

- [ ] **Step 1: Write the failing tests**

`tests/test_messages.py`:
```python
import unittest
import urllib.parse

from handoff.messages import message_rows, messages_html, wa_phone
from handoff.model import CustomerRow


class MessagesTest(unittest.TestCase):
    def test_wa_phone(self):
        self.assertEqual(wa_phone("050-123-4567"), "972501234567")
        self.assertEqual(wa_phone("+972 50 123 4567"), "972501234567")
        self.assertIsNone(wa_phone("123"))

    def test_rows_link_and_fallback(self):
        book = [CustomerRow("gid://shopify/Customer/1", gt_customer_no=1002, place_name="קפה ב", onsite_contact_phone="0502222222"),
                CustomerRow("gid://shopify/Customer/2", gt_customer_no=1001, place_name="קפה א")]
        rows = message_rows(book, {"gid://shopify/Customer/1": "0501111111"},
                            "https://forms.example/viewform?entry.1={gt_no}&entry.2={place}", "דורין", "15.10.2026")
        self.assertEqual([r["gt_no"] for r in rows], [1001, 1002])
        self.assertIsNone(rows[0]["wa_link"])
        text = urllib.parse.unquote(rows[1]["wa_link"].split("text=")[1])
        self.assertIn("entry.1=1002", text)
        self.assertIn("15.10.2026", text)
        self.assertTrue(rows[1]["wa_link"].startswith("https://wa.me/972501111111?text="))
        self.assertIn("אין מספר וואטסאפ", messages_html(rows))
```

`tests/test_forms.py`:
```python
import csv
import tempfile
import unittest
from pathlib import Path

from handoff import copy_he as T
from handoff.forms import parse_form_csv


class FormsTest(unittest.TestCase):
    def test_parse(self):
        q = T.FORM_QUESTIONS
        header = ["חותמת זמן", q["gt_no"], q["place_name"], q["kashrut"], q["onsite_contact_phone"], q["receiving_restrictions"]]
        rows = [["1", "1001", "קפה א", "כשר — בד״ץ", "0501", ""], ["2", "7777", "x", "לא כשר", "", ""], ["3", "", "y", "", "", ""]]
        path = Path(tempfile.mkdtemp()) / "r.csv"
        with path.open("w", encoding="utf-8-sig", newline="") as fh:
            csv.writer(fh).writerows([header] + rows)
        answers, problems = parse_form_csv(path, {1001: "gid://shopify/Customer/1"})
        self.assertEqual(answers, {"gid://shopify/Customer/1": {"place_name": "קפה א", "kashrut": "badatz", "onsite_contact_phone": "0501"}})
        self.assertEqual(len(problems), 2)
```

- [ ] **Step 2: Run to verify they fail**

Expected: `ModuleNotFoundError` for `handoff.messages` and `handoff.forms`.

- [ ] **Step 3: Implement `messages.py`**

```python
"""Per-customer WhatsApp links for the switch announcement — a person presses send, never automation."""
from __future__ import annotations

import html
import re
import urllib.parse

from . import copy_he as T
from .brand import font_face_css, tokens_css
from .model import CustomerRow


def wa_phone(raw: str | None) -> str | None:
    d = re.sub(r"\D", "", raw or "")
    if d.startswith("972") and len(d) == 12:
        return d
    if d.startswith("0") and len(d) == 10:
        return "972" + d[1:]
    return None


def message_rows(book: list[CustomerRow], phones: dict[str, str], form_link_template: str, sender: str,
                 switch_date_he: str) -> list[dict]:
    """form_link_template: the Google Form prefill link with {gt_no} and {place} where the answers go."""
    out = []
    for r in sorted(book, key=lambda r: r.gt_customer_no or 0):
        link = form_link_template.format(gt_no=r.gt_customer_no, place=urllib.parse.quote(r.place_name or ""))
        text = T.CUSTOMER_MESSAGE.format(place_name=r.place_name, switch_date_he=switch_date_he, form_link=link, sender=sender)
        phone = wa_phone(phones.get(r.shopify_customer_id)) or wa_phone(r.onsite_contact_phone)
        out.append({"gt_no": r.gt_customer_no, "place_name": r.place_name, "phone": phone, "text": text,
                    "wa_link": f"https://wa.me/{phone}?text={urllib.parse.quote(text)}" if phone else None})
    return out


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Heebo',sans-serif;background:var(--paper);color:var(--ink);padding:18px}
h1{font-family:'Rubik';font-weight:700;color:var(--green);font-size:24px}
p.how{margin:6px 0 16px;font-weight:500}
.row{display:flex;align-items:center;justify-content:space-between;gap:12px;background:#fff;border:1px solid var(--line);
     border-radius:10px;padding:10px 14px;margin-bottom:8px}
.row b{font-family:'Rubik';font-weight:600;color:var(--green);margin-left:10px}
a.send{background:var(--green);color:var(--paper);text-decoration:none;font-family:'Rubik';font-weight:600;
       padding:8px 18px;border-radius:20px}
.none{color:var(--coral);font-weight:500}
"""


def messages_html(rows: list[dict]) -> str:
    esc = html.escape
    items = "".join(
        f"<div class='row'><span><b>{r['gt_no']}</b>{esc(r['place_name'] or '')}</span>"
        + (f"<a class='send' href='{esc(r['wa_link'])}' target='_blank'>{T.MESSAGES_SEND}</a>" if r["wa_link"]
           else f"<span class='none'>{T.MESSAGES_NO_PHONE}</span>") + "</div>" for r in rows)
    return (f"<!doctype html><html lang='he' dir='rtl'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'><title>{T.MESSAGES_TITLE}</title>"
            f"<style>{tokens_css()}{font_face_css()}{CSS}</style></head><body><h1>{T.MESSAGES_TITLE}</h1>"
            f"<p class='how'>{T.MESSAGES_HOW}</p>{items}</body></html>")
```

- [ ] **Step 4: Implement `forms.py`**

```python
"""Google Form responses (CSV export) → per-customer answers. The GT number arrives prefilled."""
from __future__ import annotations

import csv
from pathlib import Path

from . import copy_he as T


def parse_form_csv(path: Path, customer_by_no: dict[int, str]) -> tuple[dict[str, dict], list[str]]:
    title_to_key = {v: k for k, v in T.FORM_QUESTIONS.items()}
    answers: dict[str, dict] = {}
    problems: list[str] = []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            rec = {title_to_key[h]: (v or "").strip() for h, v in row.items() if h in title_to_key}
            try:
                no = int(rec.pop("gt_no", ""))
            except ValueError:
                problems.append(f"תשובה בלי מספר לקוח: {rec.get('place_name', '')}")
                continue
            cid = customer_by_no.get(no)
            if not cid:
                problems.append(f"מספר לקוח לא קיים: {no}")
                continue
            if rec.get("kashrut"):
                rec["kashrut"] = T.FORM_KASHRUT_OPTIONS.get(rec["kashrut"], "")
            answers[cid] = {k: v for k, v in rec.items() if v}  # rows are chronological: the latest answer wins
    return answers, problems
```

- [ ] **Step 5: Add the two subcommands to `run.py`**

Add these imports next to the existing ones:
```python
from handoff import forms, messages
```

Add these functions above `main`:
```python
def cmd_messages(args) -> int:
    with db.connect() as conn:
        book = [r for r in db.load_book(conn).values() if r.active and (args.region is None or r.region == args.region)]
        phones = db.whatsapp_phones(conn)
    switch = date.fromisoformat(args.switch_date).strftime("%d.%m.%Y")
    rows = messages.message_rows(book, phones, args.form_link, args.sender, switch)
    path = OUT / "messages.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(messages.messages_html(rows), encoding="utf-8")
    print(f"messages → {path} · {len(rows)} customers · {sum(1 for r in rows if not r['wa_link'])} without WhatsApp")
    return 0


def cmd_import_form(args) -> int:
    with db.connect() as conn:
        by_no = {r.gt_customer_no: cid for cid, r in db.load_book(conn).items()}
    answers, problems = forms.parse_form_csv(Path(args.csv), by_no)
    path = RAW / "form_answers.json"
    merged = _j(path) if path.exists() else {}
    merged.update(answers)
    _dump(path, merged)
    print(f"form: {len(answers)} answers imported ({len(merged)} total) · {len(problems)} problems — run `seed` next")
    for p in problems:
        print("  -", p)
    return 0
```

Add inside `main`, before `args = parser.parse_args(argv)`:
```python
    m = sub.add_parser("messages")
    m.add_argument("--form-link", required=True, help="prefill link with {gt_no} and {place}")
    m.add_argument("--sender", required=True)
    m.add_argument("--switch-date", required=True, help="YYYY-MM-DD")
    m.add_argument("--region", choices=["center", "north", "south"])
    m.set_defaults(fn=cmd_messages)
    f = sub.add_parser("import-form")
    f.add_argument("csv")
    f.set_defaults(fn=cmd_import_form)
```

- [ ] **Step 6: Run to verify the tests pass**

Expected: `Ran 41 tests … OK`; `run.py --help` lists `messages` and `import-form`.

- [ ] **Step 7: Commit**

```bash
cd /home/user/gt-factory-os && git add scripts/distributor-handoff/handoff/messages.py scripts/distributor-handoff/handoff/forms.py scripts/distributor-handoff/run.py scripts/distributor-handoff/tests/test_messages.py scripts/distributor-handoff/tests/test_forms.py
git commit -m "feat(distributor-handoff): switch-message WhatsApp links and form import"
```

---

### Task 9: CONTROLLER — apply the migration, first live run, send Tom the review

Never delegated. Every command runs in the controller session.

- [ ] **Step 1: Push the gt-factory-os branch and open a draft PR**

```bash
cd /home/user/gt-factory-os && git push -u origin claude/shopify-customer-identifier-cwm1j1
```
Open a draft PR (`mcp__github__create_pull_request`, base `main`), then immediately `mcp__Claude_Code_Remote__unsubscribe_pr_activity` for it. Wait for the `typecheck` check on the PR to be green (the diff adds no TypeScript; a red check that is also red on `main` is not this PR's — note it and continue per the deploy gates).

- [ ] **Step 2: Pre-flight stock truth**

```sql
select private_core.rebuild_verifier();
```
Expected: `0`. Anything else → HALT, report to Tom, do not apply.

- [ ] **Step 3: Slot check, one-line announcement, apply**

`ls db/migrations | sort | tail -3` → `0352_sales_core_price_book.sql` is still the highest. Tell Tom in one line (visibility, not permission): "מחיל עכשיו את מיגרציה 0352 — שלוש טבלאות חדשות ותצוגה ב־sales_core, בלי נגיעה במלאי." Then `mcp__Supabase__apply_migration` with name `0352_sales_core_price_book` and the file's exact content.

- [ ] **Step 4: Post-deploy health**

```bash
cd /home/user/gt-factory-os && psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/tests/0352_sales_core_price_book.test.sql | grep -cE "^ok"
psql "$DATABASE_URL" -Atc "select private_core.rebuild_verifier(), (select count(*) from sales_core.v_customer_price)"
```
Expected: `21`; then `0|0`.

- [ ] **Step 5: Pull, seed, G1, review**

```bash
cd /home/user/gt-factory-os/scripts/distributor-handoff
.venv/bin/python run.py pull
.venv/bin/python run.py seed
.venv/bin/python run.py gates --g1-only
.venv/bin/python run.py review
```
Expected: `active` ≈ 584; `list prices` ≥ 40; LionWheel `wp_order_id` values match Shopify order names (sanity: `by_customer` returned > 0 customers — print `len(lw)` if needed); `terms mapped` lists the codes whose meaning was proven (`-1` only if the evidence proves it).

Sanity SQL:
```sql
select (select count(*) from sales_core.customer_book) as book,
       (select count(*) from sales_core.customer_price) as prices,
       (select count(*) from sales_core.list_price where general) as general,
       (select count(*) from sales_core.v_customer_price where price_ex_vat is null) as nulls;
```
Expected: `book` = active count, `nulls` = 0.

- [ ] **Step 6: Send Tom the review and the customer-facing drafts**

`SendUserFile` with `out/review.html` (display `render`). In the same message, quote `copy_he.CUSTOMER_MESSAGE` and `FORM_QUESTIONS` verbatim for approval, and ask for the switch date, the GT contact name/phone for Ice Dream, and the sender name. HOLD until Tom answers; Tasks 10–12 continue meanwhile.

---

### Task 10: Package data and the Excel workbook

**Files:**
- Create: `scripts/distributor-handoff/handoff/{package.py,render_excel.py}`
- Test: `scripts/distributor-handoff/tests/{test_package.py,test_render_excel.py}`

**Interfaces:**
- Consumes: `CustomerRow`, `copy_he`, `customers.REGION_ORDER`, `customers.delivery_days_he`, `config.VAT`.
- Produces: `package.CUSTOMER_FIELDS`; `package.PackageData(meta, customers, specials, general, days, cards)`; `package.meta(base, calendar) -> dict`; `package.build_package_data(book, matrix, list_rows, zones, calendar, meta, region=None, images=None, only=None) -> PackageData`; `render_excel.build_workbook(data) -> Workbook`; `render_excel.sheet(wb, title, headers, widths, rows, money_cols=(), groups=None, meta=None)`; `render_excel.write_csvs(data, out_dir) -> list[Path]`; `render_excel.customer_ids(xlsx_path) -> list[str]`.

- [ ] **Step 1: Write the failing tests**

`tests/test_package.py`:
```python
import unittest
from datetime import date
from decimal import Decimal

from handoff import package
from handoff.model import CustomerRow

CAL = {"calendar": {"sunday": "center", "monday": "center", "tuesday": "north", "wednesday": "south",
                    "thursday": "center", "friday": None, "saturday": None}}
ZONES = {"Center": ["תל אביב", "tel aviv"], "North": ["חיפה"], "South": ["באר שבע"]}


def m(cid, sku, price, lst, family=None, general=True, name="מוצר"):
    return {"shopify_customer_id": cid, "sku": sku, "name_he": name, "size_label": "", "barcode": "1", "family": family,
            "general": general, "price_ex_vat": Decimal(price), "price_inc_vat": (Decimal(price) * Decimal("1.18")).quantize(Decimal("0.01")),
            "list_price_ex_vat": None if lst is None else Decimal(lst), "basis": "last_paid"}


BOOK = [CustomerRow("n1", gt_customer_no=1003, place_name="ב", city="חיפה", region="north", last_order_on=date(2026, 9, 1)),
        CustomerRow("c1", gt_customer_no=1001, place_name="א", city="תל אביב", region="center"),
        CustomerRow("x", gt_customer_no=1009, place_name="ג", region="center", active=False)]
MATRIX = [m("c1", "GT-HIB-LOW-1L", "58.50", "65", "TEA_1L", name="FRESH"), m("c1", "GT-ODK-MAN-1", "60", "60"),
          m("c1", "PRIV", "24", None, general=False), m("n1", "GT-ODK-MAN-1", "60", "60")]
LIST = [{"sku": "GT-HIB-LOW-1L", "name_he": "FRESH", "size_label": "1 ליטר", "barcode": "1", "family": "TEA_1L",
         "price_ex_vat": Decimal("65"), "general": True, "active": True},
        {"sku": "GT-ODK-MAN-1", "name_he": "מחית מנגו", "size_label": "", "barcode": "2", "family": None,
         "price_ex_vat": Decimal("60"), "general": True, "active": True},
        {"sku": "PRIV", "name_he": "פרטי", "size_label": "", "barcode": None, "family": None,
         "price_ex_vat": None, "general": False, "active": True}]


class PackageTest(unittest.TestCase):
    def setUp(self):
        meta = package.meta({"version": 1, "date_he": "24.09.2026", "switch_date_he": "15.10.2026",
                             "contact_name": "דורין", "contact_phone": "03-0000000"}, CAL)
        self.data = package.build_package_data(BOOK, MATRIX, LIST, ZONES, CAL, meta)

    def test_order_and_active_only(self):
        self.assertEqual([c["gt_no"] for c in self.data.customers], [1001, 1003])
        self.assertEqual(self.data.customers[1]["last_order_on"], "01.09.2026")

    def test_specials_are_only_differences_and_private_products(self):
        self.assertEqual([s["sku"] for s in self.data.specials["c1"]], ["GT-HIB-LOW-1L", "PRIV"])
        self.assertEqual(self.data.specials["n1"], [])

    def test_general_list_cards_days_meta(self):
        self.assertEqual([g["sku"] for g in self.data.general], ["GT-HIB-LOW-1L", "GT-ODK-MAN-1"])
        self.assertEqual(self.data.general[0]["price_inc_vat"], Decimal("76.70"))
        self.assertEqual([c["name_he"] for c in self.data.cards], ["FRESH", "מחית מנגו"])
        self.assertEqual([d["city"] for d in self.data.days], ["תל אביב", "חיפה", "באר שבע"])
        self.assertEqual(self.data.meta["days_summary_he"], "מרכז: ראשון, שני, חמישי · צפון: שלישי · דרום: רביעי")

    def test_region_and_only_filters(self):
        meta = self.data.meta
        self.assertEqual([c["gt_no"] for c in package.build_package_data(BOOK, MATRIX, LIST, ZONES, CAL, meta, region="north").customers], [1003])
        self.assertEqual([c["gt_no"] for c in package.build_package_data(BOOK, MATRIX, LIST, ZONES, CAL, meta, only={1001}).customers], [1001])
```

`tests/test_render_excel.py`:
```python
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from handoff import copy_he as T
from handoff import render_excel
from tests.test_package import BOOK, CAL, LIST, MATRIX, ZONES
from handoff import package


class ExcelTest(unittest.TestCase):
    def setUp(self):
        meta = package.meta({"version": 1, "date_he": "24.09.2026", "switch_date_he": "15.10.2026",
                             "contact_name": "דורין", "contact_phone": "03-0000000"}, CAL)
        self.data = package.build_package_data(BOOK, MATRIX, LIST, ZONES, CAL, meta)
        self.dir = Path(tempfile.mkdtemp())
        self.path = self.dir / "w.xlsx"
        render_excel.build_workbook(self.data).save(self.path)
        self.wb = load_workbook(self.path)

    def test_sheets_rtl_and_headers(self):
        self.assertEqual(self.wb.sheetnames, [T.SHEET_README, T.SHEET_CUSTOMERS, T.SHEET_SPECIALS, T.SHEET_GENERAL, T.SHEET_DAYS])
        self.assertTrue(all(ws.sheet_view.rightToLeft for ws in self.wb.worksheets))
        ws = self.wb[T.SHEET_CUSTOMERS]
        self.assertEqual([c.value for c in ws[2]], T.CUSTOMER_HEADERS)
        self.assertEqual(ws.freeze_panes, "A3")

    def test_rows_and_money_format(self):
        sp = self.wb[T.SHEET_SPECIALS]
        self.assertEqual(sp.max_row, 3)  # header + 2 specials
        self.assertEqual(sp.cell(row=2, column=7).value, 58.5)
        self.assertIn("₪", sp.cell(row=2, column=7).number_format)
        self.assertEqual(sp.cell(row=2, column=10).value, T.FAMILY_NOTE)
        self.assertEqual(sp.cell(row=3, column=9).value, T.MISSING)

    def test_readme_carries_the_switch_date(self):
        text = " ".join(str(c.value) for row in self.wb[T.SHEET_README].iter_rows() for c in row if c.value)
        self.assertIn("15.10.2026", text)

    def test_customer_ids_and_csvs(self):
        self.assertEqual(render_excel.customer_ids(self.path), ["c1", "n1"])
        files = render_excel.write_csvs(self.data, self.dir)
        self.assertEqual(sorted(p.name for p in files), ["customers.csv", "general.csv", "specials.csv"])
        self.assertTrue(files[0].read_bytes().startswith(b"\xef\xbb\xbf"))
```

- [ ] **Step 2: Run to verify they fail**

Expected: `ModuleNotFoundError` for `handoff.package` / `handoff.render_excel`.

- [ ] **Step 3: Implement `package.py`**

```python
"""Everything the renderers need, assembled once from the database (spec §7). Renderers never query."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

from . import copy_he as T
from .config import VAT
from .customers import REGION_ORDER, delivery_days_he
from .model import CustomerRow

CUSTOMER_FIELDS = ["gt_no", "place_name", "legal_name", "tax_id", "chain", "business_type",
                   "accounting_email", "invoice_address", "payment_terms_he",
                   "street", "house_number", "city", "region_he", "days_he", "delivery_notes",
                   "onsite_contact_name", "onsite_contact_phone", "receiving_restrictions",
                   "kashrut_he", "last_order_on", "orders_per_month", "shopify_customer_id"]
FAMILY_ORDER = {"TEA_1L": 0, "TEA_05L": 1}
REGIONS = ("center", "north", "south")


@dataclass
class PackageData:
    meta: dict
    customers: list[dict]
    specials: dict[str, list[dict]]
    general: list[dict]
    days: list[dict]
    cards: list[dict] = field(default_factory=list)


def meta(base: dict, calendar: dict) -> dict:
    region_days = {z: delivery_days_he(z, calendar) for z in REGIONS}
    summary = " · ".join(f"{T.REGION_HE[z]}: {d.replace(' · ', ', ')}" for z, d in region_days.items() if d)
    return {**base, "region_days": region_days, "days_summary_he": summary}


def customer_display(r: CustomerRow) -> dict:
    return {"gt_no": r.gt_customer_no, "place_name": r.place_name, "legal_name": r.legal_name, "tax_id": r.tax_id,
            "chain": r.chain, "business_type": r.business_type, "accounting_email": r.accounting_email,
            "invoice_address": r.invoice_address, "payment_terms_he": r.payment_terms_he, "street": r.street,
            "house_number": r.house_number, "city": r.city, "region": r.region,
            "region_he": T.REGION_HE.get(r.region or ""), "days_he": r.delivery_days_he, "delivery_notes": r.delivery_notes,
            "onsite_contact_name": r.onsite_contact_name, "onsite_contact_phone": r.onsite_contact_phone,
            "receiving_restrictions": r.receiving_restrictions, "kashrut_he": T.KASHRUT_HE.get(r.kashrut or ""),
            "last_order_on": r.last_order_on.strftime("%d.%m.%Y") if r.last_order_on else None,
            "orders_per_month": r.orders_per_month, "shopify_customer_id": r.shopify_customer_id}


def _sort_key(row: dict) -> tuple:
    return (FAMILY_ORDER.get(row["family"] or "", 2), row["name_he"], row["sku"])


def build_cards(general: list[dict], images: dict[str, str]) -> list[dict]:
    """One card per product; tea flavors show both sizes on one card."""
    cards: list[dict] = []
    by_flavor: dict[str, dict] = {}
    for g in general:
        size = {"size": g["size_label"], "sku": g["sku"], "barcode": g["barcode"], "price": g["price_ex_vat"]}
        if g["family"]:
            card = by_flavor.get(g["name_he"])
            if card is None:
                card = {"name_he": g["name_he"], "sizes": [], "image": None}
                by_flavor[g["name_he"]] = card
                cards.append(card)
            card["sizes"].append(size)
            card["image"] = card["image"] or images.get(g["sku"])
        else:
            cards.append({"name_he": g["name_he"], "sizes": [size], "image": images.get(g["sku"])})
    return cards


def build_package_data(book: list[CustomerRow], matrix: list[dict], list_rows: list[dict], zones: dict, calendar: dict,
                       meta_: dict, region: str | None = None, images: dict[str, str] | None = None,
                       only: set[int] | None = None) -> PackageData:
    rows = [r for r in book if r.active and (region is None or r.region == region)
            and (only is None or r.gt_customer_no in only)]
    rows.sort(key=lambda r: (REGION_ORDER.get(r.region or "", 9), r.city or "", r.place_name or "", r.gt_customer_no or 0))
    ids = {r.shopify_customer_id for r in rows}
    specials: dict[str, list[dict]] = {cid: [] for cid in ids}
    for mrow in matrix:
        cid = mrow["shopify_customer_id"]
        if cid not in ids:
            continue
        differs = mrow["list_price_ex_vat"] is not None and mrow["price_ex_vat"] != mrow["list_price_ex_vat"]
        if (not mrow["general"]) or differs:
            specials[cid].append({k: mrow[k] for k in ("sku", "name_he", "size_label", "barcode", "family", "general",
                                                     "price_ex_vat", "price_inc_vat", "list_price_ex_vat", "basis")})
    for cid in specials:
        specials[cid].sort(key=_sort_key)
    general = sorted(({k: lr[k] for k in ("sku", "name_he", "size_label", "barcode", "family", "price_ex_vat")}
                      | {"price_inc_vat": (lr["price_ex_vat"] * VAT).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)}
                      for lr in list_rows if lr["general"] and lr["active"]), key=_sort_key)
    days = []
    for zone, cities in zones.items():
        if zone.startswith("_"):
            continue
        z = zone.lower()
        for city in sorted({c for c in cities if re.search(r"[א-ת]", c)}):
            days.append({"city": city, "region_he": T.REGION_HE[z], "days_he": delivery_days_he(z, calendar),
                         "_order": REGION_ORDER.get(z, 9)})
    days.sort(key=lambda d: (d.pop("_order"), d["city"]))
    return PackageData(meta_, [customer_display(r) for r in rows], specials, general, days, build_cards(general, images or {}))
```

- [ ] **Step 4: Implement `render_excel.py`**

```python
"""The Ice Dream workbook (spec §7.1): Hebrew, RTL, brand colors, printable. No formulas, no hidden cells."""
from __future__ import annotations

import csv
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from . import copy_he as T
from .package import CUSTOMER_FIELDS, PackageData

GREEN, INK, PAPER, LINE, MUTED, WASH = "263B18", "241C15", "EFE6D6", "D8CCB4", "7C6E58", "F7F2E9"
FONT = "Arial"  # Excel cannot embed fonts; Arial renders Hebrew on every Windows PC
MONEY = "₪ #,##0.00"
CUSTOMER_WIDTHS = [9, 24, 28, 12, 14, 12, 26, 26, 14, 18, 7, 12, 8, 18, 26, 18, 14, 22, 12, 12, 9, 30]


def _float(v):
    return float(v) if v is not None and not isinstance(v, (str, int)) else v


def sheet(wb: Workbook, title: str, headers: list[str], widths: list[int], rows: list[list], money_cols=(),
          groups: list[tuple[str, int]] | None = None, meta: dict | None = None):
    ws = wb.create_sheet(title)
    ws.sheet_view.rightToLeft = True
    head_row = 1
    if groups:
        col = 1
        for label, span in groups:
            ws.merge_cells(start_row=1, start_column=col, end_row=1, end_column=col + span - 1)
            c = ws.cell(row=1, column=col, value=label)
            c.font = Font(name=FONT, bold=True, size=11, color=GREEN)
            c.fill = PatternFill("solid", fgColor=PAPER)
            c.alignment = Alignment(horizontal="center", vertical="center")
            col += span
        head_row = 2
    for i, (h, w) in enumerate(zip(headers, widths), start=1):
        c = ws.cell(row=head_row, column=i, value=h)
        c.font = Font(name=FONT, bold=True, size=12, color=PAPER)
        c.fill = PatternFill("solid", fgColor=GREEN)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[head_row].height = 32
    line = Side(style="thin", color=LINE)
    for r_i, row in enumerate(rows, start=head_row + 1):
        zebra = PatternFill("solid", fgColor=WASH) if (r_i - head_row) % 2 == 0 else None
        for c_i, value in enumerate(row, start=1):
            c = ws.cell(row=r_i, column=c_i, value=_float(value) if c_i in money_cols else value)
            c.font = Font(name=FONT, size=12, color=INK, bold=bool(money_cols) and c_i == money_cols[0])
            c.alignment = Alignment(horizontal="right", vertical="center", wrap_text=True)
            c.border = Border(bottom=line)
            if zebra:
                c.fill = zebra
            if c_i in money_cols and isinstance(c.value, float):
                c.number_format = MONEY
        ws.row_dimensions[r_i].height = 22
    ws.freeze_panes = ws.cell(row=head_row + 1, column=1).coordinate
    ws.auto_filter.ref = f"A{head_row}:{get_column_letter(len(headers))}{head_row + max(len(rows), 1)}"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = f"1:{head_row}"
    if meta:
        ws.oddHeader.right.text = f"{T.PACKAGE_TITLE} · {T.VERSION_LINE.format(**meta)}"
        ws.oddFooter.right.text = T.CONFIDENTIAL
        ws.oddFooter.left.text = "&P / &N"
    return ws


def _readme(wb: Workbook, meta: dict) -> None:
    ws = wb.active
    ws.title = T.SHEET_README
    ws.sheet_view.rightToLeft = True
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 86
    ws["B2"] = f"{T.PACKAGE_TITLE} — {T.PACKAGE_FOR}"
    ws["B2"].font = Font(name=FONT, bold=True, size=20, color=GREEN)
    ws["B3"] = f"{T.VERSION_LINE.format(**meta)} · {T.CONFIDENTIAL}"
    ws["B3"].font = Font(name=FONT, size=11, color=MUTED)
    for i, (key, text) in enumerate(T.readme_rules(meta), start=5):
        k = ws.cell(row=i, column=2, value=key)
        k.font = Font(name=FONT, bold=True, size=13, color=INK)
        v = ws.cell(row=i, column=3, value=text)
        v.font = Font(name=FONT, size=13, color=INK)
        v.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[i].height = 34


def _special_rows(data: PackageData) -> list[list]:
    rows = []
    for c in data.customers:
        for s in data.specials.get(c["shopify_customer_id"], []):
            note = T.FAMILY_NOTE if s["family"] else ("" if s["general"] else T.PRIVATE_NOTE)
            rows.append([c["gt_no"], c["place_name"], s["name_he"], s["size_label"], s["barcode"], s["sku"],
                         s["price_ex_vat"], s["price_inc_vat"],
                         s["list_price_ex_vat"] if s["list_price_ex_vat"] is not None else T.MISSING, note])
    return rows


def build_workbook(data: PackageData) -> Workbook:
    wb = Workbook()
    _readme(wb, data.meta)
    sheet(wb, T.SHEET_CUSTOMERS, T.CUSTOMER_HEADERS, CUSTOMER_WIDTHS,
          [[c[f] for f in CUSTOMER_FIELDS] for c in data.customers], groups=T.CUSTOMER_GROUPS, meta=data.meta)
    sheet(wb, T.SHEET_SPECIALS, T.SPECIAL_HEADERS, [9, 24, 26, 10, 16, 18, 12, 12, 12, 30], _special_rows(data),
          money_cols=(7, 8, 9), meta=data.meta)
    sheet(wb, T.SHEET_GENERAL, T.GENERAL_HEADERS, [30, 12, 16, 20, 12, 12],
          [[g["name_he"], g["size_label"], g["barcode"], g["sku"], g["price_ex_vat"], g["price_inc_vat"]] for g in data.general],
          money_cols=(5, 6), meta=data.meta)
    sheet(wb, T.SHEET_DAYS, T.DAYS_HEADERS, [22, 10, 26], [[d["city"], d["region_he"], d["days_he"]] for d in data.days],
          meta=data.meta)
    return wb


def write_csvs(data: PackageData, out_dir: Path) -> list[Path]:
    """UTF-8 with BOM, so Excel opens the Hebrew correctly."""
    tables = {
        "customers.csv": (T.CUSTOMER_HEADERS, [[c[f] for f in CUSTOMER_FIELDS] for c in data.customers]),
        "specials.csv": (T.SPECIAL_HEADERS, _special_rows(data)),
        "general.csv": (T.GENERAL_HEADERS, [[g["name_he"], g["size_label"], g["barcode"], g["sku"], g["price_ex_vat"],
                                             g["price_inc_vat"]] for g in data.general]),
    }
    paths = []
    for name, (headers, rows) in tables.items():
        path = out_dir / name
        with path.open("w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(headers)
            w.writerows(rows)
        paths.append(path)
    return paths


def customer_ids(xlsx: Path) -> list[str]:
    """Reads the saved workbook back (G4 checks the real file): the last column of the customers sheet."""
    ws = load_workbook(xlsx, read_only=True)[T.SHEET_CUSTOMERS]
    col = len(T.CUSTOMER_HEADERS)
    return [row[col - 1] for row in ws.iter_rows(min_row=3, values_only=True) if row[col - 1]]
```

- [ ] **Step 5: Run to verify they pass**

Expected: `Ran 49 tests … OK`.

- [ ] **Step 6: Commit**

```bash
cd /home/user/gt-factory-os && git add scripts/distributor-handoff/handoff/package.py scripts/distributor-handoff/handoff/render_excel.py scripts/distributor-handoff/tests/test_package.py scripts/distributor-handoff/tests/test_render_excel.py
git commit -m "feat(distributor-handoff): package data and the Ice Dream workbook"
```

---

### Task 11: The printed binder

Design: **"working ledger, dressed in the brand"** — editorial type on an operational grid. White pages (office printers, toner), brand green structure, coral only for labels and the tea rule. The one unforgettable element: the customer number in huge Rubik on every page, and a region tab on the outer edge whose **position** (top / middle / bottom third) encodes the region, so the region reads from a closed binder even on a black-and-white printout.

**Files:**
- Create: `scripts/distributor-handoff/handoff/render_pdf.py`
- Test: `scripts/distributor-handoff/tests/test_render_pdf.py`

**Interfaces:**
- Consumes: `PackageData`, `copy_he`, `brand`, `config.CHROME`.
- Produces: `binder_rows(specials) -> list[dict]`; `plan_pages(data) -> list[tuple[str, object]]`; `binder_html(data) -> tuple[str, list]`; `page_doc(data, page_no) -> str`; `html_to_pdf(html_path, pdf_path)`; `pdf_pages(pdf_path) -> int`; `screenshot(html_doc, png_path)`; `fetch_images(urls, cache) -> dict[str, str]`.

- [ ] **Step 1: Write the failing test**

`tests/test_render_pdf.py`:
```python
import os
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from handoff import package, render_pdf
from handoff.config import CHROME
from tests.test_package import BOOK, CAL, LIST, MATRIX, ZONES


def data():
    meta = package.meta({"version": 1, "date_he": "24.09.2026", "switch_date_he": "15.10.2026",
                         "contact_name": "דורין", "contact_phone": "03-0000000"}, CAL)
    return package.build_package_data(BOOK, MATRIX, LIST, ZONES, CAL, meta)


class BinderTest(unittest.TestCase):
    def test_family_rows_collapse(self):
        specials = [{"family": "TEA_1L", "name_he": "FRESH", "size_label": "1 ליטר", "price_ex_vat": Decimal("58.50"),
                     "price_inc_vat": Decimal("69.03")},
                    {"family": "TEA_1L", "name_he": "DETOX", "size_label": "1 ליטר", "price_ex_vat": Decimal("58.50"),
                     "price_inc_vat": Decimal("69.03")}]
        rows = render_pdf.binder_rows(specials)
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["family"])

    def test_plan_and_markers(self):
        d = data()
        plan = render_pdf.plan_pages(d)
        kinds = [k for k, _ in plan]
        self.assertEqual(kinds, ["cover", "guide", "index", "divider", "customer", "divider", "customer", "general", "catalog"])
        html, _ = render_pdf.binder_html(d)
        self.assertEqual(html.count("data-kind='customer'"), 2)
        self.assertLess(html.index("data-customer='c1'"), html.index("data-customer='n1'"))
        self.assertIn("class='tab north'", html)

    def test_long_price_list_continues(self):
        d = data()
        d.specials["c1"] = [{"family": None, "general": True, "name_he": f"מוצר {i}", "size_label": "", "price_ex_vat": Decimal("1"),
                             "price_inc_vat": Decimal("1.18")} for i in range(render_pdf.FIRST_ROWS + 3)]
        kinds = [k for k, _ in render_pdf.plan_pages(d)]
        self.assertEqual(kinds.count("continued"), 1)

    @unittest.skipUnless(os.path.exists(CHROME), "chromium not available")
    def test_pdf_page_count_matches_plan(self):
        d = data()
        html, plan = render_pdf.binder_html(d)
        tmp = Path(tempfile.mkdtemp())
        (tmp / "b.html").write_text(html, encoding="utf-8")
        render_pdf.html_to_pdf(tmp / "b.html", tmp / "b.pdf")
        self.assertEqual(render_pdf.pdf_pages(tmp / "b.pdf"), len(plan))
```

- [ ] **Step 2: Run to verify it fails**

Expected: `ModuleNotFoundError: No module named 'handoff.render_pdf'`.

- [ ] **Step 3: Implement `render_pdf.py`**

```python
"""The printed binder (spec §7.2): A4, RTL, GT brand. One page per customer; region tabs on the outer edge."""
from __future__ import annotations

import base64
import hashlib
import html
import math
import subprocess
import urllib.request
from decimal import Decimal
from pathlib import Path

from pypdf import PdfReader

from . import copy_he as T
from .brand import font_face_css, tokens_css
from .config import CHROME
from .package import PackageData

FIRST_ROWS, CONT_ROWS, INDEX_ROWS, GENERAL_ROWS, CARDS_PER_PAGE = 14, 30, 40, 26, 12
REGIONS = ("center", "north", "south")
esc = html.escape

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
@page{size:A4;margin:0}
html,body{background:#fff}
body{font-family:'Heebo',sans-serif;color:var(--ink);-webkit-font-smoothing:antialiased;font-size:10.5pt;line-height:1.45}
.page{position:relative;width:210mm;height:297mm;overflow:hidden;page-break-after:always;direction:rtl;
      padding:16mm 16mm 20mm 22mm}
.page:last-child{page-break-after:auto}
.tab{position:absolute;left:0;width:9mm;height:62mm;display:flex;align-items:center;justify-content:center;color:#fff}
.tab span{writing-mode:vertical-rl;transform:rotate(180deg);font-family:'Rubik';font-weight:600;font-size:11pt;letter-spacing:.24em}
.tab.center{top:26mm;background:var(--green)}
.tab.north{top:117mm;background:var(--coral)}
.tab.south{top:208mm;background:var(--muted)}
.head{display:grid;grid-template-columns:1fr auto;align-items:end;gap:8mm;padding-bottom:5mm;border-bottom:1.4pt solid var(--green)}
.head .name{font-family:'Rubik';font-weight:600;font-size:22pt;line-height:1.12}
.head .legal{margin-top:2mm;color:var(--muted);font-size:9.5pt}
.head .no{text-align:left;direction:ltr}
.head .no b{display:block;font-family:'Rubik';font-weight:700;font-size:52pt;line-height:.9;color:var(--green)}
.head .no small{display:block;text-align:right;direction:rtl;font-size:8pt;color:var(--muted);letter-spacing:.18em;margin-top:1.5mm}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:4.5mm;margin-top:6mm}
.box{border:.8pt solid var(--line);border-radius:2.5mm;padding:4mm 4.5mm}
.box h3{font-family:'Rubik';font-weight:600;font-size:8.5pt;letter-spacing:.22em;color:var(--coral);margin-bottom:2mm}
.box .big{font-weight:500;font-size:14pt;line-height:1.3}
.box .line{margin-top:1mm}
.muted{color:var(--muted)}
.chip{display:inline-block;margin-top:2.5mm;padding:1mm 3.2mm;border-radius:9mm;background:var(--wash);
      border:.6pt solid var(--line);font-weight:500}
.kosher{font-family:'Rubik';font-weight:600;font-size:13pt;color:var(--green)}
.prices{margin-top:7mm}
.prices h2{font-family:'Rubik';font-weight:600;font-size:13pt;margin-bottom:2.5mm}
table{width:100%;border-collapse:collapse}
th{font-weight:500;font-size:8.5pt;color:var(--muted);text-align:right;padding:1.6mm 2mm;border-bottom:.8pt solid var(--line)}
td{padding:2mm;border-bottom:.5pt solid var(--line);font-size:10.5pt}
tr:nth-child(even) td{background:var(--wash)}
td.p{font-family:'Rubik';font-weight:600;font-size:12pt;white-space:nowrap}
td.v{color:var(--muted);white-space:nowrap}
tr.fam td:first-child::before{content:'';display:inline-block;width:2.2mm;height:2.2mm;border-radius:50%;
      background:var(--coral);margin-left:2mm;vertical-align:middle}
.rest{margin-top:4mm;padding:3mm 4mm;background:var(--paper);border-radius:2mm;font-weight:500}
.foot{position:absolute;bottom:8mm;right:16mm;left:22mm;display:flex;justify-content:space-between;
      font-size:7.5pt;color:var(--muted);border-top:.5pt solid var(--line);padding-top:2mm}
.foot .mark{font-family:'Rubik';font-weight:700;color:var(--green);letter-spacing:.03em}
.cover{background:var(--paper);display:flex;flex-direction:column;justify-content:center;padding:30mm 26mm}
.cover .mark{font-family:'Rubik';font-weight:700;font-size:40pt;color:var(--green);direction:ltr;text-align:right}
.cover h1{font-family:'Rubik';font-weight:700;font-size:40pt;line-height:1.08;margin-top:22mm}
.cover .sub{font-size:14pt;color:var(--muted);margin-top:4mm}
.cover .conf{margin-top:26mm;font-family:'Rubik';font-weight:500;font-size:9pt;letter-spacing:.3em;color:var(--coral)}
.divider{display:flex;flex-direction:column;justify-content:center;padding:0 26mm}
.divider h1{font-family:'Rubik';font-weight:700;font-size:72pt;color:var(--green);line-height:1}
.divider .days{font-size:18pt;margin-top:6mm;font-weight:500}
.divider .count{color:var(--muted);margin-top:2mm;font-size:12pt}
.list h1,.guide h1{font-family:'Rubik';font-weight:600;font-size:20pt;margin-bottom:6mm}
.rule{display:grid;grid-template-columns:52mm 1fr;gap:4mm;padding:3.4mm 0;border-bottom:.5pt solid var(--line);font-size:12pt}
.rule b{font-family:'Rubik';font-weight:600}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:5mm}
.card{border:.8pt solid var(--line);border-radius:2.5mm;overflow:hidden}
.card .img{height:44mm;background:var(--wash) center/contain no-repeat}
.card .img.mono{display:flex;align-items:center;justify-content:center;font-family:'Rubik';font-weight:700;font-size:24pt;color:var(--green)}
.card .t{padding:2.5mm 3mm}
.card .t b{font-family:'Rubik';font-weight:600;font-size:11pt;display:block}
.card .t .row{display:flex;justify-content:space-between;gap:2mm;font-size:8.5pt;color:var(--muted);margin-top:1mm}
.card .t .row .p{color:var(--ink);font-family:'Rubik';font-weight:600;font-size:10pt}
"""


def money(x) -> str:
    return T.MISSING if x is None else f"₪{Decimal(x):,.2f}"


def binder_rows(specials: list[dict]) -> list[dict]:
    """One row per tea family (all flavors share the price); every other special as is."""
    out, seen = [], set()
    for s in specials:
        fam = s.get("family")
        if fam:
            if fam in seen:
                continue
            seen.add(fam)
            out.append({"name": T.FAMILY_HE[fam], "size": T.ALL_FLAVORS, "ex": s["price_ex_vat"], "inc": s["price_inc_vat"], "family": True})
        else:
            out.append({"name": s["name_he"], "size": s["size_label"], "ex": s["price_ex_vat"], "inc": s["price_inc_vat"], "family": False})
    return out


def plan_pages(data: PackageData) -> list[tuple[str, object]]:
    pages: list[tuple[str, object]] = [("cover", None), ("guide", None)]
    pages += [("index", i) for i in range(max(1, math.ceil(len(data.customers) / INDEX_ROWS)))]
    for region in REGIONS + (None,):
        group = [c for c in data.customers if c["region"] == region]
        if not group:
            continue
        pages.append(("divider", (region, len(group))))
        for c in group:
            rows = binder_rows(data.specials.get(c["shopify_customer_id"], []))
            pages.append(("customer", (c, rows[:FIRST_ROWS])))
            rest = rows[FIRST_ROWS:]
            for k in range(0, len(rest), CONT_ROWS):
                pages.append(("continued", (c, rest[k:k + CONT_ROWS])))
    pages += [("general", i) for i in range(max(1, math.ceil(len(data.general) / GENERAL_ROWS)))]
    pages += [("catalog", i) for i in range(math.ceil(len(data.cards) / CARDS_PER_PAGE))]
    return pages


def _foot(n: int, total: int, meta: dict) -> str:
    return (f"<div class='foot'><span class='mark'>gt everyday</span>"
            f"<span>{esc(T.VERSION_LINE.format(**meta))} · {T.CONFIDENTIAL}</span><span dir='ltr'>{n} / {total}</span></div>")


def _tab(region: str | None) -> str:
    return f"<div class='tab {region}'><span>{T.REGION_HE[region]}</span></div>" if region else ""


def _cover(meta: dict) -> str:
    return (f"<div class='page cover'><div class='mark'>gt everyday</div><h1>{T.PACKAGE_TITLE}</h1>"
            f"<div class='sub'>{T.PACKAGE_FOR}</div><div class='sub'>{esc(T.VERSION_LINE.format(**meta))}</div>"
            f"<div class='conf'>{T.CONFIDENTIAL}</div></div>")


def _guide(meta: dict, n: int, total: int) -> str:
    rules = "".join(f"<div class='rule'><b>{esc(k)}</b><span>{esc(v)}</span></div>" for k, v in T.readme_rules(meta))
    return f"<div class='page guide'><h1>{T.B_GUIDE}</h1>{rules}{_foot(n, total, meta)}</div>"


def _index(chunk: list[dict], first_page: dict[str, int], n: int, total: int, meta: dict) -> str:
    th = "".join(f"<th>{h}</th>" for h in T.B_INDEX_HEADERS)
    trs = "".join(f"<tr><td class='p'>{c['gt_no']}</td><td>{esc(c['place_name'] or '')}</td><td>{esc(c['city'] or '')}</td>"
                  f"<td>{esc(c['region_he'] or T.NO_REGION)}</td><td>{first_page[c['shopify_customer_id']]}</td></tr>" for c in chunk)
    return f"<div class='page list'><h1>{T.B_INDEX}</h1><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>{_foot(n, total, meta)}</div>"


def _divider(region: str | None, count: int, n: int, total: int, meta: dict) -> str:
    label = T.REGION_HE[region] if region else T.NO_REGION
    days = meta["region_days"].get(region) if region else None
    return (f"<div class='page divider'>{_tab(region)}<h1>{label}</h1>"
            + (f"<div class='days'>{T.B_DAYS}: {esc(days)}</div>" if days else "")
            + f"<div class='count'>{T.B_CUSTOMERS_IN_REGION.format(n=count)}</div>{_foot(n, total, meta)}</div>")


def _customer(c: dict, rows: list[dict], general_page: int, n: int, total: int, meta: dict, continued: bool) -> str:
    title = esc(c["place_name"] or "") + (f" · {T.B_CONTINUED}" if continued else "")
    head = (f"<div class='head'><div><div class='name'>{title}</div>"
            f"<div class='legal'>{esc(c['legal_name'] or '')} · {T.B_TAX_ID} {esc(c['tax_id'] or T.MISSING)}</div></div>"
            f"<div class='no'><b>{c['gt_no']}</b><small>{T.B_CUSTOMER_NO}</small></div></div>")
    body = ""
    if not continued:
        address = " ".join(x for x in (c["street"], c["house_number"]) if x) or T.MISSING
        delivery = (f"<div class='box'><h3>{T.B_DELIVERY}</h3><div class='big'>{esc(address)}</div>"
                    f"<div class='line'>{esc(c['city'] or T.MISSING)}</div>"
                    + (f"<div class='line muted'>{esc(c['delivery_notes'])}</div>" if c["delivery_notes"] else "")
                    + f"<div class='chip'>{T.B_DAYS}: {esc(c['days_he'] or T.MISSING)}</div></div>")
        site = (f"<div class='box'><h3>{T.B_SITE}</h3><div class='big'>{esc(c['onsite_contact_name'] or T.MISSING)}</div>"
                f"<div class='line big'><span dir='ltr'>{esc(c['onsite_contact_phone'] or '')}</span></div>"
                + (f"<div class='line muted'>{esc(c['receiving_restrictions'])}</div>" if c["receiving_restrictions"] else "")
                + "</div>")
        invoice = (f"<div class='box'><h3>{T.B_INVOICE}</h3><div class='line'><b>{esc(c['legal_name'] or T.MISSING)}</b></div>"
                   f"<div class='line'>{T.B_TAX_ID} {esc(c['tax_id'] or T.MISSING)}</div>"
                   f"<div class='line'><span dir='ltr'>{esc(c['accounting_email'] or '')}</span></div>"
                   f"<div class='line muted'>{esc(c['payment_terms_he'] or '')}</div></div>")
        kosher = f"<div class='box'><h3>{T.B_KASHRUT}</h3><div class='kosher'>{esc(c['kashrut_he'] or T.MISSING)}</div></div>"
        body = f"<div class='grid'>{delivery}{site}{invoice}{kosher}</div>"
    if rows:
        th = "".join(f"<th>{h}</th>" for h in T.B_PRICE_HEADERS)
        trs = "".join(f"<tr class='{'fam' if r['family'] else ''}'><td>{esc(r['name'])}</td><td>{esc(r['size'] or '')}</td>"
                      f"<td class='p'><span dir='ltr'>{money(r['ex'])}</span></td>"
                      f"<td class='v'><span dir='ltr'>{money(r['inc'])}</span></td></tr>" for r in rows)
        prices = (f"<div class='prices'><h2>{T.B_PRICES}</h2><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>"
                  f"<div class='rest'>{T.B_REST.format(page=general_page)}</div></div>")
    else:
        prices = f"<div class='prices'><div class='rest'>{T.B_ONLY_GENERAL.format(page=general_page)}</div></div>"
    kind = "continued" if continued else "customer"
    return (f"<div class='page' data-customer='{esc(c['shopify_customer_id'])}' data-kind='{kind}'>"
            f"{_tab(c['region'])}{head}{body}{prices}{_foot(n, total, meta)}</div>")


def _general(chunk: list[dict], n: int, total: int, meta: dict) -> str:
    th = "".join(f"<th>{h}</th>" for h in T.GENERAL_HEADERS)
    trs = "".join(f"<tr><td>{esc(g['name_he'])}</td><td>{esc(g['size_label'] or '')}</td>"
                  f"<td><span dir='ltr'>{esc(g['barcode'] or '')}</span></td><td><span dir='ltr'>{esc(g['sku'])}</span></td>"
                  f"<td class='p'><span dir='ltr'>{money(g['price_ex_vat'])}</span></td>"
                  f"<td class='v'><span dir='ltr'>{money(g['price_inc_vat'])}</span></td></tr>" for g in chunk)
    return f"<div class='page list'><h1>{T.B_GENERAL}</h1><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>{_foot(n, total, meta)}</div>"


def _catalog(chunk: list[dict], n: int, total: int, meta: dict) -> str:
    cards = []
    for c in chunk:
        img = (f"<div class='img' style=\"background-image:url('{c['image']}')\"></div>" if c["image"]
               else f"<div class='img mono'>{esc(c['name_he'][:2])}</div>")
        sizes = "".join(f"<div class='row'><span>{esc(s['size'] or '')} · <span dir='ltr'>{esc(s['barcode'] or s['sku'])}</span></span>"
                        f"<span class='p' dir='ltr'>{money(s['price'])}</span></div>" for s in c["sizes"])
        cards.append(f"<div class='card'>{img}<div class='t'><b>{esc(c['name_he'])}</b>{sizes}</div></div>")
    return f"<div class='page list'><h1>{T.B_CATALOG}</h1><div class='cards'>{''.join(cards)}</div>{_foot(n, total, meta)}</div>"


def _parts(data: PackageData) -> tuple[list[str], list[tuple[str, object]]]:
    plan = plan_pages(data)
    total = len(plan)
    first_page = {p[0]["shopify_customer_id"]: i for i, (k, p) in enumerate(plan, start=1) if k == "customer"}
    general_page = next(i for i, (k, _) in enumerate(plan, start=1) if k == "general")
    parts = []
    for i, (kind, p) in enumerate(plan, start=1):
        if kind == "cover":
            parts.append(_cover(data.meta))
        elif kind == "guide":
            parts.append(_guide(data.meta, i, total))
        elif kind == "index":
            parts.append(_index(data.customers[p * INDEX_ROWS:(p + 1) * INDEX_ROWS], first_page, i, total, data.meta))
        elif kind == "divider":
            parts.append(_divider(p[0], p[1], i, total, data.meta))
        elif kind in ("customer", "continued"):
            parts.append(_customer(p[0], p[1], general_page, i, total, data.meta, continued=kind == "continued"))
        elif kind == "general":
            parts.append(_general(data.general[p * GENERAL_ROWS:(p + 1) * GENERAL_ROWS], i, total, data.meta))
        elif kind == "catalog":
            parts.append(_catalog(data.cards[p * CARDS_PER_PAGE:(p + 1) * CARDS_PER_PAGE], i, total, data.meta))
    return parts, plan


def _wrap(parts: list[str]) -> str:
    return (f"<!doctype html><html lang='he' dir='rtl'><head><meta charset='utf-8'><title>{T.PACKAGE_TITLE}</title>"
            f"<style>{tokens_css()}{font_face_css()}{CSS}</style></head><body>{''.join(parts)}</body></html>")


def binder_html(data: PackageData) -> tuple[str, list[tuple[str, object]]]:
    parts, plan = _parts(data)
    return _wrap(parts), plan


def page_doc(data: PackageData, page_no: int) -> str:
    """A one-page document for visual QA (1-based page number)."""
    parts, _ = _parts(data)
    return _wrap([parts[page_no - 1]])


def html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()], check=True, capture_output=True, timeout=900)


def pdf_pages(pdf_path: Path) -> int:
    return len(PdfReader(str(pdf_path)).pages)


def screenshot(html_doc: str, png_path: Path) -> None:
    src = png_path.with_suffix(".html")
    src.write_text(html_doc, encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--window-size=794,1123",
                    f"--screenshot={png_path}", src.resolve().as_uri()], check=True, capture_output=True, timeout=120)


def _mime(data: bytes) -> str:
    if data.startswith(b"\x89PNG"):
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def fetch_images(urls: dict[str, str], cache: Path) -> dict[str, str]:
    """sku -> data URI (Shopify CDN at 500px). Cached on disk; a failed download leaves the card's initials."""
    cache.mkdir(parents=True, exist_ok=True)
    out = {}
    for sku, url in urls.items():
        f = cache / hashlib.sha1(url.encode()).hexdigest()
        if not f.exists():
            try:
                with urllib.request.urlopen(url + ("&" if "?" in url else "?") + "width=500", timeout=60) as resp:
                    f.write_bytes(resp.read())
            except Exception as e:  # printed, never silent
                print(f"image skipped for {sku}: {e}")
                continue
        raw = f.read_bytes()
        out[sku] = f"data:{_mime(raw)};base64,{base64.b64encode(raw).decode()}"
    return out
```

- [ ] **Step 4: Run to verify it passes**

Expected: `Ran 53 tests … OK` (the Chromium test runs here — Chromium is installed).

- [ ] **Step 5: Visual QA of one customer page, the cover and a catalog page**

```bash
cd /home/user/gt-factory-os/scripts/distributor-handoff && .venv/bin/python - <<'EOF'
from pathlib import Path
from tests.test_render_pdf import data
from handoff import render_pdf
d = data(); _, plan = render_pdf.binder_html(d)
out = Path("out/qa"); out.mkdir(parents=True, exist_ok=True)
for i, (kind, _) in enumerate(plan, start=1):
    if kind in ("cover", "customer", "catalog"):
        render_pdf.screenshot(render_pdf.page_doc(d, i), out / f"p{i:02d}_{kind}.png")
print(sorted(p.name for p in out.glob("*.png")))
EOF
```
Open each PNG with the Read tool. Check: Hebrew renders in Rubik/Heebo (no boxes, no fallback serif); the customer number reads first; the region tab sits on the left edge at the region's height; prices keep `₪58.50` order; nothing overflows the page. Fix the CSS until all four checks pass, re-run the tests, then commit.

- [ ] **Step 6: Commit**

```bash
cd /home/user/gt-factory-os && git add scripts/distributor-handoff/handoff/render_pdf.py scripts/distributor-handoff/tests/test_render_pdf.py
git commit -m "feat(distributor-handoff): the printed binder"
```

---

### Task 12: Weekly update and the package command

**Files:**
- Create: `scripts/distributor-handoff/handoff/updates.py`
- Modify: `scripts/distributor-handoff/run.py` (add `package`, `update`)
- Test: `scripts/distributor-handoff/tests/test_updates.py`

**Interfaces:**
- Consumes: `PackageData`, `CUSTOMER_FIELDS`, `render_excel.sheet`, everything from Tasks 7–11.
- Produces: `updates.snapshot(data) -> dict`; `updates.diff(prev, cur) -> list[dict]`; `updates.update_workbook(changes, meta) -> Workbook`.

- [ ] **Step 1: Write the failing test**

`tests/test_updates.py`:
```python
import unittest

from handoff import copy_he as T
from handoff import updates


def snap(customers, prices, names=None):
    return {"meta": {"version": "2", "date_he": "01.10.2026"}, "customers": customers, "prices": prices, "names": names or {}}


BASE = {f: None for f in updates.CUSTOMER_FIELDS}


class DiffTest(unittest.TestCase):
    def test_changes_new_removed_and_prices(self):
        prev = snap({"1001": {**BASE, "place_name": "א", "city": "תל אביב"}, "1002": {**BASE, "place_name": "ב"}},
                    {"1001": {"A": "58.50", "B": "40.00"}, "1002": {}}, {"A": "FRESH 1 ליטר", "B": "מחית"})
        cur = snap({"1001": {**BASE, "place_name": "א", "city": "רמת גן", "last_order_on": "01.10.2026"},
                    "1003": {**BASE, "place_name": "ג"}},
                   {"1001": {"A": "55.00", "C": "10.00"}, "1003": {}}, {"C": "כוס"})
        rows = updates.diff(prev, cur)
        whats = [(r["gt_no"], r["what"]) for r in rows]
        self.assertIn((1001, "עיר"), whats)
        self.assertIn((1001, T.CHANGE_PRICE.format(product="FRESH 1 ליטר")), whats)
        self.assertIn((1001, T.CHANGE_PRICE_GONE.format(product="מחית")), whats)
        self.assertIn((1001, T.CHANGE_PRICE_NEW.format(product="כוס")), whats)
        self.assertIn((1003, T.CHANGE_NEW_CUSTOMER), whats)
        self.assertIn((1002, T.CHANGE_REMOVED), whats)
        self.assertNotIn((1001, "הזמנה אחרונה"), whats)

    def test_workbook(self):
        wb = updates.update_workbook([{"gt_no": 1001, "place_name": "א", "what": "עיר", "was": "תל אביב", "now": "רמת גן"}],
                                     {"version": "2", "date_he": "01.10.2026"})
        ws = wb[T.UPDATE_SHEET]
        self.assertTrue(ws.sheet_view.rightToLeft)
        self.assertEqual([c.value for c in ws[1]], T.UPDATE_HEADERS)
        self.assertEqual(ws.cell(row=2, column=5).value, "רמת גן")
```

- [ ] **Step 2: Run to verify it fails**

Expected: `ModuleNotFoundError: No module named 'handoff.updates'`.

- [ ] **Step 3: Implement `updates.py`**

```python
"""Weekly update (spec §9): what changed between two package snapshots."""
from __future__ import annotations

from openpyxl import Workbook

from . import copy_he as T
from .package import CUSTOMER_FIELDS, PackageData
from .render_excel import sheet

SKIP = {"last_order_on", "orders_per_month", "shopify_customer_id"}  # planning hints and keys are not changes


def snapshot(data: PackageData) -> dict:
    return {"meta": {"version": str(data.meta["version"]), "date_he": data.meta["date_he"]},
            "customers": {str(c["gt_no"]): {f: None if c[f] is None else str(c[f]) for f in CUSTOMER_FIELDS}
                          for c in data.customers},
            "prices": {str(c["gt_no"]): {s["sku"]: str(s["price_ex_vat"]) for s in data.specials.get(c["shopify_customer_id"], [])}
                       for c in data.customers},
            "names": {s["sku"]: (s["name_he"] + (f" {s['size_label']}" if s["size_label"] else ""))
                      for specials in data.specials.values() for s in specials}}


def diff(prev: dict, cur: dict) -> list[dict]:
    labels = dict(zip(CUSTOMER_FIELDS, T.CUSTOMER_HEADERS))
    names = {**prev.get("names", {}), **cur.get("names", {})}
    rows: list[dict] = []

    def add(no: str, place, what: str, was="", now="") -> None:
        rows.append({"gt_no": int(no), "place_name": place, "what": what, "was": was or "", "now": now or ""})

    for no, c in sorted(cur["customers"].items(), key=lambda kv: int(kv[0])):
        p = prev["customers"].get(no)
        if p is None:
            add(no, c.get("place_name"), T.CHANGE_NEW_CUSTOMER)
            continue
        for f in CUSTOMER_FIELDS:
            if f not in SKIP and p.get(f) != c.get(f):
                add(no, c.get("place_name"), labels[f], p.get(f), c.get(f))
        pp, cp = prev["prices"].get(no, {}), cur["prices"].get(no, {})
        for sku in sorted(set(pp) | set(cp)):
            name = names.get(sku, sku)
            if sku not in pp:
                add(no, c.get("place_name"), T.CHANGE_PRICE_NEW.format(product=name), "", f"₪{cp[sku]}")
            elif sku not in cp:
                add(no, c.get("place_name"), T.CHANGE_PRICE_GONE.format(product=name), f"₪{pp[sku]}", T.GENERAL_LIST)
            elif pp[sku] != cp[sku]:
                add(no, c.get("place_name"), T.CHANGE_PRICE.format(product=name), f"₪{pp[sku]}", f"₪{cp[sku]}")
    for no, p in sorted(prev["customers"].items(), key=lambda kv: int(kv[0])):
        if no not in cur["customers"]:
            add(no, p.get("place_name"), T.CHANGE_REMOVED)
    return sorted(rows, key=lambda r: r["gt_no"])


def update_workbook(changes: list[dict], meta: dict) -> Workbook:
    wb = Workbook()
    wb.remove(wb.active)
    sheet(wb, T.UPDATE_SHEET, T.UPDATE_HEADERS, [10, 26, 30, 26, 26],
          [[r["gt_no"], r["place_name"], r["what"], r["was"], r["now"]] for r in changes], meta=meta)
    return wb
```

- [ ] **Step 4: Add `package` and `update` to `run.py`**

Add to the imports:
```python
from handoff import package, render_excel, render_pdf, updates
```

Add these functions above `main`:
```python
def cmd_package(args) -> int:
    if not args.draft and cmd_gates(argparse.Namespace(g1_only=False)) != 0:
        print("gates failed — nothing leaves GT (use --draft for an internal preview)")
        return 1
    today = date.today()
    calendar = _j(ROUTE_CALENDAR)
    meta = package.meta({"version": args.version, "date_he": today.strftime("%d.%m.%Y"),
                         "switch_date_he": date.fromisoformat(args.switch_date).strftime("%d.%m.%Y"),
                         "contact_name": args.contact_name, "contact_phone": args.contact_phone}, calendar)
    with db.connect() as conn:
        book = [r for r in db.load_book(conn).values() if r.active]
        matrix = db.price_matrix(conn)
        lrows = db.list_prices(conn)
    _, _, img_urls = shopify.barcode_maps(_j(RAW / "variants.json"))
    general_skus = {r["sku"] for r in lrows if r["general"] and r["active"]}
    images = render_pdf.fetch_images({s: u for s, u in img_urls.items() if s in general_skus}, RAW / "images")
    only = {int(x) for x in args.only.split(",")} if args.only else None
    data = package.build_package_data(book, matrix, lrows, _j(ZONES), calendar, meta, args.region, images, only)
    tag = "update" if only else (args.region or "all")
    out = OUT / f"v{args.version}_{today:%Y%m%d}_{tag}"
    out.mkdir(parents=True, exist_ok=True)
    xlsx = out / f"GT_customers_prices_v{args.version}.xlsx"
    render_excel.build_workbook(data).save(xlsx)
    render_excel.write_csvs(data, out)
    doc, plan = render_pdf.binder_html(data)
    (out / "binder.html").write_text(doc, encoding="utf-8")
    pdf = out / f"GT_binder_v{args.version}.pdf"
    render_pdf.html_to_pdf(out / "binder.html", pdf)
    problems = gates.g4_integrity([c["shopify_customer_id"] for c in data.customers], render_excel.customer_ids(xlsx),
                                  [p[0]["shopify_customer_id"] for k, p in plan if k == "customer"])
    pages = render_pdf.pdf_pages(pdf)
    if pages != len(plan):
        problems.append(f"PDF: {pages} עמודים, צפוי {len(plan)}")
    _dump(out / "snapshot.json", updates.snapshot(data))
    _dump(out / "manifest.json", {"customers": len(data.customers), "pages": pages, "draft": args.draft, "problems": problems})
    print(f"package → {out} · customers {len(data.customers)} · pages {pages} · G4 problems {len(problems)}")
    for p in problems:
        print("  -", p)
    return 1 if problems else 0


def cmd_update(args) -> int:
    prev, cur = _j(Path(args.prev)), _j(Path(args.cur))
    changes = updates.diff(prev, cur)
    path = Path(args.cur).parent / f"GT_update_v{cur['meta']['version']}.xlsx"
    updates.update_workbook(changes, cur["meta"]).save(path)
    changed = sorted({r["gt_no"] for r in changes if r["what"] != updates.T.CHANGE_REMOVED})
    print(f"{len(changes)} changes → {path}")
    print(f"reprint binder pages: run.py package --only {','.join(map(str, changed))} ... (same version flags)")
    return 0
```

Add inside `main`, before `args = parser.parse_args(argv)`:
```python
    k = sub.add_parser("package")
    k.add_argument("--version", required=True, type=int)
    k.add_argument("--switch-date", required=True, help="YYYY-MM-DD")
    k.add_argument("--contact-name", required=True)
    k.add_argument("--contact-phone", required=True)
    k.add_argument("--region", choices=["center", "north", "south"])
    k.add_argument("--only", help="comma-separated GT numbers (binder pages for an update)")
    k.add_argument("--draft", action="store_true", help="internal preview; skips the gates, never sent")
    k.set_defaults(fn=cmd_package)
    u = sub.add_parser("update")
    u.add_argument("--prev", required=True, help="previous out/v…/snapshot.json")
    u.add_argument("--cur", required=True, help="current out/v…/snapshot.json")
    u.set_defaults(fn=cmd_update)
```

- [ ] **Step 5: Run to verify it passes**

Expected: `Ran 55 tests … OK`; `run.py --help` lists all nine subcommands.

- [ ] **Step 6: Commit and push**

```bash
cd /home/user/gt-factory-os && git add scripts/distributor-handoff/handoff/updates.py scripts/distributor-handoff/run.py scripts/distributor-handoff/tests/test_updates.py
git commit -m "feat(distributor-handoff): weekly update and the package command"
git push origin claude/shopify-customer-identifier-cwm1j1
```

---

### Task 13: CONTROLLER — decisions, form, gates, the center pilot, delivery

Never delegated. Depends on Tom's answers from Task 9.

- [ ] **Step 1: Record Tom's decisions**

Turn Tom's reply into `out/decisions_<date>.json` (format in Task 7). Catalog decisions (C1) are edits to `gt-factory-os-production-brain/docs/warehouses/catalog-truth.md` — commit them there ("general" → add a row to the right section with the TSV price; "not sold" → add to the negative section), then acknowledge the flag in the decisions file. Run:
```bash
cd /home/user/gt-factory-os/scripts/distributor-handoff
.venv/bin/python run.py decide out/decisions_<date>.json
.venv/bin/python run.py seed
.venv/bin/python run.py gates --g1-only
```

- [ ] **Step 2: Form and messages**

With Tom's approval of the message and questions: create the Google Form (or have Doreen create it) with `copy_he.FORM_QUESTIONS` verbatim, question 1 prefilled; take its prefill link and replace the two prefilled answers with `{gt_no}` and `{place}`. Then:
```bash
.venv/bin/python run.py messages --form-link "<prefill link>" --sender "<Tom's choice>" --switch-date <YYYY-MM-DD> --region center
```
`SendUserFile` `out/messages.html` to Tom for Doreen/Alex. After responses arrive: export the responses sheet as CSV, then
```bash
.venv/bin/python run.py import-form <responses.csv>
.venv/bin/python run.py seed
.venv/bin/python run.py gates
```
G2 problems become Doreen's call list (only those customers).

- [ ] **Step 3: Build the center pilot**

When `gates` exits 0 for the center region's customers:
```bash
.venv/bin/python run.py package --version 1 --region center --switch-date <YYYY-MM-DD> --contact-name "<name>" --contact-phone "<phone>"
```
Expected: exit 0, `G4 problems 0`.

- [ ] **Step 4: Hand check 3/3**

Pick 3 random center customers from the package. For each, compare every field and every special price in the Excel and on its binder page against Shopify (customer + last orders) and Green Invoice (client + latest invoice). 3/3 or stop and fix the cause.

- [ ] **Step 5: Deliver to Drive and report**

Upload the Excel, the PDF and the three CSVs to a private Google Drive folder (`mcp__Google_Drive__create_file`), not shared with anyone. Report to Tom: the Drive link, counts (customers, special prices, pages), the gates' results, and the one next action — sitting with Ice Dream's clerk for the first 10 customers.

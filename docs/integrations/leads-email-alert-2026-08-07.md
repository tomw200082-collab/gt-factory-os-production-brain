# Lead-arrival email alert — diagnosis and repair

**Date:** 2026-08-07 · **Requested by:** Tom ("רק מייל בכל פעם שליד נכנס")
**Systems touched:** Make (team `1240098`), Google Sheets, Gmail. **No** Postgres, **no**
`stock_ledger`, **no** factory-os core schema, **no** customer-facing send.

> Findings doc, not authority. Records what was inspected, what was changed, and what is
> still blocked on Tom. Does not promote anything to authority and does not open a module.

---

## 1. Ask

An email to `tom@gteveryday.com` every time a new lead arrives. Internal notification only —
nothing is sent to the lead. `SALES_CUSTOMER_OUTREACH_WRITE_ENABLED` is untouched and stays
`false`; it does not govern this path.

## 2. What already existed

Make team `1240098` has a folder **"GT Sales Pipeline"** (`folderId 324562`) containing three
scenarios, **all inactive, all with `executions: 0` — none has ever run**:

| ID | Scenario | Shape | State |
|---|---|---|---|
| 5174396 | `GT Leads — Instant` | Facebook Lead Ads → Sheets `LEADS_RAW` → error-path email | inactive |
| 5195363 | `GT — התראת ליד חדש` | Sheets `watchRows` → Gmail, every 900s | inactive, `isinvalid: true` |
| 5176271 | `GT Leads — Health Check` | Sheets → router → email | inactive |

Nothing had to be built from scratch. The alert path existed and was broken.

## 3. Root cause of "no leads since June"

**The Facebook OAuth connection expired on `2026-06-07T20:37:12Z`. The last lead in the
sheet is dated `07/06/2026`.** Same day. Lead intake did not decay — it was cut at the moment
the token died.

All three Facebook connections on the team are expired:

| Connection | ID | Expired | In use by |
|---|---|---|---|
| `gteveryday` | 6309050 | **2026-06-07** | `GT Leads — Instant` |
| `My Facebook connection` | 6309131 | 2026-05-30 | — |
| `tom witt` | 6228080 | 2026-05-26 | — |

The email side is healthy: Gmail `new leads` (6308857) valid to **2027-02-03**, Google
Restricted (6228926) to **2026-10-09**, Google (6228582) no expiry.

The Facebook webhook itself is still registered and live — hook `2797155`, `enabled: true`,
`gone: false`, bound to page `1939072889681856` / form `1656468138571162`, `queueCount: 0`.
Only the OAuth credential behind it is dead.

## 4. Defects found in the alert scenario (5195363)

Verified against real rows in the watched tab, not inferred.

**Defect A — template variables were never wrapped.** The HTML body and subject carried bare
integers instead of references: the subject was literally `🟢 ליד חדש: 14 | 15`. Every
delivered email would have read "14" and "15" in place of the business and contact name.

**Defect B — every field index was off by one (+1).** The template was written against a
1-based reading of the columns while Make's interface for this module is 0-based.

Confirmed against row `l:985104160866442`, where index `13` holds `שרונה בית קפה` (business)
and `14` holds `קובי` (contact):

| Field in email | Pointed at | Actually holds | Corrected to |
|---|---|---|---|
| שם העסק | 14 | שם מלא | **13** |
| איש קשר | 15 | email | **14** |
| אימייל | 16 | מספר טלפון | **15** |
| טלפון | 17 | city | **16** |
| עיר | 18 | lead_status | **17** |
| מודעה | 4 | adset_id | **3** |
| קמפיין | 8 | form_id | **7** |
| מנהל/בעלים | 13 | שם העסק | **12** |

**Defect C — `p:` prefix on phone numbers.** Values are stored as `p:+972532308708`, so the
`tel:` link could never dial. Now stripped via `{{replace(1.16; "p:"; "")}}`.

## 5. Architectural gap — still open, needs Tom's decision

The writer and the watcher point at **different spreadsheets**:

- `GT Leads — Instant` **writes** to `1oXC9Ce…` — "GT Sales Pipeline CRM", tab `LEADS_RAW`
- `GT — התראת ליד חדש` **watches** `1G2HpMp…` — "לידים GT", tab `לידים נכנסים`

Their column layouts differ entirely. Even with both scenarios switched on and every defect
above fixed, the alert would still never fire, because the lead lands in a sheet nobody is
watching.

Spreadsheet `1G2HpMp…` ("לידים GT") holds two tabs:

| Tab | Layout | Rows | Latest |
|---|---|---|---|
| curated | `סטטוס \| תאריך \| שם העסק \| שם מלא \| טלפון \| אימייל \| עיר \| בעלים? \| מודעה \| הערות` | ~248 | **07/06/2026** |
| `לידים נכנסים` | 26 raw Facebook columns | ~51 | **04/05/2026** |

Both tabs stop before today (2026-08-07), consistent with §3.

**Unresolved:** all three Make scenarios have `executions: 0`, so **something other than Make
wrote these rows** — a native Facebook integration, another automation account, or manual
paste. That writer is unidentified. Wiring the alert to the wrong tab means silence.

**Recommendation:** point the alert at whichever tab is the real system of record for leads.
The curated tab is the one Tom actually works in and the one with the freshest data; the raw
tab is the one the alert's column map already matches. Not decided here — picking the CRM
layout is Tom's call, not a technical detail.

## 6. What was changed

**Make scenario 5195363 `GT — התראת ליד חדש` — blueprint updated** (`lastEdit`
`2026-08-07T16:03:15.793Z`):

- all field references wrapped and re-pointed per §4 (Defects A + B)
- `tel:` and `mailto:` links now resolve; `p:` prefix stripped (Defect C)
- trigger `limit` 2 → 10, so a burst of leads is not left behind between polls
- `sequential: true`, so alerts arrive in lead order

The scenario **remains inactive**. Nothing was switched on. No email was sent. The visual
design of the original email was preserved as-is.

**Not caused by this change:** `isinvalid: true` was already set before the edit — it is
visible in the first inventory of the folder, prior to any write.

## 7. Blocked on Tom — cannot be done from here

1. **Reconnect Facebook.** OAuth re-authorization happens in a browser session. Until then no
   Facebook-triggered scenario can run, whatever else is fixed.
2. **Set the trigger's starting row, then activate.** A `watchRows` trigger has no starting
   pointer until one is chosen, and that pointer has no field in the blueprint — it is only
   settable in the Make UI. This is also the safety gate: choosing **"from now on"** rather
   than the first row is what prevents ~51 historical rows from firing ~51 emails at once.
   This is why activation was deliberately left undone rather than automated.
3. **Decide the system-of-record tab** (§5), so writer and watcher agree.

## 8. Governance

- No new module opened. `sales` Amendment A (PR #98, `sales_core.lead` et al.) remains
  **AWAITING TOM**; nothing here depends on it or presumes it.
- No frozen flag or code sentinel touched.
- `stock_ledger`, `balance_anchors`, and all factory-os core schema untouched.
- The single external write was a blueprint edit to an **inactive** scenario in Tom's own Make
  account — reversible, single-scope, zero runtime effect while inactive.
- No customer-facing send; the only recipient in the scenario is `tom@gteveryday.com`.

## 9. Verification status

Honest accounting, per the evidence standard:

- **Verified by inspection:** connection expiry dates, hook liveness, scenario states, both
  tabs' real contents and column order, the +1 offset confirmed against a named row, and the
  updated blueprint re-fetched after the write showing the corrected references.
- **Not verified end-to-end:** no email has been delivered, because the scenario is inactive
  and the Facebook connection is dead. **This is not proof the alert works.** Proof requires a
  real lead arriving after §7 is done, and the resulting email read in the inbox.

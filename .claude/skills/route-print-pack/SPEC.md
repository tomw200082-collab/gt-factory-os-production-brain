# SPEC — route-print-pack stock-movement detection

> caveman-encoded. §G goal · §C constraint · §I interface · §V invariant · §T task · §B bug · §? unknown.
> sharpened via 2x /ck:grill (Tom, 2026-06-29). spec sole mutator.
> HARD LAW (both caps): never write `stock_ledger` direct. all stock moves → inbox → human approve (sanctioned append). skill PROPOSES only.

---

## §G goal

- **G1 FG-OUT detect** — route-pack auto-detect LW stop w/ 0 `order_items` that maps to outbound GI doc w/ product lines (delivery-note shipped w/o Shopify/LW link) → surface + propose FG decrement. (live case 2026-06-29: "אלי אברהמי - תעודת שילוח 20269", 0 LW items, GI 20269 = 4 product lines.)
- **G2 RM goods-receipt** — channel-agnostic RM/component intake. route-pack feeds it from LW supplier-pickup stops, but LW = ONE channel of many (most supplier arrivals have NO LW event).

## §C constraint

### shared
- **C0** never INSERT/UPDATE `stock_ledger` direct. propose → inbox pending approval → human enters/confirms line(s) → sanctioned approve mutation does the append. (CLAUDE.md "stock truth sacred".)
- **C0b** never invent qty. unmapped / conflicting → "needs decision" line inside same proposal, never silent drop, never guess.
- **C0c** every proposal idempotent + reversible + audited.

### C1 FG-OUT (G1)
- **C1.1** action = flag in summary + file pending FG-OUT inventory-movement approval. ledger only on human approve.
- **C1.2** trigger = stop has linked GI doc containing product lines whose barcode maps to FG item. no GI-w/-products, or note=pickup/check/exchange → excluded.
- **C1.3** item master = sole authority. qty convert deterministic via item `case_pack`/`sales_uom`/`base_fill_qty_per_unit`. GI pack-descriptor matches master → auto-close line. GI vs master conflict, OR barcode→pack-item vs unit-item ambiguity → "needs decision" line. barcode unmapped → "unidentified" line.
- **C1.4** GI binding tiered: (1) explicit doc# parsed from stop title/note ("תעודת שילוח NNNNN") → (2) GI link on task driver_note/notes → (3) `wp_order_id`. no single unambiguous doc → "needs decision".
- **C1.5** dedup: `idempotency_key` = GI doc id. re-run + future `LIONWHEEL_FG_OUT_BRIDGE` never double-post same doc.
- **C1.6** v1 scope NARROW: only (0 `order_items`) AND (bound to OUTBOUND doc: delivery-note / tax-invoice = goods leaving) → FG-OUT. credit/return/quote → excluded + flagged (wrong sign / not delivery).

### C2 RM-GR (G2)
- **C2.1** action = pending GR proposal → inbox. RM posts only on human approve, via existing `GR_POSTED` path. qty never invented.
- **C2.2** anchor = the COMPONENT (RM item). supplier = secondary metadata, non-blocking, NOT authority (suppliers swap often). free-text supplier allowed.
- **C2.3** component id tiered: (1) linked supplier doc/GI line → component → (2) procurement-spec store (goods-receipt-from-invoice already captures supplier catalog spec) → (3) empty/flagged → human picks component at approval.
- **C2.4** qty received ONCE, linked. GI = price-evidence; GR = physical-receipt. if invoice-GR already posted qty → pickup proposal shows "already received", does not add.
- **C2.5** single channel-agnostic GR model. triggers: (i) LW supplier-pickup [route-pack], (ii) supplier invoice/photo [goods-receipt-from-invoice], (iii) manual "arrived, no LW". first channel confirming physical arrival = canonical qty; others reconcile. route-pack must NOT assume LW is only inbound path.

## §I interface

- **I1** `classify_stop(stop) -> {kind: fg_out|rm_pickup|delivery|check_pickup|exchange|none, gi_doc?, confidence}` — read-only over LW task + GI.
- **I2** `resolve_lines(gi_doc) -> [{barcode, item_id?, master_qty?, raw_qty, raw_desc, status: ok|conflict|unmapped}]` — deterministic master-data convert (C1.3).
- **I3** `propose_fg_out(stop, gi_doc, lines) -> inbox pending approval` — idempotency_key = gi_doc.id (C1.5).
- **I4** `propose_gr(arrival, component?, supplier?, qty?) -> inbox pending approval` — component-centric, supplier optional (C2.2).
- **I5** existing sanctioned append paths unchanged: FG-OUT → inventory-movement approve mutation; RM-GR → `GR_POSTED`. skill never bypasses.

## §V invariant (verify)

- **V1** no code path writes `stock_ledger` outside the sanctioned approve mutation. grep: skill never imports a ledger INSERT.
- **V2** every emitted proposal carries idempotency_key; re-run on same date+doc emits 0 new proposals (dedup proven).
- **V3** qty on any auto-closed line = master-derived (`case_pack`×cases or 1:1 by UOM), never parsed from free text.
- **V4** conflict/unmapped line never auto-decrements — always rendered as needs-decision/unidentified in the proposal.
- **V5** FG-OUT only on outbound doc; a credit/return doc never yields a negative FG decrement.
- **V6** RM-GR qty posts once per physical arrival across all 3 channels (no double count vs invoice-GR).

## §T task

| id | task | dep | status |
|----|------|-----|--------|
| T1 | `classify_stop` + outbound-doc/pickup discrimination (C1.2,C1.6,C2.2) | - | todo |
| T2 | `resolve_lines` deterministic master convert + conflict/unmapped tagging (C1.3) | T1 | todo |
| T3 | GI binding tiered + doc# parse from stop title (C1.4) | T1 | todo |
| T4 | `propose_fg_out` → inbox pending approval, idempotent on GI doc id (C1.1,C1.5) | T2,T3 | todo |
| T5 | component-centric `propose_gr` + tiered component id (C2.1,C2.3) | T1 | todo |
| T6 | channel-agnostic GR model + cross-channel dedup key (C2.4,C2.5) | T5 | todo |
| T7 | summary/email surfacing of both proposal kinds | T4,T5 | todo |
| T8 | tests: V1–V6, incl. 2026-06-29 live fixtures (20269 FG-OUT, י.ש.ר אריזות RM pickup) | T4,T6 | todo |

## §B bug

| id | cause | fix | §V added |
|----|-------|-----|----------|
| (none yet) | | | |

## §? unknown (parked — never guessed)

- **?1** exact reconciliation key linking LW task ↔ supplier invoice ↔ component (C2.4) — where RM-truth breaks if wrong.
- **?2** UX for manual "arrived, no LW" GR entry (C2.5 trigger iii).
- **?3** partial-overlap stop (some LW `order_items` + extra GI lines) — out of G1 v1.
- **?4** credit/return reverse-direction handling (FG stock-IN) — out of G1 v1.
- **?5** reliable LW-recipient → supplier-master key (only if/when supplier metadata needs hardening; component anchor avoids blocking on it).

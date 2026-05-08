# LionWheel fixture fixtures

**Owner:** Window 4
**Consumers:** `src/lionwheel/__tests__/mapper.spec.ts`, `src/lionwheel/__tests__/replay.ts`

## Purpose

Deterministic, redacted JSON samples of LionWheel API response shapes, used to:

1. exercise the Zod schemas in `src/lionwheel/api-schemas.ts`
2. exercise the mapper in `src/lionwheel/mapper.ts`
3. provide a replay corpus for regression testing before and after runtime wiring

These fixtures are **not real LionWheel responses** captured verbatim. They are hand-authored to match the *shape* observed during the prior read-only inspection pass (see contract pack Appendix A) while:

- using fixture-labelled `wp_order_id` values (`#GT-FIXTURE-XXX`)
- using non-PII placeholder names / phones / addresses
- using plausible-but-redacted credentialed URL for `driver_note`
- using a small but realistic subset of fields (schemas are `.passthrough()`,
  so real responses with more fields will still parse)

## Redaction rules

| Field | Redaction |
|---|---|
| `recipient_name` | `"FIXTURE_RECIPIENT"` / `"FIXTURE_RECIPIENT_A"` / etc. |
| `phone`, `phone2` | `"+972500000000"` |
| `city` | `"FIXTURE_CITY"` |
| `street` | `"FIXTURE_STREET"` |
| `driver_str`, driver names | `"FIXTURE_DRIVER"` |
| `driver_note` (Green Invoice signed URL) | `"https://example.com/FIXTURE_REDACTED"` |
| `wp_order_id` | `"#GT-FIXTURE-NNN"` |
| `wp_order_key` | fixture integers prefixed with `99999...` |
| `email` | empty string |

`latitude` / `longitude` use plausible values inside Israel's bounding box but not real delivery addresses. `sku` uses GT's real SKU convention (`GT-HIB-LOW-1L`, etc.) because that is a master-data join key, not PII.

## Fixture catalogue

| File | Purpose | Shape |
|---|---|---|
| `task-show--completed-single-visit.json` | happy-path COMPLETED task, single visit, single order_item | `TaskShowResponse` |
| `task-show--canceled.json` | CANCELED task, exercises `is_terminal` derivation | `TaskShowResponse` |
| `tasks-by-order-id--split.json` | two tasks sharing one `wp_order_id`, exercises non-unique assumption | `TasksByOrderIdResponse` |
| `routes--populated.json` | one route with embedded visits, exercises `/routes` array form | `RoutesListResponse` |
| `routes--empty.json` | empty array, exercises "no routes today" path | `RoutesListResponse` |
| `error--401.json` | auth error body, observed verbatim shape | `LionWheelErrorBody` |
| `error--404.json` | not-found body, observed verbatim shape | `LionWheelErrorBody` |

## Adding a new fixture

1. Filename convention: `<endpoint-form>--<scenario>.json`.
2. Every field value must either (a) match an inspected real value or (b) be a redaction from the table above. Never invent field *names*.
3. Update this README's catalogue.
4. Add at least one assertion in `mapper.spec.ts` that touches the new fixture; otherwise the fixture is dead weight.

## What these fixtures intentionally do NOT do

- do not contain real customer or driver PII
- do not contain the real LionWheel API token
- do not contain real Green Invoice signed document URLs
- do not drive any live HTTP call
- do not serve as a source of truth for field completeness — the Zod schemas in `api-schemas.ts` are the source of truth; fixtures only exercise the observed happy paths and the enumerated edge cases (split, cancel, empty, error)

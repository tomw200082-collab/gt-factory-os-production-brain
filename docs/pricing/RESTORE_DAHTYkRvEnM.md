# Restoring the drinks catalog `DAHTYkRvEnM`

The catalog was repriced on 2026-08-26 from
`.claude/skills/drinks-pricelist/drinks_final_figures.json`. Canva exposes no
undo through the MCP API, so this is the only rollback that exists.

## What was captured

`docs/pricing/backups/2026-08-26_DAHTYkRvEnM_pre-repricing.json` holds the
original text of every element the repricing could touch, and nothing else:

- **48 drink pages** — cost, price and margin per page, each with its element
  locator, its textRegion count and its font size, plus the drink title and the
  figures-file page it maps to.
- **The summary table on page 60** — all four column strings, including the
  names column, which the repricing never writes.

That is everything a restore needs. The full structured dump the backup was
built from is session-local and runs to megabytes; it is not committed.

## Restoring

```bash
python3 scripts/canva_catalog_backup.py --emit-restore
```

Prints 147 ordered `edit-design` operations — 3 per drink page, 3 for the
summary columns — as JSON. Open an editing transaction on `DAHTYkRvEnM`, apply
them one page per call, then commit.

Cost and price use `find_and_replace_text` on the digits only. This is not a
style preference: those two elements each hold two textRegions, a normal-weight
`₪` followed by bold digits. `replace_text` collapses them into one region and
the shekel sign inherits the bold weight — a visible typographic change on every
page. Margin is a single region and uses `replace_text`.

The printed `find_text` values come from the figures file, i.e. what the page
says now. If the catalog has been repriced again since, pass the figures file
that matches the current state:

```bash
python3 scripts/canva_catalog_backup.py --emit-restore BACKUP --figures FIGURES
```

## Element ids are not stable

The locator ids in the backup were measured in the session that captured it.
Canva ids are per page and are not stable across sessions. Both modes of the
script therefore re-locate elements **by content pattern and font size**, never
by a stored id:

| Field | Pattern | Font size |
|---|---|---|
| cost | `^₪\d+\.\d\d$` | banded 40–80 (measured 48.0002) |
| price | `^₪\d+$` | banded 40–80 (measured 48.0002) |
| margin | `^\d\d%$` | banded 40–80 (measured 50.6668) |

The band matters — sibling pages vary in the last decimals. Before applying a
restore, re-read the design and confirm each page still yields exactly one match
per field. A page that yields anything else is a stop, not a guess.

## Proving nothing else moved

```bash
python3 scripts/canva_catalog_backup.py --verify BEFORE.json AFTER.json
```

Takes two raw structured dumps and reports every element whose characters
differ. After the 2026-08-26 repricing the differing set was exactly the 144
drink-page figure elements plus the 3 summary columns — 147 elements, zero
others.

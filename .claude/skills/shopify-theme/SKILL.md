---
name: shopify-theme
description: Building, uploading and previewing Shopify themes for GT — theme duplication, themeFilesUpsert, asset hosting and delivery, preview URLs, Liquid size limits, and the RTL/Hebrew traps that only appear once a design is flipped. Use when the work touches a Shopify theme, a Liquid section or layout, theme assets, a theme preview link, or turning a designed page into a live storefront. Triggers — "theme", "Liquid", "section", "preview", "אתר תדמית", "להעלות לשופיפיי", "לערוך את ה-theme", "תצוגה מקדימה".
---

# Shopify themes — GT

How GT's theme work is actually done, and the things that cost time the first
time. Store `greenteaeveryday.myshopify.com`, primary domain `gteveryday.com`.

## Architecture

**A theme is the whole storefront, not a page.** A theme containing only a
brand page breaks every product, collection, cart and account URL the moment it
is published. To put a new page on the store without that risk:

1. `themeDuplicate(id: <MAIN>, name: …)` → a full unpublished copy. Wait for
   `processing: false` before writing to it.
2. `themeFilesCopy` the existing `templates/index.json` to
   `templates/index.<name>.json` — it stays reachable at `?view=<name>` for
   side-by-side comparison instead of being lost.
3. Upsert the new `layout/`, `sections/`, `templates/index.json` and assets.
4. Everything else keeps rendering from the duplicated theme underneath.

**Assets and Liquid are separate worlds.** Files under `assets/` are served
statically — Liquid never runs over them. A `.js` asset cannot use
`asset_url`, so anything it needs from Liquid has to be handed to it: set a
custom property or a `window.*` global from the section, and have the asset
read that.

To derive an assets base URL inside Liquid:
`{{ 'some-file.css' | asset_url | split: '?' | first | remove: 'some-file.css' }}`
— `asset_url` returns protocol-relative with a `?v=` cache-buster, and both
have to come off.

## Traps

**`themeFilesUpsert` accepts `body.type: URL`.** Shopify fetches the file
server-side. Use it for everything — a public raw.githubusercontent.com URL for
text files, the original URL for remote images — and no base64 ever passes
through the agent. `type: BASE64` and `type: TEXT` also exist; prefer URL.

**`upsertedThemeFiles` comes back empty even on success.** It is not an error
signal. Verify by querying the theme's `files(filenames: […])` and checking
`size` and `contentType`.

**`?preview_theme_id=` sets a cookie, then redirects.** A client without a
cookie jar follows the redirect and gets the *live* theme back, which reads
exactly like "the upload did not work". `curl -c jar -b jar -L`. Tell humans to
open the full URL in a browser, and that the preview sticks to that browser
until it is closed — seeing the new site at a clean domain URL does not mean it
was published.

**Theme image assets are content-negotiated.** A `.webp` asset is served as a
PNG to any client that does not advertise webp — measured on one hero image:
94 KB webp vs 800 KB PNG. Never conclude an asset is bloated from a `curl`
without `Accept: image/webp`.

**The Shopify MCP blocks the dangerous ones.** `themePublish` and theme
deletion are refused, and `themeFilesUpsert`/`themeFilesCopy` are refused
against the live MAIN theme. Useful, but do not rely on it as the only guard.

**Size limits** (`shopify.dev/docs/storefronts/themes/architecture/limits`):
Liquid file (section/snippet/layout) **256 KB** · JSON template 512 KB ·
`settings_data.json` 1.5 MB · **25 sections per JSON template** · 50 blocks per
section.

## RTL / Hebrew

`dir="rtl"` flips normal flow for free. Three classes of thing it does not fix:

- **Transform-driven tracks.** A carousel that moves with `translateX(-N%)`
  over a flex row lands backwards once the row lays out RTL. Pin the track
  `direction:ltr` and put `direction:rtl` back on its contents — the maths then
  needs no change at all.
- **Absolutely positioned chrome.** `left`/`right` stay physical. Close
  buttons, accordion markers, dropdowns and prev/next all need mirroring, and
  prev/next need their chevron glyphs turned round too, not just their sides.
- **Directional photography.** A hero shot composed with the subject on one
  side and negative space on the other is composed *for* the original reading
  direction. Under RTL the copy moves onto the subject. Measure before
  assuming: edge-density centre-of-mass per image tells you which side the
  subject is on across a whole set in seconds.

**Two CSS mechanics that cost real time here:**

- **`url()` inside a CSS custom property resolves against the stylesheet that
  substitutes it, not the document.** A relative path set from JS as
  `--x: url('assets/a.webp')` and consumed in `theme.css` resolves relative to
  the CSS file. Absolute URLs are immune — which is why `asset_url` output is
  safe and a hand-rolled relative path is not.
- **`backdrop-filter` makes an element the containing block for its own
  `position:fixed` descendants.** A full-height fixed panel inside a blurred
  sticky nav collapses to the height of the bar. Disable the filter while the
  panel is open.

**To mirror a background image without mirroring the content on top of it:**
hand the image to CSS as a custom property and render it flipped on a
pseudo-element. Mirroring the element itself carries its children along.

## Canonical queries

```graphql
# themes + which is live
query { themes(first: 20) { nodes { id name role updatedAt } } }

# what is actually in a theme (glob works in filenames)
query { node(id: "gid://shopify/OnlineStoreTheme/<id>") {
  ... on OnlineStoreTheme { name role processing
    files(first: 250, filenames: ["assets/prefix-*"]) {
      pageInfo { hasNextPage endCursor }
      nodes { filename size contentType } } } } }
```

## OPEN

- No CI in `gt-site`; `tools/validate.js` is run by hand.
- Splitting a one-section page into editable sections with `{% schema %}` has
  not been done yet — until it is, nothing on the page is editable from the
  theme editor.

## LEARNED — append-only log

> Compact into the sections above when this passes ~30 lines, then clear it and
> stamp the header with the date.

- 2026-08-31 · First GT theme built this way (`gt-site` → theme 162206646513,
  unpublished). Everything in Traps and RTL above was found during that build.

---
name: shopify-theme
description: "Building and shipping GT's Shopify themes: the one ship path (whole GT set, push, drift check), preview links, Liquid limits, RTL/Hebrew traps. For any theme, Liquid section or storefront page work: \"אתר תדמית\", \"להעלות לשופיפיי\", \"לערוך את ה-theme\", \"תצוגה מקדימה\"."
---

# Shopify themes — GT

How GT's theme work is actually done, and the things that cost time the first
time. Store `greenteaeveryday.myshopify.com`, primary domain `gteveryday.com`.

## Architecture

**A theme is the whole storefront, not a page.** A theme containing only a
brand page breaks every product, collection, cart and account URL the moment it
is published. So GT's pages live as a small set of `gt-*` files inside a full
copy of the store theme, and everything else keeps rendering from underneath.

## Shipping — one path (gt-site `PUBLISH.md`, since 2026-09-27)

**Stage the whole GT set, push all of it, check the theme against it.**
`gt-site/tools/theme_ship.py` does the three in one command, with the Shopify
CLI and a Theme Access password (`SHOPIFY_CLI_THEME_TOKEN`):

```sh
python3 tools/theme_ship.py check <theme_id>                  # read-only diff
python3 tools/theme_ship.py push  <preview_id>                # ends "drift: 0"
python3 tools/theme_ship.py push  <live_id> --allow-live      # on Tom's word only
```

- **Never upload only the files a change touched.** That is how #22, #23 and
  #25 were merged but never live, and the landing pages ran two PRs behind,
  until 2026-09-27. The set (`gt_set()` plus `theme/assets.manifest.json`) is
  defined once, in the tool.
- **Never ship code by publishing a theme.** Publishing swaps every file,
  including anything an admin set in MAIN after the copy was taken (the
  favicon, 2026-09-25, lived only in MAIN). The live theme is pushed in place.
- **A preview is a copy of MAIN, taken when it is needed**, never a copy of
  another unpublished theme. Keep one and re-push the whole set to it each round.
- **Theme-owned stays theme-owned.** `config/settings_data.json` is never in
  the set, and each template's `sections.main.settings` is copied from the
  target when the set is staged.

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

**`theme push` deletes remote files that are not in the local folder** unless
it gets `--nodelete`. The tool always passes it and stages into a folder that
holds only the GT set. It still prints "Cleaning your remote theme [100%]";
that line deletes nothing when `--nodelete` is set (976 files before and after,
2026-09-27).

**A fresh duplicate is still copying when `theme duplicate` returns.** A push
that lands then is overwritten by the copy job: on 2026-09-27 five sections
reverted, and only the check caught it. The tool waits until `processing` is
false.

**Checksums.** The Admin API's `checksumMd5` is the md5 of the file for Liquid,
CSS, JS and images, the same as a CLI pull gives. JSON templates are not:
Shopify stores them minified and serves them with a `/* … */` header, so
compare them as parsed JSON. `upsertedThemeFiles` from `themeFilesUpsert` comes
back empty even on success; never read it as a result.

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
against the live MAIN theme. The CLI is the path that writes to live, and it
needs `--allow-live` to do so.

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

- Splitting a one-section page into editable sections with `{% schema %}` has
  not been done yet — until it is, nothing on the page is editable from the
  theme editor.

## LEARNED — append-only log

> Compact into the sections above when this passes ~30 lines, then clear it and
> stamp the header with the date.

- 2026-08-31 · First GT theme built this way (`gt-site` → theme 162206646513,
  unpublished). Everything in Traps and RTL above was found during that build.
- 2026-09-27 · Three merged PRs were missing from live because each upload sent
  only its own files. Replaced by the one ship path above (gt-site
  `tools/theme_ship.py`, `PUBLISH.md`).

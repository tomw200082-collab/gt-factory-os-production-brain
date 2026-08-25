# Movement 3 — the system

Built with `ui-ux-pro-max`. Everything below is computed from one number, not chosen
by eye.

**Scope note.** That skill is written for app UI. Its touch-target, animation,
navigation, dark-mode and safe-area rules do not apply to a static PDF and are not
carried. The rules that do apply and are honoured here: `visual-hierarchy` (hierarchy
by size, spacing and contrast — never colour alone), `font-scale`, `spacing-scale`
(4/8 rhythm), `number-tabular`, `line-height`, `line-length-control`,
`letter-spacing`, `whitespace-balance`, `truncation-strategy` (wrap, never truncate),
`contrast-readability`, `color-not-only`.

## The one number

The page is authored at 1080px wide and read fit-to-width on a ~390px phone.

```
390 / 1080 = 0.3611
```

Every size below is quoted with what it actually becomes in the reader's hand. This
is the whole reason the type looks absurdly large in the source and correct on the
phone. **Judge every screen from a PNG rendered at 390px, never from the 1080px
source.**

## Type scale

| Token | Design px | On a 390px phone | Face / weight | Purpose |
|---|---|---|---|---|
| `--t-legal` | 30 | 10.8 | Heebo 400 | the asterisk footnote only — **exempt from D4**, `.legal` |
| `--t-micro` | 36 | 13.0 | Heebo 400 | running footer, screen number. **The floor. Nothing smaller.** |
| `--t-panel` | 38 | 13.7 | Heebo 400 | ingredient panels |
| `--t-body` | 42 | 15.2 | Heebo 400 | default body |
| `--t-label` | 40 | 14.4 | Rubik 600, `letter-spacing: .18em` | spaced capitals — kickers, column heads |
| `--t-lead` | 48 | 17.3 | Heebo 400 | the one lead paragraph per screen |
| `--t-drink` | 62 | 22.4 | Rubik 600 | a drink's name |
| `--t-figure` | 72 | 26.0 | Rubik 700 | per-drink cost / price / margin / profit |
| `--t-section` | 88 | 31.8 | Rubik 700 | screen title |
| `--t-product` | 130 | 46.9 | Rubik 700 | a product name |
| `--t-cover` | 150 | 54.2 | Rubik 700 | the cover headline |
| `--t-hero` | 180 | 65.0 | Rubik 700 | the one hero figure on a hero screen |

Line-height: `1.5` on body and panels (per `line-height`), `1.08` on everything from
`--t-drink` up — display Hebrew at 130px does not want 1.5.

Measure: content column is 904px. At `--t-body` that is ~43 characters, inside the
35–60 the skill wants for mobile (`line-length-control`).

## Spacing scale

8px base, per `spacing-scale`. Section tiers per `section spacing hierarchy`.

| Token | px | Use |
|---|---|---|
| `--s-1` | 8 | inside a figure cluster |
| `--s-2` | 16 | label to its value |
| `--s-3` | 24 | between rows of a drink block |
| `--s-4` | 40 | between drink blocks |
| `--s-5` | 64 | between a heading and its content |
| `--s-6` | 96 | between sections |
| `--s-7` | 128 | around the single hero element |

## The 1920px vertical rhythm

```
  0    ┌──────────────────────────── screen top
  96   │  top margin
       │  ── content starts
       │
       │  content, 904px wide, 88px side margins
       │
 1824  │  ── content ends
       │  footer baseline: deck name · screen number, --t-micro, --muted
 1920  └──────────────────────────── screen bottom
```

Side margins 88px each. Content column 1080 − 176 = **904px**.
Every screen holds the same top/bottom margins so the deck does not breathe unevenly
when flicked through at speed.

## Hierarchy rules for a drink block

Strict order, top to bottom, every time:

1. Drink name — `--t-drink`, Rubik 600, `--ink`.
2. The four figures on one row — `--t-figure`, tabular, each under a `--t-label`
   spaced-caps column head. Cost in `--cost`, profit in `--profit`, price and margin
   in `--ink`.
3. One-line preparation — `--t-panel`, `--muted`.
4. A hairline in `--line` closing the block. **No box, no card, no shadow.**

The block is identified by its name in type, never by its colour — `color-not-only`.

## RTL conventions

- Root is `dir="rtl"`, `lang="he"`.
- Every figure, price and Latin token sits in `<span class="num">` carrying
  `direction: ltr; unicode-bidi: isolate` — exactly as `drinks-pricelist/style.css`
  does for `.latin`. Without it `₪12.34` can render `12.34₪` or reorder its digits,
  which ships a wrong number. This is landmine 11.
- `font-variant-numeric: tabular-nums` on every figure, per `number-tabular`, so
  columns of prices line up down the screen.
- Product names (`FRESH`, `DETOX`, `NAMASTEA`, `MATCHA`) are Latin and stay Latin.
  They are set as spaced capitals and isolated the same way.
- Text wraps. Nothing truncates — `truncation-strategy`.

## What carries identity

Size, weight and position carry hierarchy. Colour only ever reinforces it. Pull every
hue out of the deck and it still reads correctly — which is the test `color-not-only`
actually asks for, and the reason the contrast WARN on `--hue-matcha` is answered
rather than ignored.

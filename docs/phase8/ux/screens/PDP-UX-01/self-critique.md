---
run: PDP-UX-01
authored: 2026-05-09
status: SELF-CRITIQUE — 5 remaining visual weaknesses
---

# PDP-UX-01 Self-Critique

Five remaining visual weaknesses observed in after-screenshots at 1440×900, 1280×800, and 390px.

---

## 1. Today lane hidden at 1280px (comprehension failure)

**Viewport affected:** 1280×800 and narrower.

The timeline rail correctly shows today (SAT May 9) with a glowing cyan dot at the far right. But the corresponding day lane is not visible in the board at 1280px — it is horizontally scrolled off-screen. The 5-second comprehension contract requires "where is today?" to be answerable without scrolling. At 1280px a user sees overdue days but cannot see today's lane.

**Minimum fix:** Cap the board board at 7 evenly distributed columns when viewport width ≥ 1024px (each column ~130px minimum instead of 196px), switching to 196px min only at ≥ 1440px. This keeps all 7 lanes visible above 1024px.

---

## 2. No scroll affordance on the board at narrow viewports

**Viewport affected:** 1280×800 and 390px.

The board container uses `overflow-x-auto` with `minWidth: max-content`, which creates a horizontal scroll zone. But nothing visual signals that more lanes exist off-screen. At 390px, the two-column view is correct for mobile but there is no sticky week-strip or swipe affordance to navigate to other days.

**Minimum fix:** Add a `scroll-indicator` gradient fade on the right edge of the board container (a `::after` pseudo element on the outer div using `bg-gradient-to-r from-transparent to-bg`). On mobile, a sticky compact day-picker strip above the board (the "week strip selector" referenced in § 7 as optional for 768–1279px) would complete the intent.

---

## 3. KPI strip lacks semantic accent borders

**Viewport affected:** all.

The spec (§ 3 Layer 2) called for "4 micro-cards with semantic accent borders." The current implementation renders the four stats as plain large numbers separated by pipe-dividers. At a glance, `6 PLANNED` and `0 COMPLETED` look identical in weight — neither carries a semantic signal (warning for unfinished planned items, success for completed). The planned count in particular deserves an amber left-border or amber number color when >0 to visually reinforce the "work remaining this week" reading.

**Minimum fix:** Add `border-l-2 border-warning` to the PLANNED kpi cell and `border-l-2 border-success` to the COMPLETED cell. Optionally color the number text accordingly. No new tokens needed.

---

## 4. Load bar hue undifferentiated across overdue days

**Viewport affected:** 1440×900 and 1280×800.

All four overdue past days (Sun–Wed) show the same amber/warning load bar color. Because the current week has similarly-sized plans on each day, the bars look like a flat wall of amber with no information gradient. A viewer cannot quickly tell which day was heaviest or if there is a pattern in the load distribution.

**Minimum fix:** This is partially a data reality issue (similar qty each day), but the bar opacity or height-encoding is already applied. No code change needed — this critique is a flag for the next content cycle: when plan quantities vary significantly, the relative height encoding will become legible. Lower severity than the other items.

---

## 5. Cancelled card visual weight still competes with live plans

**Viewport affected:** all (SUN May 3 lane visible at 1440px).

The SUN lane contains 1 cancelled card (500 L, greyed, Hebrew cancel reason) and 2 live planned cards. The cancelled card occupies the full card width and nearly the same vertical height as live cards, with only opacity-70 and line-through on the quantity as distinguishing treatment. In a dense lane this creates visual noise — the eye has to parse the card to determine it's cancelled rather than immediately deprioritizing it.

**Minimum fix:** Reduce cancelled card height: collapse to a compact single-line summary row (`h-9 px-3 py-2` with quantity + strikethrough + cancel reason in one line, no action strip, no BOM toggle) behind a `isCancelled` branch in `ProductionJobCard`. This halves the vertical footprint of cancelled entries without removing them. Alternatively, move cancelled cards to a collapsible "Cancelled (N)" footer section at the bottom of each lane.

---

## Summary verdict

The page is **meaningfully better** than the pre-run state on every primary criterion from the handoff packet:
- ✅ Week reads as time (timeline rail)
- ✅ Today is unmistakable (cyan glow, SAT label, cyan notch)
- ✅ Overdue is urgent but not flooding (thin danger underlines, not red backgrounds)
- ✅ Empty days look intentional (centered Plus + "No production planned")
- ✅ Quantity-first card hierarchy (26px bold dominant, item name secondary)
- ✅ Honest materials state ("Pending data source" chip, no fake quantities)
- ✅ Build passes, typecheck passes, no new tokens added

Items 1 and 3 are the highest-priority post-run fixes. Items 2, 4, 5 are polish-level.

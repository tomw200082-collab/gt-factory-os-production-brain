# Design System Rules — GT Factory OS Portal

**Owner agent:** `visual-system-designer`
**Authoritative status:** DRAFT. Token values from portal/tailwind.config.ts (authoritative).
**Update rule:** Additions by visual-system-designer; token changes require Tom authorization.
**Release-gate relevance:** Token drift (hardcoded colors) = P2; inconsistent component variants = P1.

---

## What belongs here

- Canonical design system rules derived from the Operational Precision theme.
- Component variant registry.
- Spacing and typography scale rules.
- Dark mode coverage rules.

## What must never go here

- Microcopy or copy strings (→ CONTENT_AND_MICROCOPY_GUIDE.md).
- Backend contracts or DB semantics.
- Accessibility rules (→ ACCESSIBILITY_CHECKLIST.md).

---

## Operational Precision design system (from tailwind.config.ts)

The GT Factory OS portal uses a custom theme called "Operational Precision" with these locked values:

### Color tokens (authoritative from tailwind.config.ts)
- Accent: petrol teal (`brand-*` CSS custom properties)
- Background light: warm bone paper (`neutral-50` / `bone-*`)
- Background dark: warm graphite (`neutral-900`)
- All colors referenced as CSS custom properties (`var(--brand-500)`, etc.)
- **Hardcoded hex values in component files are always a drift violation.**

### Typography
- Base font size: 14px
- Type scale: Tailwind default (text-xs=12px, text-sm=14px, text-base=16px, text-lg=18px)
- Monospace for IDs, codes, and system-internal values only.
- No italic for emphasis in operational UI.
- Numbers in tables: `font-variant-numeric: tabular-nums` (`tabular-nums` Tailwind class).

### Spacing scale
- Use Tailwind spacing scale exclusively: `p-2` (8px), `p-4` (16px), `p-6` (24px), `gap-4` (16px).
- Arbitrary values (`gap-[13px]`, `mt-[7px]`) are violations unless documented with a comment.

### Border radius
- Cards and panels: `rounded-lg` (8px)
- Inputs and buttons: `rounded-md` (6px)
- Badges and chips: `rounded-full` or `rounded-sm`

### Shadows
- Card elevation: `shadow-sm`
- Modal/dialog: `shadow-lg`
- No `shadow-xl` or `shadow-2xl` in operational UI.

---

## Component variant registry (shadcn/ui based)

### Button variants
| Variant | Use case |
|---------|---------|
| `default` | Primary actions (Save, Submit, Approve) |
| `secondary` | Secondary actions (Cancel, Back, Keep) |
| `destructive` | Irreversible/destructive confirms (Delete, Cancel plan, Post final) |
| `ghost` | Low-emphasis actions (icon-only, inline edit toggle) |
| `outline` | Alternative secondary; use sparingly |
| `link` | Navigation only; not form actions |

**Rule:** Never use `default` variant for destructive actions. `destructive` variant is required.

### Badge/status chip variants
| Variant | Color | Use for |
|---------|-------|---------|
| Status OK | Green | Completed, Published, Approved |
| Status Warning | Amber | At Risk, Pending |
| Status Error | Red | Blocked, Rejected, Error |
| Status Neutral | Gray | Planned, Draft, Open |
| Status Info | Blue | Running, In Progress |

**Rule:** Status color must never be the sole differentiator — always pair with a label.

### Card patterns
- List card: thin border (`border`), `rounded-lg`, `p-4`
- Detail card / section: `rounded-lg`, `p-6`, `shadow-sm`
- Alert/notice card: colored left-border (`border-l-4`) + matching background tint

### Empty state
- Centered in the content area
- Muted icon (24–32px, `text-muted-foreground`)
- Heading: `text-base font-medium text-foreground`
- Body: `text-sm text-muted-foreground`
- CTA button: `variant="default"`, centered below body

---

## Dark mode rules

- All components must specify dark mode variants where they use color or background.
- `dark:` prefix Tailwind classes must mirror the light mode intent, not just invert.
- Test: every component must be legible in both light and dark at 4.5:1 contrast minimum.
- Dark mode is toggled via the existing system/class mechanism in globals.css.

---

## Forbidden patterns

- Hardcoded hex, rgb, or hsl color values in component files without a corresponding CSS custom property.
- `shadow-xl` or `shadow-2xl` in operational surfaces.
- Arbitrary spacing values without a documented reason.
- Custom font-size values (`text-[15px]`) — use the standard Tailwind scale.
- Multiple elevation levels on the same surface (flat + shadow-lg on adjacent components).

---

## Token change protocol

Proposing a new design token or changing an existing one:
1. `visual-system-designer` documents the proposal in a handoff packet.
2. Tom reviews and authorizes.
3. `portal-production-executor` applies the change to `tailwind.config.ts` and `globals.css`.
4. All affected components are updated in the same commit.
5. Dark mode variants are updated alongside light mode.

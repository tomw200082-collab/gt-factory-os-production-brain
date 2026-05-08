# /design-system-check

Invoke `visual-system-designer` to audit visual hierarchy, component consistency, and design
token hygiene on a named portal route or across the entire portal.

## Purpose

Checks for: token drift (hardcoded colors/values), component variant misuse, inconsistent spacing,
typographic hierarchy problems, and dark-mode coverage gaps. Produces system rules, not one-off fixes.

## Usage

```
/design-system-check <route>
/design-system-check /(ops)/goods-receipt
/design-system-check --tokens     # check global token usage only
/design-system-check --components # check component consistency only
```

## Agents involved

Primary: `visual-system-designer`

## Required outputs

```
## design-system-check — <Route or scope>

### Operational Precision token audit
| Token type | Violations | Finding |
|---|---|---|
| Colors (hardcoded) | <count> | VISUAL-NNN |
| Spacing (arbitrary) | <count> | ... |
| Dark mode gaps | <count> | ... |

### Component consistency
| Component | Correct variant | Issue |
|---|---|---|

### Proposed system rules
<rules to add to UX_OPERATING_PRINCIPLES.md or DESIGN_SYSTEM_RULES.md>

### Token changes required (Tom approval needed)
<list>

### Handoff packet
[YAML]
```

## Write policy

**Read-only.** Reports may be saved to `PRODUCTION/docs/phase8/dry-runs/`.
Token changes require Tom approval before any `tailwind.config.ts` edit.

## Not usable for

- Editing `tailwind.config.ts` or `globals.css` directly.
- Proposing new shadcn/ui components not already installed.
- Backend or DB changes.

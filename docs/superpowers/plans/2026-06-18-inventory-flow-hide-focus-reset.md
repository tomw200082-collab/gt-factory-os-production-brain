# Inventory Flow — Hide / Focus / Reset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let Tom hide individual product rows on `/planning/inventory-flow`, isolate a few via a focus mode, and restore them one-by-one or all at once — pure client state, no backend.

**Architecture:** A single `useRowVisibility` hook in `InventoryFlowClient` owns an ephemeral `hiddenIds` set plus focus-mode selection state. Visible rows = existing `filteredItems` minus `hiddenIds`. A new `RowVisibilityToggle` (per-row hide button / select checkbox) and `RowFocusControls` (Focus toggle + Hidden tray + Show all) drive the set. All new component props default off so other grid callers (supply view) are unchanged.

**Tech Stack:** Next.js 15 App Router (client components), React 19, TypeScript, Tailwind tokens + `btn` utility classes, lucide-react icons, Vitest 2 + @testing-library/react 16 (happy-dom), colocated `*.test.tsx`.

**Repo / cwd:** All paths are relative to the portal repo root (`window2-portal-sandbox`, executed in a worktree off `origin/main`). Run all test commands from that root.

## Global Constraints

- No backend/API/DB/migration/contract change. No URL-param change. Portal client state only.
- New props on `FlowGridDesktop`, `MobileCardStream`, `MobileItemCard` default off — supply view and every other caller render unchanged.
- `hiddenIds` is ephemeral `useState` — resets only on full page reload; must survive TanStack background refetch (never key it off `data`).
- Hidden tray lists items by **name, not id**.
- UI copy is English / LTR.
- Mobile hide button + checkbox touch target ≥44px (use `size="touch"`). Desktop uses `size="sm"`.
- The `Hidden (N)` pill + tray are always rendered while N>0 (hidden rows never silently lost).
- Existing risk/family/search filters keep working unchanged.
- Accessibility: hide button, checkbox, tray buttons carry aria-labels; keyboard operable; visible focus.
- Use existing token / `btn` classes (match `FilterBar.tsx` and the Refresh button in `InventoryFlowClient.tsx`). Do not invent class names — if unsure a class exists, grep `globals.css` / `tailwind.config.ts` / existing components first.

---

### Task 1: Visibility model — pure helpers + `useRowVisibility` hook

**Files:**
- Create: `src/app/(planning)/planning/inventory-flow/_lib/visibility.ts`
- Create: `src/app/(planning)/planning/inventory-flow/_lib/visibility.test.ts`
- Create: `src/app/(planning)/planning/inventory-flow/_lib/useRowVisibility.ts`
- Create: `src/app/(planning)/planning/inventory-flow/_lib/useRowVisibility.test.ts`

**Interfaces:**
- Produces:
  - `selectVisible<T extends { item_id: string }>(items: T[], hiddenIds: Set<string>): T[]`
  - `type EmptyStateKind = "all-hidden" | "no-match" | null`
  - `emptyStateKind(visibleCount: number, filteredCount: number): EmptyStateKind`
  - `useRowVisibility(): RowVisibility` where
    ```ts
    interface RowVisibility {
      hiddenIds: Set<string>;
      hiddenCount: number;
      isHidden: (id: string) => boolean;
      hide: (id: string) => void;
      restore: (id: string) => void;
      showAll: () => void;
      focusMode: boolean;
      enterFocus: () => void;
      cancelFocus: () => void;
      selectedIds: Set<string>;
      selectedCount: number;
      isSelected: (id: string) => boolean;
      toggleSelect: (id: string) => void;
      confirmFocus: (visibleIds: string[]) => void;
    }
    ```

- [ ] **Step 1: Write the failing tests for the pure helpers**

Create `_lib/visibility.test.ts`:
```ts
import { describe, it, expect } from "vitest";
import { selectVisible, emptyStateKind } from "./visibility";

describe("selectVisible", () => {
  const items = [{ item_id: "a" }, { item_id: "b" }, { item_id: "c" }];
  it("returns all items when nothing hidden", () => {
    expect(selectVisible(items, new Set())).toHaveLength(3);
  });
  it("removes hidden items by item_id, preserving order", () => {
    const r = selectVisible(items, new Set(["b"]));
    expect(r.map((i) => i.item_id)).toEqual(["a", "c"]);
  });
});

describe("emptyStateKind", () => {
  it("returns null when visible rows exist", () => {
    expect(emptyStateKind(3, 5)).toBeNull();
  });
  it("returns all-hidden when nothing visible but the filter had rows", () => {
    expect(emptyStateKind(0, 5)).toBe("all-hidden");
  });
  it("returns no-match when the filter itself produced nothing", () => {
    expect(emptyStateKind(0, 0)).toBe("no-match");
  });
});
```

- [ ] **Step 2: Run the helper tests, verify they fail**

Run: `npx vitest run src/app/\(planning\)/planning/inventory-flow/_lib/visibility.test.ts`
Expected: FAIL — cannot resolve `./visibility`.

- [ ] **Step 3: Implement the pure helpers**

Create `_lib/visibility.ts`:
```ts
// Pure, deterministic visibility helpers for the Inventory Flow grid.
// No React, no backend. Unit-tested in visibility.test.ts.

export function selectVisible<T extends { item_id: string }>(
  items: T[],
  hiddenIds: Set<string>,
): T[] {
  if (hiddenIds.size === 0) return items;
  return items.filter((it) => !hiddenIds.has(it.item_id));
}

export type EmptyStateKind = "all-hidden" | "no-match" | null;

/**
 * Distinguish "no rows because the operator hid them all" (recoverable via
 * Show all) from "no rows because the filter matched nothing".
 *   visibleCount  — rows after hidden-set removal
 *   filteredCount — rows after risk/family/search filters, before hiding
 */
export function emptyStateKind(
  visibleCount: number,
  filteredCount: number,
): EmptyStateKind {
  if (visibleCount > 0) return null;
  if (filteredCount > 0) return "all-hidden";
  return "no-match";
}
```

- [ ] **Step 4: Run the helper tests, verify they pass**

Run: `npx vitest run src/app/\(planning\)/planning/inventory-flow/_lib/visibility.test.ts`
Expected: PASS (5 tests).

- [ ] **Step 5: Write the failing tests for the hook**

Create `_lib/useRowVisibility.test.ts`:
```ts
import { describe, it, expect } from "vitest";
import { act, renderHook } from "@testing-library/react";
import { useRowVisibility } from "./useRowVisibility";

describe("useRowVisibility", () => {
  it("hide adds, restore removes, showAll clears", () => {
    const { result } = renderHook(() => useRowVisibility());
    act(() => result.current.hide("a"));
    act(() => result.current.hide("b"));
    expect(result.current.hiddenCount).toBe(2);
    expect(result.current.isHidden("a")).toBe(true);

    act(() => result.current.restore("a"));
    expect(result.current.isHidden("a")).toBe(false);
    expect(result.current.hiddenCount).toBe(1);

    act(() => result.current.showAll());
    expect(result.current.hiddenCount).toBe(0);
  });

  it("focus flow: enter, select keepers, confirm hides the rest and exits", () => {
    const { result } = renderHook(() => useRowVisibility());
    act(() => result.current.enterFocus());
    expect(result.current.focusMode).toBe(true);

    act(() => result.current.toggleSelect("a"));
    expect(result.current.isSelected("a")).toBe(true);
    expect(result.current.selectedCount).toBe(1);

    act(() => result.current.confirmFocus(["a", "b", "c"]));
    expect(result.current.focusMode).toBe(false);
    expect(result.current.isHidden("a")).toBe(false); // kept
    expect(result.current.isHidden("b")).toBe(true); // hidden
    expect(result.current.isHidden("c")).toBe(true);
    expect(result.current.selectedCount).toBe(0); // cleared
  });

  it("cancelFocus exits without hiding anything", () => {
    const { result } = renderHook(() => useRowVisibility());
    act(() => result.current.enterFocus());
    act(() => result.current.toggleSelect("a"));
    act(() => result.current.cancelFocus());
    expect(result.current.focusMode).toBe(false);
    expect(result.current.hiddenCount).toBe(0);
    expect(result.current.selectedCount).toBe(0);
  });

  it("toggleSelect is idempotent off-on-off", () => {
    const { result } = renderHook(() => useRowVisibility());
    act(() => result.current.enterFocus());
    act(() => result.current.toggleSelect("a"));
    act(() => result.current.toggleSelect("a"));
    expect(result.current.isSelected("a")).toBe(false);
    expect(result.current.selectedCount).toBe(0);
  });
});
```

- [ ] **Step 6: Run the hook tests, verify they fail**

Run: `npx vitest run src/app/\(planning\)/planning/inventory-flow/_lib/useRowVisibility.test.ts`
Expected: FAIL — cannot resolve `./useRowVisibility`.

- [ ] **Step 7: Implement the hook**

Create `_lib/useRowVisibility.ts`:
```ts
"use client";

import { useCallback, useState } from "react";

export interface RowVisibility {
  hiddenIds: Set<string>;
  hiddenCount: number;
  isHidden: (id: string) => boolean;
  hide: (id: string) => void;
  restore: (id: string) => void;
  showAll: () => void;
  focusMode: boolean;
  enterFocus: () => void;
  cancelFocus: () => void;
  selectedIds: Set<string>;
  selectedCount: number;
  isSelected: (id: string) => boolean;
  toggleSelect: (id: string) => void;
  /** Hide every id in visibleIds that is NOT currently selected; exit focus. */
  confirmFocus: (visibleIds: string[]) => void;
}

/**
 * Ephemeral per-session row visibility for the Inventory Flow grid.
 * State lives here (useState) so it survives TanStack background refetch
 * (the component does not remount) and resets only on a full page reload.
 */
export function useRowVisibility(): RowVisibility {
  const [hiddenIds, setHiddenIds] = useState<Set<string>>(() => new Set());
  const [focusMode, setFocusMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(() => new Set());

  const hide = useCallback((id: string) => {
    setHiddenIds((prev) => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
  }, []);

  const restore = useCallback((id: string) => {
    setHiddenIds((prev) => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  }, []);

  const showAll = useCallback(() => setHiddenIds(new Set()), []);

  const enterFocus = useCallback(() => {
    setSelectedIds(new Set());
    setFocusMode(true);
  }, []);

  const cancelFocus = useCallback(() => {
    setSelectedIds(new Set());
    setFocusMode(false);
  }, []);

  const toggleSelect = useCallback((id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  // Not memoized: must read the current `selectedIds` closure.
  const confirmFocus = (visibleIds: string[]) => {
    setHiddenIds((prev) => {
      const next = new Set(prev);
      for (const id of visibleIds) {
        if (!selectedIds.has(id)) next.add(id);
      }
      return next;
    });
    setSelectedIds(new Set());
    setFocusMode(false);
  };

  return {
    hiddenIds,
    hiddenCount: hiddenIds.size,
    isHidden: (id) => hiddenIds.has(id),
    hide,
    restore,
    showAll,
    focusMode,
    enterFocus,
    cancelFocus,
    selectedIds,
    selectedCount: selectedIds.size,
    isSelected: (id) => selectedIds.has(id),
    toggleSelect,
    confirmFocus,
  };
}
```

- [ ] **Step 8: Run the hook tests, verify they pass**

Run: `npx vitest run src/app/\(planning\)/planning/inventory-flow/_lib/useRowVisibility.test.ts`
Expected: PASS (4 tests).

- [ ] **Step 9: Commit**

```bash
git add "src/app/(planning)/planning/inventory-flow/_lib/visibility.ts" "src/app/(planning)/planning/inventory-flow/_lib/visibility.test.ts" "src/app/(planning)/planning/inventory-flow/_lib/useRowVisibility.ts" "src/app/(planning)/planning/inventory-flow/_lib/useRowVisibility.test.ts"
git commit -m "feat(inventory-flow): visibility model — hide/focus/reset hook + pure helpers"
```

---

### Task 2: `RowVisibilityToggle` — per-row hide button / select checkbox

**Files:**
- Create: `src/app/(planning)/planning/inventory-flow/_components/RowVisibilityToggle.tsx`
- Create: `src/app/(planning)/planning/inventory-flow/_components/RowVisibilityToggle.test.tsx`

**Interfaces:**
- Produces:
  ```ts
  interface RowVisibilityToggleProps {
    itemId: string;
    itemName: string;
    onHide?: (id: string) => void;           // absent => no hide button
    selectMode?: boolean;                    // true => render checkbox instead
    selected?: boolean;
    onToggleSelect?: (id: string) => void;
    size?: "sm" | "touch";                   // 'touch' => ≥44px (mobile)
  }
  export function RowVisibilityToggle(props: RowVisibilityToggleProps): JSX.Element | null
  ```

- [ ] **Step 1: Write the failing test**

Create `_components/RowVisibilityToggle.test.tsx`:
```tsx
import { afterEach, describe, it, expect, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom/vitest";
import { RowVisibilityToggle } from "./RowVisibilityToggle";

afterEach(() => cleanup());

describe("RowVisibilityToggle", () => {
  it("renders a hide button with an item-named aria-label and fires onHide", async () => {
    const onHide = vi.fn();
    const user = userEvent.setup();
    render(<RowVisibilityToggle itemId="a" itemName="Babka Red" onHide={onHide} />);
    await user.click(screen.getByRole("button", { name: /hide babka red/i }));
    expect(onHide).toHaveBeenCalledWith("a");
  });

  it("renders nothing interactive when onHide is absent and not in select mode", () => {
    render(<RowVisibilityToggle itemId="a" itemName="Babka Red" />);
    expect(screen.queryByRole("button")).toBeNull();
    expect(screen.queryByRole("checkbox")).toBeNull();
  });

  it("in select mode renders a checkbox reflecting `selected` and firing onToggleSelect", async () => {
    const onToggleSelect = vi.fn();
    const user = userEvent.setup();
    render(
      <RowVisibilityToggle
        itemId="a"
        itemName="Babka Red"
        selectMode
        selected={false}
        onToggleSelect={onToggleSelect}
        onHide={() => {}}
      />,
    );
    const cb = screen.getByRole("checkbox", { name: /select babka red/i });
    expect(cb).not.toBeChecked();
    await user.click(cb);
    expect(onToggleSelect).toHaveBeenCalledWith("a");
    // hide button must NOT show while selecting
    expect(screen.queryByRole("button", { name: /hide/i })).toBeNull();
  });
});
```

- [ ] **Step 2: Run the test, verify it fails**

Run: `npx vitest run src/app/\(planning\)/planning/inventory-flow/_components/RowVisibilityToggle.test.tsx`
Expected: FAIL — cannot resolve `./RowVisibilityToggle`.

- [ ] **Step 3: Implement the component**

Create `_components/RowVisibilityToggle.tsx`:
```tsx
"use client";

import { EyeOff } from "lucide-react";
import { cn } from "@/lib/cn";

interface RowVisibilityToggleProps {
  itemId: string;
  itemName: string;
  /** When absent, no hide button renders (keeps default callers unchanged). */
  onHide?: (id: string) => void;
  /** When true, render a select checkbox instead of the hide button. */
  selectMode?: boolean;
  selected?: boolean;
  onToggleSelect?: (id: string) => void;
  /** 'sm' = compact desktop hover control; 'touch' = ≥44px mobile target. */
  size?: "sm" | "touch";
}

export function RowVisibilityToggle({
  itemId,
  itemName,
  onHide,
  selectMode = false,
  selected = false,
  onToggleSelect,
  size = "sm",
}: RowVisibilityToggleProps) {
  const touch = size === "touch";

  if (selectMode) {
    return (
      <label
        className={cn(
          "inline-flex cursor-pointer items-center justify-center",
          touch ? "h-11 w-11" : "h-7 w-7",
        )}
      >
        <input
          type="checkbox"
          checked={selected}
          onChange={() => onToggleSelect?.(itemId)}
          aria-label={`Select ${itemName}`}
          className="h-4 w-4 cursor-pointer"
        />
      </label>
    );
  }

  if (!onHide) return null;

  return (
    <button
      type="button"
      onClick={(e) => {
        e.stopPropagation();
        onHide(itemId);
      }}
      aria-label={`Hide ${itemName}`}
      title={`Hide ${itemName}`}
      className={cn(
        "inline-flex items-center justify-center rounded-sm text-fg-faint transition-colors hover:bg-bg-muted hover:text-fg-muted",
        touch ? "h-11 w-11" : "h-7 w-7 opacity-50 hover:opacity-100",
      )}
    >
      <EyeOff size={touch ? 18 : 14} strokeWidth={2} aria-hidden />
    </button>
  );
}
```

- [ ] **Step 4: Run the test, verify it passes**

Run: `npx vitest run src/app/\(planning\)/planning/inventory-flow/_components/RowVisibilityToggle.test.tsx`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add "src/app/(planning)/planning/inventory-flow/_components/RowVisibilityToggle.tsx" "src/app/(planning)/planning/inventory-flow/_components/RowVisibilityToggle.test.tsx"
git commit -m "feat(inventory-flow): RowVisibilityToggle — per-row hide button / select checkbox"
```

---

### Task 3: `RowFocusControls` — Focus toggle + Hidden tray + Show all

**Files:**
- Create: `src/app/(planning)/planning/inventory-flow/_components/RowFocusControls.tsx`
- Create: `src/app/(planning)/planning/inventory-flow/_components/RowFocusControls.test.tsx`

**Interfaces:**
- Produces:
  ```ts
  interface RowFocusControlsProps {
    focusMode: boolean;
    onEnterFocus: () => void;
    onCancelFocus: () => void;
    onConfirmFocus: () => void;
    selectedCount: number;     // keepers ticked
    hideOtherCount: number;    // how many visible rows confirm will hide
    hiddenItems: { item_id: string; item_name: string }[];
    onRestore: (id: string) => void;
    onShowAll: () => void;
  }
  export function RowFocusControls(props: RowFocusControlsProps): JSX.Element
  ```
- Behaviour: confirm button is disabled when `selectedCount === 0` (must keep ≥1 — prevents accidental hide-all). Tray renders only when `hiddenItems.length > 0`.

- [ ] **Step 1: Write the failing test**

Create `_components/RowFocusControls.test.tsx`:
```tsx
import { afterEach, describe, it, expect, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom/vitest";
import { RowFocusControls } from "./RowFocusControls";

function setup(overrides: Partial<Parameters<typeof RowFocusControls>[0]> = {}) {
  const props = {
    focusMode: false,
    onEnterFocus: vi.fn(),
    onCancelFocus: vi.fn(),
    onConfirmFocus: vi.fn(),
    selectedCount: 0,
    hideOtherCount: 0,
    hiddenItems: [] as { item_id: string; item_name: string }[],
    onRestore: vi.fn(),
    onShowAll: vi.fn(),
    ...overrides,
  };
  render(<RowFocusControls {...props} />);
  return props;
}

afterEach(() => cleanup());

describe("RowFocusControls", () => {
  it("Focus button enters focus mode", async () => {
    const user = userEvent.setup();
    const props = setup();
    await user.click(screen.getByRole("button", { name: /^focus$/i }));
    expect(props.onEnterFocus).toHaveBeenCalledTimes(1);
  });

  it("confirm is disabled with 0 selected", () => {
    setup({ focusMode: true, selectedCount: 0, hideOtherCount: 5 });
    expect(screen.getByRole("button", { name: /hide the other 5/i })).toBeDisabled();
  });

  it("confirm fires when at least one is selected", async () => {
    const user = userEvent.setup();
    const props = setup({ focusMode: true, selectedCount: 2, hideOtherCount: 3 });
    await user.click(screen.getByRole("button", { name: /hide the other 3/i }));
    expect(props.onConfirmFocus).toHaveBeenCalledTimes(1);
  });

  it("Cancel exits focus mode", async () => {
    const user = userEvent.setup();
    const props = setup({ focusMode: true, selectedCount: 1, hideOtherCount: 2 });
    await user.click(screen.getByRole("button", { name: /cancel/i }));
    expect(props.onCancelFocus).toHaveBeenCalledTimes(1);
  });

  it("renders no Hidden tray when nothing is hidden", () => {
    setup({ hiddenItems: [] });
    expect(screen.queryByRole("button", { name: /hidden \(/i })).toBeNull();
  });

  it("Hidden tray lists item names and restores one", async () => {
    const user = userEvent.setup();
    const props = setup({
      hiddenItems: [
        { item_id: "a", item_name: "Babka Red" },
        { item_id: "b", item_name: "Muza 200ml" },
      ],
    });
    await user.click(screen.getByRole("button", { name: /hidden \(2\)/i }));
    expect(screen.getByText("Babka Red")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /restore babka red/i }));
    expect(props.onRestore).toHaveBeenCalledWith("a");
  });

  it("Show all resets everything", async () => {
    const user = userEvent.setup();
    const props = setup({ hiddenItems: [{ item_id: "a", item_name: "Babka Red" }] });
    await user.click(screen.getByRole("button", { name: /hidden \(1\)/i }));
    await user.click(screen.getByTestId("show-all"));
    expect(props.onShowAll).toHaveBeenCalledTimes(1);
  });
});
```

- [ ] **Step 2: Run the test, verify it fails**

Run: `npx vitest run src/app/\(planning\)/planning/inventory-flow/_components/RowFocusControls.test.tsx`
Expected: FAIL — cannot resolve `./RowFocusControls`.

- [ ] **Step 3: Implement the component**

Create `_components/RowFocusControls.tsx`. (Token/`btn` classes mirror `FilterBar.tsx`. If any class is uncertain, grep before substituting.)
```tsx
"use client";

import { useState } from "react";
import { Eye, EyeOff, RotateCcw } from "lucide-react";

interface RowFocusControlsProps {
  focusMode: boolean;
  onEnterFocus: () => void;
  onCancelFocus: () => void;
  onConfirmFocus: () => void;
  selectedCount: number;
  hideOtherCount: number;
  hiddenItems: { item_id: string; item_name: string }[];
  onRestore: (id: string) => void;
  onShowAll: () => void;
}

export function RowFocusControls({
  focusMode,
  onEnterFocus,
  onCancelFocus,
  onConfirmFocus,
  selectedCount,
  hideOtherCount,
  hiddenItems,
  onRestore,
  onShowAll,
}: RowFocusControlsProps) {
  const [trayOpen, setTrayOpen] = useState(false);
  const hiddenCount = hiddenItems.length;

  return (
    <div className="flex flex-wrap items-center gap-2">
      {!focusMode ? (
        <button
          type="button"
          onClick={onEnterFocus}
          className="inline-flex items-center gap-1.5 rounded-sm border border-border bg-bg-subtle px-2.5 py-1.5 text-xs font-medium text-fg-muted transition-colors hover:border-accent/40 hover:text-fg"
        >
          <Eye className="h-3.5 w-3.5" strokeWidth={2} aria-hidden />
          Focus
        </button>
      ) : (
        <div className="inline-flex items-center gap-2 rounded-sm border border-accent-border bg-accent-soft px-2.5 py-1.5 text-xs">
          <span className="text-fg-muted">Pick rows to keep</span>
          <button
            type="button"
            onClick={onConfirmFocus}
            disabled={selectedCount === 0}
            className="inline-flex items-center gap-1 rounded-sm border border-accent-border bg-bg-raised px-2 py-1 font-medium text-accent transition-opacity hover:shadow-sm disabled:cursor-not-allowed disabled:opacity-40"
          >
            <EyeOff className="h-3.5 w-3.5" strokeWidth={2} aria-hidden />
            Hide the other {hideOtherCount}
          </button>
          <button
            type="button"
            onClick={onCancelFocus}
            className="rounded-sm px-2 py-1 text-fg-muted transition-colors hover:text-fg"
          >
            Cancel
          </button>
        </div>
      )}

      {hiddenCount > 0 ? (
        <div className="relative">
          <button
            type="button"
            onClick={() => setTrayOpen((o) => !o)}
            aria-expanded={trayOpen}
            aria-haspopup="menu"
            className="inline-flex items-center gap-1.5 rounded-sm border border-border bg-bg-subtle px-2.5 py-1.5 text-xs font-medium text-fg-muted transition-colors hover:text-fg"
          >
            <EyeOff className="h-3.5 w-3.5" strokeWidth={2} aria-hidden />
            Hidden ({hiddenCount})
          </button>
          {trayOpen ? (
            <div
              role="menu"
              className="absolute right-0 z-40 mt-1 w-64 rounded-md border border-border bg-bg-raised p-1 shadow-lg"
            >
              <ul className="max-h-64 overflow-y-auto">
                {hiddenItems.map((it) => (
                  <li
                    key={it.item_id}
                    className="flex items-center justify-between gap-2 rounded-sm px-2 py-1 hover:bg-bg-subtle"
                  >
                    <span className="truncate text-xs text-fg">{it.item_name}</span>
                    <button
                      type="button"
                      onClick={() => onRestore(it.item_id)}
                      aria-label={`Restore ${it.item_name}`}
                      title="Restore"
                      className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-sm text-fg-faint transition-colors hover:bg-bg-muted hover:text-fg"
                    >
                      <RotateCcw className="h-3.5 w-3.5" strokeWidth={2} aria-hidden />
                    </button>
                  </li>
                ))}
              </ul>
              <div className="mt-1 border-t border-border/60 pt-1">
                <button
                  type="button"
                  data-testid="show-all"
                  onClick={() => {
                    onShowAll();
                    setTrayOpen(false);
                  }}
                  className="w-full rounded-sm px-2 py-1.5 text-left text-xs font-medium text-accent hover:bg-accent-soft"
                >
                  Show all
                </button>
              </div>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
```

- [ ] **Step 4: Run the test, verify it passes**

Run: `npx vitest run src/app/\(planning\)/planning/inventory-flow/_components/RowFocusControls.test.tsx`
Expected: PASS (7 tests).

- [ ] **Step 5: Commit**

```bash
git add "src/app/(planning)/planning/inventory-flow/_components/RowFocusControls.tsx" "src/app/(planning)/planning/inventory-flow/_components/RowFocusControls.test.tsx"
git commit -m "feat(inventory-flow): RowFocusControls — focus toggle + hidden tray + show all"
```

---

### Task 4: Wire the toggle into desktop + mobile rows

**Files:**
- Create: `src/app/(planning)/planning/inventory-flow/_lib/flowFixture.ts` (test-support fixture builder)
- Modify: `src/app/(planning)/planning/inventory-flow/_components/FlowGridDesktop.tsx` (props on `FlowGridDesktop` + `ItemRow`; render toggle in the sticky wrapper near the existing chevron)
- Modify: `src/app/(planning)/planning/inventory-flow/_components/MobileCardStream.tsx` (forward props)
- Modify: `src/app/(planning)/planning/inventory-flow/_components/MobileItemCard.tsx` (render toggle in the card; read the file first to place it)
- Create: `src/app/(planning)/planning/inventory-flow/_components/FlowGridDesktop.rowvis.test.tsx`

**Interfaces:**
- Consumes: `RowVisibilityToggle` (Task 2).
- Adds to `FlowGridDesktop`, `MobileCardStream`, `MobileItemCard` these OPTIONAL props (default off):
  ```ts
  onHide?: (id: string) => void;
  selectMode?: boolean;
  selectedIds?: Set<string>;
  onToggleSelect?: (id: string) => void;
  ```
  Desktop renders `<RowVisibilityToggle size="sm" .../>`; mobile renders `size="touch"`.

- [ ] **Step 1: Write the failing desktop wiring test + fixture**

Create `_lib/flowFixture.ts`:
```ts
import type { FlowItem } from "./types";

/** Test-support: a fully-populated single-day/single-week FlowItem. */
export function makeFlowItem(over: Partial<FlowItem> = {}): FlowItem {
  return {
    item_id: "a",
    item_name: "Babka Red",
    family: "BAKERY",
    sku_kind: "ITEM",
    supply_method: "MANUFACTURED",
    risk_tier: "healthy",
    days_of_cover: 30,
    effective_lead_time_days: 3,
    current_on_hand: 100,
    earliest_stockout_date: null,
    stockout_at_day_with_production: null,
    days_cover_with_production: 56,
    days: [
      {
        day: "2026-06-18",
        is_working_day: true,
        holiday_name_he: null,
        demand_lionwheel: 0,
        demand_forecast: 0,
        incoming_supply: 0,
        projected_on_hand_eod: 100,
        inflow_from_production: 0,
        incoming_supply_combined: 0,
        projected_on_hand_eod_with_production: 100,
        tier: "healthy",
        cell_tier_with_production: "healthy",
        shortfall_qty: 0,
        shortfall_qty_with_production: 0,
      },
    ],
    weeks: [
      {
        week_start: "2026-06-21",
        min_on_hand: 100,
        stockout_day: null,
        tier: "healthy",
        min_on_hand_with_production: 100,
        stockout_day_with_production: null,
        cell_tier_with_production: "healthy",
        max_shortfall_qty: 0,
      },
    ],
    ...over,
  };
}
```

Create `_components/FlowGridDesktop.rowvis.test.tsx`:
```tsx
import { afterEach, beforeAll, describe, it, expect, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom/vitest";
import { FlowGridDesktop } from "./FlowGridDesktop";
import { makeFlowItem } from "../_lib/flowFixture";

beforeAll(() => {
  // happy-dom lacks Element.scrollTo, which FlowGridDesktop calls on mount.
  // @ts-expect-error — test shim
  window.HTMLElement.prototype.scrollTo = vi.fn();
});

afterEach(() => cleanup());

describe("FlowGridDesktop row visibility wiring", () => {
  it("renders a hide button per row and fires onHide with the item id", async () => {
    const onHide = vi.fn();
    const user = userEvent.setup();
    render(<FlowGridDesktop items={[makeFlowItem()]} onHide={onHide} />);
    await user.click(screen.getByRole("button", { name: /hide babka red/i }));
    expect(onHide).toHaveBeenCalledWith("a");
  });

  it("renders a select checkbox per row in select mode", () => {
    render(
      <FlowGridDesktop
        items={[makeFlowItem()]}
        onHide={() => {}}
        selectMode
        selectedIds={new Set()}
        onToggleSelect={() => {}}
      />,
    );
    expect(
      screen.getByRole("checkbox", { name: /select babka red/i }),
    ).toBeInTheDocument();
  });

  it("renders no hide button when onHide is not passed (default callers unchanged)", () => {
    render(<FlowGridDesktop items={[makeFlowItem()]} />);
    expect(screen.queryByRole("button", { name: /hide babka red/i })).toBeNull();
  });
});
```

- [ ] **Step 2: Run the test, verify it fails**

Run: `npx vitest run src/app/\(planning\)/planning/inventory-flow/_components/FlowGridDesktop.rowvis.test.tsx`
Expected: FAIL — `onHide` prop not accepted / no hide button rendered.

- [ ] **Step 3: Add props to `FlowGridDesktop` and `ItemRow`, render the toggle**

In `FlowGridDesktop.tsx`:
1. Add import: `import { RowVisibilityToggle } from "./RowVisibilityToggle";`
2. Add to `FlowGridDesktopProps`:
   ```ts
   onHide?: (id: string) => void;
   selectMode?: boolean;
   selectedIds?: Set<string>;
   onToggleSelect?: (id: string) => void;
   ```
3. Destructure them in `FlowGridDesktop({ ... })` and pass each into `<ItemRow ... />`.
4. Add the same four to `ItemRowProps`, destructure in `ItemRow`.
5. Inside `ItemRow`, in the sticky wrapper `div` (the `sticky left-0 z-20` block that already holds the chevron), render the toggle top-right, above the chevron:
   ```tsx
   {(onHide || selectMode) ? (
     <span className="absolute right-1 top-1 z-30">
       <RowVisibilityToggle
         itemId={item.item_id}
         itemName={item.item_name}
         onHide={onHide}
         selectMode={selectMode}
         selected={selectedIds?.has(item.item_id) ?? false}
         onToggleSelect={onToggleSelect}
         size="sm"
       />
     </span>
   ) : null}
   ```

- [ ] **Step 4: Run the desktop test, verify it passes**

Run: `npx vitest run src/app/\(planning\)/planning/inventory-flow/_components/FlowGridDesktop.rowvis.test.tsx`
Expected: PASS (3 tests).

- [ ] **Step 5: Forward the props through mobile (read files first)**

Read `MobileCardStream.tsx` and `MobileItemCard.tsx`. Then:
1. In `MobileCardStream.tsx`: add the four optional props to `MobileCardStreamProps`, destructure, and pass them through to each `<MobileItemCard .../>` (`selected={selectedIds?.has(item.item_id) ?? false}`).
2. In `MobileItemCard.tsx`: add `onHide?`, `selectMode?`, `selected?`, `onToggleSelect?` to its props; import `RowVisibilityToggle`; render it in the card header/top-right with `size="touch"`:
   ```tsx
   {(onHide || selectMode) ? (
     <RowVisibilityToggle
       itemId={item.item_id}
       itemName={item.item_name}
       onHide={onHide}
       selectMode={selectMode}
       selected={selected}
       onToggleSelect={onToggleSelect}
       size="touch"
     />
   ) : null}
   ```
   Place it so it does not sit inside the card's navigation `<Link>` (so tapping hide does not navigate). If the whole card is a Link, render the toggle as a sibling outside the Link, or stop propagation (the toggle already calls `e.stopPropagation()` on hide).

- [ ] **Step 6: Typecheck the whole package**

Run: `npx tsc --noEmit`
Expected: no errors. (If `MobileItemCard` is wrapped in a Link such that the toggle cannot be a child, restructure per Step 5 note.)

- [ ] **Step 7: Run the full inventory-flow test set**

Run: `npx vitest run src/app/\(planning\)/planning/inventory-flow/`
Expected: PASS (all tasks 1–4 tests green).

- [ ] **Step 8: Commit**

```bash
git add "src/app/(planning)/planning/inventory-flow/_lib/flowFixture.ts" "src/app/(planning)/planning/inventory-flow/_components/FlowGridDesktop.tsx" "src/app/(planning)/planning/inventory-flow/_components/FlowGridDesktop.rowvis.test.tsx" "src/app/(planning)/planning/inventory-flow/_components/MobileCardStream.tsx" "src/app/(planning)/planning/inventory-flow/_components/MobileItemCard.tsx"
git commit -m "feat(inventory-flow): render hide/select toggle on desktop + mobile rows"
```

---

### Task 5: Integrate into `InventoryFlowClient` + "All rows hidden" empty state

**Files:**
- Modify: `src/app/(planning)/planning/inventory-flow/InventoryFlowClient.tsx`

**Interfaces:**
- Consumes: `useRowVisibility` (Task 1), `selectVisible` + `emptyStateKind` (Task 1), `RowFocusControls` (Task 3), the new grid/mobile props (Task 4).

- [ ] **Step 1: Add imports**

In `InventoryFlowClient.tsx`, add:
```ts
import { RowFocusControls } from "./_components/RowFocusControls";
import { useRowVisibility } from "./_lib/useRowVisibility";
import { selectVisible, emptyStateKind } from "./_lib/visibility";
```

- [ ] **Step 2: Call the hook and derive visible/hidden sets**

After `filteredItems` is computed, add:
```ts
const vis = useRowVisibility();

const visibleItems = useMemo(
  () => selectVisible(filteredItems, vis.hiddenIds),
  [filteredItems, vis.hiddenIds],
);

const hiddenItems = useMemo(
  () =>
    (data?.items ?? [])
      .filter((it) => vis.hiddenIds.has(it.item_id))
      .map((it) => ({ item_id: it.item_id, item_name: it.item_name })),
  [data, vis.hiddenIds],
);

const hideOtherCount = useMemo(
  () => visibleItems.filter((it) => !vis.isSelected(it.item_id)).length,
  [visibleItems, vis],
);
```

- [ ] **Step 3: Render `RowFocusControls` under `FilterBar`**

In the main render, immediately after `<FilterBar families={families} items={data.items} />`, add:
```tsx
<RowFocusControls
  focusMode={vis.focusMode}
  onEnterFocus={vis.enterFocus}
  onCancelFocus={vis.cancelFocus}
  onConfirmFocus={() => vis.confirmFocus(visibleItems.map((it) => it.item_id))}
  selectedCount={vis.selectedCount}
  hideOtherCount={hideOtherCount}
  hiddenItems={hiddenItems}
  onRestore={vis.restore}
  onShowAll={vis.showAll}
/>
```

- [ ] **Step 4: Swap `filteredItems` → `visibleItems` and branch the empty state**

Replace the existing `filteredItems.length === 0 ? (<EmptyState .../>) : isMobile ? (...) : (...)` block so it uses `visibleItems` for the grid/mobile streams and distinguishes the two empty reasons via `emptyStateKind(visibleItems.length, filteredItems.length)`:
```tsx
{(() => {
  const kind = emptyStateKind(visibleItems.length, filteredItems.length);
  if (kind === "all-hidden") {
    return (
      <div className="space-y-3">
        <EmptyState
          title="All rows hidden"
          description="You hid every row in view. Show all to bring them back."
        />
        <div className="flex justify-center">
          <button
            type="button"
            onClick={vis.showAll}
            className="btn btn-ghost btn-sm"
          >
            Show all
          </button>
        </div>
      </div>
    );
  }
  if (kind === "no-match") {
    return (
      <EmptyState
        title="No items match your filters"
        description={
          atRiskOnlyClient
            ? "No products at risk in the next 14 days. Toggle to All items to see the full view."
            : "No items match the current search or family filter."
        }
      />
    );
  }
  return isMobile ? (
    <MobileCardStream
      items={visibleItems}
      summary={summary}
      overlayEnabled={overlayEnabled}
      plannedByItemDate={plannedByItemDate}
      onHide={vis.hide}
      selectMode={vis.focusMode}
      selectedIds={vis.selectedIds}
      onToggleSelect={vis.toggleSelect}
    />
  ) : (
    <FlowGridDesktop
      items={visibleItems}
      overlayEnabled={overlayEnabled}
      plannedByItemDate={plannedByItemDate}
      plannedRows={plannedRows}
      onHide={vis.hide}
      selectMode={vis.focusMode}
      selectedIds={vis.selectedIds}
      onToggleSelect={vis.toggleSelect}
    />
  );
})()}
```
(If `btn btn-ghost btn-sm` is not the project's button class, match the Refresh button in this same file.)

- [ ] **Step 5: Typecheck**

Run: `npx tsc --noEmit`
Expected: no errors.

- [ ] **Step 6: Run the full inventory-flow suite + the whole project suite**

Run: `npx vitest run src/app/\(planning\)/planning/inventory-flow/`
Then: `npx vitest run`
Expected: all green (page client has no unit test — its logic is covered by Task 1's `selectVisible`/`emptyStateKind`/hook tests; integration is verified manually in Step 7).

- [ ] **Step 7: Manual verification (dev server)**

Run the dev server, open `/planning/inventory-flow`, toggle "All items", and confirm:
1. Hovering a desktop row shows the eye-off hide button; clicking it removes that row and a `Hidden (1)` pill appears.
2. Open `Hidden (N)` → the hidden item is listed by name; restore (↩) brings it back; `Show all` clears all.
3. `Focus` → checkboxes appear; tick 2 rows; `Hide the other N` leaves only those 2; confirm disabled when 0 ticked; `Cancel` aborts with no change.
4. Hide every visible row → "All rows hidden" empty state with a working `Show all`.
5. A background refetch (wait ~60s or click `Refresh now`) does NOT clear the hidden set; a full browser reload DOES.
6. Existing risk/family/search filters still work alongside hiding.
Record the result in the task report.

- [ ] **Step 8: Commit**

```bash
git add "src/app/(planning)/planning/inventory-flow/InventoryFlowClient.tsx"
git commit -m "feat(inventory-flow): wire hide/focus/reset into the page + all-hidden empty state"
```

---

## Self-Review

**Spec coverage:**
- Per-row hide → Task 2 (toggle) + Task 4 (wiring) + Task 5 (`vis.hide`). ✓
- Focus/isolate → Task 1 (`enterFocus`/`toggleSelect`/`confirmFocus`) + Task 3 (controls) + Task 5 (wiring). ✓
- Hidden tray + per-item restore → Task 3 + Task 5 (`hiddenItems`, `vis.restore`). ✓
- Show all / reset → Task 1 (`showAll`) + Task 3 + Task 5. ✓
- Ephemeral, survives refetch → Task 1 (`useState`) + Task 5 Step 7.5 manual check. ✓
- Names not ids in tray → Task 3 renders `item_name`; Task 5 builds `hiddenItems` from names. ✓
- Mobile ≥44px → Task 2 `size="touch"`, Task 4 mobile uses it. ✓
- All-rows-hidden empty state → Task 1 `emptyStateKind` + Task 5 Step 4. ✓
- Default callers unchanged → all new props optional/off; Task 4 Step 1 test asserts no hide button without `onHide`. ✓
- No backend/URL change → no task touches API/DB/searchParams. ✓

**Placeholder scan:** none — every step carries complete code or an exact command.

**Type consistency:** `hiddenIds`/`selectedIds: Set<string>`, `selectVisible`/`emptyStateKind` signatures, and the four optional grid/mobile props are identical across Tasks 1, 4, 5. `RowVisibilityToggle` and `RowFocusControls` prop names match their consumers. ✓

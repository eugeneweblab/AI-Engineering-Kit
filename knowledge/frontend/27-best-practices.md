---
id: frontend/27-best-practices
topic: frontend
slug: best-practices
title: "Frontend Best Practices"
type: doc
order: 27
status: ready
tags: [frontend, best-practices, Cart, formatMoney, useState, setTotal, useEffect, useCallback]
related: [frontend/02-component-driven-development, frontend/04-state-management, frontend/09-accessibility, frontend/08-performance, frontend/30-engineering-principles]
when_to_use: "Read before writing or reviewing any component, hook, or view to check it against the baseline the whole codebase expects."
---
# Frontend Best Practices

## Purpose

This document collects the cross-cutting habits that make frontend code correct,
accessible, and maintainable — the defaults every component and view is expected to meet.
It is the baseline a reviewer checks against. Topic-specific depth lives in the dedicated
docs (accessibility, state, performance); this is the shared floor no code should fall
below.

## Why It Matters

Most frontend defects are not exotic — they are the same handful of mistakes repeated:
unkeyed lists, unguarded async, inaccessible controls, state that duplicates the server,
effects that fire too often. Each is individually small, but together they decide whether
a codebase is pleasant or painful to work in. Consistent practices also lower the cost of
change: when every component follows the same conventions, any engineer (or agent) can
edit any file without relearning local rules. The payoff is speed *and* safety; the cost
of skipping it is a slow accretion of special cases.

## Core Principles

- **Derive, don't duplicate, state.** Compute values from a single source of truth during
  render instead of copying them into extra state that must be kept in sync.
- **Make the DOM semantic and accessible by default.** The correct element (`<button>`,
  `<a>`, `<label>`) gives you keyboard, focus, and AT support for free; a `<div>` with an
  `onClick` gives you a bug.
- **Type the boundaries.** Props, API responses, and events are contracts — type them
  precisely so misuse fails at compile time, not in the user's browser.
- **Keep components small and honest.** A component should do one job; when a render
  function branches five ways, it is five components wearing a trench coat.
- **Optimize only what you measure.** Ship the simple version, then use the profiler and
  real-user data to find real bottlenecks — premature memoization adds bugs and noise.

## Best Practices

- Give list items a **stable, data-derived `key`** (an id), never the array index —
  index keys corrupt state when the list reorders or filters.
- Guard every async call: `try/catch`, a timeout, a loading state, and an error state.
  A component that only renders the happy path is unfinished.
- Prefer **controlled data flow**: pass data down, events up. Reach for context or a store
  only when prop-drilling genuinely hurts; global state is a cost, not a default.
- Keep effects for *synchronizing with the outside world*, not for deriving data. Every
  effect needs a correct dependency list and a cleanup that cancels its work.
- Handle the full lifecycle of every view: loading, empty, error, and success — plus
  edge content (long text, zero items, huge numbers). The empty and error states are not
  optional.
- Never build interactive controls from non-interactive elements. If you must, add the
  full ARIA + keyboard contract — but reaching for the native element first is almost
  always correct.
- Keep styling consistent with the design system: use tokens, not magic hex values and
  pixel constants. One-off values are how a UI drifts out of alignment.
- Avoid layout shift: reserve space for images/embeds (width/height or aspect-ratio) and
  never inject content above what the user is reading.

## Examples

**Good Example** — derived state, stable keys, guarded async, semantic control

```tsx
function Cart({ items }: { items: Item[] }) {
  // Derived during render — no second source of truth to fall out of sync.
  const total = items.reduce((s, i) => s + i.price, 0);

  return (
    <ul>
      {items.map((i) => (
        <li key={i.id}>{i.name}</li> // stable id key survives reorders
      ))}
      <li>Total: {formatMoney(total)}</li>
    </ul>
  );
}
// Real <button> → keyboard, focus ring, and AT support come for free.
<button type="button" onClick={checkout}>Check out</button>;
```

**Bad Example** — duplicated state, index keys, div-as-button

```tsx
function Cart({ items }: { items: Item[] }) {
  const [total, setTotal] = useState(0);
  useEffect(() => {                      // effect to derive a value = drift + extra render
    setTotal(items.reduce((s, i) => s + i.price, 0));
  }, [items]);                           // total is stale for one render, every time

  return items.map((i, idx) => <li key={idx}>{i.name}</li>); // index key corrupts on reorder
}
<div onClick={checkout}>Check out</div>; // no keyboard, no focus, invisible to screen readers
```

## Common Mistakes

- Using array index as a React key in a list that can reorder, filter, or grow.
- Copying props or server data into `useState`, then fighting to keep them in sync.
- Firing effects to compute derived values instead of computing them during render.
- `<div onClick>` controls that are unreachable by keyboard and screen readers.
- Rendering only the success state; no loading, empty, or error branch.
- Hardcoded colors/spacing instead of design tokens, causing visual drift.
- Wrapping everything in `useMemo`/`useCallback` without a measured reason.

## Production Tips

- Enforce the baseline with tooling: ESLint (react-hooks, jsx-a11y), TypeScript in strict
  mode, and Prettier — so these rules are checked in CI, not left to reviewers.
- Add a lint rule against inline hex colors and magic spacing to keep the design system
  authoritative.

## AI Review Checklist

- Do list items use a stable, data-derived key (not the array index)?
- Is derived data computed during render rather than stored in state or an effect?
- Does every async path have loading, error, and empty handling?
- Are interactive controls native elements (or fully ARIA + keyboard equipped)?
- Are props and API responses precisely typed at the boundary?
- Are colors and spacing sourced from design tokens, not literals?
- Is memoization justified by a measurement, not applied by reflex?

## Related

- `knowledge/frontend/02-component-driven-development.md`
- `knowledge/frontend/04-state-management.md`
- `knowledge/frontend/09-accessibility.md`
- `knowledge/frontend/08-performance.md`
- `knowledge/frontend/30-engineering-principles.md`

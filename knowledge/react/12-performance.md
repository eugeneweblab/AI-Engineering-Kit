---
id: react/12-performance
topic: react
slug: performance
title: "React Performance"
type: doc
order: 12
status: ready
tags: [react, performance, useMemo, React.memo, useCallback, lazy, onSelect, memo]
related: [react/11-rendering, react/08-hooks, react/10-context-api, performance/06-rendering]
when_to_use: "Read before optimizing or reviewing React performance and memoization decisions."
---
# React Performance

## Purpose

This document defines the engineering standards for optimizing React applications.

The objective is to build applications that remain fast, scalable, and maintainable without introducing unnecessary complexity.

Performance optimization should be driven by measurement rather than assumptions.

---

## Core Principle

Measure first.

Optimize second.

Every optimization introduces additional complexity and should provide measurable value.

---

## Performance Workflow

Every optimization should follow this process.

```
Identify Problem
        ↓
Measure
        ↓
Locate Bottleneck
        ↓
Choose Solution
        ↓
Implement
        ↓
Measure Again
        ↓
Document
```

Never optimize blindly.

---

## Performance Priorities

Optimize in this order:

1. Prevent unnecessary rendering.
2. Reduce JavaScript execution.
3. Reduce network requests.
4. Reduce bundle size.
5. Optimize images.
6. Optimize expensive calculations.
7. Optimize animations.

---

## Rendering Performance

Review:

- unnecessary re-renders;
- duplicated rendering;
- unstable props;
- unstable callbacks;
- unnecessary state updates.

Most React performance issues originate from excessive rendering.

---

## React.memo

Use `React.memo` only when:

- rendering is expensive;
- props change infrequently;
- profiling confirms unnecessary renders.

Good candidates:

- data tables;
- charts;
- large cards;
- complex forms.

Avoid wrapping every component with `React.memo`.

---

## useMemo

Use `useMemo` for expensive calculations.

Good:

```tsx
const filteredProducts = useMemo(() => {
    return products.filter(matchesFilter);
}, [products, matchesFilter]);
```

Avoid:

```tsx
const title = useMemo(() => "Dashboard", []);
```

Do not memoize inexpensive computations.

---

## useCallback

Use `useCallback` when callback identity affects rendering.

Examples:

- memoized child components;
- dependency arrays;
- reusable hooks.

Avoid wrapping every function.

Bad:

```tsx
const handleClick = useCallback(() => {
    console.log("Click");
}, []);
```

---

## Derived Values

Compute values instead of storing them.

Prefer:

```tsx
const completed = todos.filter(
    todo => todo.completed
);
```

Avoid duplicating derived state.

---

## State Optimization

Review:

- duplicated state;
- oversized state objects;
- deeply nested updates;
- unnecessary global state.

Smaller state generally produces fewer renders.

---

## Component Splitting

Split components when:

- unrelated sections render independently;
- only part of the UI changes;
- rendering becomes expensive.

Smaller components allow React to update less UI.

---

## Lazy Loading

Use lazy loading for:

- routes;
- dashboards;
- admin panels;
- large dialogs;
- rarely used features.

Example:

```tsx
const SettingsPage = lazy(() =>
    import("./SettingsPage")
);
```

---

## Code Splitting

Split bundles by:

- route;
- feature;
- large dependency.

Avoid creating a single large JavaScript bundle.

---

## Lists

Large collections should be reviewed carefully.

Consider:

- pagination;
- infinite scrolling;
- virtualization.

Rendering thousands of DOM nodes simultaneously should be avoided.

---

## Virtualization

Use virtualization for very large datasets.

Examples:

- tables;
- logs;
- activity feeds;
- search results.

Render only visible elements.

---

## Expensive Calculations

Move expensive calculations:

- outside rendering;
- into `useMemo`;
- to the server;
- into background workers when appropriate.

Rendering should remain lightweight.

---

## Images

Review:

- responsive images;
- lazy loading;
- modern formats;
- image dimensions.

Images frequently dominate page weight.

---

## Network Performance

Review:

- duplicate requests;
- unnecessary refetching;
- request waterfalls;
- oversized payloads.

Reducing network activity often has a greater impact than micro-optimizing rendering.

---

## Profiling

Always profile before optimization.

Useful tools include:

- React DevTools Profiler;
- browser Performance panel;
- Lighthouse;
- Web Vitals.

Decisions should be based on measurements.

---

## Accessibility

Performance optimizations must never reduce accessibility.

Verify:

- keyboard navigation;
- focus management;
- screen reader behavior;
- reduced motion support.

---

## AI Execution Checklist

## Investigation

☐ Performance issue identified.

☐ Rendering analyzed.

☐ Bundle size reviewed.

☐ Network activity reviewed.

---

## Planning

☐ Select the simplest optimization.

☐ Verify expected impact.

☐ Avoid premature optimization.

---

## Verification

☐ Performance measured before changes.

☐ Performance measured after changes.

☐ No unnecessary memoization.

☐ Bundle size acceptable.

☐ Accessibility preserved.

---

## Examples

**Good Example** — measure, then fix the cause rather than adding memo everywhere

```tsx
// The expensive computation is memoised on the values it actually depends on.
export function Report({ rows, filter }: { rows: Row[]; filter: Filter }) {
  const visible = useMemo(
    () => rows.filter((row) => matches(row, filter)).sort(byDate),
    [rows, filter],
  );

  // A long list virtualised: the DOM holds the visible window, not 10,000 nodes.
  return (
    <Virtuoso
      data={visible}
      itemContent={(_, row) => <ReportRow row={row} />}
      style={{ height: 600 }}
    />
  );
}
```

```tsx
// State moved down, so typing does not re-render the expensive siblings.
export function Page() {
  return (
    <>
      <SearchInput />          {/* owns its own query state */}
      <ExpensiveDashboard />   {/* unaffected by keystrokes */}
    </>
  );
}
```

```tsx
// Route-level code splitting: a heavy screen is not in the initial bundle.
const Analytics = lazy(() => import('./routes/analytics'));
```

**Bad Example** — memo applied everywhere, cause untouched

```tsx
// memo on a component whose props change on every render does nothing except
// add a comparison. The parent creates a new array and a new function each time.
const Row = memo(function Row({ item, onSelect }: RowProps) {
  return <li onClick={() => onSelect(item.id)}>{item.name}</li>;
});

export function List({ items }: { items: Item[] }) {
  return (
    <ul>
      {items.map((item) => (
        <Row key={item.id} item={{ ...item }} onSelect={(id) => console.log(id)} />
      ))}
    </ul>
  );
}

export function Dashboard({ rows }: { rows: Row[] }) {
  // useMemo with a dependency that is a new array every render: the memo never
  // hits, and the cost of the comparison is added to the cost of the work.
  const total = useMemo(() => rows.reduce((s, r) => s + r.value, 0), [[...rows]]);

  // 10,000 rows rendered into the DOM, then hidden with CSS.
  return <table>{rows.map((r) => <tr key={r.id} hidden={!r.visible}>{r.name}</tr>)}</table>;
}
```

---

## Common Mistakes

Avoid:

Using `useMemo` everywhere.

Using `useCallback` everywhere.

Wrapping every component with `React.memo`.

Optimizing without profiling.

Ignoring bundle size.

Ignoring network performance.

Trading readability for insignificant gains.

---

## Completion Criteria

Performance optimization is complete when:

- the bottleneck has been identified;
- improvements have been measured;
- unnecessary rendering has been reduced;
- bundle size remains appropriate;
- accessibility has been preserved;
- code readability has not been significantly reduced.

---

## Summary

Effective React performance optimization focuses on measurable improvements rather than theoretical ones.

By minimizing unnecessary rendering, reducing bundle size, optimizing network usage, and profiling before making changes, applications remain fast, maintainable, and scalable as they grow.

## Related

- `knowledge/react/11-rendering.md`
- `knowledge/react/08-hooks.md`
- `knowledge/react/10-context-api.md`
- `knowledge/performance/06-rendering.md`

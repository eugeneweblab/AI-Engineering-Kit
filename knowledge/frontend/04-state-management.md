---
id: frontend/04-state-management
topic: frontend
slug: state-management
title: "State Management"
type: doc
order: 4
status: ready
tags: [frontend, state-management, setState, fetchCart, useQuery, useSearchParams, Cart, isValid, stale, store, debugging]
related: [frontend/01-frontend-architecture, frontend/02-component-driven-development, frontend/05-routing, frontend/06-data-fetching, frontend/12-forms]
when_to_use: "Read before adding state, choosing a store, or debugging stale, duplicated, or out-of-sync UI state."
---
# State Management

## Purpose

This document defines where each kind of state should live and how to move data
between those places without creating bugs. It lets an agent decide whether a value
belongs in a component, the URL, a shared store, or a server cache — and avoid the
most common source of frontend defects: the same fact stored in two places.

The central question is never "which state library?" It is "who owns this value, and
what is it derived from?" Answer that first; the tool follows.

## Why It Matters

Most UI bugs are synchronization bugs: two copies of the same data drift apart, or a
value is stored when it should have been derived. A checkbox that does not reflect
the server, a filter lost on reload, a total that disagrees with its line items —
all are one fact stored twice. Reaching for a global store makes this worse, not
better, because it invites copying server data into client state where it goes stale.

Choosing the right home for each value eliminates whole categories of bugs before
they exist and keeps re-renders localized, which is also a performance win.

## Core Principles

- **Every value has exactly one owner.** If a value can be computed from another,
  compute it — do not store it. Derived-then-stored is drift waiting to happen.
- **Classify state before storing it.** There are four kinds and each has a home:
  *server* state (belongs to the backend), *URL* state (shareable/navigational),
  *local UI* state (transient, one component), and *form* state (in-progress input).
- **Server state is a cache, not your state.** It is fetched, cached, invalidated,
  and refetched — use a server-cache library, not a global store copy.
- **Keep state as local as possible.** Lift only when a shared ancestor needs it;
  globalize only when truly cross-cutting. Scope limits blast radius and re-renders.
- **State updates are explicit and traceable.** Prefer pure reducers/actions for
  complex transitions over scattered `setState` calls you cannot follow.

## Best Practices

- Default to component-local state (`useState`/`useReducer`). Reach for shared or
  global state only when you have a concrete cross-component need.
- Put shareable, bookmarkable, or reload-surviving state in the URL — filters,
  tabs, pagination, selected id. See [routing](05-routing.md).
- Manage server data with a dedicated cache (TanStack Query, RTK Query, SWR) that
  handles caching, deduping, and invalidation. Do not mirror it into a global store.
  See [data fetching](06-data-fetching.md).
- For genuinely global client state (theme, auth session, feature flags), use a
  small store; keep it minimal.
- Derive, don't duplicate: compute totals, filtered lists, and flags from source
  state at render time.

## Examples

**Good Example** — each fact owned once, server state cached, derived values derived

```tsx
function Cart() {
  // Server state: owned by the backend, cached and revalidated by the query lib.
  const { data: items } = useQuery({ queryKey: ["cart"], queryFn: fetchCart });

  // URL state: the coupon is shareable and must survive reload.
  const [params] = useSearchParams();
  const coupon = params.get("coupon");

  // Derived, not stored — the total can never drift from the items.
  const total = items.reduce((s, i) => s + i.price * i.qty, 0);

  return <Summary items={items} coupon={coupon} total={total} />;
}
```

**Bad Example** — server data copied into a global store, total stored separately

```tsx
// Cart items are copied from the server into a global store, so they go stale the
// moment the backend changes. `total` is stored independently, so it silently
// disagrees with the items after any quantity edit. Two facts, three copies.
globalStore.set("cartItems", await fetchCart());
globalStore.set("cartTotal", computeTotal(globalStore.get("cartItems")));
// ...later, an edit updates items but forgets to recompute total → wrong price shown.
```

## Common Mistakes

- Copying fetched server data into a global store, where it goes stale.
- Storing derived values (totals, filtered lists, `isValid`) instead of computing them.
- Putting transient UI state (hover, open/closed) in a global store, causing wide
  re-renders and coupling.
- Keeping filter/tab/pagination state in memory, so it is lost on reload and cannot
  be shared via URL.
- Reaching for a global store by default instead of the least-powerful option.
- Multiple `setState` calls for one logical transition, creating impossible
  intermediate states.

## Production Tips

- Configure sensible cache staleness and invalidation for server state; the default
  is usually too aggressive or too lax for your data.
- Use devtools (query cache, store timeline) to inspect what is stored and why a
  component re-rendered.
- When two values must always agree, that is a signal to store one and derive the
  other, or to make them a single object updated atomically.

## AI Review Checklist

- Is each value owned in exactly one place, and is derived data derived, not stored?
- Is server data managed by a cache library rather than copied into a global store?
- Is shareable/reload-surviving state (filters, tabs, ids) kept in the URL?
- Is state kept as local as possible, globalized only when genuinely cross-cutting?
- Are complex state transitions expressed as explicit, traceable updates?

## Related

- `knowledge/frontend/01-frontend-architecture.md`
- `knowledge/frontend/02-component-driven-development.md`
- `knowledge/frontend/05-routing.md`
- `knowledge/frontend/06-data-fetching.md`
- `knowledge/frontend/12-forms.md`

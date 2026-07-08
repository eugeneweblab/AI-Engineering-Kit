---
id: frontend/30-engineering-principles
topic: frontend
slug: engineering-principles
title: "Engineering Principles"
type: doc
order: 30
status: ready
tags: [frontend, engineering-principles]
related: [frontend/27-best-practices, frontend/08-performance, frontend/09-accessibility, frontend/13-error-handling, frontend/04-state-management]
when_to_use: "Read before making a structural or technical decision in a frontend codebase — choosing state, drawing component boundaries, or deciding what runs on the client."
---
# Engineering Principles

## Purpose

This document defines the durable principles that separate frontend code that survives
years of change from code that rots after one sprint. It is written so an agent can make
a structural decision — where state lives, what is a component boundary, what runs on the
client — and justify it, rather than copy a pattern it half-remembers.

These are not framework rules. They hold across React, Vue, Svelte, and Solid because they
come from the constraints of the medium: an untrusted client, a network you do not control,
a human staring at a screen, and a bundle that ships over the wire every visit.

## Why It Matters

The frontend is the one layer the user actually experiences. A backend can be slow and
nobody sees it if the UI hides the latency; a UI that janks, blocks, or lies about its
state loses the user regardless of how correct the server is. Frontend code also runs in an
environment you do not own — arbitrary devices, throttled networks, hostile input — so
principles that "just work" on your laptop routinely fail in production.

Frontend mistakes compound. A leaky component boundary, state kept in the wrong place, or an
effect that fires on every render does not crash — it slowly makes every future change
riskier and every render slower. Principled structure is what keeps the marginal cost of the
next feature flat instead of exponential.

## Core Principles

- **The client is untrusted; the server is the source of truth.** Validate and authorize on
  the server always. Client-side checks are UX, not security — a disabled button stops
  nobody with devtools.
- **State has one home.** Every piece of state lives in exactly one place, derived
  everywhere else. Duplicated state drifts out of sync; that drift is the single most common
  class of UI bug.
- **Render is a pure function of state.** `UI = f(state)`. Do not mutate the DOM imperatively
  around your framework, and do not stash render-affecting data outside the state system.
- **Make the loading and error states first-class.** Every async read has three states, not
  one. Design loading, empty, and error before the happy path, because in production they are
  the common path.
- **Boundaries follow ownership, not visual layout.** A component owns its data and behavior;
  split when responsibilities diverge, not because a file got long.
- **Ship less.** Every kilobyte of JavaScript is parsed and executed on the user's device.
  The fastest code is the code you do not send.
- **Accessibility is correctness, not decoration.** A control a keyboard or screen reader
  cannot operate is a broken control, the same as one that throws.

## Best Practices

- Colocate state with the component that owns it; lift it only to the nearest common ancestor
  that needs it. Do not default to a global store — global state is shared mutable state.
- Separate server state (fetched, cached, invalidated) from client state (UI toggles, form
  drafts). Use a data-fetching library for the former; do not hand-roll cache invalidation.
- Keep components pure: no side effects in render, effects only for synchronizing with
  external systems (network, DOM, subscriptions). An effect that sets state from props is
  usually a derivation in disguise.
- Derive, don't store. If a value can be computed from existing state, compute it; storing it
  creates a second source of truth you must keep in sync.
- Make impossible states unrepresentable. Model `{ status: 'loading' | 'error' | 'success' }`
  as one discriminated union, not three independent booleans that can all be true at once.
- Handle failure at a boundary: wrap route or feature subtrees in an error boundary so one
  broken component does not blank the whole page.
- Budget the bundle. Code-split at the route level, lazy-load below-the-fold and interaction-
  gated code, and treat a bundle-size regression as a failing test.

## Examples

**Good Example** — one source of truth, state modeled as a union, derived values computed

```tsx
// Server state owned by the query cache; UI derives from it, stores nothing extra.
function Cart() {
  const { data, status } = useQuery(["cart"], fetchCart);

  if (status === "pending") return <Spinner />;      // loading is a real state
  if (status === "error") return <RetryPanel />;     // so is failure

  const total = data.items.reduce((s, i) => s + i.price * i.qty, 0); // derived, not stored
  return <CartView items={data.items} total={total} />;
}
```

**Bad Example** — duplicated state that drifts, effect used as a derivation

```tsx
function Cart() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0); // second source of truth for the same data

  useEffect(() => {
    fetchCart().then((c) => setItems(c.items)); // no loading or error state at all
  }, []);

  useEffect(() => {
    // Recomputing total in an effect means an extra render where total is stale.
    setTotal(items.reduce((s, i) => s + i.price * i.qty, 0));
  }, [items]);

  return <CartView items={items} total={total} />; // total can lag items by a frame
}
```

## Common Mistakes

- Keeping derived values in state and syncing them with effects, instead of computing them.
- Treating server data as client state — manually caching, refetching, and invalidating by
  hand instead of using a query library.
- Reaching for a global store on day one, making every value app-wide and every change risky.
- Modeling async with parallel booleans (`isLoading`, `isError`, `data`) that permit
  contradictory combinations.
- Trusting the client: enforcing rules only in the UI and assuming the API is safe.
- Only building the happy path, then bolting on spinners and error toasts after QA finds them.
- Shipping one giant bundle because code-splitting was "an optimization for later."

## Production Tips

- Set a JavaScript bundle budget in CI and fail the build when a route exceeds it; regressions
  are easiest to catch at the PR that introduces them.
- Instrument Core Web Vitals (LCP, INP, CLS) from real users, not just lab runs — field data
  is the only measure that reflects your actual device and network distribution.
- Test the failure paths: mock a 500, a timeout, and an empty result, and assert the UI stays
  usable. These are the states users hit most and developers test least.

## AI Review Checklist

- Is every piece of state stored in exactly one place, with the rest derived?
- Is server state managed by a caching layer rather than hand-rolled effects?
- Does every async read render distinct loading, empty, and error states?
- Are async states modeled as a union, so contradictory combinations are unrepresentable?
- Is any security or authorization decision enforced only on the client?
- Are components pure, with effects reserved for external-system synchronization?
- Is the code split so a route ships only the JavaScript it needs?
- Can every interactive control be operated by keyboard and screen reader?

## Related

- `knowledge/frontend/27-best-practices.md`
- `knowledge/frontend/04-state-management.md`
- `knowledge/frontend/08-performance.md`
- `knowledge/frontend/09-accessibility.md`
- `knowledge/frontend/13-error-handling.md`

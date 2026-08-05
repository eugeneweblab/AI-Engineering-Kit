---
id: frontend/02-component-driven-development
topic: frontend
slug: component-driven-development
title: "Component Driven Development"
type: doc
order: 2
status: ready
tags: [frontend, component-driven-development]
related: [frontend/01-frontend-architecture, frontend/03-design-systems, frontend/04-state-management, frontend/09-accessibility, frontend/22-testing]
when_to_use: "Read before building or refactoring UI components, deciding component boundaries, or designing a props API."
---
# Component Driven Development

## Purpose

This document defines how to decompose a UI into components: where to draw
boundaries, how to design a props API, how to split presentation from logic, and
how to keep components composable and testable. It lets an agent build a component
that reads clearly and can be reused without surprises.

A component is a function from state to UI plus a small, explicit contract (its
props). The quality of that contract determines whether the component is a reusable
building block or a liability.

## Why It Matters

Components are the unit of reuse, testing, and reasoning in a frontend. A
well-bounded component can be developed in isolation, tested without the whole app,
and dropped into new contexts. A poorly-bounded one — one that fetches its own data,
knows about global state, and renders differently per caller via boolean flags —
becomes impossible to reuse and dangerous to change.

Because components compose, a bad boundary does not stay contained: it forces the
next component to work around it, and the cost multiplies up the tree.

## Core Principles

- **One responsibility per component.** A component either arranges layout, renders
  data, or manages interaction — not all three. Split when it does more than one.
- **Separate presentational from container concerns.** Presentational components
  take props and render; container components/hooks fetch and hold state. Mixing
  them makes both untestable.
- **Props are a contract, not a config bag.** Prefer a few meaningful props over
  many booleans. Three booleans is eight states; most are nonsense.
- **Composition over configuration.** Pass `children` and slots instead of a flag
  for every variation. Composition scales; flags accumulate.
- **State lives as low as it can.** Lift it only when a shared ancestor truly needs
  it. See [state management](04-state-management.md).

## Best Practices

- Keep components small and named for what they render (`InvoiceRow`), not how
  (`SmallBlueBox`).
- Type every prop; make required props required and optional props genuinely
  optional with sane defaults.
- Do not fetch data inside a presentational component — pass it in, so the component
  can be rendered in tests, stories, and other screens.
- Avoid `useEffect` for anything that is not a synchronization with an external
  system; derive values during render instead. Effects are the top source of bugs.
- Build against [design-system primitives](03-design-systems.md) rather than raw
  HTML, so spacing, color, and focus behavior stay consistent.
- Provide a semantic, accessible DOM by default (labels, roles, focus). See
  [accessibility](09-accessibility.md).

## Examples

**Good Example** — presentational component with a clean contract

```tsx
type BadgeProps = {
  label: string;
  tone?: "neutral" | "success" | "danger"; // a closed set, not three booleans
};

// Pure: same props always render the same output, so it is trivially testable
// and reusable. No data fetching, no global state, no side effects.
export function Badge({ label, tone = "neutral" }: BadgeProps) {
  return <span className={`badge badge--${tone}`}>{label}</span>;
}

// The container decides *what* to show; Badge only knows *how* to show it.
function OrderStatus({ orderId }: { orderId: string }) {
  const { data } = useOrder(orderId);           // side effects live in the container
  return <Badge label={data.status} tone={data.paid ? "success" : "danger"} />;
}
```

**Bad Example** — one component doing everything, flag-driven variants

```tsx
// Fetches its own data, mutates global state, and forks behavior on four booleans.
// Cannot be rendered in a test without a network mock and a store; the boolean
// combinations create states that were never intended (isError && isSuccess).
function Badge({ orderId, isSmall, isError, isSuccess, isAdmin }) {
  const [data, setData] = useState(null);
  useEffect(() => { fetch(`/orders/${orderId}`).then(r => r.json()).then(setData); }, [orderId]);
  if (isAdmin) globalStore.track("badge_seen"); // side effect during render
  return <span className={isSmall ? "s" : "l"}>{isError ? "!" : data?.status}</span>;
}
```

## Common Mistakes

- Presentational components that fetch their own data, making them unusable in
  tests and other contexts.
- A wall of boolean props instead of a variant union or composition.
- Prop drilling many levels deep instead of composing with `children` or lifting
  state to the right owner.
- Overusing `useEffect` to compute values that could be derived during render.
- Giant "god" components that own layout, data, and interaction at once.
- Copy-pasting a component to tweak one detail instead of parameterizing it.

## Production Tips

- Develop and document components in isolation (Storybook or a stories file) so
  edge states — empty, loading, error, long text — are visible and testable.
- Add a visual-regression or interaction test for shared primitives; they are used
  everywhere, so a regression is expensive.
- Keep a component's file, styles, tests, and stories colocated.

## AI Review Checklist

- Does each component have a single, clear responsibility?
- Are presentational components free of data fetching and global-state access?
- Is the props API a small set of meaningful props rather than many booleans?
- Is state kept at the lowest level that needs it?
- Are effects limited to genuine external synchronization, not derived values?
- Is the rendered markup semantic and accessible by default?

## Related

- `knowledge/frontend/01-frontend-architecture.md`
- `knowledge/frontend/03-design-systems.md`
- `knowledge/frontend/04-state-management.md`
- `knowledge/frontend/09-accessibility.md`
- `knowledge/frontend/22-testing.md`

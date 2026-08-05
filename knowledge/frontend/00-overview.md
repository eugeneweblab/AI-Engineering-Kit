---
id: frontend/00-overview
topic: frontend
slug: overview
title: "Overview"
type: doc
order: 0
status: ready
tags: [frontend, overview]
related: [frontend/01-frontend-architecture, frontend/02-component-driven-development, frontend/04-state-management, frontend/05-routing, frontend/03-design-systems]
when_to_use: "Read first when starting any frontend work to orient yourself in this topic and pick the right document."
---
# Overview

## Purpose

This document is the map for the `frontend` topic. It orients an agent to what a
modern frontend is responsible for, how the documents in this topic relate, and
which one to open for a given task. Read it first, then jump to the specific doc
that matches the work in front of you.

The frontend is the part of the system a human actually touches. It runs on a
device you do not control, over a network you cannot trust, and must stay correct,
fast, and accessible while doing so. These docs teach how to build that layer
deliberately rather than by accretion.

## Why It Matters

Frontend defects are the ones users see directly: a broken form, a layout that
collapses on mobile, a spinner that never resolves. Unlike a backend bug behind a
retry, a frontend bug is the product experience. And because the frontend ships
to every browser and device, mistakes scale to your entire audience at once.

Frontend also carries real security and correctness weight — it renders untrusted
data, holds session state, and is the first target for XSS and injection. Treating
it as "just the UI" is how those bugs get in.

## Core Principles

- **Structure before styling.** Decide component boundaries, state ownership, and
  data flow before writing CSS. Layout is cheap to change; architecture is not.
- **State has one owner.** Every piece of state lives in exactly one place, as
  close as possible to where it is used. Duplication is the root of UI bugs.
- **The server is the source of truth.** The client mirrors server state; it never
  becomes the authority for data it did not create.
- **Accessibility and performance are requirements, not polish.** They are cheapest
  to build in from the start and most expensive to retrofit.
- **Render untrusted data safely.** All dynamic content is hostile until escaped.

## How These Documents Fit Together

- **[Frontend Architecture](01-frontend-architecture.md)** — the top-level shape:
  layers, module boundaries, folder structure, and how data flows through the app.
  Start here for any new project or large refactor.
- **[Component-Driven Development](02-component-driven-development.md)** — how to
  decompose a UI into composable, testable components with clear props and state.
- **[Design Systems](03-design-systems.md)** — design tokens, shared primitives,
  and the contract that keeps many components visually and behaviorally consistent.
- **[State Management](04-state-management.md)** — where each kind of state lives
  (local, shared, server, URL) and how to move data between them without tangling.
- **[Routing](05-routing.md)** — mapping URLs to views, nested layouts, guards,
  code-splitting boundaries, and treating the URL as shareable state.

Later docs in this topic cover data fetching, rendering strategy, performance,
accessibility, forms, testing, and security in depth. Reach for them once the
structural decisions above are settled.

## Best Practices

- Read the topic-level doc that matches your task **before** editing code; most
  frontend bugs come from ignoring an established boundary, not from typos.
- Choose the least powerful tool that solves the problem: local state over global
  state, a link over a router guard, CSS over JavaScript.
- Keep the four kinds of state distinct — server, URL, local UI, and form state —
  and never store one as if it were another.
- Ship a working skeleton (routes, layout, data flow) before adding visual detail.

## Examples

**Good Example** — state placed at the level that owns it

```tsx
// Filter state lives in the URL because it is shareable and survives reload.
// Row-hover state lives locally because no one else needs it.
function ProductList() {
  const [params, setParams] = useSearchParams(); // URL: the shared, bookmarkable state
  const category = params.get("category") ?? "all";
  const { data } = useProducts(category);        // server state, cached separately
  return data.map((p) => <ProductRow key={p.id} product={p} />);
}
```

**Bad Example** — everything crammed into one global store

```tsx
// Global store holds server data, the current URL, and transient hover state
// together. Now a hover change re-renders the whole tree and reload loses the
// filter — three unrelated concerns share one owner.
globalStore.set({ products, currentCategory, hoveredRowId });
```

## Common Mistakes

- Writing components before deciding where state lives, then bolting on a global
  store to paper over the tangle.
- Treating the frontend as untyped glue — skipping types, tests, and boundaries.
- Retrofitting accessibility and performance at the end instead of designing for
  them.
- Copying data into client state and letting it drift from the server.

## AI Review Checklist

- Does the change respect the layer and module boundaries in
  [frontend architecture](01-frontend-architecture.md)?
- Is each new piece of state owned in exactly one place, at the right level?
- Is dynamic, user-supplied content escaped before rendering?
- Are the correct topic docs consulted for the task (routing, state, components)?

## Related


- `knowledge/frontend/01-frontend-architecture.md`
- `knowledge/frontend/02-component-driven-development.md`
- `knowledge/frontend/04-state-management.md`
- `knowledge/frontend/05-routing.md`
- `knowledge/frontend/03-design-systems.md`

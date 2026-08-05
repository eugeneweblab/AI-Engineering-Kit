---
id: frontend/01-frontend-architecture
topic: frontend
slug: frontend-architecture
title: "Frontend Architecture"
type: doc
order: 1
status: ready
tags: [frontend, frontend-architecture]
related: [frontend/02-component-driven-development, frontend/04-state-management, frontend/05-routing, frontend/03-design-systems, frontend/25-folder-structure, frontend/07-rendering]
when_to_use: "Read before starting a new frontend app, adding a major feature area, or refactoring folder and module structure."
---
# Frontend Architecture

## Purpose

This document defines the top-level shape of a frontend application: how code is
layered, how modules depend on one another, how data flows, and how the file tree
reflects all of that. It is written so an agent can place new code in the right
layer and reviewers can tell when a boundary has been crossed.

Architecture is the set of decisions that are expensive to reverse. Getting it
right early is cheaper than any refactor later.

## Why It Matters

A frontend without architecture becomes a graph where every file can import every
other file. Small changes ripple unpredictably, features cannot be reasoned about
in isolation, and the bundle grows because nothing can be split cleanly. The cost
is not visible on day one; it compounds until every change is slow and risky.

Good architecture makes the dependency direction explicit and one-way. That single
property is what lets you test a feature alone, split it into its own bundle, and
delete it without collateral damage.

## Core Principles

- **Dependencies point one direction.** UI depends on features, features depend on
  shared/domain code — never the reverse. Enforce it, because unenforced rules rot.
- **Separate by feature, not by file type.** Colocate everything a feature needs
  (components, hooks, state, tests) so it can be understood and removed as a unit.
- **Keep a thin, framework-agnostic core.** Business rules and data shapes should
  not import React, the router, or the HTTP client. Frameworks change; rules persist.
- **Push side effects to the edges.** Data fetching, storage, and I/O live in a
  clear layer; the rest of the app is pure transformation of props and state.
- **The boundary is the contract.** A module exposes a small public surface (an
  index barrel); everything else is private and may change freely.

## Best Practices

- Organize the tree around features/routes, with a `shared/` (or `ui/`, `lib/`)
  area for cross-cutting primitives. See [folder structure](25-folder-structure.md).
- Give each feature a single public entry point and import features only through it,
  so internal refactors never break other features.
- Isolate external dependencies (HTTP client, analytics, feature flags) behind a
  thin adapter, so swapping or mocking them touches one file.
- Enforce boundaries mechanically with lint rules (e.g. `import/no-restricted-paths`
  or an `eslint-plugin-boundaries` config) — reviews alone will not hold the line.
- Decide the rendering strategy (CSR / SSR / SSG) at the architecture level; it
  drives data-fetching and routing choices. See [rendering](07-rendering.md).

## Examples

**Good Example** — feature-sliced, one-way dependencies

```
src/
  features/
    checkout/
      components/   CartSummary.tsx, PayButton.tsx
      hooks/        useCart.ts
      api/          checkoutApi.ts     // side effects isolated here
      index.ts      // public surface: exports <Checkout/> only
  shared/
    ui/             Button.tsx, Input.tsx   // no feature imports
    lib/            formatMoney.ts
  app/
    routes.tsx      // wires features to URLs
```

```ts
// checkout/index.ts — the only thing other code may import from this feature.
export { Checkout } from "./components/Checkout";
// Internals (useCart, checkoutApi) stay private and can change without breaking callers.
```

**Bad Example** — cross-feature reach-in, type-based folders

```ts
// components/PayButton.tsx
import { cart } from "../../hooks/useCart";          // by file type, not feature
import { discountRules } from "../orders/internal";  // reaches into another feature's guts

// Now "orders" cannot refactor its internals, "checkout" cannot be split or deleted,
// and a change to useCart ripples across unrelated screens.
```

## Common Mistakes

- Grouping by file type (`components/`, `hooks/`, `utils/`) so one feature is
  scattered across the tree and cannot be reasoned about or removed as a unit.
- Circular or upward dependencies (shared code importing a feature).
- A "utils" or "helpers" dumping ground that every file imports, coupling everything.
- Business logic living inside components, so it cannot be tested without a DOM.
- No enforced boundaries — the architecture exists only in a diagram, not in lint.

## Production Tips

- Add an architecture lint check to CI so boundary violations fail the build, not
  the review.
- Track bundle size per feature; a feature that cannot be code-split is usually a
  boundary that has leaked. See [code splitting](21-code-splitting.md).
- Document each feature's public surface in its `index.ts`; treat additions to it
  as API changes.

## AI Review Checklist

- Do all imports point in the allowed direction (UI → feature → shared/core)?
- Is each feature self-contained and imported only through its public entry point?
- Are side effects (HTTP, storage, analytics) isolated behind adapters?
- Is business logic free of framework imports and unit-testable without a DOM?
- Are architectural boundaries enforced by lint, not just convention?

## Related


- `knowledge/frontend/02-component-driven-development.md`
- `knowledge/frontend/04-state-management.md`
- `knowledge/frontend/05-routing.md`
- `knowledge/frontend/03-design-systems.md`
- `knowledge/frontend/25-folder-structure.md`
- `knowledge/frontend/07-rendering.md`

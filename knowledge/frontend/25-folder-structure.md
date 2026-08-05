---
id: frontend/25-folder-structure
topic: frontend
slug: folder-structure
title: "Frontend Folder Structure"
type: doc
order: 25
status: ready
tags: [frontend, folder-structure, SearchBar, Button.tsx, dependencies, no-restricted-imports, index.ts, eslint-plugin-boundaries]
related: [frontend/01-frontend-architecture, frontend/02-component-driven-development, frontend/21-code-splitting, frontend/24-documentation, frontend/19-build-tools]
when_to_use: "Read before creating a new frontend project or adding a feature that needs new directories."
---
# Frontend Folder Structure

## Purpose

This document defines how to organize files in a frontend codebase so that code is easy
to find, safe to change, and hard to entangle. It covers the trade-off between grouping
by type versus by feature, where shared code lives, and how to encode boundaries the
build can enforce. The aim is a structure where a file's location tells you what it does
and what it may depend on.

## Why It Matters

Folder structure is architecture made physical. It decides what is easy: if related
files sit together, a feature is a self-contained change; if they are scattered, every
change touches ten directories and reviewers cannot reason about blast radius. A bad
structure invites accidental coupling — a "shared" util imported by half the app becomes
un-deletable, and features reach into each other's internals because nothing stops them.
Because the structure is copied by every new file, the first decision compounds for the
life of the project. Getting it right early is cheap; fixing it later is a migration.

## Core Principles

- **Group by feature, not by file type.** Co-locate everything a feature needs
  (component, hooks, tests, styles, types). "Screaming" structure — folders named for
  domain concepts — beats `components/`, `hooks/`, `utils/` mega-folders that force you
  to open five directories to understand one feature.
- **Depend downward only.** Features may depend on shared/foundation code; shared code
  must never import a feature. This keeps shared code reusable and features independent.
- **Encode the public surface.** Each feature exposes an `index.ts` barrel; imports from
  another feature go through the barrel, never into its internals. This makes refactors
  local.
- **Co-locate tests and stories with source.** `Button.tsx`, `Button.test.tsx`,
  `Button.stories.tsx` together — proximity keeps them in sync and easy to delete as a unit.
- **Shallow beats deep.** Prefer a handful of clear top-level areas over deep nesting.
  Deep trees hide code and make imports fragile.

## Best Practices

- Use a small, stable top level: `src/features/` (or `modules/`), `src/shared/` (or `ui/`,
  `lib/`), `src/app/` (routing, providers, entry). Everything else is a subfolder of a feature.
- Put truly cross-cutting primitives (design-system components, `fetchClient`, formatters)
  in `shared/`. If something is used by exactly one feature, it belongs *in* that feature —
  do not pre-promote it to shared.
- Name folders after domain concepts (`checkout/`, `search/`), not layers (`containers/`,
  `presentational/`). Layer names age badly and hide intent.
- Enforce boundaries with tooling — ESLint `no-restricted-imports` / `eslint-plugin-boundaries`
  or Nx/Turborepo tags — so a forbidden cross-feature import fails CI, not code review.
- Align route folders with feature folders (e.g. Next.js `app/checkout/` maps to
  `features/checkout/`) so code-split boundaries follow feature boundaries.
- Keep barrels thin: re-export only the feature's public API. Avoid `export *` from deep
  trees — it defeats tree-shaking and leaks internals.

## Examples

**Good Example** — feature-grouped, boundaries enforceable

```text
src/
  features/
    checkout/
      CheckoutPage.tsx
      useCart.ts
      cart.test.ts
      index.ts            # public API: exports CheckoutPage only
  shared/
    ui/Button.tsx         # design-system primitive, used everywhere
    lib/fetchClient.ts
  app/
    router.tsx
    providers.tsx
// search imports checkout via `features/checkout` — the barrel, not its internals.
```

**Bad Example** — grouped by type; coupling is invisible

```text
src/
  components/  Button.tsx  CheckoutPage.tsx  SearchBar.tsx   // unrelated files jumbled
  hooks/       useCart.ts  useSearch.ts                      // logic split from its UI
  utils/       helpers.ts                                    // dumping ground everyone imports
// Changing checkout means editing components/, hooks/, utils/ — three folders, no boundary.
// Any file can deep-import useCart, so nothing is safe to refactor.
```

## Common Mistakes

- A `utils/helpers.ts` catch-all that grows unbounded and is imported everywhere.
- Promoting code to `shared/` "just in case" before a second consumer exists.
- Deep-importing another feature's internal file instead of its barrel.
- Splitting a component from its hook, test, and styles across four type-based folders.
- Mirroring backend layer names (`services/`, `dtos/`) in the UI where they add nothing.
- No lint rule for boundaries, so architecture erodes one convenient import at a time.

## Production Tips

- In a monorepo, express features as packages with explicit `dependencies`; the package
  manifest becomes the boundary the toolchain enforces.
- Add a scaffolding generator (Plop/Hygen) so new features are born with the correct
  structure, barrel, and test files — consistency by default, not by discipline.

## AI Review Checklist

- Is the new code grouped by feature/domain rather than by file type?
- Does it depend only downward (feature → shared), never shared → feature?
- Are cross-feature imports routed through a barrel, not into internals?
- Are tests and stories co-located with the source they cover?
- Is anything placed in `shared/` that has only one consumer (should be feature-local)?
- Is there a lint/tooling rule that fails forbidden imports in CI?

## Related

- `knowledge/frontend/01-frontend-architecture.md`
- `knowledge/frontend/02-component-driven-development.md`
- `knowledge/frontend/21-code-splitting.md`
- `knowledge/frontend/24-documentation.md`
- `knowledge/frontend/19-build-tools.md`

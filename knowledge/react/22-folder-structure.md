---
id: react/22-folder-structure
topic: react
slug: folder-structure
title: "React Folder Structure"
type: doc
order: 22
status: ready
tags: [react, folder-structure]
related: [react/02-component-architecture, react/23-code-style, react/30-engineering-principles, react/18-state-management, react/09-custom-hooks]
when_to_use: "Read before creating new files or organizing the folder and directory structure of a React project."
---
# React Folder Structure

## Purpose

This document defines the recommended folder structure for React applications.

The objective is to organize code in a way that improves discoverability, scalability, maintainability, and collaboration between engineers and AI coding assistants.

A consistent project structure reduces cognitive load and makes large applications easier to navigate.

---

## Core Principle

**Organize code by feature, not by file type.** Files that change together should
live together. When you build the "edit profile" screen you touch its component, its
hook, its API call, and its types — if those are scattered across `components/`,
`hooks/`, `api/`, and `types/`, every change is a treasure hunt across four folders.
Group them by the feature they serve and the change stays in one directory.

The type-based layout looks tidy at 20 files and collapses at 500: every folder holds
files from every feature, so nothing tells you where a feature begins or ends, and
deleting a feature means grepping the whole tree.

**Bad Example** — grouped by technical type. To understand or delete `checkout` you
must visit six folders, and none of them makes the feature's boundary visible.

```
src/
  components/
    CheckoutForm.tsx      # checkout
    ProductCard.tsx       # products
    LoginForm.tsx         # auth
  hooks/
    useCheckout.ts        # checkout
    useProductSearch.ts   # products
  api/
    checkout.ts           # checkout
    products.ts           # products
  types/
    checkout.ts           # checkout
    product.ts            # products
```

**Good Example** — grouped by feature. Everything `checkout` needs sits under one
folder; the feature is a unit you can read, test, move, or delete in one place.

```
src/
  features/
    checkout/
      components/CheckoutForm.tsx
      hooks/useCheckout.ts
      api/checkout.ts
      checkout.types.ts
      index.ts            # the feature's public surface
    products/
      components/ProductCard.tsx
      hooks/useProductSearch.ts
      api/products.ts
      products.types.ts
      index.ts
```

This is the same idea Next.js and Remix encode with route/segment folders and what
Feature-Sliced Design formalizes at scale. The principle is framework-independent:
proximity should track change, not technology.

---

## Design Principles

Every project structure should follow these principles:

- predictable;
- scalable;
- discoverable;
- reusable;
- framework-independent where practical.

Folder organization should reflect the architecture of the application.

---

## Recommended Structure

```
src/
  app/          # composition root: providers, router, entry point
  features/     # business capabilities — the bulk of the app lives here
  components/   # cross-feature, presentational UI (Button, Modal, Spinner)
  hooks/        # cross-feature reusable hooks (useDebounce, useMediaQuery)
  services/     # framework-agnostic logic (analytics, auth token store)
  api/          # HTTP client + shared request/response plumbing
  layouts/      # reusable page shells (AppLayout, AuthLayout)
  pages/        # route-level components that compose features + layouts
  providers/    # app-wide context providers, wired together in app/
  store/        # global client state (see 18-state-management)
  utils/        # pure, framework-independent helpers
  types/        # cross-feature TypeScript types
  constants/    # shared constants (routes, limits)
  assets/       # images, icons, fonts
  styles/       # global CSS, design tokens, theme variables
  test/         # shared render helpers, mocks, setup
```

Not every project requires every directory. Only create folders that provide clear
value — an empty `services/` or `contexts/` folder is noise. A small app may collapse
`store/`, `contexts/`, and `providers/` into `app/` and grow them out later.

> Framework note: with Next.js App Router, `app/` is a reserved routing directory, so
> put this composition/config layer under `src/` alongside `features/` (or name it
> `bootstrap/`) to avoid colliding with the router's semantics. With Vite/React Router
> there is no such collision and `src/app/` is fine.

---

## App

The `app` directory contains application-level configuration.

Examples:

- routing;
- providers;
- initialization;
- global configuration.

Avoid placing feature-specific code here.

---

## Features

The `features` directory contains business functionality. Each feature is a
self-contained module owning its components, hooks, API calls, types, and tests:

```
features/
  authentication/
    components/
      LoginForm.tsx
      LoginForm.test.tsx
    hooks/
      useSession.ts
    api/
      auth.ts
    auth.types.ts
    index.ts            # public surface — the ONLY entry point for outsiders
```

**Expose a public surface with a barrel `index.ts`.** Everything a feature deliberately
shares goes through its `index.ts`; everything else is private to the folder. This lets
you refactor a feature's internals freely as long as the barrel stays stable.

```ts
// features/authentication/index.ts
export { LoginForm } from "./components/LoginForm";
export { useSession } from "./hooks/useSession";
export type { Session } from "./auth.types";
// api/auth.ts is intentionally NOT exported — it is an internal detail.
```

**Good Example** — outsiders import only the feature's public surface.

```ts
// pages/LoginPage.tsx
import { LoginForm } from "@/features/authentication";
```

**Bad Example** — reaching into a feature's internals. This couples the caller to a
file path that should be free to move, and quietly turns a private helper into public
API. Enforce the boundary with an ESLint rule (e.g. `no-restricted-imports` or
`eslint-plugin-boundaries`) so deep imports fail in CI, not just in review.

```ts
// pages/LoginPage.tsx
import { LoginForm } from "@/features/authentication/components/LoginForm";
import { refreshToken } from "@/features/authentication/api/auth"; // private detail!
```

**Keep features from importing each other directly.** Cross-feature dependencies
create cycles and make features un-deletable. If `checkout` needs the current user,
depend on shared state (`store/`) or lift the shared piece into `features/shared/` or
a top-level module — do not import `features/profile` from `features/checkout`.

---

## Components

The `components` directory contains reusable UI components.

Examples:

```
components/
  Button/
  Modal/
  Card/
  Avatar/
  Spinner/
```

Components in this directory must not depend on business features. The dependency
arrow points one way: `features/` may import from `components/`, never the reverse. A
`components/` file that imports from `features/` is a design smell — the component
belongs inside that feature instead.

---

## Hooks

Store reusable Custom Hooks.

Examples:

```
hooks/
  useDebounce.ts
  useBreakpoint.ts
  useLocalStorage.ts
```

Feature-specific hooks should remain inside their corresponding feature.

---

## Services

Services contain business logic that is independent of React.

Examples:

- authentication;
- analytics;
- storage;
- notifications.

Avoid placing rendering logic inside services.

---

## API

The `api` directory contains communication with external systems.

Examples:

- HTTP clients;
- request helpers;
- API endpoints;
- response mappers.

Components should communicate through this layer rather than directly performing network requests.

---

## Layouts

Layouts define reusable page structures.

Examples:

- AdminLayout;
- DashboardLayout;
- MarketingLayout.

Layouts coordinate structure rather than business logic.

---

## Providers

The `providers` directory contains application-wide providers.

Examples:

- theme;
- authentication;
- query client;
- localization.

Keep provider configuration centralized.

---

## Contexts

Contexts expose shared application state.

Use Context only when state is naturally shared across multiple branches of the component tree.

Avoid using Context as a replacement for all state management.

---

## Store

Store global application state when required.

Examples:

- authentication;
- user preferences;
- feature flags.

Feature-specific state should remain within the feature whenever possible.

---

## Utils

Utility functions should be:

- pure;
- reusable;
- framework-independent.

Avoid adding business logic to generic utility modules.

---

## Types

Shared TypeScript definitions belong here.

Examples:

- interfaces;
- type aliases;
- enums.

Feature-specific types should remain within the feature.

---

## Constants

Store shared constants.

Examples:

- routes;
- limits;
- configuration values.

Avoid magic numbers and repeated string literals.

---

## Assets

Store static resources.

Examples:

- images;
- icons;
- fonts;
- videos.

Optimize assets before adding them to the project.

---

## Styles

Global styles belong here.

Examples:

- resets;
- typography;
- design tokens;
- theme variables.

Component-specific styles should remain close to the component.

---

## Tests

Shared testing utilities may live here.

Examples:

- render helpers;
- mock data;
- testing configuration.

Feature-specific tests should remain close to the code they verify.

---

## Co-location

Prefer keeping related files together. A component is a folder, not a lone file, once
it has more than one concern:

```
ProductCard/
  ProductCard.tsx
  ProductCard.test.tsx
  ProductCard.types.ts
  ProductCard.module.css
  index.ts
```

The folder's `index.ts` re-exports the component so imports read
`import { ProductCard } from "@/components/ProductCard"` regardless of internal layout.

A co-located React 19 component keeps its type, its markup, and its local logic in one
place — `ref` is an ordinary prop (no `forwardRef`), and a form action is expressed
with `useActionState`:

```tsx
// components/ProductCard/ProductCard.tsx
import type { Ref } from "react";
import { useActionState } from "react";
import styles from "./ProductCard.module.css";
import type { Product } from "./ProductCard.types";

export function ProductCard({
  product,
  ref, // React 19: ref is a normal prop, forwardRef is no longer required
  onAdd,
}: {
  product: Product;
  ref?: Ref<HTMLDivElement>;
  onAdd: (id: string) => Promise<void>;
}) {
  const [error, addAction, isPending] = useActionState(async () => {
    try {
      await onAdd(product.id);
      return null;
    } catch {
      return "Could not add to cart.";
    }
  }, null);

  return (
    <div ref={ref} className={styles.card}>
      <h3>{product.name}</h3>
      <form action={addAction}>
        <button disabled={isPending}>{isPending ? "Adding…" : "Add to cart"}</button>
      </form>
      {error && <p role="alert">{error}</p>}
    </div>
  );
}
```

Files that evolve together should remain together — you never edit the markup without
glancing at its types, and the test sits one line away.

**A note on barrels.** Per-folder `index.ts` files that re-export a single component are
cheap and helpful. A single giant `src/components/index.ts` that re-exports the whole
library is not: it defeats tree-shaking in some bundler setups and invites circular
imports. Barrel at the boundary of a module, not across the entire codebase.

---

## Naming

Use consistent naming.

Examples:

Use `PascalCase` for component folders and files, `camelCase` for hooks and utilities,
and `kebab-case` for feature/route folders — pick a convention per category and hold to
it. Match a component's file name to its exported component so search and imports line up.

```
Button/          # component folder — PascalCase
UserProfile/
CheckoutForm/
useSession.ts    # hook — camelCase, use* prefix
```

Avoid:

```
button/          # inconsistent casing for a component
buttonComponent/ # redundant suffix
newFolder/       # says nothing
misc/            # a junk drawer that only grows
```

Directory names should communicate responsibility.

---

## AI Execution Checklist

## Investigation

☐ Review current project structure.

☐ Identify feature boundaries.

☐ Identify reusable components.

☐ Identify shared modules.

---

## Planning

☐ Organize by feature.

☐ Keep related files together.

☐ Separate reusable code.

☐ Minimize cross-feature dependencies.

---

## Verification

☐ Folder structure remains predictable.

☐ Features remain isolated.

☐ Shared code centralized.

☐ No unnecessary directories.

☐ Naming is consistent.

---

## Common Mistakes

Avoid:

Organizing everything by file type.

Creating generic folders such as `helpers` or `misc`.

Mixing business logic with reusable UI.

Creating deep directory hierarchies.

Duplicating shared utilities.

Moving feature-specific code into global directories.

---

## Completion Criteria

The project structure is complete when:

- features are clearly separated;
- reusable components are centralized;
- shared modules are organized consistently;
- related files are co-located;
- folder names communicate responsibility;
- the architecture supports future growth.

---

## Summary

A well-designed folder structure reflects the architecture of the application rather than individual technologies.

By organizing code around features, responsibilities, and reuse, React projects remain easier to understand, scale, and maintain throughout their lifecycle.
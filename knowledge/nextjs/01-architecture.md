---
id: nextjs/01-architecture
topic: nextjs
slug: architecture
title: "Next.js Architecture"
type: doc
order: 1
status: ready
tags: [nextjs, architecture]
related: [nextjs/02-project-structure, nextjs/03-app-router, nextjs/06-server-components, nextjs/08-rendering-strategies, react/02-component-architecture]
when_to_use: "Read before establishing the overall architecture of a new Next.js application."
---
# Next.js Architecture

## Purpose

This document defines the architectural principles for building applications with Next.js.

The objective is to create applications that are scalable, maintainable, performant, secure, and easy to understand by following a consistent server-first architecture.

Architecture decisions should prioritize long-term maintainability over short-term implementation speed.

---

## Core Principle

Render on the server whenever possible.

Move to the client only when necessary.

The server is the default execution environment.

---

## Architectural Goals

Every Next.js application should strive for:

- server-first rendering;
- minimal client-side JavaScript;
- clear separation of responsibilities;
- scalable feature organization;
- predictable data flow;
- high performance;
- accessibility by default.

---

## Server-First Architecture

Prefer executing logic on the server.

Examples:

- data fetching;
- authentication;
- authorization;
- metadata generation;
- SEO;
- caching;
- data transformation.

Move logic to the client only when browser APIs or user interaction require it.

---

## Rendering Hierarchy

Design the application using the following hierarchy.

```
Application

        ↓

Route

        ↓

Layout

        ↓

Page

        ↓

Feature

        ↓

Component
```

Each layer should have a clearly defined responsibility.

In the App Router this hierarchy maps directly onto the `app/` directory. Special files are reserved names, not conventions you invent:

```
app/
    layout.tsx          # root layout: <html>/<body>, providers, persistent UI
    page.tsx            # "/" route
    dashboard/
        layout.tsx      # nested layout, wraps all dashboard routes
        page.tsx        # "/dashboard"
        loading.tsx     # streaming fallback (React Suspense boundary)
        error.tsx       # error boundary ("use client" required)
        [id]/
            page.tsx    # "/dashboard/:id" dynamic segment
    api/
        health/
            route.ts    # Route Handler at "/api/health"
```

Every file under `app/` is a Server Component by default. Adding `"use client"` at the top of a file opts that module (and its imports) into the client boundary.

---

## Separation of Responsibilities

Each layer should own a specific concern.

## Layout

Responsible for:

- shared page structure;
- navigation;
- providers;
- persistent UI.

---

## Page

Responsible for:

- route-specific composition;
- data loading;
- metadata;
- feature composition.

---

## Feature

Responsible for:

- business functionality;
- state coordination;
- user workflows.

---

## Component

Responsible for:

- rendering UI;
- receiving props;
- emitting events.

Components should remain focused and reusable.

---

## Data Flow

Prefer one-way data flow.

```
Server

↓

Page

↓

Feature

↓

Component
```

Avoid unnecessary bidirectional dependencies.

---

## Business Logic

Business logic should remain independent from presentation.

Prefer placing business logic in:

- services;
- server actions;
- custom hooks (client-side);
- utility modules.

Avoid embedding business logic inside UI components.

Mutations belong in Server Actions — functions marked `"use server"` that run only on the server and can be invoked directly from a form or a client event. They keep write logic, validation, and revalidation off the client bundle.

```tsx
// app/features/products/actions.ts
"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { requireUser } from "@/features/auth/service";
import { createProduct } from "@/features/products/service";

export async function createProductAction(formData: FormData) {
  const user = await requireUser(); // authorize on the server, always
  const name = String(formData.get("name") ?? "").trim();

  if (!name) {
    return { error: "Name is required." }; // validate on the server
  }

  await createProduct({ name, ownerId: user.id });
  revalidatePath("/products"); // invalidate the cached route
  redirect("/products");
}
```

```tsx
// app/products/new/page.tsx  (Server Component — no "use client" needed)
import { createProductAction } from "@/features/products/actions";

export default function NewProductPage() {
  return (
    <form action={createProductAction}>
      <input name="name" required />
      <button type="submit">Create</button>
    </form>
  );
}
```

Re-authorize and re-validate inside every action. A Server Action is a public HTTP endpoint — never trust that the caller is the UI you shipped.

---

## Client Components

Use Client Components only when required.

Examples:

- browser APIs;
- event handlers;
- local state;
- animations;
- interactive forms.

Everything else should remain on the server.

The `"use client"` directive marks a boundary, not a leaf. Once a module is a Client Component, everything it imports is bundled and hydrated on the client. Keep the boundary as small and as deep in the tree as possible, and pass Server Components through as `children` rather than importing them into the client module.

```tsx
// Bad — the whole page becomes a Client Component just to hold one toggle.
// Data fetching, secrets access, and static markup all ship to the browser.
"use client";

import { useState } from "react";

export default function ProductPage({ id }: { id: string }) {
  const [open, setOpen] = useState(false);
  // fetch, auth, and rendering now all run client-side. Avoid.
}
```

```tsx
// Good — the page stays a Server Component. Only the interactive island
// is a Client Component, and the server-rendered detail is passed in as a child.
// app/products/[id]/page.tsx  (Server Component by default)
import { getProduct } from "@/features/products/service";
import { Expandable } from "@/features/products/expandable";
import { ProductDetail } from "@/features/products/product-detail";

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params; // params is async in Next.js 15+
  const product = await getProduct(id);

  return (
    <Expandable summary={product.name}>
      <ProductDetail product={product} />
    </Expandable>
  );
}
```

```tsx
// app/../expandable.tsx  (the only client module)
"use client";

import { useState, type ReactNode } from "react";

export function Expandable({
  summary,
  children,
}: {
  summary: string;
  children: ReactNode; // a Server Component, rendered on the server
}) {
  const [open, setOpen] = useState(false);
  return (
    <section>
      <button onClick={() => setOpen((v) => !v)} aria-expanded={open}>
        {summary}
      </button>
      {open && children}
    </section>
  );
}
```

Note that in Next.js 15+, `params` and `searchParams` on pages are Promises and must be awaited.

---

## Server Components

Prefer Server Components for:

- static content;
- database access;
- API requests;
- authentication;
- SEO;
- metadata generation.

Server Components reduce client-side JavaScript and improve performance.

Server Components can be `async` and fetch directly from the data source. In Next.js 15+, `fetch()` is **uncached by default** — a bare `fetch` runs on every request. Opt into caching explicitly when the data is safe to reuse.

```tsx
// app/dashboard/page.tsx  (Server Component)
export default async function DashboardPage() {
  // Uncached by default: revalidated on every request.
  const live = await fetch("https://api.example.com/metrics").then((r) =>
    r.json(),
  );

  // Opt-in caching: reuse for up to 60s (Incremental Static Regeneration).
  const config = await fetch("https://api.example.com/config", {
    next: { revalidate: 60 },
  }).then((r) => r.json());

  // Opt-in caching: cache indefinitely until manually revalidated.
  const terms = await fetch("https://api.example.com/terms", {
    cache: "force-cache",
  }).then((r) => r.json());

  return <Metrics live={live} config={config} terms={terms} />;
}
```

Direct database or ORM access (which does not go through `fetch`) is never cached automatically — colocate it behind the `use cache` directive or a service function when caching is desired. See `09-data-fetching` and `10-caching` for the full model.

---

## Feature Organization

Organize the application by feature rather than technology.

Example:

```
features/

    authentication/

    dashboard/

    checkout/

    products/

    profile/
```

Each feature should remain as self-contained as practical.

---

## Shared Components

Reusable UI belongs in shared component directories.

Examples:

```
components/

    Button/

    Card/

    Modal/

    Avatar/
```

Shared components should remain independent from business features.

---

## State Management

Keep state as close as possible to where it is used.

Prefer:

- server state on the server;
- local UI state inside components;
- global state only for application-wide concerns.

Avoid unnecessary global state.

---

## Performance

Architecture should encourage:

- small client bundles;
- minimal hydration;
- efficient caching;
- streaming;
- code splitting.

Performance should result from good architecture rather than excessive optimization.

---

## Security

Keep sensitive operations on the server.

Examples:

- secrets;
- API keys;
- database access;
- authorization checks.

Never trust client-side validation alone.

Environment variables enforce this boundary. Only variables prefixed with `NEXT_PUBLIC_` are inlined into the client bundle; every other variable exists only on the server. Reading a non-public secret in a Client Component yields `undefined` — but the real risk is prefixing a secret by mistake.

```tsx
// Bad — the secret is now baked into the client bundle and shipped to browsers.
// NEXT_PUBLIC_STRIPE_SECRET_KEY=sk_live_...   <-- never prefix a secret
const key = process.env.NEXT_PUBLIC_STRIPE_SECRET_KEY;
```

```tsx
// Good — the secret is read only in server code (Server Component, Route
// Handler, or Server Action) and never crosses the network to the client.
// STRIPE_SECRET_KEY=sk_live_...
const key = process.env.STRIPE_SECRET_KEY;
```

Use `NEXT_PUBLIC_` only for values that are genuinely public (analytics IDs, public API base URLs). Keep secrets, database URLs, and API keys unprefixed and server-side.

---

## Accessibility

Architecture should support accessibility by default.

Examples:

- semantic HTML;
- keyboard navigation;
- accessible layouts;
- logical heading hierarchy.

Accessibility should not depend on client-side JavaScript.

---

## AI Execution Checklist

## Investigation

☐ Identify server responsibilities.

☐ Identify client responsibilities.

☐ Review feature boundaries.

☐ Review shared components.

---

## Planning

☐ Keep rendering on the server.

☐ Minimize client components.

☐ Separate business logic.

☐ Organize by feature.

---

## Verification

☐ Server-first architecture followed.

☐ Components remain reusable.

☐ Business logic separated.

☐ State ownership is clear.

☐ Performance considered.

☐ Accessibility preserved.

---

## Examples

**Good Example** — the boundary between server and client is a deliberate line

```tsx
// app/products/[id]/page.tsx — a Server Component: data access stays on the server.
import { getProduct } from '@/lib/products';       // imports the DB client
import { AddToCart } from './add-to-cart';         // the only interactive part

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const product = await getProduct(id);            // no API round trip, no client bundle

  return (
    <article>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      {/* Interactivity is isolated to one small leaf component. */}
      <AddToCart productId={product.id} priceCents={product.priceCents} />
    </article>
  );
}
```

```tsx
// app/products/[id]/add-to-cart.tsx
'use client';

export function AddToCart({ productId, priceCents }: { productId: string; priceCents: number }) {
  const [pending, setPending] = useState(false);
  return <button disabled={pending} onClick={() => setPending(true)}>Add — {priceCents / 100} €</button>;
}
```

The database client, the product query, and the pricing logic never reach the browser. Only
`AddToCart` ships JavaScript.

**Bad Example** — the whole page marked as a Client Component

```tsx
'use client';                       // one directive pushes everything below to the browser

import { db } from '@/lib/db';      // a server-only module in a client bundle:
                                    // either the build fails, or credentials ship
export default function ProductPage({ params }: { params: { id: string } }) {
  const [product, setProduct] = useState<Product | null>(null);

  // A request that could have been a direct query now costs a round trip, runs
  // after hydration, and shows a spinner where server-rendered HTML would have been.
  useEffect(() => {
    fetch(`/api/products/${params.id}`)
      .then((r) => r.json())
      .then(setProduct);
  }, [params.id]);

  if (!product) return <Spinner />;
  return <h1>{product.name}</h1>;
}
```

---

## Common Mistakes

Avoid:

Making entire pages Client Components.

Fetching data inside presentation components.

Duplicating business logic.

Creating unnecessary global state.

Mixing server and client responsibilities.

Ignoring feature boundaries.

Placing secrets in client-side code.

---

## Completion Criteria

The architecture is complete when:

- server-first principles are followed;
- client components are used only when necessary;
- responsibilities are clearly separated;
- feature organization is consistent;
- security has been considered;
- accessibility has been preserved;
- the architecture supports long-term scalability.

---

## Summary

A well-designed Next.js architecture leverages the strengths of the server while keeping the client lightweight.

By clearly separating responsibilities, minimizing client-side JavaScript, and organizing the application around features, teams can build applications that are scalable, maintainable, secure, and performant.

## Related

- `knowledge/nextjs/02-project-structure.md`
- `knowledge/nextjs/03-app-router.md`
- `knowledge/nextjs/06-server-components.md`
- `knowledge/nextjs/08-rendering-strategies.md`
- `knowledge/react/02-component-architecture.md`

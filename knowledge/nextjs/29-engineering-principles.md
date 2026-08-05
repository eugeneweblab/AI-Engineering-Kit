---
id: nextjs/29-engineering-principles
topic: nextjs
slug: engineering-principles
title: "Next.js Engineering Principles"
type: doc
order: 29
status: ready
tags: [nextjs, engineering-principles]
related: [nextjs/06-server-components, nextjs/07-client-components, nextjs/10-caching, nextjs/11-server-actions, nextjs/28-best-practices]
when_to_use: "Read before designing a new Next.js feature or reviewing an architectural decision in an App Router codebase."
---
# Next.js Engineering Principles

## Purpose

This document defines the non-negotiable principles that govern how code is written in a
Next.js App Router application. It is the "constitution" the other documents elaborate on.
An agent applies these when deciding *where* logic lives (server vs client), *how* data
flows, and *what* trade-off to accept when two correct-looking options exist.

These are decision rules, not style preferences. Each states what to do, why, and the cost
of ignoring it.

## Why It Matters

The App Router blurs a line that used to be enforced by the runtime: the same TypeScript
file can execute on the server or ship to the browser. That flexibility is powerful and
dangerous. A single misplaced `"use client"` can drag a data layer, a secret, or a 200 KB
dependency into every user's browser. A misunderstood cache boundary can serve one user's
data to another. These mistakes compile cleanly and often pass a happy-path test — they
surface as security incidents and performance regressions in production. Principles exist
to make the right structure the default so those failures never get written.

## Core Principles

- **Server-first by default.** A component is a Server Component unless it *needs* the
  browser (state, effects, event handlers, browser APIs). Reach for `"use client"` only at
  the leaf where interactivity actually lives, because everything below a client boundary
  ships to the browser and cannot access server resources.
- **The network boundary is a security boundary.** Anything a Client Component can import,
  the browser can read. Never let secrets, database clients, or private business logic
  cross into client code — the cost of a leak is total exposure, not a bug.
- **Data flows down through the server, not sideways through the client.** Fetch data in
  Server Components and pass serializable props down. Do not fetch on the client to hydrate
  what the server could have rendered — it adds a round trip, a spinner, and a waterfall.
- **Mutations go through Server Actions or Route Handlers, never trust the client.**
  Re-validate every input and re-check authorization on the server for every mutation,
  because the client is attacker-controlled.
- **Caching is explicit and intentional.** Know for every request whether it is static,
  dynamic, or revalidated, and why. An accidental cache is a correctness bug; an accidental
  dynamic render is a performance bug.
- **Measure before optimizing.** Optimize against real signals (Core Web Vitals, RUM,
  bundle analysis), not intuition. The cost of premature optimization is complexity that
  hides the real bottleneck.

## Best Practices

- Keep `"use client"` at leaves. Pass Server Components into Client Components as `children`
  props rather than importing server logic into a client module.
- Colocate data fetching with the component that renders it; let React dedupe and let
  independent fetches run concurrently instead of forming waterfalls.
- Validate all external input (form data, params, search params) with a schema (e.g. Zod)
  at the server boundary before use.
- Prefer the framework primitive over a library: `next/image`, `next/font`, `next/link`,
  Server Actions, and the built-in cache before adding a client-side data or router library.
- Make dynamic rendering a deliberate choice. Reading `cookies()`, `headers()`, or
  `searchParams` opts a route into dynamic rendering — do it because the page truly needs
  per-request data, not by accident.
- Return typed, serializable data across the server/client boundary. Class instances, Dates
  passed carelessly, and functions do not serialize.

## Examples

**Good Example** — server fetches, client leaf handles interactivity

```tsx
// app/products/page.tsx — Server Component (no "use client")
import { getProducts } from "@/lib/products"; // server-only data access
import { AddToCart } from "./add-to-cart";

export default async function Page() {
  const products = await getProducts(); // runs on the server, no client JS, no round trip
  return (
    <ul>
      {products.map((p) => (
        <li key={p.id}>
          {p.name}
          {/* Only the interactive button is a Client Component */}
          <AddToCart productId={p.id} />
        </li>
      ))}
    </ul>
  );
}
```

**Bad Example** — client fetch drags data access to the browser

```tsx
"use client"; // makes the whole tree client-side
import { db } from "@/lib/db"; // DANGER: bundles the DB client + credentials to the browser
import { useEffect, useState } from "react";

export default function Page() {
  const [products, setProducts] = useState([]);
  useEffect(() => {
    // extra round trip + spinner + waterfall the server could have avoided
    fetch("/api/products").then((r) => r.json()).then(setProducts);
  }, []);
  return <ul>{products.map((p) => <li key={p.id}>{p.name}</li>)}</ul>;
}
```

## Common Mistakes

- Adding `"use client"` to a page or layout "to be safe," turning the whole subtree client-side.
- Importing server-only modules (db clients, secret config) into files reachable from client code.
- Fetching on the client what a Server Component could render, creating request waterfalls.
- Trusting `searchParams` or form data without server-side validation and authorization.
- Treating caching as automatic — not knowing whether a given route is static or dynamic.
- Optimizing perceived-slow code before profiling, while the real bottleneck goes untouched.

## Production Tips

- Run `next build` in CI and inspect the route table: confirm each route's render mode
  (static/dynamic) matches intent. An unexpected `ƒ` (dynamic) or `○` (static) marker is a review flag.
- Analyze the bundle (`@next/bundle-analyzer`) on every meaningful change to catch a
  dependency that accidentally crossed the client boundary.
- Track Core Web Vitals from real users (`useReportWebVitals` or a RUM provider), not just lab scores.

## AI Review Checklist

- Is every `"use client"` at an interactive leaf, not on a page or layout by default?
- Can any server-only secret or data client be reached from a Client Component's import graph?
- Is data fetched on the server and passed down, rather than fetched on the client?
- Does every mutation re-validate input and re-check authorization on the server?
- Is each route's static/dynamic render mode intentional and understood?
- Is any optimization justified by a measurement rather than a guess?

## Related

- `knowledge/nextjs/06-server-components.md`
- `knowledge/nextjs/07-client-components.md`
- `knowledge/nextjs/10-caching.md`
- `knowledge/nextjs/11-server-actions.md`
- `knowledge/nextjs/28-best-practices.md`

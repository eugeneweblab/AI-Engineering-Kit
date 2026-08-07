---
id: nextjs/09-data-fetching
topic: nextjs
slug: data-fetching
title: "Next.js Data Fetching"
type: doc
order: 9
status: ready
tags: [nextjs, data-fetching, ProfilePage, getUser, getOrders, ProductsPage, no-store, API_URL]
applies_to: [app-router]
related: [nextjs/06-server-components, nextjs/10-caching, nextjs/12-api-routes, react/16-data-fetching]
when_to_use: "Read before fetching data from a database or API in a Next.js app."
---
# Next.js Data Fetching

## Purpose

This document defines the engineering standards for fetching data in Next.js applications.

The objective is to build applications that are fast, scalable, secure, and maintainable by leveraging the server-first architecture of the App Router.

Every data request should have a clear purpose, an appropriate caching strategy, and a predictable lifecycle.

---

## Core Principle

Fetch data on the server whenever possible.

Move data fetching to the client only when real-time interaction or browser APIs require it.

---

## General Workflow

Every data request should follow this lifecycle.

```
Request

↓

Determine Rendering Strategy

↓

Determine Cache Strategy

↓

Fetch Data

↓

Validate Response

↓

Transform Data

↓

Render UI
```

Every step should be intentional.

---

## Preferred Data Sources

Prefer accessing data directly from its source.

Examples:

- database;
- internal service;
- external API;
- CMS;
- authentication provider.

Avoid introducing unnecessary proxy layers.

---

## Fetching in Server Components

Server Components are the preferred location for data fetching.

Example:

```tsx
export default async function ProductsPage() {
    const products = await getProducts();

    return <ProductsTable products={products} />;
}
```

Benefits include:

- reduced client JavaScript;
- improved security;
- simplified architecture;
- automatic streaming support.

---

## Avoid Client Fetching

Avoid fetching initial page data inside Client Components.

Bad example:

```tsx
"use client";

useEffect(() => {
    loadProducts();
}, []);
```

Prefer fetching on the server and passing the result as props.

---

## Using fetch()

Use the built-in `fetch()` API whenever possible.

Benefits:

- automatic request memoization;
- opt-in caching and revalidation;
- integration with Next.js rendering;
- support for tag- and time-based revalidation.

In Next.js 15+, `fetch()` is uncached by default. Opt into caching explicitly with `cache: "force-cache"` or `next: { revalidate }`.

Avoid introducing alternative HTTP clients unless required by the project.

---

## Request Memoization

Within a single request, identical `fetch()` calls are automatically memoized.

Example:

```
Component A

↓

fetch("/api/products")

↓

Component B

↓

fetch("/api/products")

↓

Single Network Request
```

Avoid implementing manual request deduplication for identical server-side requests.

---

## Cache Strategies

Choose a cache strategy intentionally.

In Next.js 15+, `fetch()` defaults to uncached (`no-store`). Caching is opt-in.

Common options include:

- `no-store` (the default; fetches fresh on every request)
- `force-cache` (opt in to indefinite caching)
- time-based revalidation via `next: { revalidate }`
- tag-based revalidation via `next: { tags }`

The selected strategy should reflect business requirements.

---

## Static Data

Examples:

- documentation;
- legal pages;
- marketing content;
- configuration.

Prefer aggressive caching.

---

## Frequently Updated Data

Examples:

- product catalog;
- blog;
- CMS content;
- pricing.

Prefer time-based revalidation.

---

## User-Specific Data

Examples:

- profile;
- dashboard;
- notifications;
- orders.

Prefer dynamic rendering with minimal caching.

Never cache user-specific responses publicly.

---

## Database Access

When using:

- Prisma;
- Drizzle;
- Sequelize;
- MongoDB;
- Redis;

query the database directly from the server.

Avoid creating unnecessary internal HTTP requests between the frontend and backend running within the same application.

---

## External APIs

External APIs should be accessed through reusable service modules.

Example:

```
services/

    github.service.ts

    stripe.service.ts

    cms.service.ts
```

Keep HTTP implementation separate from UI.

---

## Data Transformation

Transform data before rendering.

Examples:

- formatting;
- filtering;
- sorting;
- aggregation;
- mapping.

Presentation components should receive data in the format they require.

---

## Validation

Never assume external data is valid.

Validate:

- required fields;
- types;
- nullable values;
- response status;
- error payloads.

Fail gracefully when validation fails.

---

## Error Handling

Every request should define:

- loading state;
- success state;
- error state;
- recovery strategy.

Avoid silent failures.

---

## Parallel Fetching

Independent requests should execute in parallel.

Example:

```
Products

     ↘

      Render

     ↗

Categories
```

Avoid sequential requests when dependencies do not exist.

---

## Sequential Fetching

Fetch sequentially only when one request depends on another.

Example:

```
User

↓

Permissions

↓

Dashboard
```

Document the dependency clearly.

---

## Waterfalls

Avoid request waterfalls.

Bad example:

```
Page

↓

Fetch User

↓

Render

↓

Fetch Orders

↓

Render

↓

Fetch Products
```

Prefer parallel execution whenever practical.

---

## Server Actions

Server Actions should be responsible for:

- mutations;
- form submissions;
- updates;
- deletes;
- business workflows.

Avoid using Server Actions for simple read-only queries.

---

## Streaming

Combine data fetching with streaming for slow or independent content.

Examples:

- analytics;
- dashboards;
- reports;
- recommendations.

Streaming improves perceived performance.

---

## Security

Never expose:

- database credentials;
- API keys;
- private endpoints;
- authorization rules.

Keep sensitive operations on the server.

---

## Accessibility

Loading states should remain accessible.

Verify:

- progress indicators;
- live regions;
- keyboard accessibility;
- focus management after loading.

---

## AI Execution Checklist

## Investigation

☐ Identify data source.

☐ Determine freshness requirements.

☐ Select rendering strategy.

☐ Select cache strategy.

---

## Planning

☐ Fetch on the server.

☐ Avoid duplicate requests.

☐ Validate responses.

☐ Transform data before rendering.

---

## Verification

☐ No unnecessary client fetching.

☐ Cache strategy documented.

☐ Error handling implemented.

☐ Parallel requests used where appropriate.

☐ Sensitive data protected.

☐ Accessibility preserved.

---

## Examples

**Good Example** — fetch where the data is used, in parallel, with explicit caching

```tsx
// Requests for the same URL in one render pass are deduplicated automatically,
// so each component can ask for what it needs without prop-drilling.
async function getUser(id: string) {
  const res = await fetch(`${process.env.API_URL}/users/${id}`, {
    next: { revalidate: 60, tags: [`user:${id}`] },   // cached, taggable
  });
  if (!res.ok) throw new Error(`Failed to load user ${id}: ${res.status}`);
  return res.json() as Promise<User>;
}

export default async function ProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  // Independent requests start together: total latency is the slowest, not the sum.
  const [user, orders] = await Promise.all([getUser(id), getOrders(id)]);

  return <Profile user={user} orders={orders} />;
}
```

```ts
// After a write, invalidate exactly what changed.
'use server';

import { updateTag } from 'next/cache';

export async function updateUser(id: string, data: UpdateUser) {
  await db.user.update({ where: { id }, data });
  updateTag(`user:${id}`);              // not the whole path, not the whole site
}
```

**Bad Example** — a waterfall, an unbounded cache, and errors that vanish

```tsx
export default async function ProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  // Sequential awaits with no dependency between them: two round trips where
  // one would do.
  const user = await getUser(id);
  const orders = await getOrders(id);

  return <Profile user={user} orders={orders} />;
}

async function getUser(id: string) {
  // force-cache on user data: the first response is served to every visitor
  // until the next deploy, and there is no tag to invalidate it.
  const res = await fetch(`${process.env.API_URL}/users/${id}`, { cache: 'force-cache' });

  // A 500 has res.ok === false but does not throw. Parsing it yields undefined
  // fields and the page renders blanks instead of an error boundary.
  return res.json();
}
```

---

## Common Mistakes

Avoid:

Fetching server data inside `useEffect`.

Making HTTP requests to your own backend from Server Components.

Creating request waterfalls.

Ignoring caching.

Duplicating identical requests.

Passing raw API responses directly into UI.

Trusting external data without validation.

Fetching more data than required.

---

## Completion Criteria

A data-fetching implementation is complete when:

- data is fetched from the appropriate location;
- rendering strategy is appropriate;
- caching strategy is defined;
- responses are validated;
- loading and error states exist;
- unnecessary requests have been eliminated;
- sensitive data remains on the server.

---

## Summary

Data fetching is one of the most important architectural concerns in a Next.js application.

By fetching data on the server, choosing the correct caching strategy, validating responses, and avoiding unnecessary client-side requests, applications become faster, more secure, easier to maintain, and significantly more scalable.

## Related

- `knowledge/nextjs/06-server-components.md`
- `knowledge/nextjs/10-caching.md`
- `knowledge/nextjs/12-api-routes.md`
- `knowledge/react/16-data-fetching.md`

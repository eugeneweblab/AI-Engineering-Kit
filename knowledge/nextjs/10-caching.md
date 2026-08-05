---
id: nextjs/10-caching
topic: nextjs
slug: caching
title: "Next.js Caching"
type: doc
order: 10
status: ready
tags: [nextjs, caching, revalidateTag, API_URL, getProduct, revalidatePath]
applies_to: [app-router]
related: [nextjs/09-data-fetching, nextjs/08-rendering-strategies, nextjs/20-performance, performance/08-caching]
when_to_use: "Read before configuring caching or revalidation for data and routes in Next.js."
---
# Next.js Caching

## Purpose

This document defines the engineering standards for caching in Next.js applications.

The objective is to maximize performance, reduce infrastructure costs, improve scalability, and ensure data freshness through intentional caching strategies.

Caching should be considered during application architecture rather than added as an optimization after development.

---

## Core Principle

Cache intentionally.

In Next.js 15+, server-side `fetch()` is uncached by default. Caching is opt-in.

Enable caching deliberately with `cache: "force-cache"`, `next: { revalidate }`, or the `use cache` directive.

Every cached resource should have a clearly defined invalidation strategy.

---

## Cache Layers

A typical Next.js application contains multiple cache layers.

```
Browser Cache

↓

CDN Cache

↓

Next.js Route Cache

↓

Data Cache

↓

Database / External API
```

Each layer serves a different purpose.

Avoid disabling caches without understanding their role.

---

## Cache Strategy

Every request should answer the following questions:

- Can the response be cached?
- How long should it remain valid?
- What event invalidates it?
- Is the cache user-specific?
- Is real-time freshness required?

Caching decisions should be explicit.

---

## Static Content

Examples:

- documentation;
- marketing pages;
- blog posts;
- legal pages.

Prefer long-lived caching.

---

## Dynamic Content

Examples:

- dashboards;
- account information;
- notifications;
- shopping carts.

Prefer dynamic rendering with minimal or no shared caching.

Never publicly cache personalized content.

---

## Data Cache

In Next.js 15+, server-side `fetch()` requests are uncached by default. Opt into the Data Cache explicitly with `cache: "force-cache"` or `next: { revalidate }`, or use the `use cache` directive.

Benefits of caching eligible requests include:

- reduced network traffic;
- improved response times;
- request reuse across renders;
- lower infrastructure costs.

Enable the Data Cache whenever data can tolerate staleness, and leave requests uncached only when fresh data is required on every request.

---

## Route Cache

Static routes can be cached after rendering.

Suitable for:

- landing pages;
- documentation;
- product pages;
- CMS content.

Route caching reduces server workload and improves response times.

---

## Browser Cache

Leverage browser caching for static assets.

Examples:

- images;
- fonts;
- JavaScript bundles;
- CSS;
- icons.

Static assets should be fingerprinted to enable long cache lifetimes safely.

---

## CDN Cache

Use a CDN to cache globally distributed content.

Typical candidates:

- static assets;
- prerendered pages;
- public media;
- downloadable files.

The CDN should serve requests before they reach the application whenever possible.

---

## Revalidation

Use revalidation when stale data is acceptable for a limited period.

Suitable for:

- product catalogs;
- blogs;
- documentation;
- CMS-driven content.

Choose a revalidation interval that reflects business needs.

---

## Cache Invalidation

Every cache requires a clear invalidation strategy.

Common triggers include:

- content publication;
- product updates;
- inventory changes;
- user actions;
- scheduled refreshes.

Invalidation should be predictable and documented.

---

## User-Specific Data

Avoid caching:

- authentication state;
- user profiles;
- private messages;
- orders;
- payment information.

Personalized content should remain isolated per user.

---

## Cache Granularity

Cache the smallest practical unit.

Prefer caching:

- individual requests;
- reusable datasets;
- independent page sections.

Avoid invalidating unrelated content.

---

## Freshness vs Performance

Balance:

- response speed;
- infrastructure cost;
- data accuracy;
- user expectations.

Not every request requires real-time data.

---

## Error Handling

Define cache behavior during failures.

Examples:

- stale content fallback;
- retry strategy;
- graceful degradation.

The application should remain usable even when fresh data cannot be retrieved immediately.

---

## Monitoring

Monitor:

- cache hit ratio;
- cache misses;
- response times;
- revalidation frequency;
- infrastructure load.

Caching effectiveness should be measurable.

---

## Security

Never cache:

- secrets;
- authorization responses;
- private API payloads;
- session-specific information.

Public caches must never expose user data.

---

## Accessibility

Caching should never interfere with accessibility.

Loading indicators, streamed updates, and refreshed content should remain accessible to all users.

---

## AI Execution Checklist

## Investigation

☐ Identify cacheable resources.

☐ Determine freshness requirements.

☐ Identify invalidation events.

☐ Review personalization.

---

## Planning

☐ Select cache strategy.

☐ Define invalidation.

☐ Avoid caching private data.

☐ Minimize redundant requests.

---

## Verification

☐ Cache strategy documented.

☐ Invalidation implemented.

☐ Personalized data protected.

☐ Performance improved.

☐ Accessibility preserved.

☐ Monitoring available.

---

## Examples

**Good Example** — tagged entries, invalidated by the write that changed them

```ts
// lib/products.ts
export async function getProduct(id: string): Promise<Product> {
  const res = await fetch(`${process.env.API_URL}/products/${id}`, {
    next: { revalidate: 300, tags: ['products', `product:${id}`] },
  });
  if (!res.ok) throw new Error(`product ${id}: ${res.status}`);
  return res.json();
}
```

```ts
// app/products/actions.ts
'use server';

export async function renameProduct(id: string, name: string) {
  await db.product.update({ where: { id }, data: { name } });

  // Precise: this product's pages, and any listing that declared the broader tag.
  revalidateTag(`product:${id}`);
  revalidateTag('products');
}
```

```tsx
// Opt out deliberately where freshness matters more than cost, and say why.
export default async function StockPage() {
  // Stock changes per second; a cached value would show items that are gone.
  const stock = await fetch(`${process.env.API_URL}/stock`, { cache: 'no-store' });
  return <StockTable rows={await stock.json()} />;
}
```

**Bad Example** — cached without a key to invalidate, then invalidated with a sledgehammer

```ts
export async function getProduct(id: string) {
  // Cached for a day, with no tag. The only way to refresh it is a redeploy.
  const res = await fetch(`${process.env.API_URL}/products/${id}`, {
    next: { revalidate: 86_400 },
  });
  return res.json();
}

'use server';
export async function renameProduct(id: string, name: string) {
  await db.product.update({ where: { id }, data: { name } });

  // Purges the entire cache for every user and every route, so the next request
  // to any page is a cold miss. This is how a cache becomes a liability.
  revalidatePath('/', 'layout');
}
```

---

## Common Mistakes

Avoid:

Disabling caching without justification.

Caching authenticated responses publicly.

Invalidating the entire cache unnecessarily.

Using real-time rendering for static content.

Ignoring cache monitoring.

Serving stale data indefinitely.

Duplicating cached requests.

---

## Completion Criteria

A caching strategy is complete when:

- appropriate cache layers are used;
- invalidation strategy is defined;
- personalized content remains protected;
- performance objectives are met;
- cache behavior is measurable;
- long-term maintainability has been considered.

---

## Summary

Effective caching is one of the highest-impact optimizations in a Next.js application.

By selecting the appropriate cache layer, defining clear invalidation rules, and protecting personalized data, applications become significantly faster, more scalable, and more cost-efficient without sacrificing correctness.

## Related

- `knowledge/nextjs/09-data-fetching.md`
- `knowledge/nextjs/08-rendering-strategies.md`
- `knowledge/nextjs/20-performance.md`
- `knowledge/performance/08-caching.md`

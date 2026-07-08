---
id: nextjs/10-caching
topic: nextjs
slug: caching
title: "Next.js Caching"
type: doc
order: 10
status: ready
tags: [nextjs, caching]
related: []
when_to_use: "Read before configuring caching or revalidation for data and routes in Next.js."
---
# Next.js Caching

## Purpose

This document defines the engineering standards for caching in Next.js applications.

The objective is to maximize performance, reduce infrastructure costs, improve scalability, and ensure data freshness through intentional caching strategies.

Caching should be considered during application architecture rather than added as an optimization after development.

---

## Core Principle

Cache by default.

Invalidate intentionally.

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

Next.js automatically caches eligible server-side `fetch()` requests.

Benefits include:

- reduced network traffic;
- improved response times;
- automatic request reuse;
- lower infrastructure costs.

Avoid bypassing the Data Cache unless the business requirements demand fresh data.

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
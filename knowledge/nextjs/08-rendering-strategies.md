---
id: nextjs/08-rendering-strategies
topic: nextjs
slug: rendering-strategies
title: "Next.js Rendering Strategies"
type: doc
order: 8
status: ready
tags: [nextjs, rendering-strategies]
related: []
when_to_use: "Read before choosing a rendering strategy for a Next.js route."
---
# Next.js Rendering Strategies

## Purpose

This document defines the engineering standards for selecting and implementing rendering strategies in Next.js applications.

The objective is to deliver the best balance between performance, scalability, freshness of data, SEO, and infrastructure cost.

Rendering strategy is an architectural decision and should be selected intentionally for every route.

---

## Core Principle

Render as early as possible.

Render as late as necessary.

Choose the least dynamic solution that satisfies the business requirements.

---

## Rendering Decision Flow

Every route should follow this decision process.

```
Can the page be static?

        │

       Yes
        │
        ▼

Static Rendering

        │

        No
        │
        ▼

Can stale data be accepted?

        │

       Yes
        │
        ▼

Incremental Static Regeneration

        │

        No
        │
        ▼

Dynamic Rendering

        │

Need faster perceived loading?

        │

       Yes
        │
        ▼

Streaming
```

---

## Static Rendering

Static Rendering generates HTML during build time.

Best suited for:

- marketing pages;
- documentation;
- blog posts;
- pricing pages;
- legal pages;
- landing pages.

Benefits:

- fastest response time;
- excellent SEO;
- minimal server load;
- CDN friendly.

---

## Dynamic Rendering

Dynamic Rendering generates HTML for every request.

Use when content depends on:

- authentication;
- cookies;
- request headers;
- user permissions;
- highly dynamic data.

Examples:

- dashboards;
- account pages;
- admin panels;
- personalized content.

Avoid Dynamic Rendering when static rendering is sufficient.

---

## Incremental Static Regeneration (ISR)

ISR combines static generation with periodic updates.

Suitable for:

- product catalogs;
- news sites;
- documentation;
- e-commerce;
- CMS-driven content.

Benefits:

- static performance;
- fresh content;
- reduced build times.

Define an appropriate revalidation interval.

---

## Streaming

Streaming allows portions of a page to be delivered as they become available.

Recommended for:

- dashboards;
- analytics;
- search results;
- complex pages with multiple data sources.

Benefits:

- improved perceived performance;
- reduced waiting time;
- progressive rendering.

---

## Partial Prerendering (PPR)

When available for the project, Partial Prerendering combines:

- static shell;
- dynamic islands.

Benefits:

- fast initial response;
- selective dynamic rendering;
- reduced server work.

Prefer PPR over making an entire page dynamic when only small sections require personalization.

---

## Client Rendering

Client-side rendering should be limited to interactive UI.

Examples:

- modals;
- dropdowns;
- editors;
- drag-and-drop interfaces.

Avoid using client rendering for primary content when server rendering is possible.

---

## Route-Level Strategy

Each route should explicitly define its rendering strategy.

Examples:

```
/

→ Static

/blog

→ ISR

/dashboard

→ Dynamic

/settings

→ Dynamic

/docs

→ Static
```

Avoid mixing unrelated rendering strategies within the same feature without justification.

---

## Data Freshness

Consider:

- update frequency;
- business requirements;
- user expectations;
- infrastructure cost.

Not all data requires real-time updates.

---

## Caching

Rendering strategy and caching should complement each other.

Review:

- browser cache;
- CDN cache;
- Next.js cache;
- data cache.

Do not disable caching without a measurable reason.

---

## SEO

Prefer server-rendered content for pages that should be indexed.

Examples:

- marketing pages;
- blog articles;
- product pages;
- documentation.

Avoid relying on client rendering for SEO-critical content.

---

## Performance

Evaluate:

- Time to First Byte (TTFB);
- Largest Contentful Paint (LCP);
- Interaction to Next Paint (INP);
- Cumulative Layout Shift (CLS).

Rendering decisions should improve user-perceived performance rather than only backend metrics.

---

## Security

Keep sensitive rendering logic on the server.

Never expose:

- secrets;
- private business rules;
- authorization decisions.

Rendering strategy must not compromise application security.

---

## Accessibility

Rendering strategy must not affect accessibility.

Verify:

- semantic HTML;
- keyboard navigation;
- loading announcements;
- focus management during streamed updates.

---

## AI Execution Checklist

## Investigation

☐ Determine how frequently the data changes.

☐ Determine SEO requirements.

☐ Determine personalization requirements.

☐ Review performance objectives.

---

## Planning

☐ Select the simplest rendering strategy.

☐ Minimize dynamic rendering.

☐ Enable caching where appropriate.

☐ Consider streaming for slow content.

---

## Verification

☐ Rendering strategy documented.

☐ SEO requirements satisfied.

☐ Performance objectives met.

☐ Caching configured appropriately.

☐ Accessibility preserved.

☐ Security maintained.

---

## Common Mistakes

Avoid:

Making every page dynamic.

Using Dynamic Rendering for static content.

Disabling caching unnecessarily.

Fetching identical data multiple times.

Rendering large interactive pages entirely on the client.

Ignoring SEO implications.

Choosing rendering strategies based solely on developer convenience.

---

## Completion Criteria

A rendering strategy is complete when:

- it matches business requirements;
- unnecessary server rendering has been avoided;
- caching strategy is aligned;
- SEO requirements are satisfied;
- performance has been considered;
- the implementation remains maintainable.

---

## Summary

Selecting the correct rendering strategy is one of the most important architectural decisions in a Next.js application.

By favoring Static Rendering whenever possible, introducing ISR for periodically changing content, reserving Dynamic Rendering for personalized experiences, and leveraging Streaming and Partial Prerendering where appropriate, applications achieve an optimal balance between performance, scalability, freshness, and maintainability.
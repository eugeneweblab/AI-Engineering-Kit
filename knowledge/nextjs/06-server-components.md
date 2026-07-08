---
id: nextjs/06-server-components
topic: nextjs
slug: server-components
title: "Next.js Server Components"
type: doc
order: 6
status: ready
tags: [nextjs, server-components]
related: []
when_to_use: "Read before building server-rendered components or moving logic to the server in Next.js."
---
# Next.js Server Components

## Purpose

This document defines the engineering standards for using React Server Components (RSC) in Next.js applications.

The objective is to maximize performance, reduce client-side JavaScript, improve security, and simplify data fetching by keeping as much logic as possible on the server.

Server Components are the default component type in the App Router and should be the first choice for new development.

---

## Core Principle

Everything is a Server Component until proven otherwise.

Only use Client Components when browser capabilities or user interaction require them.

---

## Why Server Components

Server Components provide several advantages:

- zero client-side JavaScript by default;
- direct access to databases;
- direct access to backend services;
- secure handling of secrets;
- improved SEO;
- smaller bundles;
- faster initial page loads;
- reduced hydration.

---

## Responsibilities

Server Components should be responsible for:

- data fetching;
- database queries;
- authentication;
- authorization;
- metadata generation;
- server-side transformations;
- composing Client Components.

Avoid moving these responsibilities to the client.

---

## Rendering Flow

A typical rendering flow:

```
Browser

↓

Request

↓

Server Component

↓

Database / API

↓

Rendered HTML + RSC Payload

↓

Browser

↓

Hydrate Client Components
```

Only Client Components are hydrated.

---

## Data Fetching

Prefer fetching data directly inside Server Components.

Example:

```tsx
export default async function ProductsPage() {
    const products = await getProducts();

    return <ProductsList products={products} />;
}
```

Avoid unnecessary API calls between your frontend and backend when the data is already available on the server.

---

## Database Access

Server Components may communicate directly with:

- PostgreSQL;
- MySQL;
- Prisma;
- Drizzle;
- MongoDB;
- Redis;
- internal services.

Never expose database logic to Client Components.

---

## Authentication

Authentication should be performed on the server.

Examples:

- reading cookies;
- validating sessions;
- verifying JWTs;
- loading the authenticated user.

Client Components should consume authenticated data rather than perform authentication themselves.

---

## Authorization

Authorization checks belong on the server.

Examples:

- role validation;
- permission checks;
- resource ownership.

Never rely solely on client-side authorization.

---

## Secrets

Server Components may safely access:

- API keys;
- environment variables;
- database credentials;
- private tokens.

Never pass sensitive values to Client Components.

---

## Composition Pattern

A common pattern:

```
Server Component

↓

Fetch Data

↓

Pass Props

↓

Client Component

↓

User Interaction
```

Keep the interactive portion as small as possible.

---

## Passing Data

Only pass the data required by Client Components.

Avoid passing:

- entire database models;
- unnecessary collections;
- sensitive information.

Prefer explicit, minimal props.

---

## Client Boundaries

Introducing `"use client"` creates a client boundary.

Everything imported below that boundary becomes part of the client bundle.

Keep client boundaries as small as possible.

---

## Supported Features

Server Components support:

- async/await;
- direct database access;
- server-side fetch;
- caching;
- streaming;
- Server Actions;
- metadata generation.

Take advantage of these capabilities before reaching for client-side solutions.

---

## Unsupported Features

Server Components cannot use:

- `useState`;
- `useEffect`;
- browser APIs;
- DOM APIs;
- event handlers;
- local storage;
- window;
- document.

Interactive behavior belongs in Client Components.

---

## Error Handling

Handle expected failures gracefully.

Examples:

- missing resources;
- authorization failures;
- unavailable services.

Unexpected failures should be isolated using route-level error boundaries.

---

## Performance

Server Components naturally improve:

- bundle size;
- hydration time;
- Time to First Byte (TTFB);
- Core Web Vitals.

Avoid converting components to the client without a measurable reason.

---

## Caching

Server Components integrate with Next.js caching.

Typical strategies include:

- static rendering;
- revalidation;
- dynamic rendering;
- cache tagging.

Choose the simplest strategy that satisfies the application's freshness requirements.

---

## Streaming

Server Components support streaming by default.

Use streaming for:

- dashboards;
- slow data sources;
- large pages;
- independent content sections.

Streaming improves perceived performance without increasing client complexity.

---

## Accessibility

Accessibility should be preserved regardless of rendering strategy.

Verify:

- semantic HTML;
- heading hierarchy;
- accessible forms;
- keyboard navigation.

Rendering on the server should not change accessibility requirements.

---

## AI Execution Checklist

## Investigation

☐ Identify server responsibilities.

☐ Identify interactive requirements.

☐ Review authentication needs.

☐ Review caching strategy.

---

## Planning

☐ Keep rendering on the server.

☐ Minimize client boundaries.

☐ Fetch data directly.

☐ Protect sensitive information.

---

## Verification

☐ Component remains a Server Component where possible.

☐ No browser APIs used.

☐ Data fetched on the server.

☐ Secrets remain protected.

☐ Client bundle minimized.

☐ Accessibility preserved.

---

## Common Mistakes

Avoid:

Adding `"use client"` to entire pages.

Fetching server data inside Client Components unnecessarily.

Passing sensitive information to the client.

Duplicating authentication logic.

Moving business logic into interactive components.

Using API routes as unnecessary proxies for server-side data.

---

## Completion Criteria

A Server Component implementation is complete when:

- server-first principles are maintained;
- data fetching occurs on the server;
- client boundaries are minimized;
- authentication and authorization remain server-side;
- sensitive information is protected;
- performance benefits of Server Components are preserved.

---

## Summary

React Server Components are the foundation of modern Next.js applications.

By keeping rendering, data access, authentication, and business logic on the server while limiting Client Components to interactive UI, applications become faster, more secure, easier to maintain, and significantly more scalable.
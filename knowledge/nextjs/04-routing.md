---
id: nextjs/04-routing
topic: nextjs
slug: routing
title: "Next.js Routing"
type: doc
order: 4
status: ready
tags: [nextjs, routing]
related: []
when_to_use: ""
---
# Next.js Routing

## Purpose

This document defines the engineering standards for navigation and routing in Next.js applications using the App Router.

The objective is to build routing that is predictable, maintainable, accessible, SEO-friendly, and optimized for both users and search engines.

Navigation should feel natural, preserve application state where appropriate, and minimize unnecessary page reloads.

---

## Core Principle

Routes describe resources.

Navigation describes user intent.

URLs should remain stable, meaningful, and shareable.

---

## Routing Architecture

Navigation should follow this hierarchy.

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

Each layer should own only its routing responsibility.

---

## Route Design

Good routes are:

- descriptive;
- stable;
- human-readable;
- SEO-friendly;
- resource-oriented.

Good examples:

```
/products

/products/123

/blog

/blog/react-server-components

/dashboard/settings
```

Avoid implementation-specific URLs.

Examples:

```
/page1

/content2

/view

/list

/index

/homepage
```

---

## Link Component

Always use the Next.js `Link` component for internal navigation.

Example:

```tsx
import Link from "next/link";

<Link href="/products">
    Products
</Link>
```

Benefits include:

- client-side navigation;
- automatic prefetching;
- improved performance.

Avoid using native anchor elements for internal routes unless required.

---

## Programmatic Navigation

Use the router only when navigation cannot be expressed declaratively.

Typical examples:

- after form submission;
- authentication flow;
- wizard navigation;
- conditional redirects.

Avoid imperative navigation for ordinary links.

---

## Redirects

Use server-side redirects whenever possible.

Typical examples:

- authentication;
- onboarding;
- moved resources;
- canonical URLs.

Prefer redirecting before rendering.

---

## Permanent Redirects

Permanent redirects should be used only when the URL change is intended to remain permanent.

Examples:

- renamed pages;
- URL restructuring;
- SEO migrations.

Avoid using permanent redirects for temporary application flows.

---

## Not Found

Return a Not Found response when a requested resource does not exist.

Examples:

- missing product;
- deleted article;
- invalid identifier.

Avoid rendering incomplete or misleading content.

---

## Search Parameters

Use URL search parameters for shareable application state.

Examples:

```
?page=2

?category=phones

?sort=price

?tab=settings
```

Search parameters should represent navigation state rather than temporary UI state.

---

## Dynamic Routes

Dynamic routes represent resource identifiers.

Examples:

```
/users/42

/products/iphone-17

/blog/server-components
```

Keep identifiers stable whenever possible.

---

## Navigation State

Navigation state should be recoverable from the URL whenever appropriate.

Examples:

- filters;
- sorting;
- pagination;
- selected tabs.

Avoid storing navigational state only in component state.

---

## Breadcrumbs

Breadcrumbs should reflect the current navigation hierarchy.

Example:

```
Home

↓

Products

↓

Laptops

↓

MacBook Pro
```

Breadcrumbs improve navigation and SEO.

---

## Deep Linking

Every meaningful application state should support deep linking whenever practical.

Users should be able to:

- refresh;
- bookmark;
- share;
- reopen

without losing important navigation context.

---

## Prefetching

Allow Next.js to prefetch routes whenever appropriate.

Avoid disabling prefetching without measurable performance concerns.

---

## Route Protection

Protect restricted routes on the server.

Examples:

- authentication;
- authorization;
- subscription validation.

Client-side route protection alone is insufficient.

---

## Navigation Performance

Review:

- navigation latency;
- layout persistence;
- unnecessary loading states;
- duplicated requests.

Navigation should feel immediate whenever possible.

---

## Accessibility

Navigation should support:

- keyboard users;
- screen readers;
- visible focus indicators;
- semantic landmarks;
- descriptive link text.

Navigation is one of the most important accessibility features of an application.

---

## SEO

Routes should provide:

- descriptive URLs;
- canonical paths;
- crawlable navigation;
- meaningful hierarchy.

Avoid generating multiple URLs for identical content.

---

## AI Execution Checklist

## Investigation

☐ Review route hierarchy.

☐ Review navigation flow.

☐ Review protected routes.

☐ Review URL structure.

---

## Planning

☐ Keep URLs meaningful.

☐ Prefer declarative navigation.

☐ Preserve shareable state in URLs.

☐ Protect routes on the server.

---

## Verification

☐ Internal links use `Link`.

☐ Redirects implemented correctly.

☐ Invalid resources return Not Found.

☐ Search parameters remain meaningful.

☐ Navigation is accessible.

☐ SEO preserved.

---

## Common Mistakes

Avoid:

Using native anchor elements for internal navigation.

Performing client-side redirects unnecessarily.

Encoding temporary UI state in URLs.

Creating unstable route structures.

Using opaque identifiers when readable alternatives exist.

Ignoring canonical URLs.

Protecting routes only on the client.

---

## Completion Criteria

Routing is complete when:

- URLs are stable and meaningful;
- navigation is intuitive;
- route protection is implemented on the server;
- deep linking is supported where appropriate;
- accessibility has been verified;
- SEO requirements are satisfied.

---

## Summary

Well-designed routing is more than connecting pages—it defines how users understand and navigate an application.

By keeping URLs meaningful, using declarative navigation, protecting routes on the server, and preserving shareable state, Next.js applications become easier to use, easier to maintain, and better optimized for performance and search engines.
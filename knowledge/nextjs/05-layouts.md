---
id: nextjs/05-layouts
topic: nextjs
slug: layouts
title: "Next.js Layouts"
type: doc
order: 5
status: ready
tags: [nextjs, layouts]
related: []
when_to_use: "Read before building shared layouts or persistent UI across Next.js routes."
---
# Next.js Layouts

## Purpose

This document defines the engineering standards for using layouts in Next.js applications.

The objective is to build applications with consistent page structure, shared UI, predictable navigation, and efficient rendering while maximizing the benefits of the App Router.

Layouts should eliminate duplication and provide persistent user interface elements across related routes.

---

## Core Principle

Layouts define structure.

Pages define content.

Features define business functionality.

Each layer should have a single responsibility.

---

## What is a Layout

A Layout is a React Server Component that wraps one or more routes.

Layouts are designed to:

- provide shared page structure;
- persist UI between navigations;
- reduce duplicated code;
- improve navigation performance.

Unlike pages, layouts are preserved during navigation whenever possible.

---

## Layout Hierarchy

Layouts follow the route hierarchy.

Example:

```
app/

    layout.tsx

        dashboard/

            layout.tsx

                analytics/

                    page.tsx
```

Rendering hierarchy:

```
Root Layout

↓

Dashboard Layout

↓

Analytics Page
```

Each layout adds only the structure required for its route segment.

---

## Root Layout

Every application must define a single Root Layout.

Typical responsibilities include:

- `<html>`;
- `<body>`;
- global styles;
- fonts;
- global providers;
- application shell.

The Root Layout should remain lightweight.

---

## Nested Layouts

Use nested layouts to share UI within a specific application section.

Examples:

- dashboard;
- administration;
- customer portal;
- documentation.

Avoid creating nested layouts for individual pages.

---

## Shared UI

Layouts are the correct location for persistent UI.

Examples:

- navigation;
- sidebar;
- footer;
- breadcrumbs;
- application header;
- global notifications.

Avoid duplicating these elements across multiple pages.

---

## Persistent State

Layouts preserve their rendered output between navigations.

Examples:

- expanded sidebar;
- navigation scroll position;
- active navigation state.

Take advantage of persistence to improve user experience.

---

## Data Fetching

Layouts may fetch server-side data.

Good examples:

- authenticated user;
- organization information;
- navigation menu;
- feature flags;
- localization.

Avoid loading page-specific business data inside layouts.

---

## Authentication

Authentication should generally occur at the highest practical layout level.

Examples:

```
Root Layout

↓

Authenticated Layout

↓

Dashboard
```

Protected areas should not repeat authentication logic on every page.

---

## Providers

Global providers belong as high as possible.

Examples:

- Theme Provider;
- Authentication Provider;
- Query Client;
- Internationalization;
- Analytics.

Feature-specific providers should remain inside their respective layouts or features.

---

## Metadata

Layouts may define shared metadata.

Examples:

- default title;
- Open Graph defaults;
- robots;
- viewport;
- icons.

Pages should override metadata only when necessary.

---

## Error Boundaries

Use route-level error boundaries together with layouts.

Typical structure:

```
layout.tsx

error.tsx

loading.tsx

page.tsx
```

Each layout should isolate failures within its own section of the application.

---

## Loading States

Loading UI should correspond to the layout hierarchy.

Examples:

- dashboard shell;
- sidebar skeleton;
- page placeholder.

Avoid replacing the entire application with a loading screen when only one section is loading.

---

## Performance

Layouts improve performance by:

- avoiding unnecessary rerenders;
- preserving shared UI;
- reducing repeated rendering work;
- minimizing layout shifts.

Do not introduce expensive computations into layouts.

---

## Client Components

Keep layouts as Server Components whenever possible.

Only introduce `"use client"` when required.

Examples:

- browser-only providers;
- interactive navigation;
- client-side theme switching.

Avoid making the Root Layout a Client Component unless absolutely necessary.

---

## Accessibility

Layouts should provide:

- semantic landmarks;
- logical heading structure;
- skip navigation links;
- keyboard-accessible navigation;
- predictable focus management.

Persistent UI should remain fully accessible.

---

## AI Execution Checklist

## Investigation

☐ Review application hierarchy.

☐ Identify shared UI.

☐ Identify global providers.

☐ Review authentication flow.

---

## Planning

☐ Keep layouts reusable.

☐ Minimize nesting.

☐ Keep layouts server-side.

☐ Separate page-specific logic.

---

## Verification

☐ Shared UI centralized.

☐ Providers correctly placed.

☐ Layouts remain lightweight.

☐ Authentication handled consistently.

☐ Accessibility preserved.

☐ Performance optimized.

---

## Common Mistakes

Avoid:

Making every layout a Client Component.

Fetching page-specific data inside layouts.

Duplicating navigation across pages.

Creating deeply nested layouts.

Placing business logic inside layouts.

Adding unnecessary providers to the Root Layout.

Ignoring accessibility of persistent navigation.

---

## Completion Criteria

A layout implementation is complete when:

- shared UI is centralized;
- page-specific logic remains inside pages or features;
- layouts remain Server Components whenever possible;
- providers are placed at the appropriate level;
- navigation is accessible;
- the layout hierarchy supports future scalability.

---

## Summary

Layouts are the structural foundation of a Next.js application.

By centralizing shared UI, preserving state across navigations, and maintaining a server-first architecture, layouts improve performance, reduce duplication, and provide a consistent user experience throughout the application.
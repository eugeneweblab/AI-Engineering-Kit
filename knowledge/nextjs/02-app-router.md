# Next.js App Router

## Purpose

This document defines the engineering standards for building applications using the Next.js App Router.

The objective is to create predictable, scalable, and maintainable routing structures that leverage the App Router architecture introduced in Next.js 13+.

Routes should reflect the application's domain rather than its implementation details.

---

# Core Principle

The file system defines the routing structure.

Every route should have a single, well-defined responsibility.

---

# App Directory

All application routes should reside inside the `app/` directory.

Example:

```
app/

    layout.tsx

    page.tsx

    loading.tsx

    error.tsx

    not-found.tsx

    dashboard/

        page.tsx

    settings/

        page.tsx
```

The directory structure should mirror the URL hierarchy.

---

# Route Segments

Each folder inside `app/` represents a route segment.

Example:

```
app/

    products/

        page.tsx
```

Produces:

```
/products
```

Nested folders create nested routes.

```
app/

    products/

        [id]/

            page.tsx
```

Produces:

```
/products/123
```

---

# Pages

Every publicly accessible route must define a `page.tsx`.

Responsibilities:

- compose the page;
- fetch data;
- generate metadata;
- coordinate features.

Avoid placing large amounts of business logic directly inside pages.

---

# Layouts

Layouts provide shared UI between routes.

Typical responsibilities:

- navigation;
- sidebar;
- header;
- footer;
- providers.

Layouts persist between navigation and should avoid route-specific logic.

---

# Nested Layouts

Use nested layouts when sections of the application require different structures.

Example:

```
app/

    layout.tsx

    dashboard/

        layout.tsx

        page.tsx

        analytics/

            page.tsx
```

Shared UI should live at the highest practical layout level.

---

# Route Groups

Use route groups to organize code without affecting URLs.

Example:

```
app/

    (marketing)/

    (dashboard)/
```

Route groups improve organization while preserving clean URLs.

---

# Dynamic Routes

Use dynamic segments for resource identifiers.

Example:

```
app/

    users/

        [id]/

            page.tsx
```

Avoid encoding business logic into route names.

---

# Catch-All Routes

Use catch-all segments only when necessary.

Examples:

```
[...slug]

[[...slug]]
```

Prefer explicit routing whenever possible.

---

# Parallel Routes

Use parallel routes for independent UI regions.

Examples:

- dashboards;
- side panels;
- modal content.

Do not introduce parallel routes without a clear architectural benefit.

---

# Intercepting Routes

Intercepting routes should be used sparingly.

Typical use cases:

- modal navigation;
- image previews;
- contextual overlays.

Avoid replacing normal navigation patterns unnecessarily.

---

# Special Files

The App Router recognizes special files.

Common examples:

```
page.tsx

layout.tsx

loading.tsx

error.tsx

not-found.tsx

template.tsx

default.tsx

route.ts
```

Each file has a dedicated responsibility.

---

# Route Handlers

Use `route.ts` for HTTP endpoints.

Examples:

- webhooks;
- REST endpoints;
- internal APIs.

Do not mix UI rendering with request handling.

---

# Metadata

Generate metadata at the route level.

Examples:

- title;
- description;
- Open Graph;
- Twitter cards;
- robots;
- canonical URLs.

Metadata should remain close to the route it describes.

---

# Navigation

Prefer Next.js navigation primitives.

Examples:

- `<Link>`
- `redirect()`
- `notFound()`

Avoid manipulating browser history manually unless required.

---

# Error Isolation

Each major route should define appropriate error boundaries.

Typical files:

```
error.tsx

not-found.tsx
```

Failures should remain isolated to the affected route.

---

# Loading States

Provide route-specific loading experiences.

Use:

```
loading.tsx
```

Avoid blank screens during navigation.

---

# AI Execution Checklist

## Investigation

☐ Review route hierarchy.

☐ Identify shared layouts.

☐ Identify dynamic routes.

☐ Review loading and error states.

---

## Planning

☐ Keep routes REST-like.

☐ Minimize nesting.

☐ Share layouts appropriately.

☐ Organize using route groups.

---

## Verification

☐ Routes remain predictable.

☐ Layouts are reusable.

☐ Error boundaries implemented.

☐ Loading states provided.

☐ Metadata generated correctly.

☐ URLs remain clean.

---

# Common Mistakes

Avoid:

Placing business logic inside layouts.

Creating deeply nested routes.

Duplicating layouts.

Using route groups unnecessarily.

Overusing catch-all routes.

Mixing API endpoints with UI.

Ignoring loading and error files.

---

# Completion Criteria

App Router implementation is complete when:

- routes reflect the application structure;
- layouts are shared appropriately;
- pages remain focused;
- metadata is implemented;
- loading and error handling are present;
- routing remains scalable and maintainable.

---

# Summary

The App Router provides a powerful file-based routing system that encourages server-first architecture, nested layouts, and predictable application structure.

By organizing routes around business domains and leveraging the built-in routing primitives, Next.js applications become easier to scale, easier to maintain, and more resilient as they evolve.
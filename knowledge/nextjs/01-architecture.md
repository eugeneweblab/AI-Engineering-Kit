---
id: nextjs/01-architecture
topic: nextjs
slug: architecture
title: "Next.js Architecture"
type: doc
order: 1
status: ready
tags: [nextjs, architecture]
related: []
when_to_use: ""
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
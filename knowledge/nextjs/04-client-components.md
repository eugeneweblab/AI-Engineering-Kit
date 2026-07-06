# Next.js Client Components

## Purpose

This document defines the engineering standards for using Client Components in Next.js applications.

The objective is to keep client-side JavaScript to a minimum while providing rich, responsive user interactions where they are genuinely required.

Client Components should be viewed as an optimization target rather than the default choice.

---

# Core Principle

Use Client Components only when the browser is required.

Everything else should remain a Server Component.

---

# When to Use Client Components

A Client Component is appropriate when it requires:

- event handlers;
- browser APIs;
- local component state;
- React Hooks such as `useState` or `useEffect`;
- animations;
- drag and drop;
- focus management;
- browser storage;
- real-time UI updates.

If none of these are required, prefer a Server Component.

---

# "use client"

A Client Component begins with:

```tsx
"use client";
```

This directive creates a client boundary.

Every component imported from this boundary becomes part of the client bundle.

Use it intentionally.

---

# Responsibilities

Client Components should primarily handle:

- user interaction;
- UI state;
- browser integration;
- rendering interactive controls;
- communicating with Server Actions.

Avoid placing business logic inside Client Components.

---

# Rendering Flow

Typical rendering lifecycle:

```
Server Component

↓

Render HTML

↓

Browser

↓

Hydration

↓

Client Component

↓

User Interaction
```

Only interactive components should require hydration.

---

# State Management

Client Components own temporary UI state.

Examples:

- modal visibility;
- dropdown state;
- active tab;
- accordion expansion;
- search input;
- form progress.

Avoid storing server state in local component state.

---

# Browser APIs

Client Components may access browser APIs.

Examples:

- window;
- document;
- localStorage;
- sessionStorage;
- navigator;
- IntersectionObserver;
- ResizeObserver;
- Clipboard API.

These APIs are unavailable inside Server Components.

---

# React Hooks

Client Components may use:

- `useState`
- `useEffect`
- `useReducer`
- `useRef`
- `useMemo`
- `useCallback`
- custom client hooks

Use Hooks responsibly.

Avoid unnecessary effects.

---

# Forms

Interactive forms typically belong in Client Components.

Responsibilities:

- collecting user input;
- client-side validation;
- displaying validation feedback;
- submitting data to Server Actions or APIs.

Business rules should remain on the server.

---

# Server Actions

Client Components should invoke Server Actions instead of implementing business logic locally whenever practical.

Example workflow:

```
Client Component

↓

Server Action

↓

Database

↓

Updated UI
```

The client coordinates interaction.

The server performs the work.

---

# Passing Data

Receive data from Server Components through props.

Example:

```tsx
export default function ProductList({
    products,
}: ProductListProps) {
    // Interactive UI
}
```

Avoid fetching identical data again on the client.

---

# Component Composition

Prefer this composition pattern:

```
Server Component

↓

Client Component

↓

Small Interactive Widgets
```

Avoid making entire pages Client Components.

---

# Performance

Keep Client Components:

- small;
- focused;
- isolated;
- reusable.

Large Client Components increase:

- bundle size;
- hydration cost;
- JavaScript execution time.

---

# Bundle Size

Every imported dependency contributes to the client bundle.

Review:

- large libraries;
- duplicated utilities;
- unnecessary polyfills;
- unused imports.

Import only what is required.

---

# Context

Use Context only for genuinely shared client-side state.

Good examples:

- theme;
- language selection;
- authenticated UI state;
- feature flags.

Avoid placing local component state into Context.

---

# Error Handling

Client Components should handle:

- interaction errors;
- validation failures;
- temporary network issues.

Unexpected failures should still be recoverable through route-level error boundaries.

---

# Accessibility

Every Client Component should support:

- keyboard navigation;
- visible focus indicators;
- semantic HTML;
- accessible names;
- screen reader compatibility.

Interactivity must never reduce accessibility.

---

# Security

Client Components must never contain:

- secrets;
- API keys;
- database credentials;
- authorization logic.

Everything executed in the browser should be considered public.

---

# AI Execution Checklist

## Investigation

☐ Determine whether browser APIs are required.

☐ Review interactive requirements.

☐ Review state ownership.

☐ Review server interaction.

---

## Planning

☐ Keep the client boundary minimal.

☐ Keep business logic on the server.

☐ Keep components small.

☐ Pass only required data.

---

## Verification

☐ `"use client"` added only where necessary.

☐ Browser APIs used correctly.

☐ No sensitive information exposed.

☐ Client bundle minimized.

☐ Accessibility preserved.

☐ Component remains reusable.

---

# Common Mistakes

Avoid:

Making entire pages Client Components.

Using `useEffect` for server data fetching.

Duplicating server state.

Passing unnecessary props.

Embedding business logic inside UI.

Creating oversized interactive components.

Exposing secrets in client code.

Ignoring bundle size.

---

# Completion Criteria

A Client Component implementation is complete when:

- browser-only functionality justifies its existence;
- business logic remains on the server;
- client-side JavaScript is minimized;
- state ownership is clear;
- accessibility is preserved;
- no sensitive information reaches the browser.

---

# Summary

Client Components provide the interactive layer of a Next.js application.

By limiting them to browser-specific functionality and keeping rendering, business logic, and data access on the server, applications remain fast, secure, scalable, and easier to maintain.
---
id: react/16-data-fetching
topic: react
slug: data-fetching
title: "React Data Fetching"
type: doc
order: 16
status: ready
tags: [react, data-fetching]
related: []
when_to_use: "Read before implementing or reviewing remote data fetching, caching, or synchronization in React."
---
# React Data Fetching

## Purpose

This document defines the engineering standards for fetching, caching, synchronizing, and updating remote data in React applications.

The objective is to build applications that efficiently communicate with backend services while remaining predictable, performant, and maintainable.

Remote data should be treated differently from local UI state.

---

## Core Principle

Server state is not client state.

Do not manage remote data using local component state unless there is a specific reason.

Prefer dedicated server state management solutions.

---

## Server State vs Client State

Understand the difference.

## Client State

Examples:

- modal visibility;
- selected tab;
- input values;
- sidebar state;
- theme selection.

The application owns this data.

---

## Server State

Examples:

- users;
- products;
- orders;
- blog posts;
- notifications;
- API responses.

The server owns this data.

Treat server state as a synchronized cache rather than local state.

---

## Data Fetching Workflow

Every data request should follow this lifecycle.

```
Request
        ↓
Loading
        ↓
Success / Error
        ↓
Caching
        ↓
Synchronization
        ↓
Invalidation
        ↓
Refetch
```

---

## Preferred Libraries

For modern React applications, prefer dedicated server state libraries.

Recommended:

- TanStack Query
- SWR

Avoid building custom caching solutions unless the project has specific requirements.

---

## Fetching Strategy

Data should be fetched:

- when required;
- as late as practical;
- as early as beneficial for user experience.

Avoid unnecessary requests.

---

## Loading States

Every request should expose explicit loading states.

Typical states:

- idle;
- loading;
- success;
- error.

Users should always understand what is happening.

---

## Error Handling

Every request should define an error strategy.

Examples:

- retry;
- fallback UI;
- error message;
- logging.

Never ignore failed requests.

---

## Caching

Reuse previously fetched data whenever appropriate.

Benefits:

- improved performance;
- reduced network usage;
- faster navigation;
- better user experience.

Caching should be automatic whenever possible.

---

## Cache Invalidation

Data should be refreshed when it becomes stale.

Common triggers:

- mutation;
- manual refresh;
- window focus;
- reconnect;
- scheduled refresh.

Do not invalidate more data than necessary.

---

## Background Refetching

Prefer background synchronization when appropriate.

Benefits:

- fresh data;
- minimal UI interruption;
- better perceived performance.

Avoid unnecessary loading indicators during silent updates.

---

## Mutations

Mutations change server state.

Examples:

- create;
- update;
- delete;
- upload.

Every mutation should define:

- loading state;
- success handling;
- error handling;
- cache invalidation.

---

## Optimistic Updates

Use optimistic updates only when:

- failures are uncommon;
- rollback is possible;
- user experience benefits.

Every optimistic update must support rollback.

---

## Request Deduplication

Avoid duplicate requests for identical resources.

Review:

- multiple components requesting the same data;
- repeated requests during navigation;
- unnecessary refetches.

---

## Pagination

Large datasets should support pagination or infinite loading.

Avoid requesting thousands of records at once.

Choose the strategy that best fits the product requirements.

---

## Filtering and Sorting

Filtering should be performed:

- on the server for large datasets;
- on the client only when the complete dataset is already available.

Avoid transferring unnecessary data.

---

## API Layer

Keep API communication separate from presentation.

Example:

```
Component
        ↓
Custom Hook
        ↓
API Client
        ↓
Backend
```

Components should not know implementation details of HTTP requests.

---

## Cancellation

Long-running requests should support cancellation when appropriate.

Examples:

- page navigation;
- search input;
- component unmount.

Avoid updating state after a request is no longer relevant.

---

## Authentication

Authenticated requests should:

- use centralized authentication;
- refresh tokens when required;
- handle unauthorized responses consistently.

Authentication logic should not be duplicated across components.

---

## Performance

Review:

- request frequency;
- payload size;
- duplicate requests;
- cache hit rate;
- unnecessary refetching.

Network performance is often more important than rendering performance.

---

## Accessibility

Loading and error states should be accessible.

Verify:

- loading indicators;
- status announcements;
- retry actions;
- focus management after updates.

Users should always understand the result of asynchronous operations.

---

## AI Execution Checklist

## Investigation

☐ Identify server state.

☐ Review existing API layer.

☐ Review caching strategy.

☐ Review loading and error states.

---

## Planning

☐ Select data fetching strategy.

☐ Define cache behavior.

☐ Define invalidation strategy.

☐ Define mutation workflow.

---

## Verification

☐ Server state separated from UI state.

☐ Loading states implemented.

☐ Errors handled.

☐ Cache behaves correctly.

☐ Duplicate requests avoided.

☐ Accessibility preserved.

---

## Common Mistakes

Avoid:

Using `useEffect` for every request.

Managing server state with `useState`.

Ignoring caching.

Ignoring request cancellation.

Duplicating API calls.

Refetching excessively.

Mixing API logic with UI components.

Ignoring loading and error states.

---

## Completion Criteria

Data fetching is complete when:

- server state is managed separately from UI state;
- loading, success, and error states are implemented;
- caching and invalidation are defined;
- mutations are handled consistently;
- duplicate requests have been minimized;
- accessibility requirements have been satisfied.

---

## Summary

Effective data fetching is built on clear separation between server state and client state.

By using dedicated server state management, consistent caching strategies, and predictable request lifecycles, React applications become faster, more reliable, and easier to maintain as they scale.
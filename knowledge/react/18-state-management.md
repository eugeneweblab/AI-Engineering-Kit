---
id: react/18-state-management
topic: react
slug: state-management
title: "React State Management"
type: doc
order: 18
status: ready
tags: [react, state-management]
related: []
when_to_use: ""
---
# React State Management

## Purpose

This document defines the engineering standards for managing state in React applications.

The objective is to keep state predictable, minimal, maintainable, and easy to reason about while avoiding unnecessary complexity.

State should represent information that changes over time and affects rendering.

If a value can be derived, it should not become state.

---

## Core Principle

Store the minimum amount of state required.

Everything else should be computed.

The best state is the state that does not exist.

---

## What Is State?

State is mutable data that determines what the user sees.

Examples:

- current user;
- selected tab;
- modal visibility;
- search query;
- form values;
- loading status;
- API response.

State should represent the current UI, not implementation details.

---

## State Hierarchy

Every piece of state should have a single owner.

```
Application

        ↓

Page

        ↓

Feature

        ↓

Component
```

Keep state as close as possible to where it is used.

Do not lift state higher without a clear reason.

---

## Before Creating State

Ask the following questions.

## Can It Be Derived?

Good:

```tsx
const fullName = `${firstName} ${lastName}`;
```

Avoid:

```tsx
const [fullName, setFullName] = useState("");
```

Derived values should not be stored.

---

## Is It Constant?

Constant values belong outside the component.

Good:

```tsx
const MAX_ITEMS = 20;
```

Avoid:

```tsx
const [maxItems] = useState(20);
```

---

## Can It Be a Ref?

Use refs for values that do not affect rendering.

Examples:

- timers;
- DOM elements;
- previous values;
- external library instances.

Changing a ref should not trigger a re-render.

---

## Local State

Prefer local state whenever possible.

Examples:

- open modal;
- selected tab;
- accordion state;
- input value.

Local state is easier to understand and maintain.

---

## Shared State

Lift state only when multiple components require the same information.

Examples:

- authenticated user;
- current theme;
- shopping cart;
- language selection.

Avoid global state for feature-specific data.

---

## Global State

Global state should be limited to truly application-wide concerns.

Examples:

- authentication;
- theme;
- localization;
- feature flags.

Do not place page-specific state into global stores.

---

## State Ownership

Every state value should have one source of truth.

Bad:

```
Parent

↓

Child

↓

Another Child
```

Each maintaining independent copies of the same data.

Good:

```
Parent

↓

Props

↓

Children
```

Children notify the parent through callbacks.

---

## Derived State

Compute values instead of storing them.

Good:

```tsx
const completedTasks = tasks.filter(task => task.completed);
```

Avoid:

```tsx
const [completedTasks, setCompletedTasks] = useState([]);
```

Duplicated state eventually becomes inconsistent.

---

## Updating State

Always use immutable updates.

Good:

```tsx
setUsers(users =>
    users.map(user =>
        user.id === id
            ? { ...user, active: true }
            : user
    )
);
```

Avoid mutating existing objects or arrays.

---

## Async State

Keep asynchronous state explicit.

Typical values include:

- idle;
- loading;
- success;
- error.

Avoid multiple boolean flags representing the same process.

Prefer:

```tsx
status = "loading"
```

Instead of:

```tsx
isLoading

isFetching

hasLoaded

requestFinished
```

---

## State and Effects

Do not use effects to synchronize state that can be derived.

Bad:

```tsx
useEffect(() => {
    setFilteredItems(
        items.filter(filter)
    );
}, [items]);
```

Good:

```tsx
const filteredItems = items.filter(filter);
```

Prefer computation during rendering.

---

## State Colocation

Keep state close to where it is used.

Move state upward only when multiple components need access.

Lower state ownership generally results in simpler components.

---

## Performance

Avoid unnecessary state updates.

Review:

- duplicated state;
- unnecessary re-renders;
- large state objects;
- deeply nested updates.

Smaller state generally produces simpler rendering.

---

## Accessibility

State changes should remain accessible.

Verify:

- focus management;
- keyboard interaction;
- screen reader announcements;
- loading indicators;
- error messages.

UI state should always be communicated appropriately.

---

## AI Execution Checklist

## Investigation

☐ Identify all state values.

☐ Determine state ownership.

☐ Search for derived values.

☐ Review existing state.

---

## Planning

☐ Minimize state.

☐ Keep state local where possible.

☐ Define update strategy.

☐ Plan accessibility.

---

## Verification

☐ No duplicated state.

☐ No derived state stored.

☐ Immutable updates used.

☐ State ownership is clear.

☐ Accessibility preserved.

---

## Common Mistakes

Avoid:

Storing derived values.

Duplicating state.

Using global state unnecessarily.

Mutating state directly.

Synchronizing state with effects.

Creating multiple sources of truth.

Using state for constant values.

---

## Completion Criteria

State management is complete when:

- only necessary state is stored;
- derived values are computed;
- ownership is clearly defined;
- updates are immutable;
- state remains predictable;
- accessibility requirements are satisfied.

---

## Summary

Effective state management begins with minimizing the amount of state.

Keeping state local, avoiding duplication, and deriving values whenever possible leads to simpler, more maintainable, and more predictable React applications.
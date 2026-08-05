---
id: react/09-custom-hooks
topic: react
slug: custom-hooks
title: "Custom Hooks"
type: doc
order: 9
status: ready
tags: [react, custom-hooks]
related: [react/08-hooks, react/16-data-fetching, react/14-patterns]
when_to_use: "Read before writing or reviewing a custom React hook or extracting logic out of a component."
---
# Custom Hooks

## Purpose

This document defines the engineering standards for designing and implementing Custom Hooks in React applications.

The objective is to separate business logic from presentation, maximize code reuse, and create predictable, testable, and maintainable React applications.

Custom Hooks are intended to encapsulate behavior, not visual presentation.

---

## Core Principle

Extract behavior.

Keep rendering inside components.

A Custom Hook should contain logic that can be reused independently of any specific UI.

---

## What Is a Custom Hook?

A Custom Hook is a function that:

- starts with `use`;
- uses one or more React Hooks;
- encapsulates reusable logic;
- exposes a clear and minimal API.

Example:

```tsx
function useUser() {
    // ...
}
```

---

## Responsibilities

A Custom Hook may:

- manage state;
- perform data fetching;
- coordinate side effects;
- encapsulate business logic;
- expose derived values;
- expose actions.

A Custom Hook should not render UI.

---

## When to Create a Custom Hook

Create a hook when:

- logic is duplicated;
- behavior is shared by multiple components;
- a component becomes difficult to read;
- multiple hooks work together;
- business logic grows independently from the UI.

Avoid extracting hooks prematurely.

---

## When Not to Create a Custom Hook

Do not create a hook:

- for one or two lines of code;
- only to reduce file size;
- when logic is used once;
- to wrap another hook without adding value.

Every hook should have a clear responsibility.

---

## Single Responsibility

Each hook should solve one problem.

Good examples:

- useAuth
- useModal
- usePagination
- useDebounce
- useBreakpoint
- useLocalStorage

Avoid hooks that combine unrelated responsibilities.

Bad examples:

- useDashboard
- useEverything
- useHelpers

---

## API Design

Keep the public API small.

Good:

```tsx
const {
    user,
    login,
    logout,
    isLoading
} = useAuth();
```

Avoid returning unnecessary values.

Consumers should receive only what they need.

---

## Return Values

Prefer returning an object.

Good:

```tsx
return {
    users,
    refresh,
    isLoading,
    error
};
```

Objects are easier to extend without breaking existing consumers.

Use arrays only when position has semantic meaning.

Example:

```tsx
const [
    value,
    setValue
] = useState("");
```

---

## Side Effects

Place side effects inside the hook only when they are part of its responsibility.

Examples:

- API requests;
- subscriptions;
- timers;
- browser APIs.

Avoid unrelated effects.

---

## State Ownership

State owned by a hook belongs to that hook.

Components should interact only through the exposed API.

Do not modify internal state from outside the hook.

---

## Derived Values

Prefer returning derived values.

Good:

```tsx
return {
    users,
    activeUsers
};
```

Instead of forcing every consumer to compute them independently.

---

## Error Handling

Hooks should expose errors explicitly.

Example:

```tsx
return {
    data,
    error,
    isLoading
};
```

Avoid hiding failures.

---

## Async Hooks

Expose explicit request states.

Typical values:

- idle;
- loading;
- success;
- error.

Consumers should not infer request status indirectly.

---

## Naming

Every hook should start with `use`.

Good:

```
useUser

useTheme

useProducts

useBreakpoint

useForm
```

Avoid generic names.

Bad:

```
helper

utilities

manager

logic
```

Names should describe responsibility.

---

## Dependencies

Hooks should depend on abstractions rather than specific UI components.

Avoid importing presentation components into hooks.

Business logic should remain independent from rendering.

---

## Testing

Hooks should be testable independently.

Avoid tight coupling to:

- browser globals;
- specific pages;
- unrelated components.

Isolated hooks are easier to validate and maintain.

---

## Performance

Avoid unnecessary recalculations.

Review:

- expensive computations;
- unstable callbacks;
- unnecessary effects;
- repeated subscriptions.

Optimize only when justified by measurement.

---

## Accessibility

Hooks managing UI behavior should support accessibility.

Examples:

- focus management;
- keyboard interaction;
- announcements;
- dialog behavior.

Accessibility is part of behavior, not presentation.

---

## AI Execution Checklist

## Investigation

☐ Identify duplicated logic.

☐ Define hook responsibility.

☐ Design the public API.

☐ Determine state ownership.

---

## Planning

☐ Minimize the exposed API.

☐ Separate business logic from UI.

☐ Plan error handling.

☐ Plan accessibility behavior.

---

## Verification

☐ Hook has a single responsibility.

☐ API is minimal.

☐ No rendering logic exists.

☐ Side effects are intentional.

☐ Hook is independently testable.

☐ Accessibility requirements are supported.

---

## Common Mistakes

Avoid:

Creating hooks for trivial logic.

Returning unnecessary data.

Mixing UI rendering with business logic.

Creating hooks with multiple responsibilities.

Hiding errors.

Creating unstable APIs.

Wrapping existing hooks without adding value.

---

## Completion Criteria

A Custom Hook is complete when:

- it has a single responsibility;
- its API is minimal and predictable;
- rendering logic remains inside components;
- business logic has been encapsulated;
- errors are handled explicitly;
- the hook is independently testable;
- accessibility requirements have been considered.

---

## Summary

Custom Hooks are the primary mechanism for sharing behavior in React.

Well-designed hooks isolate business logic, simplify components, and improve the overall maintainability of the application while providing a consistent developer experience.

## Related

- `knowledge/react/08-hooks.md`
- `knowledge/react/16-data-fetching.md`
- `knowledge/react/14-patterns.md`

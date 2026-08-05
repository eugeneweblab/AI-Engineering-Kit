---
id: react/100-common-antipatterns
topic: react
slug: common-antipatterns
title: "React Anti-Patterns"
type: antipatterns
order: 100
status: ready
tags: [react, common-antipatterns, useState, useEffect, setFullName, React.memo, useCallback, useMemo]
related: [react/26-best-practices, react/11-rendering, react/06-state, react/99-ai-review-checklist]
when_to_use: "Read during React implementation, code review, or refactoring to detect and avoid common anti-patterns."
---
# React Anti-Patterns

## Purpose

This document defines common React anti-patterns that reduce code quality, introduce unnecessary complexity, or negatively impact maintainability, performance, and scalability.

Understanding what to avoid is just as important as understanding best practices.

This document should be used during implementation, code review, and refactoring.

---

## Core Principle

Every anti-pattern increases technical debt.

Choose simplicity over cleverness.

Choose explicitness over hidden behavior.

Choose maintainability over short-term convenience.

---

## Large Components

Avoid components that perform multiple unrelated responsibilities.

Bad example:

- fetch data;
- manage business logic;
- perform validation;
- render UI;
- manipulate browser APIs.

Prefer separating responsibilities into:

- presentation components;
- custom hooks;
- services;
- utility functions.

---

## Deep Component Trees

Excessive nesting makes components difficult to understand.

Avoid:

```
<Page>

    <Layout>

        <Wrapper>

            <Container>

                <Section>

                    <Content>

                        <Card>
```

Prefer flatter component hierarchies whenever practical.

---

## Prop Drilling

Passing props through many intermediate components creates unnecessary coupling.

Avoid:

```
App

↓

Layout

↓

Sidebar

↓

Navigation

↓

Menu

↓

Button
```

Consider:

- composition;
- Context (when appropriate);
- dedicated state management.

Do not introduce Context solely to avoid passing one or two props.

---

## Duplicated State

Never store the same information in multiple places.

Bad:

```tsx
const [users, setUsers] = useState(...);

const [activeUsers, setActiveUsers] = useState(...);
```

Prefer:

```tsx
const activeUsers = users.filter(
    user => user.active
);
```

Derived values should not become state.

---

## Copying Props into State

Avoid:

```tsx
const [name, setName] = useState(props.name);
```

unless the component intentionally creates independent local state.

Props should generally remain the source of truth.

---

## Overusing useEffect

Do not use `useEffect` for values that can be calculated during rendering.

Bad:

```tsx
useEffect(() => {
    setFullName(`${first} ${last}`);
}, [first, last]);
```

Good:

```tsx
const fullName = `${first} ${last}`;
```

Effects should synchronize with external systems, not derive UI state.

---

## Unnecessary Memoization

Avoid adding:

- `React.memo`
- `useMemo`
- `useCallback`

without measurable benefit.

Memoization increases complexity.

Optimize only after profiling.

---

## Anonymous Functions Everywhere

Inline callbacks are acceptable in most situations.

Avoid extracting every callback solely for perceived performance improvements.

Prioritize readability over premature optimization.

---

## Business Logic Inside Components

Avoid embedding large amounts of business logic directly inside JSX components.

Instead, move logic into:

- services;
- utility functions;
- custom hooks.

Components should primarily coordinate rendering.

---

## Massive Props Interfaces

Components with dozens of props are difficult to understand.

Instead:

- split the component;
- introduce composition;
- extract child components.

Large APIs usually indicate multiple responsibilities.

---

## Generic Utility Files

Avoid creating files such as:

```
helpers.ts

utils.ts

common.ts

misc.ts
```

Organize utilities by responsibility instead.

---

## Using Context for Everything

Context is intended for shared application state.

Avoid storing:

- modal visibility;
- form state;
- local UI state;
- temporary component state.

Keep state local whenever possible.

---

## Mutable State

Never mutate React state directly.

Bad:

```tsx
users.push(newUser);
```

Prefer immutable updates.

---

## Ignoring Loading States

Every asynchronous operation should expose loading behavior.

Avoid interfaces that appear frozen while work is in progress.

---

## Ignoring Error States

Every asynchronous workflow should define:

- failure handling;
- recovery;
- retry strategy.

Applications should fail gracefully.

---

## Index as List Key

Avoid:

```tsx
key={index}
```

unless the list is static and will never change.

Prefer stable identifiers.

---

## Conditional Hooks

Never call Hooks conditionally.

Bad:

```tsx
if (isLoggedIn) {
    useEffect(...);
}
```

Hooks must always execute in the same order.

---

## Side Effects During Rendering

Rendering should never:

- perform requests;
- modify storage;
- manipulate the DOM;
- create timers.

Rendering should remain pure.

---

## Ignoring Accessibility

Avoid components that:

- cannot receive keyboard focus;
- lack accessible names;
- misuse semantic HTML;
- rely only on color;
- remove focus indicators.

Accessibility is not optional.

---

## AI Execution Checklist

## Investigation

☐ Review component responsibilities.

☐ Review state ownership.

☐ Review rendering logic.

☐ Review side effects.

---

## Planning

☐ Eliminate unnecessary complexity.

☐ Reduce duplication.

☐ Separate business logic.

☐ Improve readability.

---

## Verification

☐ No duplicated state.

☐ No unnecessary effects.

☐ No unnecessary memoization.

☐ Components remain focused.

☐ Rendering remains pure.

☐ Accessibility preserved.

---

## Common Mistakes

Avoid:

Creating oversized components.

Copying props into state.

Mutating state directly.

Overusing Context.

Ignoring loading states.

Ignoring error handling.

Premature optimization.

Deep component nesting.

---

## Completion Criteria

A React implementation satisfies this document when:

- common anti-patterns have been avoided;
- responsibilities remain clearly separated;
- state management is predictable;
- rendering is pure;
- components remain readable and maintainable;
- accessibility has not been compromised.

---

## Summary

Most React problems arise from unnecessary complexity rather than missing features.

Avoiding common anti-patterns results in applications that are easier to understand, easier to extend, and significantly easier to maintain over time.

## Related

- `knowledge/react/26-best-practices.md`
- `knowledge/react/11-rendering.md`
- `knowledge/react/06-state.md`
- `knowledge/react/99-ai-review-checklist.md`

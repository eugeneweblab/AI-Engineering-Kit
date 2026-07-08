---
id: react/11-rendering
topic: react
slug: rendering
title: "React Rendering Patterns"
type: doc
order: 11
status: ready
tags: [react, rendering]
related: []
when_to_use: "Read before writing or reviewing React rendering and re-render logic."
---
# React Rendering Patterns

## Purpose

This document defines the recommended rendering patterns for React applications.

The objective is to build components that are predictable, maintainable, performant, and easy to understand by following consistent rendering practices.

Rendering should remain a pure operation that transforms state into user interface.

---

## Core Principle

Rendering should be deterministic.

The same input should always produce the same output.

Rendering should never produce side effects.

---

## Rendering Pipeline

Every component should follow this mental model.

```
Props
        ↓
State
        ↓
Derived Values
        ↓
Render
        ↓
UI
```

Rendering should be the final step.

---

## Keep Rendering Pure

Rendering should only calculate what should be displayed.

Good examples:

- conditional rendering;
- mapping collections;
- formatting values;
- combining props;
- rendering components.

Avoid:

- API requests;
- localStorage writes;
- timers;
- subscriptions;
- DOM manipulation.

---

## Conditional Rendering

Prefer early returns for mutually exclusive states.

Good:

```tsx
if (isLoading) {
    return <Spinner />;
}

if (error) {
    return <ErrorMessage />;
}

return <Products />;
```

Avoid deeply nested conditional expressions.

---

## Rendering Lists

Always use stable keys.

Good:

```tsx
users.map(user => (
    <UserCard
        key={user.id}
        user={user}
    />
));
```

Avoid array indexes when the order may change.

Bad:

```tsx
users.map((user, index) => (
    <UserCard
        key={index}
        user={user}
    />
));
```

Stable keys improve rendering predictability.

---

## Derived Values

Compute derived values before returning JSX.

Good:

```tsx
const activeUsers = users.filter(
    user => user.active
);

return <UserList users={activeUsers} />;
```

Avoid performing complex calculations directly inside JSX.

---

## Keep JSX Simple

JSX should describe the UI.

Move complex logic outside the return statement.

Prefer:

```tsx
const canEdit =
    user.role === "admin";

return (
    <Button disabled={!canEdit} />
);
```

Instead of embedding long expressions in JSX.

---

## Extract Components

Split repeated or complex UI into separate components.

Good:

```tsx
<ProductCard />

<UserAvatar />

<CommentItem />
```

Avoid components with hundreds of lines of JSX.

---

## Avoid Deep Nesting

Prefer:

```tsx
<Page>

    <Sidebar />

    <Content />

</Page>
```

Instead of deeply nested wrapper components.

Flatten the component tree whenever practical.

---

## Rendering Collections

Prefer rendering complete components rather than inline markup.

Good:

```tsx
<OrderItem />

<ProductCard />

<UserRow />
```

This improves readability and reuse.

---

## Empty States

Every collection should define an empty state.

Example:

```tsx
if (!products.length) {
    return (
        <EmptyState />
    );
}
```

Users should always receive meaningful feedback.

---

## Loading States

Loading should be explicit.

Typical states:

- idle;
- loading;
- success;
- error.

Avoid hiding loading behavior.

---

## Error States

Every asynchronous view should define an error state.

Good examples:

- retry button;
- descriptive message;
- recovery action.

Avoid rendering nothing after failures.

---

## Render Props

Use render props only when composition provides clear value.

Modern React generally prefers:

- composition;
- custom hooks;
- reusable components.

Avoid render props for simple scenarios.

---

## Portals

Use portals for UI that should escape the normal DOM hierarchy.

Examples:

- dialogs;
- tooltips;
- dropdown overlays;
- notifications.

Do not use portals unnecessarily.

---

## Fragments

Use fragments to avoid unnecessary wrapper elements.

Good:

```tsx
<>
    <Header />
    <Content />
</>
```

Avoid meaningless wrapper `<div>` elements.

---

## Accessibility

Rendering should preserve:

- semantic HTML;
- heading hierarchy;
- keyboard navigation;
- focus management;
- accessible names.

Rendering decisions directly affect accessibility.

---

## Performance

Review rendering for:

- unnecessary re-renders;
- unstable keys;
- repeated calculations;
- deeply nested trees;
- unnecessary wrappers.

Optimize only after identifying measurable bottlenecks.

---

## AI Execution Checklist

## Investigation

☐ Identify rendering states.

☐ Review conditional rendering.

☐ Review collection rendering.

☐ Identify repeated UI.

---

## Planning

☐ Compute derived values.

☐ Keep JSX simple.

☐ Extract reusable components.

☐ Plan loading and error states.

---

## Verification

☐ Rendering remains pure.

☐ No side effects during rendering.

☐ Stable keys used.

☐ Empty states implemented.

☐ Accessibility preserved.

☐ Rendering remains readable.

---

## Common Mistakes

Avoid:

Performing side effects during rendering.

Using unstable keys.

Embedding large amounts of logic inside JSX.

Rendering deeply nested layouts.

Ignoring loading states.

Ignoring empty states.

Ignoring accessibility.

Returning inconsistent UI for identical state.

---

## Completion Criteria

Rendering is complete when:

- rendering remains pure;
- conditional states are explicit;
- collections use stable keys;
- JSX is easy to read;
- reusable components have been extracted;
- accessibility has been preserved;
- performance has been considered.

---

## Summary

Well-structured rendering produces interfaces that are predictable, readable, and easy to maintain.

By separating computation from presentation and keeping rendering pure, React components become simpler to understand, easier to test, and more resilient as applications grow.
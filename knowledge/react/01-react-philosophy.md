---
id: react/01-react-philosophy
topic: react
slug: react-philosophy
title: "React Philosophy"
type: doc
order: 1
status: ready
tags: [react, react-philosophy, useState, useEffect, Cart, round, CartItem, setTotal]
related: [react/02-component-architecture, react/06-state, react/11-rendering, react/13-component-composition]
when_to_use: "Read before writing or reviewing any React code to align with the project's core React engineering principles."
---
# React Philosophy

## Purpose

This document defines the engineering principles for building React applications within this project.

The objective is to create applications that are predictable, maintainable, reusable, and scalable while following modern React best practices.

React is a library for building user interfaces.

It should not become a place for business logic, duplicated state, or unnecessary complexity.

---

## Core Principle

Components should describe the UI.

Business logic should remain independent from presentation whenever practical.

A React component should be easy to understand by reading it from top to bottom.

---

## React Mindset

Before writing a component, ask:

- What is the responsibility of this component?
- Can this functionality be reused?
- Should this component own state?
- Does this belong in a parent component?
- Does this belong in a custom hook?
- Does this belong outside React entirely?

Prefer simple components over clever abstractions.

---

## Design Principles

Every component should follow these principles.

## Single Responsibility

Each component should have one primary responsibility.

Avoid components that:

- fetch data;
- transform data;
- manage complex business logic;
- render large sections of UI.

Split responsibilities into smaller units.

---

## Composition Over Inheritance

Build interfaces using composition.

Prefer:

```
<Card>
    <CardHeader />
    <CardBody />
    <CardFooter />
</Card>
```

Instead of creating multiple specialized versions of the same component.

---

## Reusability

Before creating a component, search the project for an existing implementation.

Reuse before creating.

Avoid duplicate UI patterns.

---

## Predictability

Component behavior should be obvious.

Avoid:

- hidden side effects;
- implicit state changes;
- unpredictable rendering.

---

## Readability

Prefer readable code over clever code.

A new engineer should understand the component without additional explanation.

---

## Component Responsibilities

A component should primarily:

- render UI;
- receive props;
- emit events;
- coordinate child components.

Avoid embedding unrelated responsibilities.

---

## State Management

Before introducing state, ask:

- Can this value be derived?
- Can this state live higher?
- Can it be computed?
- Can it remain local?

Only store information that cannot be derived.

---

## Data Flow

React applications should maintain one-way data flow.

```
Parent

↓

Props

↓

Child

↓

Events

↓

Parent
```

Avoid unnecessary bidirectional dependencies.

---

## Side Effects

Side effects should be isolated.

Examples:

- network requests;
- timers;
- subscriptions;
- browser APIs;
- local storage.

Keep rendering logic separate from side effects.

---

## Performance

Optimize only after identifying a real bottleneck.

Prefer:

- simple rendering;
- stable component trees;
- reusable components;
- minimal state.

Do not introduce premature optimizations.

---

## Accessibility

Every component should support:

- semantic HTML;
- keyboard navigation;
- focus management;
- accessible names;
- sufficient contrast.

Accessibility is part of component quality.

---

## Testing

Components should be designed so they can be tested independently.

Avoid tightly coupling components to global state or external services.

---

## AI Execution Checklist

## Investigation

☐ Understand the component's purpose.

☐ Search for existing implementations.

☐ Identify reusable patterns.

☐ Determine state ownership.

---

## Planning

☐ Define component responsibilities.

☐ Plan props.

☐ Plan events.

☐ Plan accessibility.

---

## Verification

☐ Component has a single responsibility.

☐ Existing components reused.

☐ State minimized.

☐ Side effects isolated.

☐ Accessibility preserved.

☐ Component is maintainable.

---

## Examples

**Good Example** — the UI is a function of state, and state has one owner

```tsx
// One source of truth. Everything else is derived at render time, so the values
// on screen cannot disagree with each other.
export function Cart({ items }: { items: CartItem[] }) {
  const [couponCode, setCouponCode] = useState('');

  // Derived, not stored: no effect to keep it in sync, no chance of staleness.
  const subtotalCents = items.reduce((sum, i) => sum + i.priceCents * i.quantity, 0);
  const discountCents = couponCode === 'SAVE10' ? Math.round(subtotalCents * 0.1) : 0;
  const totalCents = subtotalCents - discountCents;

  return (
    <>
      <CartLines items={items} />
      <CouponInput value={couponCode} onChange={setCouponCode} />
      <Total subtotalCents={subtotalCents} discountCents={discountCents} totalCents={totalCents} />
    </>
  );
}
```

**Bad Example** — derived values stored in state and synchronised by effects

```tsx
export function Cart({ items }: { items: CartItem[] }) {
  const [couponCode, setCouponCode] = useState('');
  const [subtotal, setSubtotal] = useState(0);
  const [discount, setDiscount] = useState(0);
  const [total, setTotal] = useState(0);

  // Three effects to keep four pieces of state consistent. Each runs one render
  // late, so the first paint after a change shows a stale total — and adding a
  // fourth derived value means adding a fourth chance to forget one.
  useEffect(() => {
    setSubtotal(items.reduce((sum, i) => sum + i.priceCents * i.quantity, 0));
  }, [items]);

  useEffect(() => {
    setDiscount(couponCode === 'SAVE10' ? Math.round(subtotal * 0.1) : 0);
  }, [couponCode, subtotal]);

  useEffect(() => {
    setTotal(subtotal - discount);
  }, [subtotal, discount]);

  return <Total subtotalCents={subtotal} discountCents={discount} totalCents={total} />;
}
```

If a value can be calculated from props and state during render, calculating it is both
simpler and correct. Storing it creates a second copy that has to be maintained.

---

## Common Mistakes

Avoid:

Creating oversized components.

Duplicating UI.

Storing derived state.

Embedding business logic inside presentation.

Creating deeply nested component trees.

Premature optimization.

Ignoring accessibility.

---

## Completion Criteria

A React component is complete when:

- it has a clear responsibility;
- it follows project architecture;
- it is reusable where appropriate;
- unnecessary state has been avoided;
- accessibility has been considered;
- the implementation remains readable and maintainable.

---

## Summary

Well-designed React applications are built from small, focused, reusable components.

Simplicity, composition, and predictable data flow create software that is easier to maintain, extend, and review.

## Related

- `knowledge/react/02-component-architecture.md`
- `knowledge/react/06-state.md`
- `knowledge/react/11-rendering.md`
- `knowledge/react/13-component-composition.md`

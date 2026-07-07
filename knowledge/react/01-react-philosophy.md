---
id: react/01-react-philosophy
topic: react
slug: react-philosophy
title: "React Philosophy"
type: doc
order: 1
status: ready
tags: [react, react-philosophy]
related: []
when_to_use: ""
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
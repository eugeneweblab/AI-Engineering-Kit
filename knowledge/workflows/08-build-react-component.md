---
id: workflows/08-build-react-component
topic: workflows
slug: build-react-component
title: "Workflow — Build a React Component"
type: doc
order: 8
status: ready
tags: [workflows, build-react-component]
related: []
when_to_use: "Follow this workflow when building or extending a React component."
---
# Workflow — Build a React Component

## Purpose

This workflow defines the standard engineering process for creating or extending a React component inside an existing project.

The objective is to build components that are reusable, predictable, accessible, performant, and fully aligned with the project's architecture and design system.

A React component should never exist in isolation.

It should become a natural part of the application's component ecosystem.

---

## Goal

Build a component that:

- satisfies the design requirements;
- follows project conventions;
- reuses existing components where possible;
- is accessible;
- is responsive;
- is easy to maintain;
- is easy to test.

---

## Workflow Overview

```
Understand Requirements
        ↓
Analyze Existing Components
        ↓
Identify Reusable Parts
        ↓
Design Component API
        ↓
Implement Structure
        ↓
Implement Styling
        ↓
Implement Logic
        ↓
Verify Accessibility
        ↓
Verify Responsiveness
        ↓
Review
```

---

## Step 1 — Understand the Requirements

Determine:

- business purpose;
- expected behavior;
- supported states;
- responsive requirements;
- accessibility requirements;
- design constraints.

Never begin implementation before understanding how the component should behave.

---

## Step 2 — Analyze Existing Components

Search the repository.

Review:

- similar components;
- shared UI library;
- layout components;
- typography components;
- button components;
- form components;
- modal components;
- utility hooks.

Reuse before creating.

---

## Step 3 — Define Component Responsibility

Every component should have one primary responsibility.

Examples:

Good

- Button
- Card
- Modal
- ProductCard
- UserAvatar

Avoid components that attempt to solve multiple unrelated problems.

---

## Step 4 — Design the Component API

Define:

- props;
- required props;
- optional props;
- callbacks;
- children;
- default values;
- controlled vs uncontrolled behavior.

The API should be small, predictable, and easy to understand.

---

## Step 5 — Build the Structure

Create semantic markup.

Prefer:

- header
- section
- article
- nav
- button
- form
- label
- ul
- li

Avoid unnecessary wrapper elements.

---

## Step 6 — Implement Styling

Follow the project's styling strategy.

Examples:

- Tailwind CSS
- CSS Modules
- Emotion
- Styled Components

Maintain consistency with:

- spacing;
- typography;
- colors;
- border radius;
- shadows;
- breakpoints.

Do not introduce a new styling approach.

---

## Step 7 — Implement Logic

Keep rendering and business logic separated.

Prefer:

- custom hooks;
- utility functions;
- shared services.

Avoid placing complex business logic directly inside JSX.

---

## Step 8 — Accessibility Review

Verify:

- semantic HTML;
- keyboard navigation;
- visible focus;
- aria attributes;
- accessible labels;
- heading hierarchy;
- color contrast.

Accessibility is a required feature.

---

## Step 9 — Responsive Review

Verify:

Desktop

Tablet

Mobile

Check:

- layout;
- spacing;
- typography;
- overflow;
- wrapping;
- touch targets.

Responsive behavior should be intentional.

---

## Step 10 — Final Review

Review:

- readability;
- naming;
- props;
- imports;
- exports;
- reusability;
- duplication;
- maintainability.

The component should be understandable without additional explanation.

---

## AI Execution Checklist

## Investigation

☐ Read the requirements.

☐ Search similar components.

☐ Review the design system.

☐ Review styling conventions.

☐ Review project architecture.

---

## Planning

☐ Define component responsibility.

☐ Design the props API.

☐ Identify reusable code.

☐ Identify required hooks.

---

## Implementation

☐ Reuse existing components.

☐ Keep responsibilities separated.

☐ Preserve styling consistency.

☐ Preserve naming conventions.

☐ Avoid duplicate logic.

---

## Verification

☐ Verify all component states.

☐ Verify responsiveness.

☐ Verify accessibility.

☐ Verify imports.

☐ Verify exports.

☐ Verify TypeScript types.

☐ Review documentation if applicable.

---

## React Best Practices

Prefer:

Small focused components

Composition over inheritance

Controlled components when appropriate

Reusable hooks

Pure rendering

Stable props

Memoization only when justified

Avoid:

Large monolithic components

Deep prop drilling

Duplicate state

Business logic inside JSX

Inline anonymous functions when unnecessary

Premature optimization

---

## Common Mistakes

Avoid:

Creating duplicate UI components.

Ignoring existing design tokens.

Hardcoding spacing values.

Using non-semantic HTML.

Mixing presentation and business logic.

Ignoring accessibility.

Ignoring responsive layouts.

Adding unnecessary abstractions.

---

## Completion Criteria

The workflow is complete only if:

- requirements are satisfied;
- the component follows project conventions;
- existing components were reused where appropriate;
- accessibility has been verified;
- responsive behavior has been verified;
- TypeScript types are correct;
- self-review has been completed.

---

## Expected AI Output

After completing this workflow, the AI should explain:

- the component's purpose;
- its public API;
- reused components and hooks;
- responsive strategy;
- accessibility considerations;
- modified files;
- verification performed.

---

## Summary

A high-quality React component is more than a rendered UI.

It is a reusable, maintainable, accessible building block that integrates naturally into the application's architecture and design system.
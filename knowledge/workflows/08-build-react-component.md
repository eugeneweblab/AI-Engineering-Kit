---
id: workflows/08-build-react-component
topic: workflows
slug: build-react-component
title: "Workflow — Build a React Component"
type: doc
order: 8
status: ready
tags: [workflows, build-react-component, aProduct, ProductCard, ProductCardProps, addToBasket, formatCurrency, repeat]
related: [react/13-component-composition, react/21-testing, examples/02-react-component]
  - react/02-component-architecture
  - react/05-props
  - react/09-custom-hooks
  - react/13-component-composition
  - react/20-accessibility
  - react/21-testing
  - react/22-folder-structure
  - react/98-production-checklist
  - frontend/02-component-driven-development
  - frontend/03-design-systems
  - accessibility/03-semantic-html
  - accessibility/04-keyboard-navigation
  - css/17-responsive-design
  - typescript/06-interfaces
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

Enumerate the states explicitly — empty, loading, error, partial, and full — before writing
markup; a component designed around only the happy path gets patched into an unreadable one
later. See [Engineering — Context-First Development](../engineering/05-context-first-development.md)
and, when the requirements come from a design file,
[Workflow — Implement a Figma Design](01-implement-figma-design.md).

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

Relevant knowledge:

- [React — Folder Structure](../react/22-folder-structure.md) — where components, hooks, and shared UI live in this codebase.
- [Frontend — Design Systems](../frontend/03-design-systems.md) — checking the design system before inventing a new primitive.
- [Engineering — Engineering Principles](../engineering/00-engineering-principles.md) — the reuse-over-duplication rule that governs this step.

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

Relevant knowledge:

- [React — Component Architecture](../react/02-component-architecture.md) — sizing a component around one responsibility.
- [Frontend — Component-Driven Development](../frontend/02-component-driven-development.md) — building from the leaf inward.

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

Relevant knowledge:

- [React — Props](../react/05-props.md) — prop naming, defaults, and why props stay read-only.
- [React — Component Composition](../react/13-component-composition.md) — `children` and slot props instead of a growing list of booleans.
- [React — Patterns](../react/14-patterns.md) — compound components, render props, and when each fits.
- [TypeScript — Interfaces](../typescript/06-interfaces.md) and [TypeScript — Unions and Intersections](../typescript/11-unions-and-intersections.md) — model the prop contract so illegal states cannot be expressed.

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

Relevant knowledge:

- [Accessibility — Semantic HTML](../accessibility/03-semantic-html.md) and [HTML — Semantic HTML](../html/02-semantic-html.md) — the element carries the role; `div` with `onClick` does not.
- [React — JSX](../react/03-jsx.md) — fragments instead of wrapper `div`s that distort the layout.

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

Relevant knowledge:

- [Frontend — Styling](../frontend/15-styling.md) and [CSS — Architecture](../css/21-architecture.md) — picking the approach the project already uses.
- [Tailwind — Utility First](../tailwind/03-utility-first.md) and [Tailwind — React](../tailwind/24-react.md) — conventions for a Tailwind codebase.
- [CSS — CSS Variables](../css/20-css-variables.md) — consuming design tokens instead of hardcoding values.
- [Figma — Design Token Extraction](../figma/03-design-token-extraction.md) — where those token values come from.

---

## Step 7 — Implement Logic

Keep rendering and business logic separated.

Prefer:

- custom hooks;
- utility functions;
- shared services.

Avoid placing complex business logic directly inside JSX.

Relevant knowledge:

- [React — Custom Hooks](../react/09-custom-hooks.md) — extracting stateful logic so it can be tested on its own.
- [React — State](../react/06-state.md) — keeping state minimal and deriving the rest in render.
- [React — Data Fetching](../react/16-data-fetching.md) — where a component gets its data, and who owns loading and error state.
- [React — Error Handling](../react/19-error-handling.md) — error boundaries around the component instead of silent failure.
- [React — Performance](../react/12-performance.md) — memoize only after profiling proves it necessary.

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

Relevant knowledge:

- [React — Accessibility](../react/20-accessibility.md) — accessible patterns in a React component tree.
- [Accessibility — Keyboard Navigation](../accessibility/04-keyboard-navigation.md) and [Accessibility — Focus Management](../accessibility/05-focus-management.md) — every interaction reachable without a mouse.
- [Accessibility — ARIA](../accessibility/07-aria.md) — used only where semantics are genuinely missing.
- [Accessibility — Color and Contrast](../accessibility/10-color-and-contrast.md) — contrast ratios for text and interactive states.
- [Accessibility — Axe](../accessibility/21-axe.md) and [Testing — Accessibility Testing](../testing/18-accessibility-testing.md) — automating the checks that can be automated.

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

Relevant knowledge:

- [CSS — Responsive Design](../css/17-responsive-design.md) and [CSS — Container Queries](../css/19-container-queries.md) — sizing a reusable component by its container, not the viewport.
- [Tailwind — Responsive Design](../tailwind/11-responsive-design.md) — breakpoint prefixes and the mobile-first default.
- [Accessibility — Responsive Accessibility](../accessibility/13-responsive-accessibility.md) — touch targets and reflow at 400% zoom.
- [Figma — Responsive Analysis](../figma/05-responsive-analysis.md) — deriving breakpoint behavior from the design.

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

Relevant knowledge:

- [React — Code Style](../react/23-code-style.md) — naming and file conventions a reviewer will expect.
- [React — Testing](../react/21-testing.md) — cover behavior through the public API, not internal state.
- [Engineering — Code Review](../engineering/02-code-review.md) — the lens a reviewer applies before you ask for one.

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

## Examples

**Good Example** — the API is decided first, and the states are all built

```tsx
// The prop contract comes from the design's variant axes, nothing more.
type ProductCardProps = {
  product: Product;
  onAddToBasket: (productId: string) => void;
  variant?: 'default' | 'compact';
};

export function ProductCard({ product, onAddToBasket, variant = 'default' }: ProductCardProps) {
  return (
    <article className={cx(styles.card, styles[variant])}>
      <img
        src={product.imageUrl}
        alt={product.imageAlt}          // from the data, never invented at render time
        width={800}
        height={600}
        loading="lazy"
      />
      <h3 className={styles.title}>{product.name}</h3>
      <p className={styles.price}>{formatCurrency(product.priceCents)}</p>
      <Button onClick={() => onAddToBasket(product.id)}>Add to basket</Button>
    </article>
  );
}
```

```tsx
// Every state the design defines has a story and a test, not just the happy one.
export const Default: Story = { args: { product: aProduct() } };
export const LongName: Story = { args: { product: aProduct({ name: 'x'.repeat(64) }) } };
export const NoImage: Story = { args: { product: aProduct({ imageUrl: null }) } };
export const Compact: Story = { args: { product: aProduct(), variant: 'compact' } };
```

**Bad Example** — build the happy path, discover the rest in production

```tsx
export function ProductCard({ data }: { data: any }) {
  // `any` props: no contract, so the compiler cannot help a caller.
  return (
    <div className="card" onClick={() => addToBasket(data.id)}>
      {/* A div with a click handler: not focusable, not keyboard-operable. */}
      <img src={data.img} />                    {/* no alt, no dimensions */}
      <div className="title">{data.name}</div>  {/* styled to look like a heading */}
      <div className="price">£{data.price / 100}</div>  {/* float arithmetic on money */}
    </div>
  );
}
```

There is no long-name state, no missing-image state, and no compact variant — so the first
64-character product name breaks the grid on a live page.

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

## Self-Verification — Topic Checklists

Before marking the component complete, run it through the `98`/`99`/`100` checklists of the
topics it touches:

- React — [Production Checklist](../react/98-production-checklist.md), [AI Review Checklist](../react/99-ai-review-checklist.md), [Common Antipatterns](../react/100-common-antipatterns.md).
- Accessibility — [Production Checklist](../accessibility/98-production-checklist.md), [AI Review Checklist](../accessibility/99-ai-review-checklist.md), [Common Antipatterns](../accessibility/100-common-antipatterns.md).
- Frontend — [Production Checklist](../frontend/98-production-checklist.md), [AI Review Checklist](../frontend/99-ai-review-checklist.md), [Common Antipatterns](../frontend/100-common-antipatterns.md).

If the component ships in a Next.js app, add
[Next.js — Production Checklist](../nextjs/98-production-checklist.md) and
[Next.js — Common Antipatterns](../nextjs/100-common-antipatterns.md) — in particular,
confirm the component is a Server Component unless it genuinely needs interactivity. For a
Tailwind codebase, close with
[Tailwind — AI Review Checklist](../tailwind/99-ai-review-checklist.md).

---

## Summary

A high-quality React component is more than a rendered UI.

It is a reusable, maintainable, accessible building block that integrates naturally into the application's architecture and design system.

## Related

- `knowledge/react/13-component-composition.md`
- `knowledge/react/21-testing.md`
- `knowledge/examples/02-react-component.md`

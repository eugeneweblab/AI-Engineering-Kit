---
id: figma/06-component-detection
topic: figma
slug: component-detection
title: "Component Detection"
type: doc
order: 6
status: ready
tags: [figma, component-detection]
related: [figma/01-figma-analysis, figma/19-design-handoff, react/13-component-composition]
when_to_use: "Read before coding, to identify reusable UI components and repeated patterns in a Figma design."
---
# Component Detection

## Purpose

This document defines the standard process for identifying reusable UI components from a Figma design before implementation.

The objective is to recognize patterns instead of individual elements.

Professional frontend development is based on reusable components rather than page-specific implementations.

---

## Core Principle

Never build pages.

Build reusable components that assemble pages.

A page should be viewed as a composition of independent UI building blocks.

---

## AI Mindset

When analyzing a design, ask:

- Does this element appear more than once?
- Could this element appear on another page?
- Does it represent a business concept?
- Can it accept different content?
- Can it be configured with properties?
- Should this become a reusable component?

If the answer is yes, create a reusable component instead of duplicating markup.

---

## Component Detection Workflow

Analyze the design using the following sequence:

```
Entire Page
        ↓
Sections
        ↓
Repeated Elements
        ↓
Variants
        ↓
States
        ↓
Properties
        ↓
Composition
        ↓
Implementation
```

Always identify components before writing HTML.

---

## Step 1 — Detect Repeated Elements

Search the entire project rather than a single page.

Typical reusable components include:

- buttons;
- cards;
- badges;
- avatars;
- inputs;
- selects;
- checkboxes;
- radios;
- tabs;
- accordions;
- breadcrumbs;
- alerts;
- modals;
- pagination.

Frequency is the strongest indicator of reusability.

---

## Step 2 — Detect Variants

A component rarely exists in only one version.

Examples:

Button

- Primary
- Secondary
- Outline
- Ghost
- Link

Card

- Default
- Featured
- Compact
- Horizontal

Input

- Default
- Error
- Success
- Disabled

Variants belong to one component rather than separate implementations.

---

## Step 3 — Detect States

Every interactive component has multiple states.

Review:

- default;
- hover;
- focus;
- active;
- disabled;
- loading;
- error;
- success.

State changes should be implemented through properties rather than duplicated markup.

---

## Step 4 — Detect Properties

Determine which values should be configurable.

Examples:

Button

Properties:

- text;
- icon;
- size;
- variant;
- disabled;
- loading;
- href;
- target.

Card

Properties:

- image;
- title;
- description;
- actions;
- badge;
- link.

Reusable components expose configuration rather than fixed content.

---

## Step 5 — Detect Composition

Components are frequently built from smaller components.

Example:

```
Product Card

    Badge

    Image

    Title

    Rating

    Price

    Button
```

Prefer composition over inheritance.

---

## Step 6 — Detect Shared Patterns

Different sections often reuse the same layout.

Examples:

Feature Card

Service Card

Team Card

Blog Card

Although their content differs, their structure may be identical.

Avoid creating separate components when a single configurable component is sufficient.

---

## Step 7 — Detect Dynamic Content

Determine which content originates from:

- WordPress;
- REST API;
- GraphQL;
- WooCommerce;
- external services;
- user input.

Dynamic data should be passed into components through properties.

Never hardcode business data.

---

## Step 8 — Detect Existing Components

Before creating a new component, search the project.

Review:

- existing React components;
- Gutenberg blocks;
- Divi modules;
- shared templates;
- UI library;
- design system;
- utility components.

Reuse before creating.

---

## Component Hierarchy

Build from simple to complex.

```
Button

↓

Button Group

↓

Card

↓

Section

↓

Page
```

Lower-level components should remain independent.

---

## Naming Components

Component names should describe business meaning.

Good:

```
PrimaryButton

ProductCard

TeamMemberCard

PricingTable

HeroSection

NewsletterForm
```

Avoid:

```
Box

Wrapper

Container2

CardNew

Component

Block1
```

Names should communicate purpose.

---

## AI Execution Checklist

## Investigation

☐ Review the entire page.

☐ Identify repeated elements.

☐ Identify variants.

☐ Identify states.

☐ Identify dynamic content.

☐ Search existing components.

---

## Planning

☐ Define reusable components.

☐ Define component hierarchy.

☐ Define properties.

☐ Define composition.

---

## Verification

☐ No duplicated components exist.

☐ Existing components were reused.

☐ Component names are descriptive.

☐ Variants are unified.

☐ States are complete.

☐ Components remain independent.

---

## Common Mistakes

Avoid:

Creating page-specific components.

Duplicating nearly identical components.

Embedding business logic inside UI components.

Hardcoding text.

Hardcoding images.

Ignoring variants.

Ignoring states.

Ignoring composition.

---

## Examples

**Good Example** — one Figma component becomes one code component with a typed API

```text
Figma: Button (component set)
  Variant  variant = primary | secondary | danger
  Variant  size    = sm | md
  Variant  state   = default | hover | disabled     ← CSS states, not props
  Instances found: 34 across 6 frames
```

```tsx
// The variant axes become the prop type; the state axis becomes CSS.
type ButtonProps = {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md';
  children: React.ReactNode;
} & React.ComponentPropsWithoutRef<'button'>;

export function Button({ variant = 'primary', size = 'md', children, ...rest }: ButtonProps) {
  return (
    <button className={cx(styles.button, styles[variant], styles[size])} {...rest}>
      {children}
    </button>
  );
}
```

```css
/* hover and disabled are states of the same component, not separate components. */
.button:hover:not(:disabled) { filter: brightness(0.95); }
.button:disabled { opacity: 0.5; cursor: not-allowed; }
```

34 instances now share one implementation, and a variant that does not exist in the design
fails to compile.

**Bad Example** — one component per visual difference

```tsx
// Each of these was created from a different frame, and they have already drifted:
// two use 12px radius, one uses 11px, and only one handles the disabled state.
export function PrimaryButton({ label }: { label: string }) { /* … */ }
export function PrimaryButtonSmall({ label }: { label: string }) { /* … */ }
export function SecondaryButton({ label }: { label: string }) { /* … */ }
export function DangerButtonSmallDisabled({ label }: { label: string }) { /* … */ }
```

The design has one component with three axes. The code has eight components with no
relationship, and the ninth combination will be written from scratch.

---

## Completion Criteria

Component detection is complete when:

- every repeated UI element has been identified;
- variants are grouped into reusable components;
- configurable properties are defined;
- component hierarchy is established;
- duplicate implementations have been eliminated.

---

## Summary

The quality of a frontend architecture depends largely on component design.

Well-designed components reduce duplication, simplify maintenance, improve consistency, and enable AI coding assistants to generate significantly higher-quality implementations.

## Related

- `knowledge/figma/01-figma-analysis.md`
- `knowledge/figma/19-design-handoff.md`
- `knowledge/react/13-component-composition.md`

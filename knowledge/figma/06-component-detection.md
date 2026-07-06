# Component Detection

## Purpose

This document defines the standard process for identifying reusable UI components from a Figma design before implementation.

The objective is to recognize patterns instead of individual elements.

Professional frontend development is based on reusable components rather than page-specific implementations.

---

# Core Principle

Never build pages.

Build reusable components that assemble pages.

A page should be viewed as a composition of independent UI building blocks.

---

# AI Mindset

When analyzing a design, ask:

- Does this element appear more than once?
- Could this element appear on another page?
- Does it represent a business concept?
- Can it accept different content?
- Can it be configured with properties?
- Should this become a reusable component?

If the answer is yes, create a reusable component instead of duplicating markup.

---

# Component Detection Workflow

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

# Step 1 — Detect Repeated Elements

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

# Step 2 — Detect Variants

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

# Step 3 — Detect States

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

# Step 4 — Detect Properties

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

# Step 5 — Detect Composition

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

# Step 6 — Detect Shared Patterns

Different sections often reuse the same layout.

Examples:

Feature Card

Service Card

Team Card

Blog Card

Although their content differs, their structure may be identical.

Avoid creating separate components when a single configurable component is sufficient.

---

# Step 7 — Detect Dynamic Content

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

# Step 8 — Detect Existing Components

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

# Component Hierarchy

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

# Naming Components

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

# AI Execution Checklist

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

# Common Mistakes

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

# Completion Criteria

Component detection is complete when:

- every repeated UI element has been identified;
- variants are grouped into reusable components;
- configurable properties are defined;
- component hierarchy is established;
- duplicate implementations have been eliminated.

---

# Summary

The quality of a frontend architecture depends largely on component design.

Well-designed components reduce duplication, simplify maintenance, improve consistency, and enable AI coding assistants to generate significantly higher-quality implementations.
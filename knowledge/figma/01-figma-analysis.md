# Figma Analysis

## Purpose

This document defines the standard process for analyzing Figma designs before writing any code.

The objective is to ensure that engineers and AI coding assistants fully understand the design, identify reusable patterns, and plan the implementation before making changes to the codebase.

No code should be written until the design has been completely analyzed.

---

# Core Principle

Figma is a specification, not an image.

Every design should be interpreted as a collection of reusable components, layouts, spacing systems, and interaction patterns.

The goal is to understand the design rather than reproduce pixels.

---

# Design Analysis Workflow

Every implementation should follow this sequence:

```
Understand the Page
        ↓
Identify Layout Structure
        ↓
Identify Reusable Components
        ↓
Identify Design Tokens
        ↓
Analyze Responsive Behavior
        ↓
Analyze Interactions
        ↓
Identify Dynamic Content
        ↓
Plan Implementation
        ↓
Begin Development
```

Skipping analysis usually results in unnecessary refactoring.

---

# Step 1 — Understand the Page

Before examining individual elements, determine:

- the business purpose of the page;
- the target audience;
- the primary user actions;
- the information hierarchy;
- conversion goals.

The layout should support the user journey.

---

# Step 2 — Identify Layout Structure

Identify the major sections.

Typical examples include:

- Header
- Hero
- Features
- Statistics
- Testimonials
- Pricing
- FAQ
- CTA
- Footer

Each section should be treated as an independent module.

---

# Step 3 — Identify Reusable Components

Search for repeated UI elements.

Examples:

- buttons;
- cards;
- badges;
- forms;
- navigation;
- tabs;
- accordions;
- modals;
- sliders;
- avatars.

A repeated element should usually become a reusable component.

---

# Step 4 — Identify Design Tokens

Document the design system before implementation.

Review:

- typography;
- font sizes;
- spacing;
- colors;
- border radius;
- shadows;
- icons;
- grid system;
- breakpoints.

Avoid hardcoding visual values.

---

# Step 5 — Analyze Alignment

Review:

- container widths;
- margins;
- paddings;
- gaps;
- vertical rhythm;
- alignment;
- whitespace.

Spacing should follow a consistent system rather than visual approximation.

---

# Step 6 — Analyze Responsive Behavior

Determine how the layout changes between:

- Desktop
- Laptop
- Tablet
- Mobile

Identify:

- stacked layouts;
- hidden elements;
- reordered sections;
- resized typography;
- responsive spacing.

Do not invent responsive behavior unless the design requires interpretation.

---

# Step 7 — Analyze States

Review every interactive element.

Examples:

- hover;
- focus;
- active;
- disabled;
- loading;
- error;
- success;
- empty state.

All visual states should be implemented.

---

# Step 8 — Identify Dynamic Content

Determine which elements are expected to change.

Examples:

- CMS content;
- API responses;
- user information;
- product data;
- blog posts;
- forms;
- galleries.

Dynamic content should never be hardcoded.

---

# Step 9 — Identify Existing Components

Before creating new UI, review the existing project.

Search for:

- buttons;
- typography;
- layouts;
- cards;
- forms;
- navigation;
- icons.

Reuse before creating.

---

# Step 10 — Plan the Implementation

Before writing code define:

- reusable components;
- page structure;
- data flow;
- responsive strategy;
- accessibility considerations;
- potential risks.

A written implementation plan reduces unnecessary iterations.

---

# AI Execution Checklist

## Investigation

☐ Read the entire Figma page.

☐ Identify every section.

☐ Identify reusable components.

☐ Review the existing project.

☐ Identify dynamic content.

---

## Planning

☐ Define the component hierarchy.

☐ Define responsive behavior.

☐ Define reusable tokens.

☐ Identify dependencies.

---

## Verification

☐ Every section has been analyzed.

☐ Every repeated element has been identified.

☐ Existing components have been reused.

☐ Responsive behavior has been planned.

☐ Dynamic content has been identified.

---

# Common Mistakes

Avoid:

Starting implementation before reviewing the full design.

Treating the design as a static image.

Hardcoding spacing.

Ignoring existing UI components.

Creating duplicate components.

Ignoring responsive layouts.

Ignoring interaction states.

Ignoring dynamic content.

---

# Completion Criteria

The design analysis is complete only when:

- the entire page has been reviewed;
- reusable components have been identified;
- layout hierarchy is understood;
- responsive behavior is documented;
- implementation can begin without uncertainty.

---

# Summary

Successful implementation begins with understanding the design rather than writing code.

A complete design analysis minimizes rework, improves consistency, and allows both engineers and AI assistants to produce predictable, maintainable implementations.
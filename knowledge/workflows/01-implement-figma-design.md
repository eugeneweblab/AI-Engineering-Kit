# Workflow — Implement a Figma Design

## Purpose

This workflow defines how an AI coding agent should transform a Figma design into production-ready code while minimizing implementation errors, unnecessary iterations, and visual inconsistencies.

The objective is not to copy pixels.

The objective is to faithfully implement the design system, layout, behavior, and user experience represented in Figma.

---

# Core Principle

Never start coding immediately after opening a Figma file.

A Figma design should first be analyzed as a complete system.

Only after the analysis is complete should implementation begin.

---

# Workflow Overview

```
Receive Design
        ↓
Analyze Entire Page
        ↓
Identify Design System
        ↓
Split Into Components
        ↓
Compare With Existing Project
        ↓
Create Implementation Plan
        ↓
Implement Components
        ↓
Assemble Layout
        ↓
Responsive Review
        ↓
Visual Verification
        ↓
Final Review
```

---

# Step 1 — Analyze the Entire Design

Before writing code:

Review the complete page.

Understand:

- page purpose;
- layout hierarchy;
- reusable sections;
- navigation;
- spacing rhythm;
- typography;
- colors;
- interactions.

Never begin implementation after inspecting only the first screen.

---

# Step 2 — Identify the Design System

Determine whether the design already contains reusable rules.

Identify:

- typography scale;
- spacing scale;
- border radius;
- shadows;
- color palette;
- grid system;
- breakpoints;
- icon library;
- button styles;
- form styles.

These become implementation constraints.

---

# Step 3 — Split the Design Into Components

Do not think in pixels.

Think in reusable components.

Example:

Instead of:

```
Landing Page
```

Think:

```
Header

Hero

CTA

Features

Statistics

Testimonials

FAQ

Footer
```

Then split again.

Example:

Hero

↓

Heading

↓

Buttons

↓

Background

↓

Illustration

↓

Badge

↓

Actions

Large UI should be decomposed recursively.

---

# Step 4 — Compare With Existing Project

Before creating anything:

Search for:

- existing buttons;
- existing cards;
- typography;
- layout containers;
- sections;
- forms;
- modals;
- sliders;
- icons.

Prefer reuse over recreation.

---

# Step 5 — Build an Implementation Plan

Before editing files determine:

Files to modify

Files to create

Existing components to reuse

Responsive strategy

Animation strategy

Accessibility requirements

Verification strategy

Implementation should follow a plan.

---

# Step 6 — Implement From Large to Small

Recommended order:

Layout

↓

Sections

↓

Components

↓

Content

↓

Interactions

↓

Animations

↓

Responsive adjustments

Avoid styling individual elements before the page structure exists.

---

# Step 7 — Preserve Design Consistency

Maintain consistency for:

Spacing

Typography

Button sizes

Icon sizing

Container widths

Grid alignment

Border radius

Color usage

Interactive states

One inconsistent component reduces the quality of the entire interface.

---

# Step 8 — Responsive Implementation

Responsive behavior should not be added after desktop implementation.

Consider responsiveness during implementation.

Review:

Desktop

Tablet

Mobile

Large mobile

Small mobile

Foldable devices (when required)

Layout should adapt naturally.

---

# Step 9 — Accessibility Review

Verify:

Semantic HTML

Keyboard navigation

Visible focus

ARIA attributes when required

Image alt text

Heading hierarchy

Label associations

Color contrast

Accessibility is part of implementation—not an optional enhancement.

---

# Step 10 — Visual Verification

Compare the implementation against the Figma design.

Review:

Spacing

Alignment

Typography

Icons

Colors

Shadows

Border radius

Hover states

Focus states

Responsive behavior

The comparison should use the complete page—not isolated components.

---

# AI Execution Checklist

## Design Analysis

☐ Review the complete page.

☐ Identify reusable components.

☐ Identify layout hierarchy.

☐ Identify design tokens.

☐ Identify breakpoints.

☐ Identify interactions.

---

## Repository Analysis

☐ Search existing components.

☐ Search typography system.

☐ Search layout system.

☐ Search utility classes.

☐ Search design tokens.

☐ Search responsive helpers.

---

## Implementation

☐ Reuse existing components.

☐ Preserve spacing scale.

☐ Preserve typography scale.

☐ Preserve responsive behavior.

☐ Match existing architecture.

☐ Avoid duplicate components.

---

## Verification

☐ Compare against Figma.

☐ Review desktop.

☐ Review tablet.

☐ Review mobile.

☐ Review accessibility.

☐ Review interactions.

☐ Review animations.

☐ Review edge cases.

---

# Common Mistakes

Avoid:

Building directly from one frame.

Ignoring reusable components.

Creating duplicate buttons.

Ignoring spacing consistency.

Hardcoding dimensions unnecessarily.

Ignoring responsive behavior until the end.

Approximating typography.

Ignoring interaction states.

Treating Figma as an image instead of a system.

---

# AI Responsibilities

Before implementation AI should explain:

- page structure;
- reusable components;
- implementation strategy;
- responsive strategy;
- existing project components that will be reused;
- possible implementation risks.

After implementation AI should explain:

- which components were reused;
- which new components were created;
- responsive considerations;
- accessibility considerations;
- manual verification recommendations.

---

# Definition of Success

A successful implementation:

Matches the design intent.

Respects the existing project architecture.

Reuses existing components whenever possible.

Maintains visual consistency.

Works across supported screen sizes.

Remains maintainable.

Introduces minimal technical debt.

---

# Summary

Figma is not a collection of pixels.

It is a specification of a design system.

AI coding agents should implement the design system rather than reproducing individual screens.

Understanding the complete design before writing code consistently produces higher-quality implementations with fewer revision cycles.
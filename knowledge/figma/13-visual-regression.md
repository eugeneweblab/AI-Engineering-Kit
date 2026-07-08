---
id: figma/13-visual-regression
topic: figma
slug: visual-regression
title: "Visual Regression"
type: doc
order: 13
status: ready
tags: [figma, visual-regression]
related: []
when_to_use: "Read before approving frontend changes, to check that new work has not visually regressed existing pages."
---
# Visual Regression

## Purpose

This document defines the standard process for identifying visual regressions after implementing a Figma design.

The objective is to ensure that new changes do not unintentionally alter the appearance, layout, responsiveness, or usability of existing pages.

Visual regression testing is a mandatory verification step before approving frontend changes.

---

## Core Principle

Every visual change must be intentional.

Unexpected differences are defects until proven otherwise.

---

## Verification Workflow

Every implementation should be verified in the following order:

```
Baseline Design
        ↓
Current Implementation
        ↓
Desktop Comparison
        ↓
Tablet Comparison
        ↓
Mobile Comparison
        ↓
Component Comparison
        ↓
Interaction Comparison
        ↓
Approval
```

---

## Step 1 — Compare Overall Layout

Verify:

- page width;
- section order;
- visual hierarchy;
- whitespace;
- content alignment;
- container consistency.

---

## Step 2 — Compare Components

Review every reusable component.

Examples:

- buttons;
- cards;
- forms;
- navigation;
- sliders;
- accordions;
- pricing cards;
- testimonials.

All instances should remain visually consistent.

---

## Step 3 — Compare Typography

Verify:

- font family;
- font size;
- font weight;
- line height;
- letter spacing;
- text alignment;
- heading hierarchy.

---

## Step 4 — Compare Spacing

Review:

- margins;
- padding;
- gaps;
- section spacing;
- grid spacing.

Spacing should follow the project's design system.

---

## Step 5 — Compare Colors

Verify:

- backgrounds;
- borders;
- text;
- icons;
- buttons;
- links;
- shadows.

Use design tokens whenever possible.

---

## Step 6 — Compare Responsive Layouts

Verify:

Desktop

↓

Laptop

↓

Tablet

↓

Mobile

Ensure that layout transitions match the design.

---

## Step 7 — Compare Interactions

Review:

- hover;
- focus;
- active;
- disabled;
- loading;
- animations.

Interactive behavior should remain consistent.

---

## Step 8 — Compare Accessibility

Verify:

- semantic HTML;
- heading order;
- keyboard navigation;
- focus visibility;
- image alt text;
- form labels.

---

## AI Checklist

## Investigation

☐ Compare layouts.

☐ Compare components.

☐ Compare typography.

☐ Compare spacing.

☐ Compare colors.

☐ Compare responsive behavior.

☐ Compare interactions.

---

## Verification

☐ All visual differences documented.

☐ Unintentional regressions identified.

☐ Responsive behavior verified.

☐ Accessibility preserved.

☐ Final implementation approved.

---

## Common Mistakes

Avoid:

Ignoring small spacing differences.

Reviewing only desktop.

Ignoring hover states.

Ignoring accessibility.

Approving visual regressions without investigation.

---

## Completion Criteria

Visual regression review is complete when:

- all layouts have been compared;
- responsive behavior has been verified;
- unexpected differences have been resolved;
- implementation accurately reflects the approved design.

---

## Summary

Visual regression testing protects design consistency and prevents unintended frontend changes from reaching production.
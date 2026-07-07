---
id: figma/16-accessibility-from-figma
topic: figma
slug: accessibility-from-figma
title: "Accessibility from Figma"
type: doc
order: 16
status: ready
tags: [figma, accessibility-from-figma]
related: []
when_to_use: ""
---
# Accessibility from Figma

## Purpose

This document defines the standard process for identifying accessibility requirements during Figma analysis before implementation begins.

Accessibility should be planned while inspecting the design—not added after development.

The goal is to produce interfaces that are usable by all users while remaining faithful to the approved design.

---

## Core Principle

Accessibility starts in the design phase.

Every UI element should be evaluated for accessibility before writing code.

Do not treat accessibility as a separate task.

---

## Accessibility Review Workflow

Follow this sequence during design analysis.

```
Analyze Layout
        ↓
Identify Semantic Structure
        ↓
Review Interactive Elements
        ↓
Review Forms
        ↓
Review Images
        ↓
Review Typography
        ↓
Review Color Contrast
        ↓
Review Keyboard Navigation
        ↓
Review Responsive Behavior
        ↓
Prepare Implementation
```

---

## Step 1 — Semantic Structure

Identify the document structure.

Verify:

- page landmarks;
- sections;
- articles;
- navigation;
- footer;
- sidebar;
- heading hierarchy.

Every visible section should have a semantic purpose.

---

## Step 2 — Heading Hierarchy

Review the complete heading structure.

Verify:

- exactly one H1 per page where appropriate;
- logical heading order;
- no skipped heading levels without justification;
- headings describe content rather than appearance.

Headings create the document outline for assistive technologies.

---

## Step 3 — Interactive Elements

Identify every interactive component.

Examples:

- buttons;
- links;
- navigation;
- menus;
- accordions;
- tabs;
- sliders;
- dialogs;
- dropdowns.

Every interactive element must be operable using both a mouse and a keyboard.

---

## Step 4 — Forms

Review every form.

Verify:

- labels;
- placeholders;
- required indicators;
- validation messages;
- error messages;
- success messages;
- helper text.

Placeholders must never replace labels.

---

## Step 5 — Images

Classify every image.

Possible categories:

- informative;
- decorative;
- functional;
- branding.

Determine whether meaningful alternative text is required.

Decorative images should not create unnecessary noise for assistive technologies.

---

## Step 6 — Icons

Determine whether icons:

- communicate information;
- trigger actions;
- are decorative.

Icons used as controls require accessible names.

Decorative icons should not be announced unnecessarily.

---

## Step 7 — Color Contrast

Review:

- text;
- buttons;
- links;
- form controls;
- icons;
- status indicators.

Do not rely on color alone to communicate meaning.

---

## Step 8 — Typography

Verify:

- readable font sizes;
- sufficient line height;
- adequate spacing;
- text alignment;
- paragraph width.

Typography directly affects readability.

---

## Step 9 — Focus Management

Review every interactive flow.

Verify:

- logical tab order;
- visible focus indicators;
- dialog focus management;
- keyboard accessibility.

Users should never lose track of keyboard focus.

---

## Step 10 — Responsive Accessibility

Review every breakpoint.

Verify:

- touch target size;
- navigation usability;
- readable typography;
- spacing;
- scrolling behavior.

Accessibility must be preserved across all supported devices.

---

## Accessibility Questions

Before implementation ask:

- Can this page be understood without visual styling?
- Can every interactive element be reached using a keyboard?
- Does every control have an accessible name?
- Does the heading hierarchy describe the content?
- Can users understand errors without relying only on color?

If any answer is "No", improve the implementation plan.

---

## AI Execution Checklist

## Investigation

☐ Semantic structure identified.

☐ Heading hierarchy reviewed.

☐ Interactive elements identified.

☐ Forms reviewed.

☐ Images classified.

☐ Icons reviewed.

☐ Color contrast considered.

☐ Responsive accessibility reviewed.

---

## Verification

☐ Accessibility requirements documented.

☐ Keyboard interaction planned.

☐ Semantic HTML planned.

☐ Form accessibility planned.

☐ Image accessibility planned.

---

## Common Mistakes

Avoid:

Replacing semantic HTML with generic containers.

Using placeholders instead of labels.

Skipping heading levels.

Relying only on color.

Removing focus indicators.

Ignoring keyboard navigation.

Using icons without accessible names.

Adding accessibility only after implementation.

---

## Completion Criteria

Accessibility planning is complete when:

- semantic structure has been defined;
- interactive elements have been reviewed;
- form accessibility has been planned;
- image accessibility has been evaluated;
- responsive accessibility has been considered;
- implementation requirements have been documented.

---

## Summary

Accessibility begins during design analysis.

Identifying accessibility requirements before implementation results in cleaner code, fewer revisions, and interfaces that are usable by a broader range of people.
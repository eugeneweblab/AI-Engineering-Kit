---
id: figma/04-auto-layout
topic: figma
slug: auto-layout
title: "Figma Auto Layout"
type: doc
order: 4
status: ready
tags: [figma, auto-layout]
related: []
when_to_use: ""
---
# Figma Auto Layout

## Purpose

This document defines the standard process for analyzing and implementing Figma Auto Layout.

Auto Layout is one of the most important sources of information in a Figma design.

It describes how components grow, shrink, align, and respond to content changes.

A correct understanding of Auto Layout significantly reduces layout bugs and unnecessary revisions during development.

---

## Core Principle

Auto Layout describes behavior, not appearance.

Do not recreate the visual result.

Recreate the layout behavior.

---

## AI Mindset

When inspecting Auto Layout, ask:

- Why is Auto Layout used here?
- Which element controls the layout?
- Which element grows?
- Which element remains fixed?
- Which spacing is intentional?
- Which alignment rule is being applied?

Understanding behavior is more important than copying values.

---

## Auto Layout Workflow

Always analyze Auto Layout in the following order:

```
Direction
        ↓
Spacing
        ↓
Padding
        ↓
Alignment
        ↓
Distribution
        ↓
Sizing
        ↓
Constraints
        ↓
Responsive Behavior
```

---

## Step 1 — Direction

Determine whether the layout flows:

- horizontally;
- vertically;
- wraps to multiple rows.

Typical mappings:

Vertical Auto Layout → Flex Column

Horizontal Auto Layout → Flex Row

Wrapping Auto Layout → Flex Wrap or CSS Grid

---

## Step 2 — Item Spacing

Determine whether spacing is:

- fixed;
- automatic;
- evenly distributed.

Spacing should become a layout property rather than individual margins.

Prefer:

```
gap: 24px;
```

Instead of:

```
margin-bottom: 24px;
```

Repeated margins usually indicate an incorrect implementation.

---

## Step 3 — Padding

Identify internal spacing.

Review:

- top;
- right;
- bottom;
- left.

Padding belongs to the container.

Never distribute container padding across child elements.

---

## Step 4 — Alignment

Review:

- start;
- center;
- end;
- stretch;
- baseline.

Alignment should come from the parent layout rather than child positioning.

---

## Step 5 — Distribution

Determine how children occupy available space.

Common behaviors:

- Hug Contents
- Fill Container
- Fixed Size

Understanding these rules is essential for responsive layouts.

---

## Step 6 — Hug Contents

"Hug Contents" means that the element sizes itself according to its content.

Typical examples:

- buttons;
- badges;
- tags;
- chips;
- labels.

Avoid assigning unnecessary fixed widths.

---

## Step 7 — Fill Container

"Fill Container" indicates that the element expands to occupy available space.

Typical examples:

- cards;
- forms;
- content columns;
- navigation items.

Usually maps to:

```
flex: 1;
```

or an equivalent layout rule.

---

## Step 8 — Fixed Size

Use fixed dimensions only when the design explicitly requires them.

Typical examples:

- logos;
- icons;
- avatars;
- decorative illustrations.

Avoid converting flexible layouts into fixed-width implementations.

---

## Step 9 — Nested Auto Layout

Auto Layout frequently contains additional Auto Layout containers.

Example:

```
Section

    Container

        Card

            Header

            Content

            Footer
```

Each nested Auto Layout usually represents a reusable layout component.

---

## Step 10 — Constraints

Review how the layout behaves when resized.

Examples:

- fixed width;
- fill width;
- hug width;
- minimum width;
- maximum width;
- proportional scaling.

Constraints often determine the responsive implementation.

---

## Mapping to CSS

Prefer layout primitives.

Examples:

Auto Layout Column

↓

display: flex;
flex-direction: column;

---

Auto Layout Row

↓

display: flex;
flex-direction: row;

---

Spacing

↓

gap

---

Padding

↓

padding

---

Alignment

↓

align-items

justify-content

---

Fill Container

↓

flex: 1

---

Hug Contents

↓

width: fit-content;

or

inline-flex

---

## Mapping to Tailwind

Examples:

```
flex

flex-col

flex-row

items-center

justify-between

gap-4

gap-6

gap-8

p-4

px-6

py-8

flex-1

w-fit
```

Prefer semantic layout over utility accumulation.

---

## AI Execution Checklist

## Investigation

☐ Review Auto Layout direction.

☐ Review spacing.

☐ Review padding.

☐ Review alignment.

☐ Review sizing behavior.

☐ Review constraints.

---

## Planning

☐ Map Auto Layout to CSS.

☐ Preserve responsive behavior.

☐ Remove unnecessary wrappers.

☐ Reuse existing layout components.

---

## Verification

☐ Layout behaves like Figma.

☐ Components resize correctly.

☐ Spacing remains consistent.

☐ Fixed sizes are justified.

☐ Responsive behavior matches the design.

---

## Common Mistakes

Avoid:

Replacing gap with margins.

Ignoring Hug Contents.

Ignoring Fill Container.

Using fixed widths everywhere.

Adding unnecessary wrapper elements.

Using absolute positioning.

Breaking responsive behavior.

Copying the visual appearance instead of the layout behavior.

---

## Completion Criteria

An Auto Layout implementation is complete when:

- layout behavior matches the design;
- spacing is controlled by containers;
- sizing follows Auto Layout rules;
- responsive behavior is preserved;
- the HTML structure remains clean and semantic.

---

## Summary

Auto Layout is the blueprint for implementation.

The best frontend code mirrors the structural behavior defined in Figma rather than reproducing its visual appearance through manual positioning.

Correct interpretation of Auto Layout leads to simpler HTML, cleaner CSS, and significantly fewer layout regressions.
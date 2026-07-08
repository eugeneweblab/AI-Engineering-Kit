---
id: figma/03-design-token-extraction
topic: figma
slug: design-token-extraction
title: "Design Token Extraction"
type: doc
order: 3
status: ready
tags: [figma, design-token-extraction]
related: []
when_to_use: "Read before extracting design tokens (colors, spacing, typography) from a Figma file instead of hardcoding values."
---
# Design Token Extraction

## Purpose

This document defines the standard process for extracting design tokens from Figma before implementation.

The objective is to identify the underlying design system instead of copying individual values from the design.

Professional frontend development is based on reusable tokens rather than hardcoded visual properties.

---

## Core Principle

Do not copy values.

Identify the system behind the values.

A design token should represent a reusable design decision rather than a single occurrence in the interface.

---

## What Are Design Tokens

Design tokens are reusable values that define the visual language of a product.

Common categories include:

- colors;
- typography;
- spacing;
- sizing;
- border radius;
- shadows;
- opacity;
- z-index;
- animation;
- breakpoints.

Tokens should be shared across the entire application.

---

## Token Extraction Workflow

Every design should be analyzed in the following order:

```
Colors
    ↓
Typography
    ↓
Spacing
    ↓
Sizing
    ↓
Border Radius
    ↓
Shadows
    ↓
Icons
    ↓
Animations
    ↓
Responsive Rules
```

Do not jump directly into implementation.

---

## Step 1 — Extract Colors

Identify the complete color palette.

Look for:

- primary colors;
- secondary colors;
- accent colors;
- background colors;
- surface colors;
- border colors;
- text colors;
- success states;
- warning states;
- error states;
- disabled states.

Repeated colors should become shared tokens.

---

## Step 2 — Extract Typography

Identify the typography system.

Review:

- font families;
- font sizes;
- font weights;
- line heights;
- letter spacing;
- heading hierarchy;
- paragraph styles;
- captions.

Do not create unique styles for every text element.

---

## Step 3 — Extract Spacing

Identify recurring spacing values.

Typical spacing scale:

```
4
8
12
16
20
24
32
40
48
64
80
96
```

Prefer a consistent spacing scale over arbitrary values.

---

## Step 4 — Extract Sizing

Review recurring dimensions.

Examples:

- buttons;
- inputs;
- avatars;
- icons;
- cards;
- containers;
- navigation elements.

Reusable dimensions should become shared tokens.

---

## Step 5 — Extract Border Radius

Review every rounded corner.

Common examples:

```
0
4
6
8
12
16
20
24
9999
```

Avoid creating unique radius values for individual components.

---

## Step 6 — Extract Shadows

Identify shadow patterns.

Review:

- elevation levels;
- modal shadows;
- dropdown shadows;
- card shadows;
- hover shadows.

Shadows should communicate hierarchy rather than decoration.

---

## Step 7 — Extract Icons

Review:

- icon sizes;
- stroke width;
- icon style;
- icon library;
- alignment.

Icons should belong to one consistent visual family.

---

## Step 8 — Extract Animation Tokens

Review:

- transition duration;
- easing curves;
- hover animation;
- modal animation;
- accordion animation;
- loading indicators.

Animations should follow consistent timing.

---

## Step 9 — Extract Responsive Tokens

Review:

- container widths;
- grid columns;
- spacing changes;
- typography scaling;
- layout changes.

Responsive behavior should also be tokenized whenever possible.

---

## Identify Existing Tokens

Before creating new tokens, inspect the existing project.

Search for:

- Tailwind configuration;
- CSS variables;
- SCSS variables;
- theme configuration;
- design system;
- component library;
- existing constants.

Never create duplicate tokens.

---

## Mapping Tokens

Translate extracted values into reusable names.

Good examples:

```
color-primary

color-surface

spacing-md

spacing-xl

radius-lg

shadow-card

text-heading-xl

container-default
```

Avoid names that describe implementation details.

Poor examples:

```
blue1

gray3

margin16

font42

buttonShadow2
```

Names should describe purpose rather than appearance.

---

## AI Execution Checklist

## Investigation

☐ Review all colors.

☐ Review typography.

☐ Review spacing.

☐ Review radius values.

☐ Review shadows.

☐ Review responsive values.

☐ Review existing project tokens.

---

## Planning

☐ Group repeated values.

☐ Remove duplicates.

☐ Define reusable names.

☐ Preserve consistency.

---

## Verification

☐ No duplicate tokens were created.

☐ Naming is semantic.

☐ Existing design system is respected.

☐ Tokens are reusable.

☐ Hardcoded values are minimized.

---

## Common Mistakes

Avoid:

Creating a new token for every value.

Ignoring the existing design system.

Hardcoding spacing.

Hardcoding colors.

Duplicating typography styles.

Using inconsistent naming.

Creating component-specific tokens that should be global.

---

## Completion Criteria

Token extraction is complete when:

- repeated visual values have been identified;
- reusable tokens have been defined;
- existing project tokens have been reused where possible;
- unnecessary duplication has been eliminated;
- implementation can reference semantic design tokens instead of raw values.

---

## Summary

A professional implementation does not reproduce individual values from Figma.

It identifies the design language behind the interface and translates it into a reusable system of design tokens that improves consistency, scalability, and long-term maintainability.
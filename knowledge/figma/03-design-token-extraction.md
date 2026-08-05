---
id: figma/03-design-token-extraction
topic: figma
slug: design-token-extraction
title: "Design Token Extraction"
type: doc
order: 3
status: ready
tags: [figma, design-token-extraction, border-radius, FILE_KEY, "--color-accent", FIGMA_TOKEN, "--color-surface"]
related: [figma/01-figma-analysis, figma/19-design-handoff, tailwind/16-theme, css/20-css-variables]
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

## Examples

**Good Example** — extract the named styles, map them once, consume the variables

```bash
# Named styles carry the design decision. Node fills do not.
curl -sS -H "X-Figma-Token: $FIGMA_TOKEN" \
  "https://api.figma.com/v1/files/$FILE_KEY/styles" \
  | jq -r '.meta.styles[] | select(.style_type=="FILL") | "\(.name)\t\(.node_id)"'
```

```json
{
  "color": {
    "surface":  { "value": "#FFFFFF", "figma": "Surface/Card" },
    "ink":      { "value": "#111827", "figma": "Ink/Primary" },
    "accent":   { "value": "#2563EB", "figma": "Accent/Blue" }
  },
  "space": { "sm": "0.5rem", "md": "1rem", "lg": "1.5rem", "xl": "2rem" },
  "radius": { "sm": "0.25rem", "md": "0.5rem", "lg": "0.75rem" }
}
```

```css
/* One generated layer. Components reference the variable, never the literal. */
:root {
	--color-surface: #ffffff;
	--color-ink: #111827;
	--color-accent: #2563eb;
	--space-md: 1rem;
	--radius-lg: 0.75rem;
}

.card {
	background: var(--color-surface);
	color: var(--color-ink);
	padding: var(--space-md);
	border-radius: var(--radius-lg);
}
```

The Figma style name is kept alongside each token, so a reviewer can trace any value back to
the decision it came from.

**Bad Example** — hex values copied per component

```css
.card {
	background: #ffffff;
	color: #111827;
	padding: 17px;            /* measured off one instance, not on the scale */
	border-radius: 12px;
}

.panel {
	background: #fff;         /* the same colour, written differently */
	color: #111827;
	padding: 16px;
	border-radius: 11px;      /* nearly the same radius, now a second value */
}
```

Six components later there are four whites, three near-identical radii, and no way to change
the brand colour without a find-and-replace that also touches unrelated values.

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

## Related

- `knowledge/figma/01-figma-analysis.md`
- `knowledge/figma/19-design-handoff.md`
- `knowledge/tailwind/16-theme.md`
- `knowledge/css/20-css-variables.md`

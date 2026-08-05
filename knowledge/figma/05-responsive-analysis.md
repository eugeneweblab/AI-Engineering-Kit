---
id: figma/05-responsive-analysis
topic: figma
slug: responsive-analysis
title: "Responsive Design Analysis"
type: doc
order: 5
status: ready
tags: [figma, responsive-analysis]
related: [figma/02-layout-analysis, figma/04-auto-layout, css/17-responsive-design]
when_to_use: "Read before implementing responsive behavior from a Figma design across breakpoints and viewport sizes."
---
# Responsive Design Analysis

## Purpose

This document defines the standard process for analyzing responsive behavior from Figma before implementation.

Responsive development is not about making the desktop layout fit smaller screens.

It is about understanding how the design system adapts across different viewport sizes while preserving usability, readability, and visual hierarchy.

---

## Core Principle

Design for behavior, not breakpoints.

Breakpoints are implementation details.

Responsive behavior is the real specification.

---

## AI Mindset

Before writing any responsive code, answer the following questions:

- What changes between screen sizes?
- What stays exactly the same?
- Which components are reused?
- Which components change layout?
- Which elements disappear?
- Which elements become interactive in a different way?

Never guess responsive behavior if it can be inferred from the design.

---

## Responsive Analysis Workflow

Analyze every page using the following sequence:

```
Desktop
      ↓
Laptop
      ↓
Tablet
      ↓
Mobile
      ↓
Component Changes
      ↓
Content Changes
      ↓
Interaction Changes
      ↓
Implementation Plan
```

Always analyze from the largest layout to the smallest.

---

## Step 1 — Compare Layouts

Compare every available design.

Review:

- section order;
- number of columns;
- container width;
- spacing;
- typography;
- navigation;
- component hierarchy.

Document every structural difference.

---

## Step 2 — Analyze Containers

Determine how containers behave.

Review:

- maximum width;
- horizontal padding;
- vertical spacing;
- alignment;
- full-width sections;
- nested containers.

Container behavior should remain consistent throughout the project.

---

## Step 3 — Analyze Grid Changes

Review how grids adapt.

Examples:

Desktop

```
4 columns
```

Tablet

```
2 columns
```

Mobile

```
1 column
```

Grid transitions should be predictable.

---

## Step 4 — Analyze Component Behavior

Review every reusable component.

Examples:

Cards

Desktop

```
Horizontal layout
```

Mobile

```
Vertical layout
```

Navigation

Desktop

```
Horizontal menu
```

Mobile

```
Hamburger menu
```

Buttons

Desktop

```
Auto width
```

Mobile

```
Full width
```

---

## Step 5 — Analyze Typography

Review:

- heading sizes;
- body text;
- line height;
- spacing;
- text wrapping;
- readability.

Typography should scale intentionally.

Avoid arbitrary font-size changes.

---

## Step 6 — Analyze Images

Determine:

- aspect ratio;
- cropping behavior;
- scaling;
- visibility;
- lazy loading requirements.

Images should preserve their purpose rather than their exact dimensions.

---

## Step 7 — Analyze Spacing

Compare spacing between layouts.

Review:

- section spacing;
- component spacing;
- internal padding;
- margins;
- grid gaps.

Spacing should follow the same design scale across all breakpoints.

---

## Step 8 — Analyze Visibility

Review which elements:

- remain visible;
- become hidden;
- become collapsible;
- move into other components.

Do not hide important functionality without design justification.

---

## Step 9 — Analyze Interactions

Responsive behavior also affects interaction.

Review:

- menus;
- dropdowns;
- accordions;
- sliders;
- hover states;
- touch targets.

Touch interfaces require different interaction patterns than desktop interfaces.

---

## Step 10 — Plan Implementation

Before writing code define:

- responsive layout strategy;
- reusable components;
- breakpoint usage;
- CSS approach;
- accessibility considerations.

Implementation should follow a clear plan rather than evolve through trial and error.

---

## Mapping to CSS

Prefer fluid layouts.

Examples:

Use:

- Flexbox
- CSS Grid
- min()
- max()
- clamp()
- relative units

Avoid relying exclusively on fixed pixel values.

---

## Mapping to Tailwind

Prefer existing responsive utilities.

Examples:

```
sm:

md:

lg:

xl:

2xl:
```

Apply responsive classes only where layout behavior actually changes.

Avoid unnecessary breakpoint-specific styling.

---

## AI Execution Checklist

## Investigation

☐ Review every available breakpoint.

☐ Compare layouts.

☐ Compare typography.

☐ Compare spacing.

☐ Compare navigation.

☐ Compare component behavior.

---

## Planning

☐ Define layout transitions.

☐ Define responsive components.

☐ Define breakpoint strategy.

☐ Preserve design consistency.

---

## Verification

☐ Desktop matches Figma.

☐ Tablet matches Figma.

☐ Mobile matches Figma.

☐ Layout transitions are smooth.

☐ No unnecessary responsive rules exist.

☐ Accessibility remains intact.

---

## Common Mistakes

Avoid:

Treating mobile as a scaled desktop.

Using excessive media queries.

Creating different components for every breakpoint.

Hardcoding widths.

Ignoring touch interactions.

Ignoring typography scaling.

Adding breakpoint-specific fixes instead of improving the layout.

---

## Examples

**Good Example** — state which breakpoints exist and what changes between them

```text
Frames present in the file
  Desktop 1440   3-column grid, sidebar visible, gap 32
  Tablet   768   2-column grid, sidebar collapses to a top bar, gap 24
  Mobile   375   1 column, sidebar becomes a drawer, gap 16

Not in the file: anything between 376 and 767, and anything above 1440.
Decision needed: does the 3-column grid keep growing past 1440, or is the
container capped? Asked in the handoff thread; answered "cap at 1280".
```

```css
/* Fluid by default; breakpoints only where the layout genuinely changes. */
.grid {
	display: grid;
	gap: 1rem;                                   /* 375 */
	grid-template-columns: 1fr;
}

@media (width >= 48rem) {                        /* 768 */
	.grid {
		gap: 1.5rem;
		grid-template-columns: repeat(2, 1fr);
	}
}

@media (width >= 90rem) {                        /* 1440 */
	.grid {
		gap: 2rem;
		grid-template-columns: repeat(3, 1fr);
		max-width: 80rem;                        /* the answer from the handoff thread */
		margin-inline: auto;
	}
}
```

**Bad Example** — one frame implemented, the rest invented

```css
/* Built from the 1440 frame only. The two breakpoints below were guessed at
   implementation time, so they match nothing in the design and will be
   re-guessed differently by the next person. */
.grid {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 32px;
}

@media (max-width: 1024px) {         /* no 1024 frame exists */
	.grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 600px) {          /* no 600 frame exists either */
	.grid { grid-template-columns: 1fr; }
}
```

Guessing is sometimes unavoidable; doing it silently is not. Record the guess and ask, so the
answer lands in the file rather than in someone's memory.

---

## Completion Criteria

Responsive analysis is complete when:

- all layouts have been reviewed;
- structural changes are understood;
- reusable responsive patterns have been identified;
- breakpoint strategy is defined;
- implementation can begin without guessing responsive behavior.

---

## Summary

Responsive implementation should reproduce the behavior of the design system rather than individual layouts.

A well-planned responsive strategy produces cleaner code, fewer media queries, and a more consistent user experience across all devices.

## Related

- `knowledge/figma/02-layout-analysis.md`
- `knowledge/figma/04-auto-layout.md`
- `knowledge/css/17-responsive-design.md`

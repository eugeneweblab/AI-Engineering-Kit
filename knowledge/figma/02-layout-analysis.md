# Figma Layout Analysis

## Purpose

This document defines the standard process for analyzing layout structure in Figma before implementation.

The objective is to understand how the interface is built rather than how it looks.

A correct layout analysis dramatically reduces implementation mistakes, prevents unnecessary refactoring, and allows AI coding assistants to produce cleaner, more maintainable code.

---

# Core Principle

Never recreate pixels.

Recreate the layout system.

The implementation should mirror the design's structure rather than its appearance.

---

# Layout Analysis Workflow

Every page should be analyzed in the following order:

```
Page
    ↓
Sections
    ↓
Containers
    ↓
Grid
    ↓
Columns
    ↓
Components
    ↓
Children
    ↓
Content
```

Never start from individual elements.

Always work from the outside inward.

---

# Step 1 — Identify Top-Level Sections

Separate the page into logical blocks.

Examples:

- Header
- Hero
- Features
- Statistics
- Gallery
- Testimonials
- Pricing
- FAQ
- CTA
- Footer

Each section should become an independent layout block.

---

# Step 2 — Identify Containers

Determine whether sections share a common container width.

Review:

- maximum width;
- horizontal padding;
- vertical spacing;
- alignment;
- centered vs full width.

Containers should be reused throughout the project.

---

# Step 3 — Analyze Grid System

Determine whether the page uses:

- fixed grid;
- responsive grid;
- CSS Grid;
- flex layouts;
- asymmetric layouts.

Look for repeating column patterns before writing code.

---

# Step 4 — Analyze Auto Layout

Auto Layout should be treated as the primary source of truth.

Review:

- direction;
- spacing;
- padding;
- alignment;
- distribution;
- wrapping;
- resizing behavior.

Avoid manually recreating spacing values when Auto Layout already defines them.

---

# Step 5 — Identify Parent–Child Relationships

Understand hierarchy before implementation.

Example:

```
Hero

    Container

        Content

            Heading

            Description

            Buttons

        Illustration
```

Component hierarchy should closely match the Figma hierarchy.

---

# Step 6 — Analyze Spacing System

Look for consistent spacing increments.

Examples:

```
4

8

12

16

24

32

40

48

64

80
```

A repeating spacing scale usually indicates design tokens.

Avoid arbitrary values.

---

# Step 7 — Analyze Alignment

Review:

- left alignment;
- center alignment;
- baseline alignment;
- vertical alignment;
- justified layouts;
- nested alignment.

Alignment should remain consistent throughout the page.

---

# Step 8 — Analyze Constraints

Review resizing behavior.

Examples:

- fixed width;
- fill container;
- hug contents;
- proportional scaling;
- minimum width;
- maximum width.

Constraints often determine responsive implementation.

---

# Step 9 — Analyze Overflow

Identify elements that may overflow.

Examples:

- sliders;
- carousels;
- code blocks;
- tables;
- image galleries;
- long text.

Plan overflow behavior before implementation.

---

# Step 10 — Analyze Layer Complexity

Review nested structures.

Questions:

- Can wrappers be reduced?
- Can layouts be simplified?
- Can components be reused?
- Is nesting caused by design or editor convenience?

Avoid reproducing unnecessary wrapper elements from Figma.

---

# Mapping Figma to HTML

Prefer semantic structure.

Example:

```
Page
    ↓
main

Section
    ↓
section

Container
    ↓
div.container

Card List
    ↓
ul

Card
    ↓
li

Content
    ↓
article

Navigation
    ↓
nav

Actions
    ↓
button
```

Do not mirror Figma layer names directly.

Translate them into semantic HTML.

---

# Mapping Figma to CSS

Prefer layout primitives.

Examples:

Use Flexbox for:

- navigation;
- button groups;
- cards;
- toolbars;
- vertical layouts.

Use Grid for:

- galleries;
- dashboards;
- pricing tables;
- feature grids;
- masonry-like layouts where appropriate.

Avoid forcing every layout into a single technique.

---

# AI Execution Checklist

## Investigation

☐ Identify all page sections.

☐ Identify container widths.

☐ Analyze Auto Layout.

☐ Analyze spacing.

☐ Analyze constraints.

☐ Analyze hierarchy.

---

## Planning

☐ Define layout primitives.

☐ Define reusable containers.

☐ Define responsive behavior.

☐ Remove unnecessary wrappers.

---

## Verification

☐ HTML hierarchy matches design intent.

☐ Layout is semantic.

☐ Auto Layout behavior is preserved.

☐ Spacing follows the design system.

☐ Responsive structure is predictable.

---

# Common Mistakes

Avoid:

Building layouts from individual elements.

Ignoring Auto Layout.

Ignoring constraints.

Creating unnecessary wrapper elements.

Using absolute positioning unnecessarily.

Hardcoding spacing.

Ignoring semantic HTML.

Mirroring Figma layer names in code.

---

# Completion Criteria

A layout analysis is complete when:

- the page hierarchy is understood;
- containers are identified;
- Auto Layout behavior is documented;
- responsive constraints are understood;
- semantic HTML structure has been planned;
- implementation can begin without layout uncertainty.

---

# Summary

Professional frontend development starts by understanding the structure behind the design.

The best implementations recreate the layout system—not the pixels—resulting in cleaner HTML, simpler CSS, and significantly fewer revisions during development.
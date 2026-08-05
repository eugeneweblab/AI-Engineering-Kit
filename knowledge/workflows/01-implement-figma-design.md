---
id: workflows/01-implement-figma-design
topic: workflows
slug: implement-figma-design
title: "Workflow — Implement a Figma Design"
type: doc
order: 1
status: ready
tags: [workflows, implement-figma-design]
related: [figma/01-figma-analysis, figma/03-design-token-extraction, figma/06-component-detection, figma/20-implementation-definition-of-done, frontend/03-design-systems, react/13-component-composition, accessibility/03-semantic-html, testing/14-visual-regression, workflows/08-build-react-component, figma/19-design-handoff]
when_to_use: "Follow this workflow when implementing a Figma design into production code."
---
# Workflow — Implement a Figma Design

## Purpose

This workflow defines how an AI coding agent should transform a Figma design into production-ready code while minimizing implementation errors, unnecessary iterations, and visual inconsistencies.

The objective is not to copy pixels.

The objective is to faithfully implement the design system, layout, behavior, and user experience represented in Figma.

---

## Core Principle

Never start coding immediately after opening a Figma file.

A Figma design should first be analyzed as a complete system.

Only after the analysis is complete should implementation begin.

---

## Workflow Overview

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

## Step 1 — Analyze the Entire Design

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

**Relevant knowledge:** [`../figma/01-figma-analysis.md`](../figma/01-figma-analysis.md) for reading a file as a system, and [`../figma/02-layout-analysis.md`](../figma/02-layout-analysis.md) for decoding layout hierarchy and spacing rhythm.

---

## Step 2 — Identify the Design System

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

**Relevant knowledge:** extract these values with [`../figma/03-design-token-extraction.md`](../figma/03-design-token-extraction.md), then map them onto your project's token layer — [`../css/20-css-variables.md`](../css/20-css-variables.md) for custom properties, [`../tailwind/21-design-system.md`](../tailwind/21-design-system.md) for a Tailwind theme, and [`../frontend/03-design-systems.md`](../frontend/03-design-systems.md) for the broader system view.

---

## Step 3 — Split the Design Into Components

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

**Relevant knowledge:** [`../figma/06-component-detection.md`](../figma/06-component-detection.md) for spotting component boundaries and variants in the file, [`../frontend/02-component-driven-development.md`](../frontend/02-component-driven-development.md) for the decomposition mindset, and [`../react/13-component-composition.md`](../react/13-component-composition.md) for turning that tree into composable components.

---

## Step 4 — Compare With Existing Project

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

**Relevant knowledge:** use [`../react/22-folder-structure.md`](../react/22-folder-structure.md) to know where existing components live, and [`../frontend/03-design-systems.md`](../frontend/03-design-systems.md) to check whether a primitive already covers the design.

---

## Step 5 — Build an Implementation Plan

Before editing files determine:

Files to modify

Files to create

Existing components to reuse

Responsive strategy

Animation strategy

Accessibility requirements

Verification strategy

Implementation should follow a plan.

**Relevant knowledge:** the generic planning discipline lives in [`./03-create-new-feature.md`](./03-create-new-feature.md); the developer handoff notes you should reconcile against are covered in [`../figma/19-design-handoff.md`](../figma/19-design-handoff.md).

---

## Step 6 — Implement From Large to Small

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

**Relevant knowledge:** build layout scaffolding with [`../css/07-grid.md`](../css/07-grid.md) and [`../css/06-flexbox.md`](../css/06-flexbox.md) (Figma auto-layout maps almost directly to flex/grid — see [`../figma/04-auto-layout.md`](../figma/04-auto-layout.md)); build individual components using the process in [`./08-build-react-component.md`](./08-build-react-component.md).

---

## Step 7 — Preserve Design Consistency

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

**Relevant knowledge:** consistency comes from driving every value from tokens rather than magic numbers — [`../figma/03-design-token-extraction.md`](../figma/03-design-token-extraction.md), [`../css/20-css-variables.md`](../css/20-css-variables.md), and [`../tailwind/16-theme.md`](../tailwind/16-theme.md).

---

## Step 8 — Responsive Implementation

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

**Relevant knowledge:** read the breakpoints straight from the file with [`../figma/05-responsive-analysis.md`](../figma/05-responsive-analysis.md), then implement them with [`../css/17-responsive-design.md`](../css/17-responsive-design.md) / [`../css/18-media-queries.md`](../css/18-media-queries.md) or [`../tailwind/11-responsive-design.md`](../tailwind/11-responsive-design.md). Do not forget [`../accessibility/13-responsive-accessibility.md`](../accessibility/13-responsive-accessibility.md) — reflow and zoom are accessibility requirements, not just visual ones.

---

## Step 9 — Accessibility Review

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

**Relevant knowledge:** map each item to its source topic — [`../accessibility/03-semantic-html.md`](../accessibility/03-semantic-html.md) (landmarks, heading order), [`../accessibility/04-keyboard-navigation.md`](../accessibility/04-keyboard-navigation.md) and [`../accessibility/05-focus-management.md`](../accessibility/05-focus-management.md) (keyboard + visible focus), [`../accessibility/07-aria.md`](../accessibility/07-aria.md) (ARIA only when native HTML falls short), [`../accessibility/09-images.md`](../accessibility/09-images.md) (alt text), and [`../accessibility/10-color-and-contrast.md`](../accessibility/10-color-and-contrast.md) (contrast). Much of this can be caught before you write code — see [`../figma/16-accessibility-from-figma.md`](../figma/16-accessibility-from-figma.md).

---

## Step 10 — Visual Verification

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

**Relevant knowledge:** run a structured pass with [`../figma/10-design-qa.md`](../figma/10-design-qa.md), automate the pixel diff via [`../figma/15-screenshot-comparison.md`](../figma/15-screenshot-comparison.md) and [`../figma/13-visual-regression.md`](../figma/13-visual-regression.md) (tooling in [`../testing/14-visual-regression.md`](../testing/14-visual-regression.md)), and gate merge on [`../figma/20-implementation-definition-of-done.md`](../figma/20-implementation-definition-of-done.md).

---

## AI Execution Checklist

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

## Examples

**Good Example** — the design is read as a document before anything is built

```text
Before writing code
  Node        Checkout / Desktop 1440 (12:340) — confirmed with the designer
  Frames      1440 and 375 only; fluid between them (agreed, not guessed)
  Tokens      Surface/Card, Ink/Primary, Accent/Blue — already in tokens.css
  Components  Button/Primary exists in src/components/button.tsx — reuse it
  Missing     field error state, empty cart → asked; designer added both

While building
  - auto layout → flexbox, no absolute positioning
  - every colour and spacing value references a token
  - the submit control is a <button>, the heading an <h2>

Before opening the PR
  npm run verify            typecheck, lint, tests, build
  npx playwright test       visual diff under 1% against the reference
  axe                       zero violations in default and error states
```

**Bad Example** — build from the picture, reconcile later

```text
- opened the Figma link, screenshotted the desktop frame
- measured spacing off the screenshot; hardcoded 17px, 23px, 31px
- copied hex values into the component's CSS module
- invented a tablet breakpoint at 1024 because "it looked cramped"
- invented an error state because the form needed one
- opened the PR; the design review found nine differences, four of which were
  the invented states and two of which were the invented breakpoint
```

Nothing here is recoverable without redoing it: the values have no source, the invented states
were never designed, and the review has to re-derive intent that was available from the start.

---

## Common Mistakes

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

## AI Responsibilities

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

## Definition of Success

A successful implementation:

Matches the design intent.

Respects the existing project architecture.

Reuses existing components whenever possible.

Maintains visual consistency.

Works across supported screen sizes.

Remains maintainable.

Introduces minimal technical debt.

---

## Close Out — Run the Topic Checklists

Before declaring the work done, self-verify against the `98`/`99`/`100` checklists of every topic this implementation touched. At minimum:

- **Frontend/React** — [`../react/98-production-checklist.md`](../react/98-production-checklist.md), [`../react/99-ai-review-checklist.md`](../react/99-ai-review-checklist.md), [`../react/100-common-antipatterns.md`](../react/100-common-antipatterns.md), and [`../frontend/98-production-checklist.md`](../frontend/98-production-checklist.md).
- **CSS** — [`../css/98-production-checklist.md`](../css/98-production-checklist.md), [`../css/99-ai-review-checklist.md`](../css/99-ai-review-checklist.md), [`../css/100-common-antipatterns.md`](../css/100-common-antipatterns.md).
- **Accessibility** — [`../accessibility/98-production-checklist.md`](../accessibility/98-production-checklist.md), [`../accessibility/99-ai-review-checklist.md`](../accessibility/99-ai-review-checklist.md), [`../accessibility/100-common-antipatterns.md`](../accessibility/100-common-antipatterns.md).
- **Testing / visual regression** — [`../testing/98-production-checklist.md`](../testing/98-production-checklist.md), [`../testing/99-ai-review-checklist.md`](../testing/99-ai-review-checklist.md).

The implementation is not finished until it passes the checklists for the surfaces it changed.

---

## Summary

Figma is not a collection of pixels.

It is a specification of a design system.

AI coding agents should implement the design system rather than reproducing individual screens.

Understanding the complete design before writing code consistently produces higher-quality implementations with fewer revision cycles.

## Related


- `knowledge/figma/01-figma-analysis.md`
- `knowledge/figma/03-design-token-extraction.md`
- `knowledge/figma/06-component-detection.md`
- `knowledge/figma/20-implementation-definition-of-done.md`
- `knowledge/frontend/03-design-systems.md`
- `knowledge/react/13-component-composition.md`
- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/testing/14-visual-regression.md`
- `knowledge/workflows/08-build-react-component.md`
- `knowledge/figma/19-design-handoff.md`

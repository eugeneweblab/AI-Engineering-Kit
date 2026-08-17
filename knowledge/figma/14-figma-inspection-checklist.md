---
id: figma/14-figma-inspection-checklist
topic: figma
slug: figma-inspection-checklist
title: "Figma Inspection Checklist"
type: doc
order: 14
status: ready
tags: [figma, figma-inspection-checklist, FIGMA_FILE_KEY, FIGMA_TOKEN, ComparisonTable, PlanCard, Desktop, style]
related:
  - figma/01-figma-analysis
  - figma/03-design-token-extraction
  - figma/19-design-handoff
  - figma/05-responsive-analysis
  - figma/06-component-detection
  - figma/18-image-assets
  - figma/20-implementation-definition-of-done
  - workflows/01-implement-figma-design
  - accessibility/23-wcag
  - frontend/03-design-systems
when_to_use: "Read before implementing any new page or section, to complete the mandatory Figma inspection checklist first."
---
# Figma Inspection Checklist

## Purpose

This document defines the mandatory inspection checklist that must be completed before implementing any Figma design.

The objective is to fully understand the design before writing code, reducing implementation mistakes, unnecessary refactoring, and repeated design revisions.

This checklist should be completed for every new page, section, or significant redesign.

---

## Core Principle

Inspect first.

Implement second.

Every minute spent analyzing the design saves significantly more time during implementation and review.

---

## Inspection Workflow

Complete every phase before beginning development.

```
Project Overview
        ↓
Layout
        ↓
Components
        ↓
Typography
        ↓
Design Tokens
        ↓
Responsive Design
        ↓
Interactions
        ↓
Dynamic Content
        ↓
Assets
        ↓
Implementation Plan
```

---

## Phase 1 — Project Overview

Verify:

☐ Business purpose is understood.

☐ Primary user journey is clear.

☐ Scope of implementation is defined.

☐ Required pages are identified.

☐ Required sections are identified.

---

## Phase 2 — Layout

Verify:

☐ Overall page structure.

☐ Container widths.

☐ Grid system.

☐ Auto Layout usage.

☐ Alignment.

☐ Spacing.

☐ Nested layouts.

☐ Section hierarchy.

---

## Phase 3 — Components

Verify:

☐ Buttons.

☐ Cards.

☐ Forms.

☐ Navigation.

☐ Tables.

☐ Tabs.

☐ Accordions.

☐ Modals.

☐ Sliders.

☐ Badges.

☐ Icons.

☐ Existing reusable patterns.

---

## Phase 4 — Typography

Verify:

☐ Font families.

☐ Heading hierarchy.

☐ Font sizes.

☐ Font weights.

☐ Line heights.

☐ Letter spacing.

☐ Text alignment.

---

## Phase 5 — Design Tokens

Verify:

☐ Colors.

☐ Typography tokens.

☐ Spacing scale.

☐ Border radius.

☐ Shadows.

☐ Icon sizes.

☐ Breakpoints.

☐ Existing project tokens.

A value used once is a value; a value used repeatedly is a token. Read the published styles
from the file rather than sampling nodes by eye:

```bash
# Published color, text, effect, and grid styles in the file.
curl -s "https://api.figma.com/v1/files/$FIGMA_FILE_KEY/styles" \
  -H "X-Figma-Token: $FIGMA_TOKEN" | jq '.meta.styles[] | {name, style_type, node_id}'
```

```json
{ "name": "Surface/Card",     "style_type": "FILL", "node_id": "12:405" }
{ "name": "Heading/XL",       "style_type": "TEXT", "node_id": "12:410" }
{ "name": "Elevation/Card",   "style_type": "EFFECT", "node_id": "12:418" }
```

A `Surface/Card` style is already a named design decision — map it to the project's
`color-surface` token instead of inventing a new name. Figma Variables (`/v1/files/:key/
variables/local`) expose modes such as light/dark directly, but that endpoint requires an
Enterprise plan; when it is unavailable, published styles are the authoritative source.
See [Design Token Extraction](03-design-token-extraction.md).

---

## Phase 6 — Responsive Design

Verify:

☐ Desktop layout.

☐ Laptop layout.

☐ Tablet layout.

☐ Mobile layout.

☐ Grid changes.

☐ Navigation changes.

☐ Component changes.

☐ Typography scaling.

☐ Section spacing.

---

## Phase 7 — Interactions

Verify:

☐ Hover states.

☐ Focus states.

☐ Active states.

☐ Disabled states.

☐ Loading states.

☐ Error states.

☐ Success states.

☐ Animations.

☐ Transitions.

---

## Phase 8 — Dynamic Content

Identify:

☐ CMS content.

☐ API content.

☐ User-generated content.

☐ WooCommerce data.

☐ Images.

☐ Videos.

☐ Icons.

☐ Links.

☐ Forms.

Nothing that should be dynamic may be hardcoded.

---

## Phase 9 — Assets

Verify:

☐ Images.

☐ SVG icons.

☐ Illustrations.

☐ Videos.

☐ Logos.

☐ Fonts.

☐ Export requirements.

☐ Image quality.

☐ Responsive assets.

Export from the file rather than screenshotting the canvas — icons must ship as vectors, and
raster assets need explicit scales:

```bash
# Icons as SVG.
curl -s "https://api.figma.com/v1/images/$FIGMA_FILE_KEY?ids=5:12,5:13&format=svg" \
  -H "X-Figma-Token: $FIGMA_TOKEN" | jq -r '.images | to_entries[] | "\(.key) \(.value)"'

# Photography at 1x and 2x for a srcset.
curl -s "https://api.figma.com/v1/images/$FIGMA_FILE_KEY?ids=7:44&format=png&scale=2" \
  -H "X-Figma-Token: $FIGMA_TOKEN"
```

The endpoint returns temporary URLs — download the files in the same run rather than storing
the links. Record the intended usage next to each asset, because it determines the markup:

```json
{
  "assets": [
    { "node": "5:12", "name": "icon-check", "format": "svg", "usage": "inline, currentColor" },
    { "node": "7:44", "name": "hero-photo", "format": "webp", "scales": [1, 2],
      "intrinsic": { "width": 1440, "height": 720 }, "usage": "next/image, priority" },
    { "node": "9:02", "name": "logo-acme", "format": "svg", "usage": "img with alt=\"Acme\"" }
  ]
}
```

Intrinsic dimensions are not optional bookkeeping: without `width`/`height` in the markup the
image reserves no space and the page shifts as it loads. See
[Image Assets](18-image-assets.md) and [Performance — Images](../performance/11-images.md).

---

## Phase 10 — Existing Project Review

Before implementation search for:

☐ Existing components.

☐ Existing layouts.

☐ Existing utilities.

☐ Existing styles.

☐ Existing templates.

☐ Existing helper functions.

☐ Existing design tokens.

Reuse existing implementations whenever possible.

---

## Phase 11 — Architecture

Determine:

☐ Component hierarchy.

☐ Folder structure.

☐ Data flow.

☐ Styling strategy.

☐ State management.

☐ Responsive strategy.

☐ Accessibility strategy.

---

## Phase 12 — Implementation Plan

Before coding define:

☐ Files to modify.

☐ Components to create.

☐ Components to reuse.

☐ Potential risks.

☐ Testing strategy.

☐ Validation strategy.

No implementation should begin without a clear plan.

---

## Final Readiness Checklist

Before implementation confirm:

☐ The complete design has been reviewed.

☐ All reusable components have been identified.

☐ Existing project components have been reviewed.

☐ Responsive behavior is understood.

☐ Dynamic content has been identified.

☐ Design tokens have been extracted.

☐ Accessibility requirements are understood.

☐ Implementation plan is complete.

Keep the completed checklist with the work as a file, not as a mental note — a reviewer can
then see what was inspected and what was assumed:

```yaml
# design/inspection/pricing.yml
page: Pricing
figma:
  file: XXXXXXXXXXXXXXXXXXXXXX
  frames: { desktop: "2:10", tablet: "2:11", mobile: "2:12" }
  inspected: [layout, components, typography, tokens, responsive, interactions, assets]

components:
  reuse:  [Button, Badge, Accordion]
  create: [PlanCard, ComparisonTable]

tokens:
  reuse: [color-surface, spacing-md, spacing-xl, radius-lg, text-heading-xl]
  new:
    - name: shadow-plan-card
      reason: "No existing elevation token matches Elevation/Card in the file."

dynamic:
  plans: "Stripe API"
  testimonials: "CMS"
  logos: "CMS media"

assets:
  svg: [icon-check, icon-minus, logo-acme]
  raster: [hero-photo@1x, hero-photo@2x]

open_questions:
  - "ComparisonTable absent from the mobile frame — scroll horizontally or collapse into cards?"
  - "Focus state not specified for PlanCard — using the project default ring."

ready_to_implement: false   # flip to true only when open_questions is empty or answered
```

`ready_to_implement: false` with two open questions is a better outcome than a confident
`true` built on two guesses.

---

## Common Mistakes

Avoid:

Inspecting only the visible section.

Ignoring responsive layouts.

Ignoring existing project components.

Ignoring Auto Layout.

Ignoring interaction states.

Ignoring accessibility.

Starting implementation before planning.

---

## Examples

**Good Example** — the inspection is recorded as answers, not as ticks

```text
Inspection — Checkout / Desktop (node 12:340), 2026-08-04

Frames          1440 only. 768 and 375 absent.                     → ASK
Type styles     Heading/XL, Body/M — both named styles              → OK
Colour styles   Surface/Card, Ink/Primary, Accent/Blue              → OK
Raw fills       2 nodes use a fill with no style (12:91, 12:104)    → ASK
Spacing         all multiples of 8 except 12:88 (padding 17)        → ASK
Components      Button/Primary, Field/Text — component sets         → OK
States          hover and disabled present; focus NOT designed      → ASK
Empty states    cart-empty missing                                  → ASK
Images          hero is 3200×1800 PNG, 4.1 MB                       → export as WebP
Contrast        Accent/Blue on Surface/Card = 5.17:1                → OK for text ≥ 16px
```

Seven questions were produced before a line of code was written. Each one is cheaper to answer
now than to discover as a review comment later.

**Bad Example** — a checklist ticked without evidence

```text
[x] Frames checked
[x] Styles checked
[x] Spacing checked
[x] Components checked
[x] Accessibility checked
```

Nothing here can be verified or disagreed with. "Accessibility checked" does not say what was
measured, so the 17px padding, the missing focus state, and the absent mobile frame all pass
inspection and surface during implementation instead.

---

## Completion Criteria

Figma inspection is complete only when:

- the entire design has been reviewed;
- reusable patterns have been identified;
- responsive behavior is understood;
- implementation risks are documented;
- a complete implementation plan has been prepared.

---

## Related Knowledge

- [Figma Analysis](01-figma-analysis.md) — the reasoning process this checklist enforces.
- [Design Token Extraction](03-design-token-extraction.md) and [Component Detection](06-component-detection.md) — Phases 3 and 5 in depth.
- [Responsive Analysis](05-responsive-analysis.md) — Phase 6 in depth.
- [Image Assets](18-image-assets.md) — Phase 9 in depth.
- [Design Handoff](19-design-handoff.md) — what to request when the file leaves a phase unanswerable.
- [Implementation Definition of Done](20-implementation-definition-of-done.md) — the closing counterpart to this opening checklist.
- [Workflow — Implement a Figma Design](../workflows/01-implement-figma-design.md) — the workflow this checklist gates.

---

## Summary

Thorough inspection is the foundation of successful implementation.

A disciplined inspection process minimizes rework, improves consistency, and enables AI coding assistants to generate more accurate, maintainable, and production-ready solutions.
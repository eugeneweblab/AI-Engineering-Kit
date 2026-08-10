---
id: figma/01-figma-analysis
topic: figma
slug: figma-analysis
title: "Figma Analysis"
type: doc
order: 1
status: ready
tags: [figma, figma-analysis, FIGMA_TOKEN, FILE_KEY, PlanCard, Primary, Desktop, URL, fully, plan, implementation]
related: [figma/02-layout-analysis, figma/03-design-token-extraction, figma/06-component-detection, workflows/01-implement-figma-design]
  - figma/02-layout-analysis
  - figma/03-design-token-extraction
  - figma/05-responsive-analysis
  - figma/06-component-detection
  - figma/14-figma-inspection-checklist
  - figma/19-design-handoff
  - figma/20-implementation-definition-of-done
  - workflows/01-implement-figma-design
  - accessibility/03-semantic-html
  - frontend/03-design-systems
when_to_use: "Read before writing any code from a Figma design, to fully analyze the design and plan implementation first."
---
# Figma Analysis

## Purpose

This document defines the standard process for analyzing Figma designs before writing any code.

The objective is to ensure that engineers and AI coding assistants fully understand the design, identify reusable patterns, and plan the implementation before making changes to the codebase.

No code should be written until the design has been completely analyzed.

---

## Core Principle

Figma is a specification, not an image.

Every design should be interpreted as a collection of reusable components, layouts, spacing systems, and interaction patterns.

The goal is to understand the design rather than reproduce pixels.

### Reading the Specification Programmatically

A Figma file is queryable data, not only a picture. When the file key and a token are
available, read the node tree instead of estimating values from a screenshot:

```bash
# File key is the segment after /design/ or /file/ in the Figma URL.
# Node id comes from the "Copy link to selection" URL (?node-id=1-234 → "1:234").
curl -s "https://api.figma.com/v1/files/$FIGMA_FILE_KEY/nodes?ids=1:234" \
  -H "X-Figma-Token: $FIGMA_TOKEN" > node.json
```

The response carries the exact values the design was built from:

```json
{
  "nodes": {
    "1:234": {
      "document": {
        "id": "1:234",
        "name": "CardProduct",
        "type": "COMPONENT",
        "layoutMode": "VERTICAL",
        "itemSpacing": 16,
        "paddingTop": 24, "paddingRight": 24, "paddingBottom": 24, "paddingLeft": 24,
        "primaryAxisSizingMode": "AUTO",
        "counterAxisAlignItems": "MIN",
        "cornerRadius": 12,
        "absoluteBoundingBox": { "x": 0, "y": 0, "width": 320, "height": 412 },
        "fills": [
          { "type": "SOLID", "color": { "r": 1, "g": 1, "b": 1, "a": 1 } }
        ],
        "styles": { "fill": "S:8a1f...", "effect": "S:3c02..." },
        "children": [ /* ... */ ]
      }
    }
  }
}
```

Two details matter when reading this payload:

- Colors are floats in the `0..1` range, not `0..255` — convert with
  `Math.round(channel * 255)` before producing a hex value.
- A non-empty `styles` map means the node references a **published style**. That style, not
  the literal value, is the token — see
  [Design Token Extraction](03-design-token-extraction.md).

---

## Design Analysis Workflow

Every implementation should follow this sequence:

```
Understand the Page
        ↓
Identify Layout Structure
        ↓
Identify Reusable Components
        ↓
Identify Design Tokens
        ↓
Analyze Responsive Behavior
        ↓
Analyze Interactions
        ↓
Identify Dynamic Content
        ↓
Plan Implementation
        ↓
Begin Development
```

Skipping analysis usually results in unnecessary refactoring.

---

## Step 1 — Understand the Page

Before examining individual elements, determine:

- the business purpose of the page;
- the target audience;
- the primary user actions;
- the information hierarchy;
- conversion goals.

The layout should support the user journey.

---

## Step 2 — Identify Layout Structure

Identify the major sections.

Typical examples include:

- Header
- Hero
- Features
- Statistics
- Testimonials
- Pricing
- FAQ
- CTA
- Footer

Each section should be treated as an independent module.

---

## Step 3 — Identify Reusable Components

Search for repeated UI elements.

Examples:

- buttons;
- cards;
- badges;
- forms;
- navigation;
- tabs;
- accordions;
- modals;
- sliders;
- avatars.

A repeated element should usually become a reusable component.

Record the inventory as data before writing any component, so the props follow from the
observed variants instead of from the first instance you happen to implement:

```json
{
  "components": [
    {
      "name": "Button",
      "figmaNode": "1:88",
      "occurrences": 14,
      "variants": { "variant": ["primary", "secondary", "ghost"], "size": ["sm", "md"] },
      "states": ["default", "hover", "focus", "disabled", "loading"],
      "existsInCodebase": "src/components/ui/Button.tsx",
      "action": "reuse"
    },
    {
      "name": "ProductCard",
      "figmaNode": "1:234",
      "occurrences": 6,
      "variants": { "layout": ["grid", "list"] },
      "states": ["default", "hover", "out-of-stock"],
      "existsInCodebase": null,
      "action": "create"
    }
  ]
}
```

`occurrences` is the argument for extraction; `existsInCodebase` is the argument against
creating anything. A component that appears once and matches nothing existing is usually
markup inside a section, not a new abstraction — see
[Component Detection](06-component-detection.md).

---

## Step 4 — Identify Design Tokens

Document the design system before implementation.

Review:

- typography;
- font sizes;
- spacing;
- colors;
- border radius;
- shadows;
- icons;
- grid system;
- breakpoints.

Avoid hardcoding visual values.

---

## Step 5 — Analyze Alignment

Review:

- container widths;
- margins;
- paddings;
- gaps;
- vertical rhythm;
- alignment;
- whitespace.

Spacing should follow a consistent system rather than visual approximation.

---

## Step 6 — Analyze Responsive Behavior

Determine how the layout changes between:

- Desktop
- Laptop
- Tablet
- Mobile

Identify:

- stacked layouts;
- hidden elements;
- reordered sections;
- resized typography;
- responsive spacing.

Do not invent responsive behavior unless the design requires interpretation.

---

## Step 7 — Analyze States

Review every interactive element.

Examples:

- hover;
- focus;
- active;
- disabled;
- loading;
- error;
- success;
- empty state.

All visual states should be implemented.

---

## Step 8 — Identify Dynamic Content

Determine which elements are expected to change.

Examples:

- CMS content;
- API responses;
- user information;
- product data;
- blog posts;
- forms;
- galleries.

Dynamic content should never be hardcoded.

---

## Step 9 — Identify Existing Components

Before creating new UI, review the existing project.

Search for:

- buttons;
- typography;
- layouts;
- cards;
- forms;
- navigation;
- icons.

Reuse before creating.

---

## Step 10 — Plan the Implementation

Before writing code define:

- reusable components;
- page structure;
- data flow;
- responsive strategy;
- accessibility considerations;
- potential risks.

A written implementation plan reduces unnecessary iterations.

The analysis is only useful if it survives into implementation. Produce it as a single
artifact — this is the handoff between analysis and code:

```yaml
# design-analysis/pricing-page.yml
page: Pricing
figma:
  file: XXXXXXXXXXXXXXXXXXXXXX
  frames: { desktop: "2:10", tablet: "2:11", mobile: "2:12" }

sections:
  - name: Hero
    element: <header>
    heading: h1
    dynamic: [headline, subheadline]
  - name: PlanGrid
    element: <section>
    heading: h2
    components: [PlanCard]
    responsive: { desktop: "3 columns", tablet: "2 columns", mobile: "1 column, stacked" }
    dynamic: [plans]          # from CMS/API — never hardcoded
  - name: FAQ
    element: <section>
    components: [Accordion]
    states: [collapsed, expanded, focus-visible]

tokens:
  reuse: [color-surface, spacing-md, spacing-xl, radius-lg, text-heading-xl]
  new:   [shadow-plan-card]   # justify every entry here

components:
  reuse:  [Button, Badge, Accordion]
  create: [PlanCard]

risks:
  - "Mobile frame omits the comparison table — confirm intended behavior with design."
  - "Plan names come from Stripe; length is unbounded, so the card must wrap."
```

Every unresolved item belongs under `risks`. An assumption written down can be corrected by
a reviewer; an assumption silently coded in cannot.

---

## AI Execution Checklist

## Investigation

☐ Read the entire Figma page.

☐ Identify every section.

☐ Identify reusable components.

☐ Review the existing project.

☐ Identify dynamic content.

---

## Planning

☐ Define the component hierarchy.

☐ Define responsive behavior.

☐ Define reusable tokens.

☐ Identify dependencies.

---

## Verification

☐ Every section has been analyzed.

☐ Every repeated element has been identified.

☐ Existing components have been reused.

☐ Responsive behavior has been planned.

☐ Dynamic content has been identified.

---

## Common Mistakes

Avoid:

Starting implementation before reviewing the full design.

Treating the design as a static image.

Hardcoding spacing.

Ignoring existing UI components.

Creating duplicate components.

Ignoring responsive layouts.

Ignoring interaction states.

Ignoring dynamic content.

---

## Examples

**Good Example** — read the file, then state what it contains

```bash
# One request returns the node tree; depth keeps the payload reviewable.
curl -sS -H "X-Figma-Token: $FIGMA_TOKEN" \
  "https://api.figma.com/v1/files/$FILE_KEY?depth=3" > design.json

# Named styles are design decisions that already exist — reuse them, do not invent names.
curl -sS -H "X-Figma-Token: $FIGMA_TOKEN" \
  "https://api.figma.com/v1/files/$FILE_KEY/styles" | jq '.meta.styles[] | {name, style_type, node_id}'
```

```text
Analysis of Checkout / Desktop (node 12:340)

Layout      3 sections, vertical auto layout, gap 32, padding 48/24
Breakpoints only 1440 present; 768 and 375 are NOT in the file  ← ask before assuming
Components  Button/Primary (4 uses), Field/Text (6 uses), Card/Summary (1 use)
Styles      Surface/Card, Ink/Primary, Accent/Blue — all named, all reusable
Missing     empty cart state, field error state, loading state for "Place order"
Risks       "Place order" is 44×44 at 1440; below 44 on mobile it fails the touch target
```

Naming what is absent is the point of the analysis: the three missing states are the ones an
implementer would otherwise invent, and the missing breakpoints are the question to ask before
any code is written.

**Bad Example** — open the file and start building

```text
"Implemented the checkout page from the Figma design."
```

Nothing was recorded, so nobody can tell which node was used, whether the mobile layout was
guessed, or what the error state should look like. The first review comment is "this is not
what the design says", and the answer is unavailable because the design was never read as a
document — only glanced at.

---

## Completion Criteria

The design analysis is complete only when:

- the entire page has been reviewed;
- reusable components have been identified;
- layout hierarchy is understood;
- responsive behavior is documented;
- implementation can begin without uncertainty.

---

## Related Knowledge

Continue with the topic that matches the next step:

- [Layout Analysis](02-layout-analysis.md) and [Auto Layout](04-auto-layout.md) — translating frames into flex and grid.
- [Design Token Extraction](03-design-token-extraction.md) — turning repeated values into a token set.
- [Responsive Analysis](05-responsive-analysis.md) — deriving breakpoint behavior from multiple frames.
- [Component Detection](06-component-detection.md) — deciding what becomes a component.
- [Figma Inspection Checklist](14-figma-inspection-checklist.md) — verifying nothing in the file was missed.
- [Workflow — Implement a Figma Design](../workflows/01-implement-figma-design.md) — the end-to-end process this analysis feeds.
- [Accessibility — Semantic HTML](../accessibility/03-semantic-html.md) — the element choices implied by the visual hierarchy.

---

## Summary

Successful implementation begins with understanding the design rather than writing code.

A complete design analysis minimizes rework, improves consistency, and allows both engineers and AI assistants to produce predictable, maintainable implementations.
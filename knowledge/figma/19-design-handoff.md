---
id: figma/19-design-handoff
topic: figma
slug: design-handoff
title: "Design Handoff"
type: doc
order: 19
status: ready
tags: [figma, design-handoff]
related: [figma/03-design-token-extraction, figma/06-component-detection, figma/20-implementation-definition-of-done]
  - figma/14-figma-inspection-checklist
  - figma/01-figma-analysis
  - figma/03-design-token-extraction
  - figma/18-image-assets
  - figma/16-accessibility-from-figma
  - figma/20-implementation-definition-of-done
  - workflows/01-implement-figma-design
  - workflows/03-create-new-feature
  - frontend/03-design-systems
  - architecture/25-documentation
when_to_use: "Read when handing off a Figma design to engineering, to align designers, developers, and QA before implementation."
---
# Design Handoff

## Purpose

This document defines the standard process for handing off a Figma design to engineering.

The objective is to ensure that designers, developers, QA engineers, and AI coding assistants share the same understanding before implementation begins.

A successful handoff minimizes ambiguity, reduces implementation iterations, and improves delivery quality.

---

## Core Principle

A design handoff is a knowledge transfer process.

It is not simply sharing a Figma file.

Every implementation should begin only after the design has been fully understood.

---

## Handoff Workflow

Every handoff should follow this sequence.

```
Project Overview
        ↓
Business Requirements
        ↓
Design Review
        ↓
Technical Review
        ↓
Asset Review
        ↓
Responsive Review
        ↓
Accessibility Review
        ↓
Implementation Planning
        ↓
Approval
```

---

## Step 1 — Project Overview

Document:

- project name;
- feature name;
- implementation scope;
- stakeholders;
- delivery priorities.

Every participant should understand the business objective before discussing implementation details.

---

## Step 2 — Business Requirements

Clarify:

- target audience;
- primary user flow;
- business goals;
- expected outcomes;
- success criteria.

Engineering decisions should support business requirements.

---

## Step 3 — Design Review

Review the complete design.

Verify:

- page hierarchy;
- section order;
- reusable components;
- design system usage;
- typography;
- spacing;
- color system.

Implementation should never begin after reviewing only isolated sections.

---

## Step 4 — Responsive Review

Review every supported breakpoint.

Verify:

- desktop layout;
- laptop layout;
- tablet layout;
- mobile layout.

Discuss expected behavior when a breakpoint is not explicitly defined.

Avoid guessing responsive behavior.

Designs are drawn at a handful of widths; browsers render every width in between. Agree on the
breakpoint contract explicitly, in writing:

```markdown
| Section          | ≥1280 (desktop) | 1024–1279       | 768–1023 (tablet) | <768 (mobile)             |
|------------------|-----------------|-----------------|-------------------|---------------------------|
| Nav              | inline links    | inline links    | hamburger         | hamburger                 |
| PlanGrid         | 3 columns       | 3 columns       | 2 columns         | 1 column, stacked         |
| ComparisonTable  | full table      | full table      | horizontal scroll | horizontal scroll (**?**) |
| Hero image       | right, 50%      | right, 50%      | below copy        | below copy, 16:9 crop     |
| Section spacing  | spacing-3xl     | spacing-3xl     | spacing-2xl       | spacing-xl                |
```

Every cell marked **?** is an open question for the designer, not a decision for the developer.
Two questions worth asking on every handoff:

- What happens between the drawn frames — does the layout stretch, or does the container cap
  at a max-width and center?
- Which elements are hidden rather than reflowed on mobile? Hiding content changes what the
  page means, so it needs an explicit decision.

See [Responsive Analysis](05-responsive-analysis.md).

---

## Step 5 — Component Review

Identify:

- reusable components;
- shared layouts;
- repeated UI patterns;
- interactive components;
- complex components.

Determine whether existing project components can be reused.

Reuse is preferred over creating new implementations.

---

## Step 6 — Dynamic Content

Identify all content sources.

Examples:

- WordPress content;
- WooCommerce data;
- REST API;
- GraphQL;
- configuration values;
- user-generated content.

Nothing intended to be editable should be hardcoded.

---

## Step 7 — Asset Review

Verify:

- images;
- illustrations;
- icons;
- logos;
- videos;
- fonts.

Confirm:

- export formats;
- naming conventions;
- optimization strategy.

Missing assets should be identified before implementation.

Hand over a manifest, not a folder of exports. It states the format, the scales, and — most
importantly — the intrinsic dimensions the markup needs:

```json
{
  "naming": "kebab-case, purpose-first: hero-pricing.webp, icon-check.svg, logo-acme.svg",
  "assets": [
    {
      "name": "hero-pricing",
      "node": "7:44",
      "format": "webp",
      "scales": [1, 2],
      "intrinsic": { "width": 1440, "height": 720 },
      "usage": "above the fold — preload, priority, never lazy",
      "alt": "decorative"
    },
    {
      "name": "logo-acme",
      "node": "9:02",
      "format": "svg",
      "usage": "customer logo wall",
      "alt": "Acme"
    },
    {
      "name": "icon-check",
      "node": "5:12",
      "format": "svg",
      "usage": "inline, inherits currentColor — no fill baked into the file"
    }
  ],
  "fonts": [
    { "family": "Inter", "weights": [400, 600], "subsets": ["latin"], "license": "SIL OFL — self-hosted" }
  ]
}
```

Three items block implementation if missing, so confirm them at handoff rather than
mid-sprint: font licensing for self-hosting, alt text for every informative image, and
intrinsic dimensions (without them the page shifts as images load). See
[Image Assets](18-image-assets.md) and [Performance — Fonts](../performance/12-fonts.md).

---

## Step 8 — Accessibility Review

Verify:

- semantic structure;
- heading hierarchy;
- image requirements;
- keyboard navigation;
- form accessibility;
- focus behavior;
- color contrast.

Accessibility requirements should be documented before development.

---

## Step 9 — Technical Review

Determine:

- project architecture;
- reusable components;
- framework-specific requirements;
- CMS integration;
- styling strategy;
- performance considerations.

The implementation approach should be agreed before coding begins.

---

## Step 10 — Implementation Plan

Document:

- implementation order;
- files to modify;
- reusable components;
- expected risks;
- testing strategy;
- review process.

Implementation should follow a documented plan.

---

## AI Handoff Requirements

Before implementation, AI should identify:

- reusable project components;
- design tokens;
- dynamic content;
- responsive behavior;
- accessibility requirements;
- implementation risks.

AI should summarize this information before generating code.

---

## Handoff Deliverables

A complete handoff should include:

- approved Figma design;
- design system references;
- required assets;
- responsive layouts;
- interaction specifications;
- implementation notes;
- acceptance criteria.

Keep it as one document in the repository, next to the code it describes:

```markdown
# Handoff — Pricing Page

**Figma**: `figma.com/design/XXXX/Marketing?node-id=2-10`
**Frames**: desktop `2:10` · tablet `2:11` · mobile `2:12`
**Status**: design approved 2026-07-09 · handoff reviewed 2026-07-10
**Owners**: design @maria · engineering @dev · QA @sam

## Scope
In: pricing page, plan cards, comparison table, FAQ.
Out: checkout flow (separate ticket), account settings.

## Token Mapping
| Figma style      | Project token       | Value            |
|------------------|---------------------|------------------|
| Surface/Card     | `--color-surface`   | #FFFFFF          |
| Heading/XL       | `text-heading-xl`   | 40/48, 600       |
| Elevation/Card   | `--shadow-card`     | 0 1px 3px rgb(0 0 0 / .1) |
| Spacing/L        | `spacing-lg`        | 24px             |

New tokens requested: `--shadow-plan-card` (no existing elevation matches Elevation/Card).

## Components
Reuse: Button, Badge, Accordion.
Create: PlanCard (6 instances, variants grid|list), ComparisonTable.

## Content Sources
plans → Stripe API · testimonials → CMS · logos → CMS media · legal copy → static.

## Interaction Specification
- PlanCard hover: elevation card → card-hover, 150ms ease-out.
- FAQ: one item open at a time? **open question**
- CTA loading state: not designed — using the project's default spinner.

## Accessibility Requirements
- One h1; plan names are h3 inside cards.
- Focus ring: not in the file — using `--color-focus`, 2px, 2px offset.
- `#9CA3AF` caption fails AA (2.54:1) — **design to supply a darker token**.

## Acceptance Criteria
- [ ] Matches the three approved frames at 1440 / 768 / 390.
- [ ] No horizontal scrolling at any width from 320px up.
- [ ] Keyboard reaches every CTA; visible focus throughout.
- [ ] axe reports zero violations on wcag2a/wcag2aa.
- [ ] LCP image preloaded; no layout shift on load.
- [ ] Plan data renders from the API, including empty and error states.

## Open Questions
1. ComparisonTable on mobile — scroll or collapse to cards?
2. Caption color replacement for `#9CA3AF`?
3. Behavior between 1024 and 1280 — stretch or cap at max-width?
```

Acceptance criteria written as checkboxes are what turn a handoff into something QA can
verify. "Looks like the design" is not a criterion — see
[Implementation Definition of Done](20-implementation-definition-of-done.md).

---

## AI Execution Checklist

## Investigation

☐ Business requirements understood.

☐ Complete design reviewed.

☐ Components identified.

☐ Dynamic content identified.

☐ Assets reviewed.

☐ Responsive behavior reviewed.

☐ Accessibility reviewed.

---

## Planning

☐ Existing components identified.

☐ Architecture selected.

☐ Implementation plan created.

☐ Risks documented.

---

## Verification

☐ Handoff is complete.

☐ Missing information identified.

☐ Open questions documented.

☐ Implementation can begin confidently.

---

## Common Mistakes

Avoid:

Starting implementation before reviewing the complete design.

Ignoring business requirements.

Ignoring reusable project components.

Guessing responsive behavior.

Implementing missing assets.

Hardcoding editable content.

Skipping accessibility discussions.

Beginning development without an implementation plan.

---

## Examples

**Good Example** — a handoff that answers the questions before they are asked

```markdown
## Checkout — handoff

**Figma**   file KEY, page "Checkout", frame `Desktop 1440` (node `12:340`)
**Status**  final; changes after 2026-08-04 go through a new ticket

### Included
- Desktop 1440, Mobile 375
- States: default, loading, field error, empty cart
- Components: Button/Primary, Field/Text (both component sets)

### Not included — decided, not forgotten
- Tablet: fluid between 375 and 1440, no dedicated frame. Agreed with design.
- Focus states: use the project's existing focus ring token, not a designed one.

### Tokens
Colours and spacing come from the published library; no raw hex in this frame
except `12:91` and `12:104`, which are **defects** — use `Surface/Card`.

### Content
Copy is final. Longest product name to support: 64 characters (see `12:402`).

### Definition of done
See [Implementation Definition of Done](20-implementation-definition-of-done.md).
```

**Bad Example** — a link and a hope

```markdown
Design is ready: https://figma.com/file/KEY

Let me know if you have questions.
```

No node id, so the right frame has to be guessed among twelve. No statement of what is final.
No list of states, so the implementer discovers the missing error state halfway through. No
token guidance, so hex values get copied. Every one of these becomes a message thread that
blocks the work.

---

## Completion Criteria

A design handoff is complete when:

- business objectives are understood;
- implementation scope is clearly defined;
- reusable components have been identified;
- assets are available;
- responsive behavior has been reviewed;
- accessibility requirements have been documented;
- implementation risks have been discussed;
- all participants are ready to begin development.

---

## Related Knowledge

- [Figma Inspection Checklist](14-figma-inspection-checklist.md) — the engineering-side inspection that consumes this handoff.
- [Figma Analysis](01-figma-analysis.md) and [Design Token Extraction](03-design-token-extraction.md) — producing the analysis and token mapping above.
- [Accessibility from Figma](16-accessibility-from-figma.md) — the accessibility section in depth.
- [Image Assets](18-image-assets.md) — asset formats, scales, and naming.
- [Implementation Definition of Done](20-implementation-definition-of-done.md) — the closing counterpart to these acceptance criteria.
- [Workflow — Implement a Figma Design](../workflows/01-implement-figma-design.md) — what happens after handoff.
- [Architecture — Documentation](../architecture/25-documentation.md) — where this document lives and how it stays current.

---

## Summary

An effective design handoff creates a shared understanding between design and engineering.

A structured handoff process reduces ambiguity, prevents unnecessary revisions, and enables developers and AI coding assistants to implement designs efficiently and consistently.
---
id: figma/20-implementation-definition-of-done
topic: figma
slug: implementation-definition-of-done
title: "Implementation Definition of Done"
type: doc
order: 20
status: ready
tags: [figma, implementation-definition-of-done, ComparisonTable, PlanCard, "@maria", Card, passes, PlanGrid]
related: [figma/10-design-qa, figma/19-design-handoff, checklists/01-pre-launch]
  - figma/10-design-qa
  - figma/13-visual-regression
  - figma/15-screenshot-comparison
  - figma/16-accessibility-from-figma
  - figma/19-design-handoff
  - workflows/01-implement-figma-design
  - workflows/05-review-pull-request
  - testing/27-quality-gates
  - performance/23-performance-budget
  - performance/18-web-vitals
  - accessibility/98-production-checklist
  - engineering/02-code-review
when_to_use: "Read before marking a Figma implementation complete, to confirm it meets the mandatory Definition of Done."
---
# Implementation Definition of Done

## Purpose

This document defines the mandatory Definition of Done (DoD) for implementing Figma designs.

The objective is to establish a consistent completion standard for all frontend implementations, regardless of framework, CMS, or AI coding assistant.

An implementation is considered complete only when every requirement in this document has been satisfied.

---

## Core Principle

Code completion is not task completion.

A feature is complete only after implementation, verification, review, testing, and documentation have been finished.

A checklist that is only ever read gets ticked from memory. Make the mechanical half
executable, so the human half gets the attention it needs:

```json
// package.json
{
  "scripts": {
    "dod": "npm-run-all --continue-on-error dod:*",
    "dod:types": "tsc --noEmit",
    "dod:lint": "eslint . --max-warnings 0",
    "dod:a11y": "playwright test tests/a11y",
    "dod:visual": "playwright test tests/visual",
    "dod:budget": "lhci autorun"
  }
}
```

`--continue-on-error` matters: you want the full list of what fails in one run, not the first
failure and a blind spot behind it. What stays manual — design fidelity, whether the
abstraction is right, whether the empty state makes sense — is exactly what no script can
judge.

---

## Definition of Done Workflow

Every implementation must complete the following stages.

```
Requirements
        ↓
Implementation
        ↓
Self Review
        ↓
Design Verification
        ↓
Accessibility Review
        ↓
Responsive Review
        ↓
Performance Review
        ↓
Code Review
        ↓
Testing
        ↓
Ready for Production
```

No stage may be skipped.

---

## Stage 1 — Requirements

Verify:

☐ Requirements are fully understood.

☐ Business objectives are satisfied.

☐ Acceptance criteria are complete.

☐ Design has been reviewed.

☐ Open questions have been resolved.

Implementation should never begin with unresolved requirements.

---

## Stage 2 — Implementation

Verify:

☐ Existing components reused.

☐ Project architecture respected.

☐ Semantic HTML used.

☐ Dynamic content implemented correctly.

☐ Design system followed.

☐ No unnecessary code introduced.

---

## Stage 3 — Design Verification

Compare implementation with the approved Figma design.

Verify:

☐ Layout.

☐ Typography.

☐ Colors.

☐ Spacing.

☐ Components.

☐ Icons.

☐ Images.

☐ Responsive behavior.

No significant visual differences should remain.

---

## Stage 4 — Accessibility

Verify:

☐ Semantic HTML.

☐ Heading hierarchy.

☐ Image accessibility.

☐ Form accessibility.

☐ Keyboard navigation.

☐ Focus indicators.

☐ Color contrast.

Accessibility issues must be resolved before completion.

---

## Stage 5 — Responsive Verification

Review:

☐ Desktop.

☐ Laptop.

☐ Tablet.

☐ Mobile.

Verify:

☐ Layout.

☐ Navigation.

☐ Typography.

☐ Images.

☐ Forms.

☐ Interactive components.

Every supported breakpoint must be verified.

---

## Stage 6 — Performance

Verify:

☐ Images optimized.

☐ Assets minimized.

☐ Lazy loading applied where appropriate.

☐ Unused code removed.

☐ Duplicate code avoided.

☐ Performance remains acceptable.

Implementation quality includes runtime performance.

"Performance remains acceptable" is unverifiable until it carries numbers. Declare the budget,
then let CI enforce it:

```json
// lighthouserc.json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:3000/pricing"],
      "numberOfRuns": 3,
      "settings": { "preset": "desktop" }
    },
    "assert": {
      "assertions": {
        "categories:performance":   ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 1.0 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "cumulative-layout-shift":  ["error", { "maxNumericValue": 0.1 }],
        "total-byte-weight":        ["warn",  { "maxNumericValue": 1600000 }],
        "unused-css-rules":         ["warn",  { "maxLength": 0 }]
      }
    },
    "upload": { "target": "temporary-public-storage" }
  }
}
```

Two failures recur when implementing a design and are worth checking directly, since both
originate in the markup rather than the build:

- **CLS from images** — an `img` without `width`/`height` (or an aspect-ratio box) reserves no
  space, so everything below it jumps when it loads.
- **LCP from the hero** — the largest above-the-fold image must be eagerly loaded and
  preloaded; a lazy-loaded hero delays LCP by a full round trip.

See [Performance — Performance Budget](../performance/23-performance-budget.md) and
[Performance — Web Vitals](../performance/18-web-vitals.md).

---

## Stage 7 — Code Quality

Verify:

☐ Naming conventions followed.

☐ Consistent formatting.

☐ No dead code.

☐ No duplicated logic.

☐ Readable implementation.

☐ Maintainable architecture.

Code should be understandable without additional explanation.

---

## Stage 8 — Testing

Verify:

☐ Manual testing completed.

☐ Existing functionality unaffected.

☐ Interactive behavior verified.

☐ Error scenarios reviewed.

☐ Browser compatibility reviewed.

☐ Regression testing completed.

Testing confirms that implementation works as intended.

---

## Stage 9 — Documentation

Verify:

☐ Required documentation updated.

☐ Comments added only when necessary.

☐ New reusable components documented.

☐ Configuration changes documented.

Documentation should remain synchronized with implementation.

---

## Stage 10 — Final Review

Before marking the task complete, confirm:

☐ Requirements satisfied.

☐ Design accurately implemented.

☐ Accessibility verified.

☐ Responsive behavior verified.

☐ Performance acceptable.

☐ Testing completed.

☐ Documentation updated.

☐ Ready for production.

---

## AI Completion Report

Before finishing a task, AI should summarize:

## Work Completed

Describe:

- implemented sections;
- modified files;
- reused components;
- new components.

---

## Verification Summary

Confirm:

- design accuracy;
- responsive review;
- accessibility review;
- performance review;
- testing status.

---

## Known Limitations

Document any remaining issues.

Examples:

- pending backend API;
- missing design assets;
- blocked dependencies.

Do not hide known limitations.

Report against the acceptance criteria from the handoff, with evidence rather than assertion:

```markdown
## Completion Report — Pricing Page

**Branch**: `feat/pricing-page` · **Handoff**: `design/handoff/pricing.md`

### Work Completed
- Created `PlanCard` (`src/components/pricing/PlanCard.tsx`) — grid | list variants.
- Created `ComparisonTable` — horizontally scrollable region below 1024px.
- Reused `Button`, `Badge`, `Accordion` — no new UI primitives introduced.
- Plans render from the Stripe API through a server component; empty and error states included.

### Verification
| Criterion | Result | Evidence |
|---|---|---|
| Matches frames at 1440 / 768 / 390 | pass | `out/diff-*.png` — max 0.8%, text antialiasing only |
| No horizontal scroll from 320px | pass | `tests/visual/pages.spec.ts` |
| Keyboard reaches every CTA, focus visible | pass | manual, Safari + Chrome |
| axe wcag2a/wcag2aa clean | pass | `npm run dod:a11y` |
| LCP < 2.5s, CLS < 0.1 | pass | LCP 1.9s · CLS 0.02 (`lhci`) |
| Plan data from API incl. empty/error | pass | `PlanGrid.test.tsx` |

### Deviations From Design
- Focus ring not specified in the file — implemented with `--color-focus` (2px, 2px offset).
- Caption color `#9CA3AF` fails AA at 2.54:1; shipped with `#6B7280` (5.05:1) pending a
  design decision. Flagged to @maria.

### Known Limitations
- ComparisonTable scrolls horizontally on mobile; the collapse-to-cards alternative from
  open question #1 was not designed. Ticket PRICE-241.
- Annual/monthly toggle is out of scope for this ticket.
```

The Deviations section is the point of the report. An unreported deviation looks identical to
a defect at review time, and identical to an accepted decision six months later.

---

## AI Execution Checklist

## Investigation

☐ Requirements reviewed.

☐ Existing implementation reviewed.

☐ Reusable components identified.

---

## Verification

☐ Design matches Figma.

☐ Accessibility verified.

☐ Responsive verified.

☐ Performance reviewed.

☐ Code reviewed.

☐ Testing completed.

☐ Documentation updated.

---

## Common Mistakes

Avoid:

Considering coding the end of the task.

Skipping responsive testing.

Skipping accessibility review.

Ignoring existing reusable components.

Leaving TODO comments without explanation.

Ignoring performance regressions.

Marking incomplete work as finished.

---

## Examples

**Good Example** — observable criteria, each one checkable by someone else

```markdown
## Definition of done — Product Card (node 44:12)

- [ ] Every colour and spacing value references a token; no literal hex or px
      outside `tokens.css`.
- [ ] Layout uses flexbox/grid mapped from auto layout; no absolute positioning.
- [ ] Renders correctly at 375, 768, and 1440 with no horizontal scroll.
- [ ] Longest supported product name (64 chars) does not overflow or clip.
- [ ] Image declares width and height; CLS contribution is 0 in Lighthouse.
- [ ] Title is an `<h3>`; the action is a `<button>` with an accessible name.
- [ ] Keyboard: the action is reachable by Tab and has a visible focus ring.
- [ ] axe reports zero violations on the component in its default and hover states.
- [ ] Visual diff against `product-card.png` is under 1% at CI's container image.
- [ ] `npm run verify` passes (typecheck, lint, unit tests).
```

Each line can be answered yes or no by a reviewer who did not write the code, and most of them
are answered by a command rather than an opinion.

**Bad Example** — criteria that cannot fail

```markdown
- [ ] Matches the design
- [ ] Responsive
- [ ] Accessible
- [ ] Good performance
- [ ] Clean code
```

"Matches the design" has no tolerance, so a 4 px difference is arguable in both directions.
"Accessible" names no standard and no tool. "Clean code" is the reviewer's taste. A checklist
of these is ticked in full by work that fails every one of them.

---

## Completion Criteria

Implementation is complete only when:

- all functional requirements have been met;
- the design has been accurately reproduced;
- responsive behavior has been verified;
- accessibility requirements have been satisfied;
- performance remains acceptable;
- testing has been completed;
- documentation has been updated;
- the feature is ready for production deployment.

---

## Related Knowledge

- [Design QA](10-design-qa.md) — the review that produces the evidence for Stage 3.
- [Screenshot Comparison](15-screenshot-comparison.md) and [Visual Regression](13-visual-regression.md) — mechanized design verification.
- [Accessibility from Figma](16-accessibility-from-figma.md) — what Stage 4 checks and where those requirements came from.
- [Design Handoff](19-design-handoff.md) — the acceptance criteria this report answers.
- [Workflow — Implement a Figma Design](../workflows/01-implement-figma-design.md) and [Workflow — Review a Pull Request](../workflows/05-review-pull-request.md) — the surrounding process.
- [Testing — Quality Gates](../testing/27-quality-gates.md) — turning these stages into CI gates.
- [Accessibility — Production Checklist](../accessibility/98-production-checklist.md), [Frontend — Production Checklist](../frontend/98-production-checklist.md), and [Performance — Production Checklist](../performance/98-production-checklist.md) — the topic checklists to close with.

---

## Summary

A consistent Definition of Done creates predictable engineering quality.

By requiring implementation, verification, testing, documentation, and review, every completed feature reaches the same production-ready standard regardless of who—or what—implemented it.
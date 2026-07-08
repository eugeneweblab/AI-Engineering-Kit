---
id: frontend/29-design-review
topic: frontend
slug: design-review
title: "Design Review"
type: doc
order: 29
status: ready
tags: [frontend, design-review]
related: [frontend/03-design-systems, frontend/09-accessibility, frontend/10-responsive-design, frontend/28-ui-patterns, frontend/99-ai-review-checklist]
when_to_use: "Read before reviewing a UI change against its design, or before requesting review of your own visual work."
---
# Design Review

## Purpose

This document defines how to review a frontend change for visual and interaction quality:
fidelity to the design, use of the design system, accessibility, responsive behavior, and
handling of every state. It gives an agent a concrete rubric so review catches the issues
users will hit — not just whether the code compiles.

## Why It Matters

Code review focuses on logic; without a design review, visual and interaction defects
ship freely. These are exactly the defects users notice first: misaligned spacing, an
inaccessible contrast ratio, a layout that breaks at 375px, a missing empty state. They
also erode a product slowly — each un-reviewed one-off value pushes the UI a little
further from the system until nothing matches. Design review is where implementation is
held to the same standard as logic, and where design-system drift is caught before it
compounds. It is cheap at PR time and expensive to reconcile later.

## Core Principles

- **Review against the design system, not just the mock.** A change can match the Figma
  frame yet introduce a rogue color or spacing value. Check that it uses tokens and
  existing components before checking pixel fidelity.
- **All states, not the happy one.** Review loading, empty, error, long content, zero and
  huge values, and RTL — not just the populated success screen the designer drew.
- **Accessibility is part of design.** Contrast, focus order, keyboard operability, and
  target size are review items, not a separate later pass.
- **Responsive is a range, not three widths.** Verify behavior across the continuum and at
  real breakpoints, including the smallest supported viewport and content reflow.
- **Consistency beats local cleverness.** A control that behaves like the rest of the app
  is better than a novel one that is marginally nicer in isolation.

## Best Practices

- Compare against the design source at real density, checking spacing, type scale,
  alignment, and color — but flag *token* usage, not raw hex/px, as the primary criterion.
- Exercise the change with the keyboard only: tab order is logical, focus is always
  visible, `Escape`/`Enter` behave, and nothing is reachable only by mouse.
- Check contrast with a tool (WCAG AA: 4.5:1 body text, 3:1 large text and UI boundaries);
  don't eyeball it.
- Resize from the largest to the smallest supported viewport; watch for overflow, clipped
  text, broken grids, and touch targets under ~44px.
- Verify every state renders deliberately — a real empty state and error state, and long
  strings that don't overflow or truncate without an ellipsis.
- Check motion: respects `prefers-reduced-motion`, animations are purposeful and short,
  and nothing causes layout shift (CLS).
- Prefer the component catalog/Storybook as the review surface so states are reproducible
  and reviewers see the same thing.

## Examples

**Good Example** — token-based, accessible, review-ready

```tsx
// Uses design tokens → automatically consistent, and a reviewer can verify at a glance.
<button
  className="bg-primary text-on-primary px-4 py-2 rounded-md
             focus-visible:ring-2 focus-visible:ring-focus"   // visible focus state
>
  {/* Contrast of --primary/--on-primary is AA-checked in the design system. */}
  Save
</button>
// Empty state is designed, not an accident:
{items.length === 0 && <EmptyState message="No results" action={<ClearFilters />} />}
```

**Bad Example** — magic values, no focus, no empty state

```tsx
<button
  style={{ background: "#3b82f6", padding: "9px 15px" }}  // rogue hex + odd px: drifts from system
>
  Save
</button>
// No :focus-visible style → keyboard users can't see where they are.
// No empty branch → the list renders blank when there are no items, looking broken.
{items.map((i) => <Row key={i.id} item={i} />)}
```

## Common Mistakes

- Approving because it matches the mock, while it hardcodes colors/spacing off-system.
- Reviewing only the populated success screen; empty and error states never checked.
- Skipping keyboard and contrast checks and treating a11y as a separate future task.
- Testing at one desktop width and missing the mobile breakdown at 375px.
- Letting a bespoke control ship because it looks nice, fragmenting interaction patterns.
- Ignoring long/overflowing content and localized strings until a user files a bug.

## Production Tips

- Add visual regression testing (Chromatic, Playwright screenshots) so unintended visual
  changes surface automatically and review focuses on intent.
- Include an accessibility linter/axe run in CI so mechanical a11y issues never reach a
  human reviewer.
- Keep a short design-review checklist attached to the PR template so it happens every time.

## AI Review Checklist

- Does the change use design tokens and existing components rather than magic values?
- Are loading, empty, error, long-content, and RTL states all handled and reviewed?
- Is it fully keyboard-operable with a visible focus indicator throughout?
- Do text and UI elements meet WCAG AA contrast, verified by a tool?
- Does it hold up from the largest to the smallest supported viewport?
- Are touch targets adequately sized and motion respectful of `prefers-reduced-motion`?
- Is the interaction consistent with established app patterns rather than a novel one-off?

## Related

- `knowledge/frontend/03-design-systems.md`
- `knowledge/frontend/09-accessibility.md`
- `knowledge/frontend/10-responsive-design.md`
- `knowledge/frontend/28-ui-patterns.md`
- `knowledge/frontend/99-ai-review-checklist.md`

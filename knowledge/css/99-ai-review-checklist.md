---
id: css/99-ai-review-checklist
topic: css
slug: ai-review-checklist
title: "CSS AI Review Checklist"
type: doc
order: 99
status: ready
tags: [css, ai-review-checklist]
related: [css/03-specificity, css/30-engineering-principles, css/100-common-antipatterns, css/23-accessibility, css/22-performance]
when_to_use: "Read when reviewing a CSS diff or pull request before approving it."
---
# CSS AI Review Checklist

## Purpose

This checklist is what an agent runs against a CSS diff during review. Each item is a
concrete yes/no question answerable from the change itself. It is scoped to what a
reviewer can verify by reading the code, complementing the
[production checklist](98-production-checklist.md), which verifies the running result.

## Why It Matters

Most CSS damage is introduced quietly in review-sized diffs: one `!important`, one
over-specific selector, one hard-coded color. Individually they pass; collectively they
are how a stylesheet decays. A structured review catches these at the point where they
are cheapest to fix — before merge — and keeps the codebase's specificity, tokens, and
accessibility invariants intact.

## Specificity and Cascade

**Rules:** [Specificity](03-specificity.md) · [Selectors](02-selectors.md)

- [ ] Is the maximum specificity in the diff a single class (`0,1,0`), with any escalation justified in a comment?
- [ ] Is `!important` absent, or confined to a documented utility layer? See [specificity](03-specificity.md).
- [ ] Are new selectors component-scoped rather than descendant chains tied to page structure?
- [ ] Does the change rely on source order for the cascade rather than raising specificity to win?

## Tokens and Values

**Rules:** [Variables](20-css-variables.md) · [Architecture](21-architecture.md)

- [ ] Are colors, spacing, font sizes, and breakpoints referenced from custom properties, not literals?
- [ ] Are there any repeated magic numbers that should be a shared token?
- [ ] Do new custom properties follow the project's naming scheme and live at the right scope?

## Responsive and Layout

**Rules:** [Responsive Design](17-responsive-design.md) · [Grid](07-grid.md)

- [ ] Is the change mobile-first (base styles small, `min-width` to grow), not `max-width` overrides?
- [ ] Does it use Flexbox/Grid for layout rather than floats, absolute positioning, or fixed pixel math?
- [ ] Are logical properties used where RTL/localization is in scope?
- [ ] Does the layout tolerate long text, empty states, and missing media without breaking?

## Accessibility

**Rules:** [Accessibility](23-accessibility.md)

- [ ] Is a visible `:focus-visible` style present, and is `outline: none` never used without a replacement?
- [ ] Do new text/background pairings meet WCAG AA contrast? See [accessibility](23-accessibility.md).
- [ ] Is animation gated behind `prefers-reduced-motion`?
- [ ] Is meaning never conveyed by color alone?

## Performance

**Rules:** [Performance](22-performance.md)

- [ ] Do animations/transitions touch only `transform` and `opacity`? See [performance](22-performance.md).
- [ ] Is `will-change` scoped and removed after use, not left on globally?
- [ ] Does the diff avoid deeply nested or universal selectors that are costly to match?
- [ ] Does the change avoid adding render-blocking `@import` chains?

## Hygiene

**Rules:** [Methodologies](29-css-methodologies.md) · [Best Practices](28-best-practices.md)

- [ ] Does the diff delete the CSS it replaces, rather than only appending overrides?
- [ ] Is there no dead, commented-out, or duplicated CSS left behind?
- [ ] Does Stylelint pass without new disable comments?
- [ ] Are modern features guarded with `@supports` or a fallback where the browserslist requires it?

## AI Review Checklist

- Has every group above been walked, with specific line references for each failure found?
- Are the flagged issues concrete ("selector at line X is `0,3,1`, exceeds one class"), not vague?
- For anti-patterns spotted, is the fix from [common antipatterns](100-common-antipatterns.md) cited?
- Would approving this diff raise the codebase's specificity ceiling or token debt? If so, block it.

## Related

- `knowledge/css/03-specificity.md`
- `knowledge/css/30-engineering-principles.md`
- `knowledge/css/100-common-antipatterns.md`
- `knowledge/css/23-accessibility.md`
- `knowledge/css/22-performance.md`

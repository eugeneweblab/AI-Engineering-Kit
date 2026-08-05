---
id: accessibility/99-ai-review-checklist
topic: accessibility
slug: ai-review-checklist
title: "Accessibility AI Review Checklist"
type: doc
order: 99
status: ready
tags: [accessibility, ai-review-checklist, jsx-a11y, aria-disabled, aria-hidden, aria-live, aria-labelledby, tabindex]
related: [accessibility/07-aria, accessibility/03-semantic-html, accessibility/04-keyboard-navigation, accessibility/08-forms, accessibility/98-production-checklist]
when_to_use: "Read when reviewing a diff or PR that touches UI, to catch accessibility defects that automated scanners and happy-path tests miss."
---
# Accessibility AI Review Checklist

## Purpose

This checklist is for an agent reviewing UI code — a diff, a component, a pull request —
rather than a running build ([production-checklist](98-production-checklist.md) covers the
running build). Each item is a yes/no an agent can verify by reading the code and, where
noted, tabbing through the rendered result.

Prioritize the failures a scanner cannot see: missing keyboard support, wrong DOM order,
focus that never moves, and meaning carried only by color. These are the defects that ship
because the happy path renders fine.

## Element Choice and Semantics

**Rules:** [Semantic HTML](03-semantic-html.md) · [ARIA](07-aria.md)

- [ ] Is each interactive element a native control (`<button>`, `<a href>`, `<input>`),
      not a clickable `<div>`/`<span>`?
- [ ] Do `<a>` elements navigate and `<button>` elements act — never the reverse?
- [ ] Is heading level chosen by document structure, not by desired font size?
- [ ] Is ARIA absent where native HTML already conveys the role, and correct where used?
- [ ] Are `role`, `aria-*` states, and properties valid for the element and kept in sync
      with actual state?

## Accessible Names

**Rules:** [ARIA](07-aria.md) · [Forms](08-forms.md)

- [ ] Does every form control have an associated `<label>`, `aria-label`, or
      `aria-labelledby`?
- [ ] Do icon-only buttons/links have an accessible name, with the icon `aria-hidden`?
- [ ] Do informative images have meaningful `alt`, and decorative images `alt=""`?
- [ ] Is link/button text meaningful without surrounding context?

## Keyboard and Focus

**Rules:** [Keyboard Navigation](04-keyboard-navigation.md) · [Focus Management](05-focus-management.md)

- [ ] Can every new interactive element be reached and activated by keyboard?
- [ ] Are custom widgets handling the expected keys (Enter/Space to activate, arrows to
      move within composites)?
- [ ] Is focus moved into newly revealed content (dialog, menu) and restored on dismiss?
- [ ] Is the focus outline preserved, or replaced with an equally visible indicator — never
      just `outline: none`?
- [ ] Are there no positive `tabindex` values and no unintended keyboard traps?

## Dynamic Content and Feedback

**Rules:** [Live Regions](19-live-regions.md) · [Error Messages](18-error-messages.md)

- [ ] Are async status, errors, and toasts announced via an `aria-live` region or focus
      move, not shown silently?
- [ ] Are validation errors linked to their field via `aria-describedby` and expressed in
      text?
- [ ] Do disabled/loading states expose `aria-disabled`/`aria-busy` where appropriate?
- [ ] Does DOM order match the intended reading order after any reordering CSS?

## Perceivable Design

**Rules:** [Color and Contrast](10-color-and-contrast.md) · [Typography](11-typography.md)

- [ ] Do color choices in the diff meet contrast minimums (4.5:1 text, 3:1 large/UI)?
- [ ] Is any state (error, selected, required) shown by more than color alone?
- [ ] Is `prefers-reduced-motion` respected for newly added animation/transition?
- [ ] Do new layouts reflow without horizontal scroll at 320 px and survive 200% text zoom?

## Verification Signals

**Rules:** [Axe](21-axe.md) · [Testing](24-accessibility-testing.md)

- [ ] Are there tests or a lint rule (`jsx-a11y`/axe) covering the new component's a11y
      contract?
- [ ] Does the PR describe how it was checked by keyboard and screen reader?

## AI Review Checklist

- Did I read the code for name/role/state on every interactive element, not just scan it?
- Did I confirm keyboard operability rather than assuming the mouse path implies it?
- Did I flag any meaning-by-color and any focus flow that never moves?
- If a custom widget replaces a native one, did I demand the full keyboard/ARIA contract?

## Related

- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/accessibility/04-keyboard-navigation.md`
- `knowledge/accessibility/08-forms.md`
- `knowledge/accessibility/98-production-checklist.md`

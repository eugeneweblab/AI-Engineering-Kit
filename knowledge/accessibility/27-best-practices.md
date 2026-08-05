---
id: accessibility/27-best-practices
topic: accessibility
slug: best-practices
title: "Accessibility Best Practices"
type: doc
order: 27
status: ready
tags: [accessibility, best-practices]
related: [accessibility/03-semantic-html, accessibility/07-aria, accessibility/04-keyboard-navigation, accessibility/24-accessibility-testing, accessibility/100-common-antipatterns]
when_to_use: "Read before writing any user-facing markup or component so accessibility is built in rather than retrofitted."
---
# Accessibility Best Practices

## Purpose

This document distills the highest-leverage accessibility rules an engineer should apply
by default, on every component, without being asked. It is the short list that prevents
most defects before they exist — the counterpart to [remediation](25-remediation.md),
which cleans them up after. Where a rule needs depth, it links to the topic doc that owns it.

The through-line: accessibility is a property of *how you build*, not a feature you add.
Get the defaults right and conformance is mostly automatic.

## Why It Matters

The cheapest accessible code is the code you wrote accessibly the first time. A native
`<button>` costs nothing; the `<div>` you have to retrofit with `role`, `tabindex`, and
key handlers costs an afternoon now and a bug later. Most violations are not exotic — they
are the same handful of habits repeated: non-semantic elements, missing labels, low
contrast, keyboard traps. Fix the habits and the defect rate collapses.

Good defaults also compound. Every developer who reaches for the semantic component
inherits its accessibility for free, so the leverage of getting the base component right
is enormous — one correct `Modal` is accessible in every feature that uses it.

## Core Principles

- **Semantic HTML first.** The right native element gives you role, state, focus, and
  keyboard behavior for free. Reach for ARIA only when HTML has no element for the job.
  See [semantic HTML](03-semantic-html.md).
- **Everything works with a keyboard.** Every action reachable by mouse must be reachable
  and operable by keyboard, in a logical order. See [keyboard navigation](04-keyboard-navigation.md).
- **Name, role, value for every control.** Assistive tech announces what it can compute;
  an unlabeled control is a mystery to a screen-reader user.
- **Don't rely on a single sense.** Never convey meaning by color, shape, or position
  alone — pair it with text or an icon so it survives colorblindness and screen readers.
- **Match the platform.** Follow expected patterns (WAI-ARIA Authoring Practices) so
  users' existing muscle memory works instead of fighting a bespoke interaction.

## Best Practices

- Use `<button>` for actions and `<a href>` for navigation. Never a clickable `<div>` or
  `<span>` — you lose focus, keyboard, and role, then rebuild them badly.
- Give every input a programmatic **label** (`<label for>` or `aria-label`), every image
  meaningful `alt` (or `alt=""` if decorative), and every icon-only control an accessible name.
- Meet **contrast** minimums: 4.5:1 for normal text, 3:1 for large text and UI components.
  See [color and contrast](10-color-and-contrast.md).
- Manage **focus** on dynamic changes: move focus into an opened dialog, return it on close,
  and never leave it on a removed element. See [focus management](05-focus-management.md).
- Announce dynamic updates with **live regions** where appropriate, not silent DOM swaps.
  See [live regions](19-live-regions.md).
- Respect **user preferences**: honor `prefers-reduced-motion`, support 200% zoom and 320px
  reflow, and never disable browser zoom.
- Write clear, associated **error messages** and don't block submission on the field the
  user is still editing. See [error messages](18-error-messages.md).
- Bake accessibility into the **definition of done** and into shared components, so it is
  the default path, not an extra step.

## Examples

**Good Example** — semantic, labeled, keyboard-ready by construction

```html
<!-- Native button: focusable, Enter/Space works, role announced, disabled honored. -->
<button type="submit">Save changes</button>

<!-- Input tied to a visible label; the label is clickable and announced. -->
<label for="email">Email address</label>
<input id="email" type="email" name="email" autocomplete="email" />

<!-- Icon-only control still has an accessible name. -->
<button type="button" aria-label="Close dialog">✕</button>
```

**Bad Example** — non-semantic and unlabeled, accessible to no one

```html
<!-- Not focusable, ignores the keyboard, announces no role or name.
     A screen-reader user hears nothing; a keyboard user cannot reach it. -->
<div class="button" onclick="save()">Save changes</div>

<!-- Placeholder is not a label: it vanishes on input and many SRs skip it. -->
<input type="email" placeholder="Email address" />

<!-- Icon with no accessible name: announced as "button" or nothing at all. -->
<div class="icon-x" onclick="close()">✕</div>
```

## Common Mistakes

- Building clickable `<div>`/`<span>` controls instead of `<button>`/`<a>`.
- Using placeholder text as a substitute for a real, persistent label.
- Conveying state or meaning with color alone (e.g., red = error, with no text).
- Reaching for ARIA to describe an element that a native tag already describes correctly.
- Forgetting icon-only buttons need an accessible name.
- Swapping DOM content without moving focus or announcing the change.
- Treating accessibility as a QA-phase checklist rather than a build-time default.

## Production Tips

- Encode these defaults in your shared component library so every feature inherits them;
  the base `Button`, `Field`, and `Modal` are where accessibility scales.
- Add lint rules (e.g., `eslint-plugin-jsx-a11y`) to catch the common misuses in the editor,
  before review — the cheapest place to fix them.
- Put a one-line accessibility item in every PR template so authors self-check the flow they
  changed with a keyboard before requesting review.

## AI Review Checklist

- Are actions `<button>` and navigation `<a href>`, with **no** clickable `<div>`/`<span>`?
- Does every input have a real **label**, every meaningful image **alt**, every icon button a **name**?
- Is meaning ever conveyed by **color/shape alone** without a text equivalent?
- Is every mouse action **keyboard-operable** in a logical order?
- Is **focus** managed on dialogs and dynamic changes, and are updates **announced**?
- Do defaults live in **shared components and lint rules**, not in per-feature effort?
- Are `prefers-reduced-motion`, 200% zoom, and 320px reflow respected?

## Related

- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/04-keyboard-navigation.md`
- `knowledge/accessibility/24-accessibility-testing.md`
- `knowledge/accessibility/100-common-antipatterns.md`

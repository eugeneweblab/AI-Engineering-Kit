---
id: accessibility/30-engineering-principles
topic: accessibility
slug: engineering-principles
title: "Accessibility Engineering Principles"
type: doc
order: 30
status: ready
tags: [accessibility, engineering-principles]
related: [accessibility/03-semantic-html, accessibility/07-aria, accessibility/05-focus-management, accessibility/24-accessibility-testing, accessibility/27-best-practices]
when_to_use: "Read before building any UI component or feature, to internalize the engineering habits that make accessibility a default rather than a retrofit."
---
# Accessibility Engineering Principles

## Purpose

This document defines the engineering mindset that produces accessible software as a
side effect of doing normal work correctly. It is not a checklist of WCAG success
criteria (see [wcag](23-wcag.md) for that) — it is the set of habits an agent applies
while writing components, forms, and interactions so that accessibility does not have to
be bolted on later.

The goal is simple: build interfaces that everyone can perceive, operate, and understand
using whatever input and output device they rely on — keyboard, screen reader, switch,
voice, magnifier, or touch. Accessibility is a property of the code, not a phase of the
project.

## Why It Matters

Inaccessible UI silently excludes real users and is expensive to fix after the fact.
Unlike a functional bug, an accessibility defect usually does not throw, log, or fail a
happy-path test — the screen renders, the click handler fires, and sighted-mouse QA
passes. The failure only surfaces for the keyboard or screen-reader user who cannot
reach the control at all.

Retrofitting is costly because accessibility is structural: it lives in the choice of
element, the DOM order, the focus flow, and the semantics — decisions that are cheap at
authoring time and painful to unwind once a `<div>`-based widget has shipped and grown
dependents. Building it in from the first commit is the only economical path, and in most
jurisdictions ([legal-requirements](26-legal-requirements.md)) it is also a legal
obligation.

## Core Principles

- **Prefer the platform.** A native `<button>`, `<a href>`, `<input>`, `<select>`, or
  `<dialog>` ships with focus, keyboard, and screen-reader behavior for free. Reach for a
  custom widget only when no native element fits — the cost of the custom path is that you
  now own every keyboard and semantic detail yourself.
- **Semantics before styling.** Choose the element for what it *means*, then style it.
  Never choose a `<div>` because it is unstyled and then reintroduce meaning with ARIA.
- **The accessibility tree is an output you own.** Every component has a name, role, and
  state exposed to assistive tech. If you cannot state what they are, the component is not
  done.
- **Keyboard is the floor, not a feature.** Anything operable by mouse must be operable by
  keyboard, in a logical order, with a visible focus indicator. If you cannot Tab to it and
  activate it, it does not work.
- **Do not convey meaning by one channel alone.** Color, position, or shape must be paired
  with text or an accessible name, because a portion of users cannot perceive that channel.
- **Test with the tools users use.** Automated checks catch ~40% of issues; the rest
  require a keyboard and a screen reader. Both are part of "done".

## Best Practices

- Start every interactive element from a native control; add ARIA only to fill a genuine
  gap the platform cannot express. The first rule of ARIA is: don't use ARIA if HTML can
  do it. See [aria](07-aria.md).
- Give every control an accessible name at authoring time — visible `<label>`, `alt`,
  or `aria-label` — not as a later audit fix. An unnamed control is invisible to screen
  readers.
- Keep DOM order equal to reading order. Reorder visually with CSS (`order`, `grid`) only
  when the sequence still makes sense to a screen reader that follows the DOM.
- Manage focus deliberately on any dynamic change: move focus into opened dialogs, restore
  it on close, and announce async results via a live region ([live-regions](19-live-regions.md)).
- Meet contrast and target-size minimums as design constraints, not afterthoughts: 4.5:1
  for body text, 3:1 for large text and UI components, 24×24 CSS px minimum target.
- Respect user preferences: honor `prefers-reduced-motion`, `prefers-contrast`, and
  system font scaling. Never trap the user in your defaults.
- Add at least one automated a11y check (axe) to CI and one keyboard-only pass to the
  definition of done for every interactive feature.

## Examples

**Good Example** — native semantics, keyboard for free, named, styled after

```html
<!-- A real button: Enter/Space, focusability, and role=button come for free.
     Styling is applied on top of correct semantics, not instead of them. -->
<button type="button" class="icon-btn" onclick="toggleMenu()">
  <svg aria-hidden="true" focusable="false"><!-- decorative icon --></svg>
  <span>Menu</span> <!-- visible, accessible name; screen readers announce "Menu, button" -->
</button>
```

**Bad Example** — div dressed as a button, semantics and keyboard lost

```html
<!-- Not focusable, no role, no Enter/Space handling, no accessible name.
     A screen reader announces nothing; a keyboard user cannot reach it.
     Adding onclick does not make it a button — it makes it a trap. -->
<div class="icon-btn" onclick="toggleMenu()">
  <svg><!-- icon only, no text --></svg>
</div>
```

## Common Mistakes

- Building clickable `<div>`/`<span>` widgets instead of `<button>`/`<a>`, then patching
  with `role` and `tabindex` and still missing keyboard activation.
- Using ARIA to *fix* a wrong element choice rather than choosing the right element.
- Placing content in DOM order that contradicts the visual reading order.
- Removing the focus outline (`outline: none`) without replacing it with a visible
  indicator.
- Communicating state (required, error, selected) with color alone.
- Treating a passing automated scan as proof of accessibility while never using a keyboard
  or screen reader.
- Adding `aria-*` attributes that duplicate or contradict native semantics
  (e.g. `role="button"` on a `<button>`).

## Production Tips

- Wire accessibility linting (`eslint-plugin-jsx-a11y` or template equivalents) and an
  axe-core check into CI so regressions fail the build, not a later audit.
- Add a keyboard-only and a screen-reader smoke test to release criteria for any new
  interactive surface.
- Capture the intended name/role/state of custom widgets in the component's tests, so the
  contract is enforced, not just documented ([documentation](29-documentation.md)).
- Build a small library of vetted accessible primitives (menu, dialog, tabs) so teams
  reuse correct behavior instead of reinventing it per feature.

## AI Review Checklist

- Is every interactive element a native control, or a custom widget with a documented
  role, name, and full keyboard support?
- Does every control have an accessible name available to assistive technology?
- Can the entire feature be operated by keyboard alone, with a visible focus indicator?
- Does DOM order match the visual reading order?
- Is any information conveyed by color, shape, or position also conveyed by text?
- Is ARIA used only to fill gaps native HTML cannot, without contradicting native roles?
- Is there at least one automated a11y check and one keyboard/screen-reader pass?

## Related

- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/05-focus-management.md`
- `knowledge/accessibility/24-accessibility-testing.md`
- `knowledge/accessibility/27-best-practices.md`

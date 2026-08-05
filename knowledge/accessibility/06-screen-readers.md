---
id: accessibility/06-screen-readers
topic: accessibility
slug: screen-readers
title: "Screen Readers"
type: doc
order: 6
status: ready
tags: [accessibility, screen-readers, "display:none", aria-hidden, aria-label, "visibility:hidden", onclick, aria-labelledby]
related: [accessibility/03-semantic-html, accessibility/07-aria, accessibility/05-focus-management, accessibility/19-live-regions, accessibility/24-accessibility-testing]
when_to_use: "Read before building UI that must be usable without sight, or when debugging why a component is announced wrong."
---
# Screen Readers

## Purpose

This document explains how screen readers turn your DOM into speech and braille, and
how to build interfaces that announce correctly. It is written so an agent can predict
what a screen reader will say for a given markup and fix components that read wrong,
out of order, or not at all.

A screen reader (VoiceOver, NVDA, JAWS, TalkBack, Narrator) is not a "blind mode" bolted
onto the page — it consumes the **accessibility tree**, a parallel structure the browser
builds from your HTML, ARIA, and computed styles. If it is not in the accessibility tree,
it does not exist for these users. Your job is to make that tree correct.

## Why It Matters

Screen reader users navigate non-linearly: they jump by heading, landmark, link, and form
control, and they read one node at a time out of visual context. A layout that "looks fine"
can be unusable if the accessibility tree is empty, mislabeled, or misordered. Unlike a
visual bug, you will never see this in a screenshot — the page renders perfectly while a
whole class of users is locked out. Because the failure is invisible to sighted developers,
screen reader correctness must be verified deliberately, not assumed.

## Core Principles

- **The accessibility tree is the contract.** Every interactive element needs an accurate
  *role*, *name*, *state*, and *value*. Missing any of the four produces a confusing or
  silent control.
- **Semantics first, ARIA second.** A native `<button>` or `<nav>` carries role, state,
  focusability, and keyboard behavior for free. Prefer [semantic HTML](03-semantic-html.md);
  reach for [ARIA](07-aria.md) only to fill genuine gaps.
- **DOM order is reading order.** Screen readers follow source order, not visual position.
  CSS that reorders content (`order`, `flex-direction: row-reverse`, absolute positioning)
  desyncs speech from sight.
- **Announce changes explicitly.** Screen readers do not narrate DOM mutations. Dynamic
  updates need a [live region](19-live-regions.md) or a deliberate focus move.
- **Do not hide from one sense only, by accident.** `display:none` and `aria-hidden` remove
  content from the tree; `visibility:hidden` removes focusability. Know which you mean.

## Best Practices

- Give every control an accessible name via visible text, `<label>`, `aria-label`, or
  `aria-labelledby`. Icon-only buttons are the most common silent control.
- Use one `<h1>` and a logical heading hierarchy (no skipped levels) — heading navigation
  is the primary way users skim a page.
- Wrap regions in landmarks (`<main>`, `<nav>`, `<header>`, `<footer>`) so users can jump
  between them. Label repeated landmarks (`aria-label="Primary"`).
- Provide visually hidden text for context a sighted user infers from layout — e.g. a
  "Results" heading before a list, or "(opens in new tab)" on such links.
- Hide purely decorative content with `aria-hidden="true"`, and hide off-screen UI (closed
  menus, inactive tabs) so the tree matches what is actually available.
- Move focus to newly revealed content (dialogs, route changes) so the reader lands there;
  see [focus management](05-focus-management.md).
- Test with a real screen reader, not just automated tools — most naming and ordering bugs
  are inaudible to linters.

## Examples

**Good Example** — an icon button that announces its role, name, and state

```html
<!-- Native button = role "button" + focusable + Enter/Space handling for free.
     aria-label supplies the name a sighted user gets from the icon.
     aria-pressed exposes the toggle STATE, which the icon alone cannot convey. -->
<button type="button" aria-label="Add to favorites" aria-pressed="false">
  <svg aria-hidden="true" focusable="false"><!-- decorative heart --></svg>
</button>
<!-- A screen reader says: "Add to favorites, toggle button, not pressed". -->
```

**Bad Example** — a silent, roleless control

```html
<!-- No role: announced as plain text, not reachable by Tab.
     No accessible name: the SVG has no text, so the reader says nothing or "graphic".
     No state: the toggle's on/off status is invisible to the tree. -->
<div class="btn" onclick="toggleFav()">
  <svg><!-- heart --></svg>
</div>
<!-- A screen reader user cannot find this, name it, or know if it is on. -->
```

## Common Mistakes

- Icon-only buttons and links with no accessible name — the single most frequent defect.
- Building controls from `<div>`/`<span>` with `onclick`, so they have no role, no focus,
  and no keyboard support.
- Assuming a visual change (spinner appears, item added) is announced. It is not without a
  live region or focus move.
- Reordering content with CSS so speech order no longer matches visual order.
- Using `aria-hidden="true"` on a container that still holds a focusable element, creating a
  control that can be tabbed to but not announced.
- Relying on placeholder text as a label — placeholders are not reliably exposed as names.

## Production Tips

- Keep a short manual test script: Tab through the page, then navigate by heading and by
  landmark with one screen reader; confirm every control's name and state are spoken.
- Test at least one browser+reader pair per platform (VoiceOver/Safari, NVDA/Firefox);
  support for ARIA features varies between them.
- Add visually hidden helper text with a reusable `.sr-only` utility (clip, not
  `display:none`) rather than ad-hoc off-screen hacks.

## AI Review Checklist

- Does every interactive element expose a role, an accessible name, and its current state?
- Do icon-only buttons and links have `aria-label` or visually hidden text?
- Is the heading hierarchy single-`h1` and gap-free, with landmarks for major regions?
- Does DOM/source order match the intended reading order?
- Are dynamic updates announced via a live region or a deliberate focus move?
- Is decorative content `aria-hidden`, and is nothing focusable hidden from the tree?

## Related

- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/05-focus-management.md`
- `knowledge/accessibility/19-live-regions.md`
- `knowledge/accessibility/24-accessibility-testing.md`

---
id: html/11-accessibility
topic: html
slug: accessibility
title: "Accessibility"
type: doc
order: 11
status: ready
tags: [html, accessibility]
related: [html/02-semantic-html, html/08-forms, html/07-tables, html/05-images]
when_to_use: "Read before shipping any UI, and when reviewing markup for screen-reader or keyboard support."
---
# Accessibility

## Purpose

This document defines how to make HTML usable by everyone, including people who navigate
with a keyboard, a screen reader, voice control, or a switch device. It covers semantic
structure, focus management, accessible names, ARIA, and the contract between visible and
programmatic state. Accessibility is not a plugin or an audit at the end — it is a
property of the markup you write from the first line.

## Why It Matters

Roughly one in five people has a disability, and accessibility overlaps heavily with SEO,
keyboard power-users, and automated testing. It is also a legal requirement in many
jurisdictions (WCAG 2.2 AA is the common bar). But the deeper reason is that the platform
already does the work: a native `<button>` is focusable, keyboard-operable, and announced
correctly for free. Every time you replace it with a `<div>`, you take on the job of
re-implementing all of that — and teams almost always miss a piece. Accessible HTML is
usually *simpler* HTML.

## Core Principles

- **Semantics first, ARIA last.** Use the correct native element (`<button>`, `<a>`,
  `<nav>`, `<h1>`–`<h6>`); it carries role, state, and keyboard behaviour. Reach for ARIA
  only when no native element fits. The first rule of ARIA is *don't use ARIA*.
- **Everything interactive is keyboard-operable.** Every action must be reachable and
  usable with Tab/Shift-Tab, Enter/Space, and Escape — no mouse-only handlers.
- **Every control has an accessible name.** Buttons, links, inputs, and images need a
  name via text, `<label>`, `alt`, or `aria-label`. A nameless control is a dead end.
- **Never break the focus order or hide focus.** Keep DOM order logical, manage focus on
  dynamic changes, and never set `outline: none` without a visible replacement.
- **Don't rely on colour or shape alone.** Convey state (error, required, selected) with
  text or icons plus colour, and meet contrast ratios (4.5:1 for body text).

## Best Practices

- Use one `<h1>` per page and nest headings without skipping levels; screen-reader users
  navigate by heading structure.
- Provide a "skip to content" link as the first focusable element so keyboard users can
  bypass repeated nav.
- Use landmarks (`<header>`, `<nav>`, `<main>`, `<footer>`, `<aside>`) — a single `<main>`
  per page — so users can jump between regions.
- Match `aria-*` state to reality: `aria-expanded`, `aria-checked`, `aria-selected`, and
  `aria-current` must update as the UI changes; a stale ARIA attribute is worse than none.
- Use `aria-live` regions (`polite`/`assertive`) to announce async updates (toasts,
  validation, results) that appear without a focus change.
- Give icon-only buttons an `aria-label`; hide purely decorative images/icons with
  `alt=""` or `aria-hidden="true"`.
- Ensure hit targets are at least 24x24 CSS px (WCAG 2.2) and focus indicators are clearly
  visible in both light and dark themes.

## Examples

**Good Example** — native semantics, real name, visible focus

```html
<!-- Native button: focusable, Enter/Space work, announced as "button".
     aria-expanded reflects real state and updates on toggle. -->
<button type="button" aria-expanded="false" aria-controls="menu">
  Menu
</button>
<ul id="menu" hidden>…</ul>

<!-- Icon-only control still has an accessible name -->
<button type="button" aria-label="Close dialog">
  <svg aria-hidden="true">…</svg> <!-- decorative icon hidden from AT -->
</button>
```

**Bad Example** — div "button", no name, no keyboard support

```html
<!-- A div is not focusable and has no role: keyboard and screen-reader
     users cannot operate it. The icon has no text alternative, so the
     control is announced as nothing. Focus is also removed globally. -->
<div class="btn" onclick="toggle()">
  <img src="/icons/gear.svg"> <!-- no alt: unnamed -->
</div>
<style>:focus { outline: none; }</style> <!-- hides focus for everyone -->
```

## Common Mistakes

- Building interactive controls from `<div>`/`<span>` instead of `<button>`/`<a>`.
- Removing focus outlines (`outline: none`) with no visible replacement.
- Icon-only buttons and meaningful images with no accessible name.
- Adding `role`/`aria-*` to fake semantics a native element already provides, or leaving
  ARIA state stale after the UI changes.
- Conveying meaning with colour alone (red = error) with no text cue.
- Skipping heading levels or using multiple `<h1>`s / multiple `<main>`s.
- Positive `tabindex` values that scramble the natural focus order.

## Production Tips

- Add automated checks (axe, Lighthouse) to CI to catch names, contrast, and roles — but
  treat them as a floor; they find ~30-40% of issues.
- Test the real thing: navigate the whole flow with the keyboard only, then with a screen
  reader (VoiceOver, NVDA).
- Respect user preferences: `prefers-reduced-motion`, `prefers-contrast`, and forced-colors
  mode.
- Manage focus on route changes and modal open/close — move focus into the dialog, trap
  it, and restore it on close.

## AI Review Checklist

- Are all interactive elements native controls (or correctly role-ed) and keyboard-operable?
- Does every control, input, and meaningful image have an accessible name?
- Is a visible focus indicator preserved everywhere (no bare `outline: none`)?
- Do `aria-*` states reflect and update with the actual UI state?
- Is there one `<h1>`, logical heading order, one `<main>`, and landmark regions?
- Is state conveyed with more than colour, and does text meet contrast ratios?
- Are dynamic updates announced via `aria-live`, and is focus managed on navigation/modals?

## Related

- `knowledge/html/02-semantic-html.md`
- `knowledge/html/05-images.md`
- `knowledge/html/07-tables.md`
- `knowledge/html/08-forms.md`

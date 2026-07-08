---
id: html/28-common-patterns
topic: html
slug: common-patterns
title: "Common Patterns"
type: doc
order: 28
status: ready
tags: [html, common-patterns]
related: [html/02-semantic-html, html/08-forms, html/11-accessibility, html/21-best-practices, html/23-progressive-enhancement]
when_to_use: "Read before hand-building a common UI widget (nav, accordion, tabs, modal, card) in HTML."
---
# Common Patterns

## Purpose

This document is a reference for the HTML structures behind everyday UI widgets:
navigation, accordions, tabs, modals, cards, breadcrumbs, and skip links. Each has a
*correct* markup shape — usually built on a native element plus the right ARIA — that is
accessible and robust, and a tempting `<div>`-soup shortcut that is not. The goal is to
reach for the established, accessible pattern instead of reinventing one that breaks with
a keyboard or a screen reader.

## Why It Matters

These widgets appear on nearly every page, so a flawed pattern multiplies across the
whole product. The failures are the kind automated tests miss and real users hit: a menu
that traps keyboard focus, an accordion a screen reader announces as plain text, a modal
that lets you tab into the page behind it. The correct patterns are well-known and cost
no more markup than the broken ones — the only thing standing between them is knowing
which element and which ARIA attributes the pattern requires.

## Core Principles

- **Start from the native element.** `<nav>`, `<details>`, `<dialog>`, `<button>`, and
  `<a>` carry semantics and keyboard behavior you would otherwise have to rebuild.
- **A control that navigates is a link; a control that acts is a button.** `<a href>`
  for going somewhere, `<button>` for doing something — never a clickable `<div>`.
- **State lives in ARIA and is kept in sync.** `aria-expanded`, `aria-selected`,
  `aria-current`, and `aria-controls` must reflect the actual visual state at all times.
- **Manage focus deliberately.** Modals trap and restore focus; menus and tabs support
  arrow-key roving; skip links move focus to the main content.
- **Follow the WAI-ARIA Authoring Practices pattern** for composite widgets (tabs, menus,
  comboboxes) rather than improvising the keyboard model.

## Best Practices

- Wrap primary navigation in `<nav aria-label="Primary">` and mark the current page with
  `aria-current="page"`; multiple `<nav>`s each need a distinct label.
- Build simple accordions from `<details>`/`<summary>` — they are keyboard- and
  screen-reader-accessible with zero JavaScript.
- Build modals on `<dialog>` with `showModal()`; save the trigger element and restore
  focus to it on close.
- Give tabs `role="tablist"` / `role="tab"` / `role="tabpanel"`, wire `aria-selected` and
  `aria-controls`, and implement arrow-key roving tabindex.
- Make card patterns keyboard-reachable: the whole card should not be a nested pile of
  links; use one primary `<a>` and stretch it, or a single actionable element.
- Provide a visually-hidden "Skip to main content" link as the first focusable element,
  targeting `<main id="main">`.
- Never remove focus outlines without replacing them with a visible focus style.

## Examples

**Good Example** — accessible accordion and current-page nav

```html
<nav aria-label="Primary">
  <ul>
    <!-- aria-current tells assistive tech which link is the active page -->
    <li><a href="/docs" aria-current="page">Docs</a></li>
    <li><a href="/api">API</a></li>
  </ul>
</nav>

<!-- <details>/<summary>: native disclosure, keyboard + SR accessible, no JS -->
<details>
  <summary>Shipping &amp; returns</summary>
  <p>Ships in 2 business days. Returns accepted within 30 days.</p>
</details>
```

**Bad Example** — div-soup disclosure with no semantics or keyboard support

```html
<!-- a <div> nav with no landmark: screen readers can't jump to navigation -->
<div class="nav">
  <!-- clickable div: not focusable, not operable by keyboard, no role -->
  <div class="link active" onclick="go('/docs')">Docs</div>
  <div class="link" onclick="go('/api')">API</div>
</div>

<!-- fake accordion: state lives only in a CSS class, invisible to assistive tech -->
<div class="accordion" onclick="this.classList.toggle('open')">
  Shipping &amp; returns
  <div class="panel">Ships in 2 business days.</div>
</div>
```

## Common Mistakes

- Using clickable `<div>`/`<span>` for interactive controls, breaking focus and keyboard
  operation.
- Omitting or desyncing ARIA state (`aria-expanded`, `aria-selected`, `aria-current`).
- Building modals that don't trap focus or don't restore it to the trigger on close.
- Reinventing tabs/menus without the WAI-ARIA keyboard model (arrow keys, `Home`/`End`).
- Multiple `<nav>` regions with no `aria-label`, so they are indistinguishable.
- Removing `:focus` outlines for aesthetics with no visible replacement.

## Production Tips

- Adopt a vetted headless component library or the ARIA APG reference implementations for
  composite widgets rather than authoring the keyboard logic from scratch.
- Add automated accessibility checks (axe, Lighthouse) to CI to catch missing roles and
  labels, and back them with manual keyboard-only testing.
- Keep a small internal catalog of your approved patterns so the same accordion/modal
  markup is reused instead of re-derived per feature.

## AI Review Checklist

- Is each interactive control a `<button>` or `<a>`, never a clickable `<div>`?
- Do navigation regions use `<nav>` with labels and `aria-current` on the active link?
- Are accordions/disclosures built on `<details>` or given full ARIA disclosure state?
- Do modals use `<dialog>`/`showModal()` and trap + restore focus?
- Do tabs/menus follow the WAI-ARIA keyboard model with synced ARIA state?
- Is there a skip link, and are focus outlines visible?

## Related

- `knowledge/html/02-semantic-html.md`
- `knowledge/html/08-forms.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/21-best-practices.md`
- `knowledge/html/23-progressive-enhancement.md`

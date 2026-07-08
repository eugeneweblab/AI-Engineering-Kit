---
id: accessibility/02-pour-principles
topic: accessibility
slug: pour-principles
title: "POUR Principles"
type: doc
order: 2
status: ready
tags: [accessibility, pour-principles]
related: [accessibility/01-accessibility-fundamentals, accessibility/03-semantic-html, accessibility/04-keyboard-navigation, accessibility/10-color-and-contrast, accessibility/23-wcag]
when_to_use: "Read when you need to categorize an accessibility issue or reason about which WCAG requirement a change must satisfy."
---
# POUR Principles

## Purpose

WCAG organizes every success criterion under four principles: content must be
**Perceivable**, **Operable**, **Understandable**, and **Robust** — POUR. This document
explains each pillar concretely so an agent can classify any barrier and reason about the
fix, instead of memorizing a flat list of 80+ criteria. POUR is the "why" behind the
specific rules in the sibling docs.

## Why It Matters

Individual WCAG criteria feel arbitrary until you see the pillar they serve. "Contrast
4.5:1" is a *Perceivable* rule; "focus visible" is *Operable*; "clear error text" is
*Understandable*; "valid, semantic markup" is *Robust*. Once you can name the pillar a
problem lives in, you can predict the fix and spot whole classes of missing coverage
(e.g. "we handled Perceivable with alt text but never checked Operable — is it
keyboard-usable?"). POUR turns a checklist into a reasoning tool.

## Core Principles

- **Perceivable** — users must be able to *sense* the content through some available
  channel. Provide text alternatives for non-text content, captions and transcripts for
  media, sufficient [color contrast](10-color-and-contrast.md), and don't rely on color
  alone to convey meaning. If information exists only as an image or only as a color, some
  users cannot receive it.
- **Operable** — users must be able to *drive* the interface with whatever input they
  have. Everything works from the [keyboard](04-keyboard-navigation.md); no keyboard
  traps; enough time to complete tasks; no content that flashes more than three times per
  second (seizure risk); clear ways to navigate and find things.
- **Understandable** — content and operation must be *predictable and clear*. Readable
  language, consistent navigation, components that behave the same everywhere, and input
  help that prevents and explains errors. See [error messages](18-error-messages.md).
- **Robust** — content must be *parseable by current and future user agents and assistive
  tech*. Valid markup, correct roles/names/states, and standard patterns so screen
  readers interpret it reliably. This is why [semantic HTML](03-semantic-html.md) matters.

## Best Practices

- When triaging a bug, name its pillar first — it tells you which criteria and which
  sibling doc apply.
- Cover all four pillars for every feature; a form can be Perceivable (labeled) yet fail
  Operable (mouse-only submit) or Understandable (cryptic errors).
- Map each pillar to a verification method: Perceivable and Robust are partly automatable
  (contrast, valid roles); Operable and Understandable need manual keyboard and
  screen-reader testing.
- Target **WCAG 2.2 AA** across all four pillars, not just the easy ones.

## Examples

**Good Example** — one status message that satisfies all four pillars

```html
<!-- Perceivable: text + icon, not color alone.  Operable: it's static text,
     nothing to operate, and it doesn't steal focus.  Understandable: says what
     to do next.  Robust: role="alert" is a standard, announced live region. -->
<p role="alert" class="error">
  <svg aria-hidden="true">…</svg>
  Card declined. Check the number and try again.
</p>
```

**Bad Example** — color-only signal that fails Perceivable and Robust

```html
<!-- Perceivable FAIL: meaning is carried by red alone — invisible to colorblind
     users and to anyone not looking.  Robust FAIL: a styled <span> has no role,
     so a screen reader never announces the change. Nothing tells the user why. -->
<span style="color: red">•</span> <input class="card-number" />
```

## Common Mistakes

- Conveying state with color only (red = error, green = valid) — a Perceivable failure
  for colorblind users. Add text, an icon, or a pattern.
- Nailing Perceivable (alt text, contrast) but forgetting Operable — a beautiful,
  labeled widget that a keyboard cannot reach.
- Cryptic or field-detached error text ("Invalid input") — an Understandable failure.
- Custom widgets with no roles/states — a Robust failure; the markup validates but
  assistive tech cannot interpret it.

## AI Review Checklist

- **Perceivable:** Are there text alternatives, captions/transcripts, sufficient contrast,
  and no color-only meaning?
- **Operable:** Is everything keyboard-operable with no traps, adequate time, and visible
  focus?
- **Understandable:** Is language clear, navigation consistent, and are errors explained
  and preventable?
- **Robust:** Is the markup valid with correct roles, names, and states for assistive
  tech?
- Have all four pillars been considered for this change, not just the obvious one?

## Related

- `knowledge/accessibility/01-accessibility-fundamentals.md`
- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/accessibility/04-keyboard-navigation.md`
- `knowledge/accessibility/10-color-and-contrast.md`
- `knowledge/accessibility/23-wcag.md`

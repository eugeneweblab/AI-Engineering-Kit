---
id: divi/12-accessibility
topic: divi
slug: accessibility
title: "Divi Accessibility"
type: doc
order: 12
status: ready
tags: [divi, accessibility, aria-label, prefers-reduced-motion, outline, onclick]
related: [divi/03-modules, divi/09-custom-css, divi/11-responsive-design, divi/29-review, divi/99-ai-review-checklist]
when_to_use: "Read before shipping any Divi page or custom module that users navigate, read, or fill in."
---
# Divi Accessibility

## Purpose

This document defines how to make a **Divi** site usable by people relying on
keyboards, screen readers, and assistive technology, and how to keep the builder's
convenience features from silently breaking that. It targets WCAG 2.2 AA — the level
most contracts, ADA/Section 508, and the European Accessibility Act (in force June 2025)
expect. An agent should be able to build or review a Divi layout against it without
guessing.

Divi generates most markup for you, which is a trap: the defaults are *acceptable*, not
*compliant*. Icon-only buttons, split headings, animated modules, and color choices in
the Design tab all produce inaccessible output unless you correct them deliberately.

## Why It Matters

Accessibility is a legal and revenue surface, not a nicety. Inaccessible sites are the
subject of thousands of US ADA lawsuits per year, and the failures are cheap to introduce
in a visual builder: one designer picks a light-gray-on-white heading, one module ships an
icon with no label, and a screen-reader user hits a wall. Because Divi hides the raw HTML,
these defects are invisible in the Visual Builder — the page looks perfect while being
unusable for a slice of every audience. The cost of fixing after launch (re-theming, legal
response) dwarfs the cost of getting it right during the build.

## Core Principles

- **Semantics over appearance.** Use the module setting that yields the correct element
  (heading level, button, list), not the one that merely looks right. A styled `<div>` is
  not a heading.
- **Every interactive element is reachable and operable by keyboard.** If you cannot Tab
  to it and activate it with Enter/Space, it is broken — no matter how it looks with a mouse.
- **Contrast is measured, not eyeballed.** Text must meet 4.5:1 (3:1 for large text); UI
  components and focus indicators 3:1. Verify with a tool, not intuition.
- **Non-text content has a text alternative.** Images, icon buttons, and background-image
  content need `alt` or an accessible name, or must be marked decorative.
- **Motion is optional.** Respect `prefers-reduced-motion`; never rely on animation or
  color alone to convey meaning.

## Best Practices

- Set exactly one `<h1>` per page (usually the Theme Builder title/heading) and use the
  module's **Heading Level** dropdown to keep h2–h4 in order — never skip a level to get a
  font size. Style size with CSS, not by choosing the wrong tag.
- Give every Image and icon its **Alt Text** in the module; mark purely decorative images
  with empty alt (`alt=""`) via the Advanced tab so screen readers skip them.
- Never ship an icon-only Button or Blurb link. Add visible text, or an accessible name via
  `aria-label` in the module's Advanced → Attributes, so its purpose is announced.
- Check color contrast for every text/background pair in the Design tab against WCAG AA
  before saving a global preset. Fix it in the preset so it propagates.
- Keep a visible focus outline. Divi and many child themes strip `outline` — if you add
  custom CSS, never set `outline: none` without a replacement `:focus-visible` style.
- Label every Contact Form / form field with a real `<label>` (Divi's field Title), not
  placeholder-only text. Placeholders disappear on input and are not reliable labels.
- Set the page/site language (`<html lang>`) and, for the Menu module, ensure the toggle
  button announces its expanded/collapsed state.
- Provide a "skip to content" link and test the full page with the keyboard only.

## Examples

**Good Example** — accessible icon button in a custom or Code module

```html
<!-- Accessible name announced to screen readers; SVG hidden from the a11y tree
     because the label already conveys meaning. Focus style is preserved. -->
<button type="button" class="et_pb_button" aria-label="Close menu">
  <svg aria-hidden="true" focusable="false" width="24" height="24">…</svg>
</button>
```

**Bad Example** — icon-only control with no name and suppressed focus

```html
<!-- Screen reader announces "button" with no purpose; keyboard users can't
     see where focus is because the outline was removed globally. -->
<div class="icon-btn" onclick="closeMenu()">
  <i class="et-pb-icon"></i>   <!-- no text, no aria-label, not focusable via div -->
</div>
<style>*:focus { outline: none; }</style>  <!-- removes the only focus cue -->
```

## Common Mistakes

- Choosing a heading level for its font size, producing skipped or duplicate levels.
- Icon-only buttons and links with no `alt`/`aria-label`, announced as bare "button"/"link".
- Low-contrast text from Design-tab color picks (light gray on white is the classic).
- Placeholder text used as the only field label in Contact Form modules.
- `outline: none` in custom CSS with no `:focus-visible` replacement, erasing focus cues.
- Auto-playing sliders/animations with no reduced-motion handling or pause control.
- Using a `<div>`/`<span>` with an `onclick` instead of a real `<button>` (not focusable).

## Production Tips

- Run an automated audit (axe DevTools or Lighthouse) on every template, but treat it as a
  floor: it catches ~30–40% of issues. Follow with a manual keyboard and screen-reader pass.
- Bake contrast-safe colors and visible focus styles into global presets and the Theme
  Builder so new pages inherit compliance instead of re-earning it.
- Add reduced-motion CSS once, site-wide:
  `@media (prefers-reduced-motion: reduce){ *{ animation: none !important; transition: none !important; } }`.

## AI Review Checklist

- Is there exactly one `<h1>`, with heading levels in order and never skipped for size?
- Does every image have meaningful `alt`, and are decorative images `alt=""`?
- Does every interactive element have an accessible name and keyboard operability?
- Do all text/background and focus-indicator pairs meet WCAG AA contrast?
- Is a visible focus style preserved (no bare `outline: none`)?
- Are form fields associated with real `<label>`s, not placeholders?
- Is `prefers-reduced-motion` respected for sliders and animations?

## Related

- `knowledge/divi/03-modules.md`
- `knowledge/divi/09-custom-css.md`
- `knowledge/divi/11-responsive-design.md`
- `knowledge/divi/29-review.md`
- `knowledge/divi/99-ai-review-checklist.md`

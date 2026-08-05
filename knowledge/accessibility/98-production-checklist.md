---
id: accessibility/98-production-checklist
topic: accessibility
slug: production-checklist
title: "Accessibility Production Checklist"
type: doc
order: 98
status: ready
tags: [accessibility, production-checklist]
related: [accessibility/23-wcag, accessibility/24-accessibility-testing, accessibility/20-testing-tools, accessibility/26-legal-requirements, accessibility/30-engineering-principles]
when_to_use: "Read before shipping any user-facing UI to production, as the final gate that the feature is usable by keyboard, screen reader, and low-vision users."
---
# Accessibility Production Checklist

## Purpose

This is the pre-release gate for accessibility. Every item is a verifiable yes/no an
agent or reviewer can confirm against the running build. The target is WCAG 2.2 Level AA
([wcag](23-wcag.md)) plus the operational hygiene that keeps a shipped feature accessible
over time. If any box is unchecked, the feature is not ready.

Do not treat a green automated scan as sufficient — automation covers roughly 40% of
criteria. The keyboard and screen-reader sections below are where real defects hide.

## Structure and Semantics

**Rules:** [Semantic HTML](03-semantic-html.md) · [ARIA](07-aria.md)

- [ ] Every interactive element is a native control (`<button>`, `<a href>`, `<input>`…)
      or a custom widget with the correct `role`, name, and state.
- [ ] The page has exactly one `<h1>`, and headings descend without skipping levels.
- [ ] Landmarks (`<header>`, `<nav>`, `<main>`, `<footer>`) wrap the page; there is one
      `<main>`.
- [ ] Lists use `<ul>`/`<ol>`/`<li>`; data grids use `<table>` with `<th scope>`, not
      layout `<div>`s.
- [ ] The document has a `lang` attribute and a descriptive, unique `<title>`.
- [ ] ARIA is used only where native HTML cannot express the semantics, and never
      contradicts the element's native role.

## Keyboard and Focus

**Rules:** [Keyboard Navigation](04-keyboard-navigation.md) · [Focus Management](05-focus-management.md)

- [ ] Every interactive element is reachable and operable with keyboard alone
      (Tab, Shift+Tab, Enter, Space, arrows as appropriate).
- [ ] Tab order follows the visual/reading order; no positive `tabindex` values.
- [ ] A visible focus indicator is present on every focusable element (contrast ≥ 3:1).
- [ ] Opening a dialog moves focus into it; closing restores focus to the trigger.
- [ ] Focus is trapped inside modal dialogs and nowhere else; there are no keyboard traps.
- [ ] A "skip to main content" link is the first focusable element.

## Names, Text Alternatives, and Language

**Rules:** [ARIA](07-aria.md) · [Images](09-images.md)

- [ ] Every form control has a programmatically associated `<label>` (or `aria-label`).
- [ ] Every informative image has meaningful `alt`; decorative images have `alt=""` or
      `aria-hidden="true"`.
- [ ] Icon-only buttons and links have an accessible name.
- [ ] Link text is meaningful out of context (no bare "click here" / "read more").

## Visual and Perceivable

**Rules:** [Color and Contrast](10-color-and-contrast.md) · [Typography](11-typography.md)

- [ ] Body text meets 4.5:1 contrast; large text and UI components meet 3:1.
- [ ] No information is conveyed by color, shape, or position alone.
- [ ] Layout reflows without horizontal scrolling at 320 CSS px width and 400% zoom.
- [ ] The UI remains usable when text is scaled to 200% via browser/OS settings.
- [ ] Interactive targets are at least 24×24 CSS px (or have adequate spacing).

## Forms, Errors, and Feedback

**Rules:** [Forms](08-forms.md) · [Error Messages](18-error-messages.md)

- [ ] Required fields and constraints are indicated in text, not color alone.
- [ ] Validation errors are announced (live region or focus move) and tied to their field
      via `aria-describedby`.
- [ ] Success/async status is announced via an appropriate `aria-live` region.
- [ ] Related inputs (radios, checkboxes) are grouped with `<fieldset>`/`<legend>`.

## Motion and Media

**Rules:** [Motion And Animation](14-motion-and-animation.md) · [Media](15-media.md)

- [ ] Non-essential animation is disabled or reduced under `prefers-reduced-motion`.
- [ ] No content flashes more than three times per second.
- [ ] Auto-playing or moving content can be paused, stopped, or hidden.
- [ ] Pre-recorded video has captions; audio-only content has a transcript.

## Verification and Process

**Rules:** [Testing Tools](20-testing-tools.md) · [Testing](24-accessibility-testing.md)

- [ ] An automated scan (axe) runs in CI and passes with no new violations.
- [ ] A keyboard-only walkthrough of the primary flows has been completed.
- [ ] A screen-reader pass (VoiceOver, NVDA, or JAWS) confirms names, roles, and states.
- [ ] Zoom/reflow tested at 400% and 320 px width.
- [ ] Known limitations and their remediation timeline are documented, not left silent.

## AI Review Checklist

- Did the review actually exercise the keyboard and a screen reader, not just run a scanner?
- Are all six perceivable/operable groups above satisfied, or are gaps explicitly tracked?
- Would a low-vision user at 400% zoom and a keyboard-only user each complete the core task?
- Is every unchecked item either fixed or filed with an owner and date?

## Related

- `knowledge/accessibility/23-wcag.md`
- `knowledge/accessibility/24-accessibility-testing.md`
- `knowledge/accessibility/20-testing-tools.md`
- `knowledge/accessibility/26-legal-requirements.md`
- `knowledge/accessibility/30-engineering-principles.md`

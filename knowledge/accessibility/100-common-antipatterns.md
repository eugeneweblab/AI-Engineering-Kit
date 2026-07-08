---
id: accessibility/100-common-antipatterns
topic: accessibility
slug: common-antipatterns
title: "Common Antipatterns"
type: doc
order: 100
status: ready
tags: [accessibility, common-antipatterns]
related: [accessibility/03-semantic-html, accessibility/07-aria, accessibility/05-focus-management, accessibility/10-color-and-contrast, accessibility/99-ai-review-checklist]
when_to_use: "Read when writing or reviewing UI, to recognize the recurring accessibility mistakes and apply their fixes before they ship."
---
# Common Antipatterns

## Purpose

This document catalogs the accessibility mistakes that appear most often in real code.
Each entry states the anti-pattern, why it is wrong (the concrete user it breaks), and the
fix. They are ordered roughly by frequency and impact. Use it as a lookup while authoring
or reviewing; the [ai-review-checklist](99-ai-review-checklist.md) turns these into pass/fail
gates.

## The `<div>` Button

- **Anti-pattern:** `<div onclick="...">` or `<span onclick="...">` styled to look like a
  control.
- **Why it is wrong:** A `<div>` has no role, is not focusable, and does not respond to
  Enter/Space. Screen-reader users hear nothing actionable; keyboard users cannot reach or
  activate it. Adding `onclick` handles only the mouse.
- **The fix:** Use `<button type="button">`. If a native element is truly impossible, add
  `role="button"`, `tabindex="0"`, and keydown handling for Enter and Space — but prefer
  the native control, which gives all of that for free.

## ARIA as a Band-Aid

- **Anti-pattern:** Reaching for `role`/`aria-*` to make a wrong element behave, e.g.
  `<div role="button" aria-pressed="true">`.
- **Why it is wrong:** ARIA changes what assistive tech *announces* but adds no behavior —
  no focus, no keyboard, no click. It papers over the semantics while the interaction is
  still broken, and mismatched ARIA is worse than none.
- **The fix:** First rule of ARIA — don't use ARIA if HTML can do the job. Choose the
  correct native element; use ARIA only for patterns HTML lacks ([aria](07-aria.md)).

## Removing the Focus Outline

- **Anti-pattern:** `*:focus { outline: none; }` (or `outline: 0`) with no replacement.
- **Why it is wrong:** Keyboard users lose the only cue showing where they are on the page,
  making the interface unusable without a mouse.
- **The fix:** Keep the default outline or provide a clearly visible alternative
  (`:focus-visible { outline: 2px solid; }`) with ≥ 3:1 contrast against the background.

## Meaning by Color Alone

- **Anti-pattern:** Marking required fields, errors, or status with color only — a red
  border, a green dot, "items in red are overdue".
- **Why it is wrong:** Users with color-blindness or low vision, and screen-reader users,
  cannot perceive the distinction. The information simply is not there for them.
- **The fix:** Pair color with a text label, icon with accessible name, or programmatic
  state (e.g. `aria-invalid` plus an error message). See
  [color-and-contrast](10-color-and-contrast.md).

## Unlabeled Controls

- **Anti-pattern:** Inputs with only placeholder text, or icon buttons with no name:
  `<input placeholder="Search">`, `<button><svg/></button>`.
- **Why it is wrong:** Placeholders vanish on input and are often ignored by assistive tech;
  an icon-only button announces as "button" with no purpose. The user cannot tell what the
  control does.
- **The fix:** Give every control a persistent accessible name — a visible `<label>`,
  `aria-label`, or `aria-labelledby` — and mark decorative icons `aria-hidden="true"`.

## Focus That Never Moves

- **Anti-pattern:** Opening a modal, drawer, or menu without moving focus into it, and not
  restoring focus when it closes.
- **Why it is wrong:** Keyboard and screen-reader users stay stranded behind the dialog,
  unaware it opened, and can Tab into hidden background content.
- **The fix:** On open, move focus to the dialog (or its first control) and trap focus
  inside; on close, return focus to the triggering element ([focus-management](05-focus-management.md)).

## Silent Dynamic Updates

- **Anti-pattern:** Injecting a toast, validation error, or search result into the DOM with
  no announcement.
- **Why it is wrong:** Screen-reader users are not notified; the change is invisible to them
  even though it drives the next action.
- **The fix:** Render status into an `aria-live` region (`polite` for non-urgent, `assertive`
  for errors), or move focus to the new content ([live-regions](19-live-regions.md)).

## Positive `tabindex`

- **Anti-pattern:** `tabindex="1"`, `tabindex="2"`… to force a tab order.
- **Why it is wrong:** Positive values jump ahead of the natural DOM order, producing an
  unpredictable, hard-to-maintain focus sequence that fights every later change.
- **The fix:** Order elements correctly in the DOM and use only `tabindex="0"` (in natural
  order) or `tabindex="-1"` (focusable only via script).

## Heading Levels Chosen for Size

- **Anti-pattern:** Picking `<h4>` because it "looks right", or skipping from `<h2>` to
  `<h5>`.
- **Why it is wrong:** Screen-reader users navigate by heading structure; a broken outline
  destroys their map of the page.
- **The fix:** Choose heading level by document hierarchy and style it with CSS. Never skip
  levels ([semantic-html](03-semantic-html.md)).

## Scanner-Only "Done"

- **Anti-pattern:** Treating a passing axe/Lighthouse run as proof of accessibility.
- **Why it is wrong:** Automated tools detect roughly 40% of issues and cannot judge whether
  a name is meaningful, focus order is logical, or a widget is operable. False confidence
  ships broken UI.
- **The fix:** Keep the automated scan, and add a keyboard-only pass plus a screen-reader
  pass to the definition of done ([accessibility-testing](24-accessibility-testing.md)).

## AI Review Checklist

- Does the diff introduce any `<div>`/`<span>` acting as a control instead of a native element?
- Is ARIA compensating for a wrong element rather than a genuine HTML gap?
- Is any focus outline removed without a visible replacement?
- Is any state conveyed by color alone, or any control left without an accessible name?
- Does newly opened content move focus, and do dynamic updates get announced?

## Related

- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/05-focus-management.md`
- `knowledge/accessibility/10-color-and-contrast.md`
- `knowledge/accessibility/99-ai-review-checklist.md`

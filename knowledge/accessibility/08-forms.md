---
id: accessibility/08-forms
topic: accessibility
slug: forms
title: "Accessibility Forms"
type: doc
order: 8
status: ready
tags: [accessibility, forms, autocomplete, inputmode, aria-invalid, aria-describedby, street-address, one-time-code]
related: [accessibility/03-semantic-html, accessibility/18-error-messages, accessibility/07-aria, accessibility/05-focus-management, accessibility/10-color-and-contrast]
when_to_use: "Read before building or reviewing any form: inputs, labels, validation, or error handling."
---
# Accessibility Forms

## Purpose

This document defines how to build forms that everyone can complete: correctly labeled
inputs, keyboard-operable controls, and validation errors that are perceivable and
recoverable. It is written so an agent can implement or review a form without stranding
users who rely on a keyboard, screen reader, or magnification.

Forms are where accessibility failures become task failures. A miscaptioned button is
annoying; an unlabeled required field means a user cannot buy, sign up, or contact you.

## Why It Matters

Forms carry the highest-stakes interactions on most sites, and they are dense with the exact
patterns that break for assistive tech: labels, grouping, dynamic errors, and focus. A field
without a programmatic label is a blank to a screen reader user — they hear "edit text" with
no idea what to type. An error shown only in red text is invisible to color-blind users and
silent to screen readers. Because forms gate conversion, their accessibility defects are also
directly business-critical.

## Core Principles

- **Every input has a programmatic label.** A visible `<label>` associated by `for`/`id` is
  the standard. Placeholders, adjacent text, and `title` are not substitutes.
- **Use the right native control.** `<select>`, `<input type="checkbox|radio|date|email">`
  bring keyboard behavior, mobile keyboards, and platform semantics you cannot fully rebuild.
- **Group related controls.** Radio and checkbox sets belong in `<fieldset>` with a
  `<legend>` so the group's purpose is announced with each option.
- **Errors must be perceivable, programmatic, and recoverable.** Identify the field in text,
  link the message with `aria-describedby`, mark it `aria-invalid`, and let the user fix and
  resubmit; see [error messages](18-error-messages.md).
- **Do not block submission on invisible rules.** If validation fails, move focus to the
  first error and explain what to change — never disable submit with no reason given.

## Best Practices

- Associate labels explicitly: `<label for="email">` + `<input id="email">`. Wrapping also
  works but explicit `for`/`id` is the most robust across assistive tech.
- Set `autocomplete` tokens (`email`, `name`, `street-address`, `one-time-code`) so browsers
  and password managers can fill fields — a WCAG requirement for known input purposes.
- Use `type` and `inputmode` to summon the right mobile keyboard (`type="email"`,
  `inputmode="numeric"`).
- Mark required fields with the `required` attribute *and* a visible indicator; do not rely
  on the asterisk color alone.
- On failed validation, set `aria-invalid="true"`, connect the message via `aria-describedby`,
  and place a summary at the top linking to each bad field. Move focus to it.
- Keep error and helper text tied to the field so it is read when the field gains focus, not
  just when submit is pressed.
- Ensure inputs, focus rings, and error indicators meet contrast minimums; see
  [color and contrast](10-color-and-contrast.md).

## Examples

**Good Example** — labeled input with programmatic, described error

```html
<label for="email">Email address</label>
<input
  id="email"
  name="email"
  type="email"
  autocomplete="email"
  required
  aria-invalid="true"
  aria-describedby="email-err"
/>
<!-- role="alert" makes the message announce immediately when it appears -->
<p id="email-err" role="alert">Enter a valid email, e.g. name@example.com.</p>
```

- `aria-invalid="true"` announces the field as invalid.
- `aria-describedby` links the message to the input, so it is read with the field.
- `role="alert"` makes the message announce the moment it appears, even if focus moved.

**Bad Example** — placeholder-as-label, error conveyed by color only

```html
<!-- Placeholder is the only label: it vanishes on typing and is not a reliable
     accessible name, so a screen reader announces "edit text".
     The error is a red border with no text, no aria-invalid, no message —
     invisible to screen readers and to color-blind users. -->
<input name="email" placeholder="Email" class="input error" />
```

## Common Mistakes

- Using `placeholder` as the label — it is not an accessible name and disappears on input.
- Custom `<div>` dropdowns and toggles that drop keyboard support and native semantics.
- Radio/checkbox groups with no `<fieldset>`/`<legend>`, so options are announced without
  their shared question.
- Errors shown only as color or only after submit, with focus left on the button.
- Disabling the submit button until valid, giving no cue about what is missing.
- Missing `autocomplete`, forcing manual entry and failing WCAG "identify input purpose".
- Removing the focus outline on inputs, so keyboard users lose their place.

## Production Tips

- Prefer the browser's native constraint validation as a baseline, then layer custom messages
  — it works before your JS loads and cannot desync from field state.
- After a failed submit, render an error summary region at the top of the form with in-page
  links to each invalid field; this is the fastest recovery path for screen reader users.
- Test the whole flow with the keyboard only and with a screen reader: reach every field,
  hear its label, trigger an error, and confirm the message is announced.

## AI Review Checklist

- Does every input have an associated `<label>` (or equivalent programmatic name)?
- Are related radios/checkboxes wrapped in `<fieldset>` with a `<legend>`?
- Do fields carry correct `type`, `inputmode`, and `autocomplete` tokens?
- On error, is the field `aria-invalid`, described by a text message, and is focus moved?
- Is required status conveyed by more than color, and is submission never silently blocked?
- Do inputs, labels, and focus indicators meet contrast requirements?

## Related

- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/accessibility/18-error-messages.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/05-focus-management.md`
- `knowledge/accessibility/10-color-and-contrast.md`

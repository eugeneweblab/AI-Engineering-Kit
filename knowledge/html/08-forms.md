---
id: html/08-forms
topic: html
slug: forms
title: "HTML Forms"
type: doc
order: 8
status: ready
tags: [html, forms]
related: [html/11-accessibility, html/19-security, html/22-validation, html/23-progressive-enhancement]
when_to_use: "Read before building or reviewing any input, form, login, checkout, or data-entry UI."
---
# HTML Forms

## Purpose

This document defines how to build HTML forms that are accessible, usable, secure by
default, and functional before any JavaScript loads. Forms are where users hand you
data — credentials, payments, personal details — so they demand correct labelling,
native validation, and the right input semantics. Most form bugs (unclickable labels,
autofill failures, mobile keyboard mismatches) come from skipping HTML fundamentals.

## Why It Matters

A form is a contract between the user and the server. Get the HTML wrong and the cost
lands on the most vulnerable users first: a missing `<label>` means a screen-reader user
cannot tell what a field is; a wrong `type` means a mobile user gets the wrong keyboard;
no `name` attribute means the data never reaches the server. Native form features —
labels, validation, autofill, submission — are free, tested across browsers, and work
without JS. Reimplementing them in JavaScript reintroduces bugs the platform already
solved and breaks whenever a script fails to load.

## Core Principles

- **Every input has a programmatic label.** Associate a `<label for="id">` with each
  control, or wrap the control in the label. Placeholder text is not a label.
- **Controls need a `name` to submit.** Without `name`, a field's value is never sent.
  The `id` is for labels/scripts; the `name` is for the server.
- **Choose `type` for meaning and keyboard.** `email`, `tel`, `url`, `number`, `date`
  trigger the right mobile keyboard, autofill, and native validation.
- **Validate on the server; use HTML validation as a first pass.** `required`,
  `pattern`, `min`/`max`, `maxlength` help users instantly but are trivially bypassed —
  never trust them for security.
- **Forms must work without JavaScript.** A real `<form action method>` that submits is
  the baseline; enhance with JS, do not depend on it.

## Best Practices

- Group related fields with `<fieldset>` and a `<legend>` (e.g. a radio-button set); the
  legend is announced as the group's name.
- Set `autocomplete` tokens (`email`, `current-password`, `new-password`, `street-address`,
  `one-time-code`) so browsers and password managers fill correctly.
- Use `inputmode` to refine the mobile keyboard when `type` is generic (e.g.
  `inputmode="numeric"` for a PIN kept as `type="text"`).
- Mark the submit control as `<button type="submit">`; give every `<button>` an explicit
  `type` (`button`, `submit`, `reset`) — the default inside a form is `submit`.
- Convey required state with the `required` attribute (not only a `*` glyph), and reflect
  errors with `aria-invalid` and `aria-describedby` pointing to the message.
- Use `<button>` for actions and `<a>` for navigation; never a `<div>` with a click
  handler as a submit control.
- Set `method="post"` for state changes and add a CSRF token; `GET` only for idempotent
  searches.

## Examples

**Good Example** — labelled, typed, native-validating, JS-optional

```html
<form action="/subscribe" method="post"> <!-- works with no JS -->
  <label for="email">Email address</label>
  <input
    id="email"                 <!-- id links the label -->
    name="email"               <!-- name is what the server receives -->
    type="email"               <!-- email keyboard + native format check -->
    autocomplete="email"       <!-- lets the browser/password-manager fill -->
    required                    <!-- native "must fill" hint -->
    aria-describedby="email-hint"
  />
  <p id="email-hint">We'll only email you the newsletter.</p>

  <button type="submit">Subscribe</button> <!-- explicit type -->
</form>
```

**Bad Example** — placeholder as label, no name, div "button"

```html
<form>
  <!-- Placeholder disappears on focus and is not a real label:
       screen readers may read nothing; the field has no name so its
       value is never submitted; type=text gives the wrong keyboard. -->
  <input type="text" placeholder="Email">

  <!-- A div is not focusable or keyboard-operable and cannot submit. -->
  <div class="btn" onclick="send()">Subscribe</div>
</form>
```

## Common Mistakes

- Using `placeholder` as the only label — it vanishes on input and fails a11y.
- Forgetting `name`, so the field submits nothing.
- Leaving every input as `type="text"`, missing keyboard, autofill, and validation.
- Relying on client-side validation for security instead of re-validating server-side.
- Building submit/reset controls from `<div>`/`<a>` that keyboards cannot operate.
- Omitting `<fieldset>`/`<legend>` around radio and checkbox groups.
- Depending on JS to submit, so the form breaks when a script fails.

## Production Tips

- Add `autocomplete="one-time-code"` to OTP inputs so mobile browsers offer the SMS code.
- Prevent double submits by disabling the button on submit *after* the form posts, not by
  replacing native submission.
- Preserve entered values on validation errors so users never retype a whole form.
- Rate-limit and CSRF-protect POST endpoints; see the security guides.

## AI Review Checklist

- Does every input have an associated `<label>` (not just a placeholder)?
- Does every field that must submit have a `name`?
- Is `type` chosen for meaning (email/tel/number/date) with appropriate `autocomplete`?
- Are radio/checkbox groups wrapped in `<fieldset>` with a `<legend>`?
- Do all `<button>`s inside forms have an explicit `type`?
- Is there real server-side validation behind any client-side checks?
- Does the form submit and function with JavaScript disabled?

## Related

- `knowledge/html/11-accessibility.md`
- `knowledge/html/19-security.md`
- `knowledge/html/22-validation.md`
- `knowledge/html/23-progressive-enhancement.md`

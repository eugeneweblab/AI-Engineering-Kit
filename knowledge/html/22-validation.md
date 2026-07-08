---
id: html/22-validation
topic: html
slug: validation
title: "Validation"
type: doc
order: 22
status: ready
tags: [html, validation]
related: [html/08-forms, html/01-document-structure, html/21-best-practices, html/11-accessibility, html/19-security]
when_to_use: "Read before shipping markup that must parse correctly, or when building form input validation."
---
# Validation

## Purpose

This document covers two distinct kinds of validation that share a name. First,
*document validation*: is the HTML well-formed and conformant so browsers, crawlers, and
assistive tech interpret it as intended? Second, *form input validation*: does the markup
constrain what users can submit, using native constraint attributes before any script
runs?

Both matter because both are about correctness — one for the document, one for the data —
and an agent should never confuse a green validator with a secure form.

## Why It Matters

Browsers recover from invalid HTML by guessing, and different browsers guess differently —
so invalid markup is a page that renders *sometimes*, in ways you did not author. A missing
closing tag can silently reparent half your content; a duplicate `id` can break every
script and label that targets it. On the form side, native validation is the first gate on
data quality and a large usability win, but it runs in the browser and is trivially
bypassed — so it must never be the *only* gate. Confusing client validation with server
validation is how bad and malicious data reaches the database.

## Core Principles

- **Conform to the spec, then verify it.** Well-formed, properly nested, uniquely-`id`'d
  markup is not optional polish; it is what makes rendering deterministic.
- **Prefer native constraint validation.** `required`, `type`, `min`/`max`, `pattern`,
  `maxlength` give instant, accessible feedback with zero JavaScript.
- **Client validation is UX, server validation is security.** Every client rule must be
  re-enforced on the server, which is the only trust boundary. See [security](19-security.md).
- **Match the input type to the data.** `type="email"`, `type="number"`, `type="url"`
  bring correct keyboards, parsing, and built-in checks.
- **Never silently drop invalid input.** Surface a clear, associated error message the
  user and assistive tech can perceive.

## Best Practices

- Validate documents against the WHATWG/W3C validator (or a build-time linter like
  html-validate) in CI; treat errors as build failures and warnings as review items.
- Keep `id` values unique per document — duplicates break `<label for>`, fragment links,
  and `getElementById`. See [document structure](01-document-structure.md).
- Use native constraint attributes as the first layer: `required`, `minlength`,
  `maxlength`, `min`, `max`, `step`, `pattern`, and the right `type`. See [forms](08-forms.md).
- Provide human-readable constraints: pair `pattern` with `title`/help text, since the
  browser's default message ("does not match the requested format") is opaque.
- Style validity states with `:valid`/`:invalid`/`:user-invalid` and expose errors via
  `aria-describedby` so they are announced. Prefer `:user-invalid` to avoid flagging
  fields the user has not touched yet.
- Re-validate everything server-side; treat all client constraints as advisory. Reject,
  do not sanitize-and-hope, when server rules fail.

## Examples

**Good Example** — conformant markup, native + described validation

```html
<!-- Well-formed, unique ids, native constraints do the first-pass validation -->
<label for="age">Age</label>
<input id="age" name="age" type="number" min="18" max="120" required
       aria-describedby="age-help" />
<!-- Human-readable constraint the browser message alone would not convey -->
<p id="age-help">Must be 18 or older.</p>

<label for="zip">ZIP code</label>
<!-- pattern + title: browser blocks submit AND explains why -->
<input id="zip" name="zip" pattern="\d{5}" title="Five digits, e.g. 90210" required />
```

**Bad Example** — invalid markup, JS-only validation, duplicate ids

```html
<!-- Duplicate id breaks label association and getElementById -->
<input id="field" />
<input id="field" />

<!-- Unclosed tag: the browser reparents following content unpredictably -->
<p>Enter your age

<!-- No native constraints; validation lives only in JS and is bypassed trivially.
     Server must NOT trust this. -->
<input name="age" onblur="checkAge(this)" />
```

## Common Mistakes

- Treating a passing HTML validator as proof the form is *safe* — it only proves it is
  *well-formed*.
- Relying on client-side validation alone, letting altered requests submit bad data.
- Duplicate `id` attributes silently breaking labels, anchors, and scripts.
- Unclosed or mis-nested tags that reparent content differently across browsers.
- `pattern` with no `title`/help, leaving users staring at a generic error.
- Wrong input `type` (`text` for email/number), losing keyboards and built-in checks.

## Production Tips

- Wire the validator/linter into pre-commit and CI so invalid markup cannot merge.
- Log server-side validation rejections; a spike often signals a client bug or an attack
  probing the endpoint.
- Test forms with keyboard and screen reader to confirm error messages are announced,
  not just colored red.

## AI Review Checklist

- Does the document pass an HTML validator with no errors?
- Are all `id` attributes unique, and are tags properly nested and closed?
- Do form controls use native constraints (`required`, `type`, `pattern`, `min`/`max`)?
- Is every client-side rule re-enforced on the server?
- Are validation errors associated via `aria-describedby` and announced to assistive tech?
- Does each `pattern` carry a human-readable `title` or help text?

## Related

- `knowledge/html/08-forms.md`
- `knowledge/html/01-document-structure.md`
- `knowledge/html/21-best-practices.md`
- `knowledge/html/11-accessibility.md`
- `knowledge/html/19-security.md`

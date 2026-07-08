---
id: frontend/12-forms
topic: frontend
slug: forms
title: "Forms"
type: doc
order: 12
status: ready
tags: [frontend, forms]
related: [frontend/09-accessibility, frontend/13-error-handling, frontend/14-security, frontend/06-data-fetching, frontend/04-state-management]
when_to_use: "Read before building or reviewing any input, validation, or submission flow in a UI."
---
# Forms

## Purpose

This document defines how to build forms that are accessible, validated, resilient to
double-submits, and honest about their state. It covers input structure, validation
timing, submission handling, and error feedback so an agent can implement or review a
form without shipping a broken or inaccessible one.

A form is the primary place a user hands data to your system. It is also where most
accessibility, validation, and data-integrity bugs live. Treat every form as an
untrusted boundary and a first-class UX surface at once.

## Why It Matters

Forms carry the highest-intent, highest-cost user actions: signup, checkout, payment,
account changes. A dropped submit, a mislabeled field, or a validation message that only
a sighted mouse user can perceive translates directly into lost conversions and support
tickets. Form bugs are also disproportionately silent — the happy path works in the demo,
while the double-click, the slow network, the screen reader, and the paste-from-password-
manager cases fail in production. Because the input reaching your handler is fully
attacker-controlled, client validation is a UX convenience, never a security control.

## Core Principles

- **Validate on the client for speed, on the server for truth.** Client validation is
  UX; it can always be bypassed. The server is the only authority. Never trust a value
  because the client checked it.
- **Every input has a programmatic label.** A visible `<label>` tied by `htmlFor`/`id`,
  not a placeholder. Placeholders vanish on focus and are invisible to assistive tech.
- **Make submission idempotent and single-flight.** Disable the submit button while a
  request is in flight; a double-click must not create two records.
- **Errors are announced, not just colored.** Bind messages with `aria-describedby` and
  set `aria-invalid`. Color alone excludes colorblind and screen-reader users.
- **Preserve the user's input on failure.** Never clear a form because the server
  rejected one field. Re-render their values with the errors attached.

## Best Practices

- Use native `<form>` with a real `<button type="submit">` so Enter-to-submit and browser
  autofill work. Handle submit on the form, not click on the button.
- Validate on **blur** for the first pass and on **change** only after a field has already
  errored. Validating on every keystroke from the start punishes users mid-typing.
- Give inputs correct `type`, `inputmode`, `autocomplete`, and `name` attributes
  (`autocomplete="email"`, `inputmode="numeric"`). This unlocks autofill and mobile
  keyboards for free.
- Reflect three submit states explicitly: idle, submitting (disabled + busy indicator),
  and error/success. Never leave the user guessing whether a click registered.
- Group related fields with `<fieldset>`/`<legend>`; associate error text with
  `aria-describedby` and mark the field `aria-invalid="true"`.
- Return field-level errors from the server in a structured shape the form can map back
  onto individual inputs, not one opaque string.
- Move focus to the first invalid field (or an error summary) on failed submit so keyboard
  and screen-reader users are not stranded.

## Examples

**Good Example** — labeled, single-flight, accessible errors

```tsx
function EmailForm({ onSubmit }: { onSubmit: (email: string) => Promise<void> }) {
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (pending) return;              // guard against double-submit
    setPending(true);
    setError(null);
    try {
      await onSubmit(email);          // server is the source of truth
    } catch (err) {
      setError("That email is already registered."); // keep the typed value
    } finally {
      setPending(false);              // always re-enable, even on failure
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <label htmlFor="email">Email</label>
      <input
        id="email"
        name="email"
        type="email"
        autoComplete="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? "email-error" : undefined}
      />
      {error && <p id="email-error" role="alert">{error}</p>} {/* announced */}
      <button type="submit" disabled={pending}>
        {pending ? "Saving…" : "Save"}
      </button>
    </form>
  );
}
```

**Bad Example** — placeholder-as-label, double-submittable, silent errors

```tsx
function EmailForm({ onSubmit }) {
  const [email, setEmail] = useState("");
  return (
    <div>
      {/* placeholder is not a label; it disappears and is unreadable by AT */}
      <input placeholder="Email" onChange={(e) => setEmail(e.target.value)} />
      {/* onClick, no <form>: Enter won't submit; button never disables */}
      <button onClick={() => onSubmit(email)}>Save</button>
      {/* no error surface at all — a rejected submit looks identical to success */}
    </div>
  );
}
```

## Common Mistakes

- Using `placeholder` as the only label — it fails contrast, vanishes on focus, and is
  ignored by screen readers.
- Treating client validation as security; skipping the equivalent check on the server.
- Not disabling the submit button in flight, allowing duplicate records on double-click.
- Clearing the form on a server rejection, forcing the user to retype everything.
- Signaling errors with red borders only — no text, no `aria-invalid`, no announcement.
- Validating aggressively on every keystroke from the first character, so a field errors
  while the user is still typing a valid value.
- Losing focus after a failed submit, leaving keyboard users with no path to the error.

## Production Tips

- Prefer a schema-first validator (Zod, Valibot) and share the schema between client and
  server so the two validations cannot drift apart.
- Debounce async validations (username availability) and cancel stale in-flight checks so
  a slow earlier request cannot overwrite a newer result.
- Persist long or multi-step forms to local draft state so a refresh or crash does not
  destroy the user's work.

## AI Review Checklist

- Does every input have a real `<label>` (not just a placeholder) associated by id?
- Is there server-side validation for every field, independent of client checks?
- Is the submit button disabled while a request is in flight to prevent double-submit?
- Are validation errors bound with `aria-describedby` and `aria-invalid`, not color alone?
- Are the user's entered values preserved when the server rejects a submit?
- Does focus move to the first invalid field or an error summary on failure?
- Are correct `type`/`inputmode`/`autocomplete` attributes set for autofill and mobile?

## Related

- `knowledge/frontend/09-accessibility.md`
- `knowledge/frontend/13-error-handling.md`
- `knowledge/frontend/14-security.md`
- `knowledge/frontend/06-data-fetching.md`
- `knowledge/frontend/04-state-management.md`

---
id: accessibility/18-error-messages
topic: accessibility
slug: error-messages
title: "Error Messages"
type: doc
order: 18
status: ready
tags: [accessibility, error-messages, aria-describedby, aria-invalid]
related: [accessibility/08-forms, accessibility/19-live-regions, accessibility/05-focus-management, accessibility/07-aria, accessibility/10-color-and-contrast]
when_to_use: "Read when a screen reader does not announce a validation failure, or before building form validation, error summaries, or any UI that reports a problem to the user."
---
# Error Messages

## Purpose

This document defines how to surface errors — validation failures, submission errors,
and system faults — so that every user can perceive them, understand them, and recover.
It covers where the error text lives, how it is associated with the control that
produced it, and how it reaches a screen reader user who cannot see a red border.

An accessible error is not "an error that appears." It is an error that is *announced,
programmatically linked, described in text, and reachable by keyboard*. If any of those
four is missing, some users hit a wall they cannot see or escape.

## Why It Matters

Errors are the moment a user is already frustrated and most likely to abandon the task.
A sighted user glances at a red field and a message; a screen reader user gets nothing
unless you tell them explicitly. Color-only error signalling (a red border, no text)
is invisible to colorblind users and to assistive tech alike. WCAG 3.3.1 (Error
Identification) and 3.3.3 (Error Suggestion) are Level A/AA requirements precisely
because unrecoverable forms are one of the most common reasons disabled users cannot
complete transactions — checkout, registration, benefits applications.

## Core Principles

- **Describe the error in text, not just color or an icon.** Color and shape are cues,
  never the message. WCAG 1.4.1 forbids color as the only channel.
- **Associate the message with its control programmatically.** Use `aria-describedby`
  so the message is read when the field gets focus, not just visually adjacent to it.
- **Mark invalid controls with `aria-invalid="true"`.** This is the state a screen
  reader announces ("invalid entry"); a red border is not.
- **Announce dynamic errors.** An error that appears after submit must reach the user
  even if focus is elsewhere — via a [live region](19-live-regions.md) or by moving
  focus to an error summary.
- **Say what is wrong and how to fix it.** "Invalid input" is useless; "Password must
  be at least 12 characters" is actionable (WCAG 3.3.3).

## Best Practices

- Give each error message a stable `id` and point the field's `aria-describedby` at it.
  Keep the element in the DOM even when empty, or toggle it, but keep the association.
- Set `aria-invalid="true"` on the control when it fails and remove it when it passes;
  drive both from the same validation state so they never disagree.
- On submit failure, render an **error summary** at the top listing each error as a link
  to its field, then move keyboard focus to the summary heading. This gives one
  predictable landing spot instead of a hunt.
- Place the message text adjacent to its field visually, so a low-vision user zoomed to
  400% (WCAG 1.4.10) does not have to scroll to connect message and input.
- Do not rely on the browser's native `:invalid` styling alone — it triggers before the
  user has finished typing and is announced inconsistently.
- Meet **3:1** contrast for the error color against its background and never encode the
  error solely in that color (see [color and contrast](10-color-and-contrast.md)).
- Validate on submit (and optionally on blur), not on every keystroke — per-keystroke
  errors spam screen readers and punish slow typists.

## Examples

**Good Example** — text message, programmatic association, announced state

```html
<label for="email">Email</label>
<input
  id="email"
  type="email"
  aria-describedby="email-error"
  aria-invalid="true"
/>
<!-- role="alert" announces the text the moment it is inserted, even if focus moved -->
<p id="email-error" role="alert">
  Enter a valid email address, for example name@example.com.
</p>
```

- `aria-describedby` links the message to the field, so it is read with it.
- `aria-invalid="true"` makes a screen reader announce "invalid entry".
- `role="alert"` announces the text the moment it is inserted, even if focus moved.

**Bad Example** — color-only, no association, silent to assistive tech

```html
<label for="email">Email</label>
<!-- red border is the ONLY signal: invisible to SR and to colorblind users -->
<input id="email" type="email" style="border: 2px solid red" />
<!-- message is not linked to the field and is never announced on change -->
<p style="color: red">Invalid</p>  <!-- "Invalid" says what, not how to fix -->
```

## Common Mistakes

- Signalling errors with color or an icon only, with no text — fails WCAG 1.4.1.
- Placing the message near the field visually but never wiring `aria-describedby`, so a
  screen reader user hears the label but never the error.
- Forgetting `aria-invalid`, so the field reads as normal despite being wrong.
- Injecting the error text into the DOM without a live region or focus move, so it
  appears silently for anyone not looking at that spot.
- Vague copy ("Error", "Invalid input") that states failure without a remedy.
- Firing validation on every keystroke, flooding the screen reader with partial errors.
- Putting `role="alert"` on a container that already holds text at load — it only
  announces content added *after* it is rendered.

## Production Tips

- Centralize error rendering in one component so association, `aria-invalid`, and the
  summary link stay consistent across every form in the app.
- In tests, assert the accessible wiring, not just the visible text: the input has
  `aria-invalid="true"` and its `aria-describedby` resolves to the message node.
- Keep server-side and client-side messages identical, so a user who fixes a field does
  not see the wording change and wonder if the problem is different.

## AI Review Checklist

- Is every error conveyed in text, not by color or icon alone?
- Is each message linked to its control via `aria-describedby`?
- Does the failing control carry `aria-invalid="true"`, cleared when it passes?
- Are dynamically inserted errors announced via a live region or a focus move to a summary?
- Does each message say how to fix the problem, not just that it failed?
- On submit failure, does focus move to a predictable error summary?
- Does the error color meet 3:1 contrast and never act as the sole signal?

## Related

- `knowledge/accessibility/08-forms.md`
- `knowledge/accessibility/19-live-regions.md`
- `knowledge/accessibility/05-focus-management.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/10-color-and-contrast.md`

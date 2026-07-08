---
id: accessibility/19-live-regions
topic: accessibility
slug: live-regions
title: "Live Regions"
type: doc
order: 19
status: ready
tags: [accessibility, live-regions]
related: [accessibility/18-error-messages, accessibility/07-aria, accessibility/06-screen-readers, accessibility/16-dialogs, accessibility/08-forms]
when_to_use: "Read before building any UI that updates content without a page reload — toasts, async status, search results, cart counts, or form-level errors."
---
# Live Regions

## Purpose

This document defines how to announce content that changes *after* the page has loaded,
so screen reader users learn about it without moving focus there. A live region is a
DOM element whose updates the assistive tech speaks automatically. It is the mechanism
behind accessible toasts, "3 results found", "Saved", loading spinners, and async
form errors.

The rule that governs live regions is subtle and easy to get wrong: the browser only
watches the region for changes *while it exists in the accessibility tree*. Insert the
region and its text in the same tick and nothing is announced. This document exists to
get that timing right.

## Why It Matters

Sighted users perceive change ambiently — a toast slides in, a counter ticks up, a
spinner spins. A screen reader user perceives only what is in the focus ring or what is
explicitly announced. Without a live region, a "Message sent" confirmation, a validation
error, or "Loading…" simply never happens for them; they act blind to the app's state.
WCAG 4.1.3 (Status Messages, Level AA) requires exactly this: status changes that do not
take focus must still be programmatically conveyed. Overuse is equally harmful — a region
set to `assertive` that fires on every keystroke makes the app unusable.

## Core Principles

- **`polite` vs `assertive`.** `aria-live="polite"` queues the announcement until the
  user is idle — use it for almost everything. `assertive` interrupts immediately — use
  it only for time-critical errors the user must hear now. Overusing `assertive` is a
  denial-of-service on your own users.
- **The region must exist before the text does.** Render the empty live region at page
  load; update its contents later. Adding region and text together often goes unspoken.
- **Prefer roles over raw attributes for common cases.** `role="alert"` implies
  `aria-live="assertive"`; `role="status"` implies `polite`. They are clearer and better
  supported.
- **Announce text, not structure.** Live regions read out the changed text; screen
  readers may ignore complex markup inside them. Keep the payload a short string.
- **One region, reused.** Keep a small number of persistent regions and swap their text,
  rather than spawning a new live element per message.

## Best Practices

- Use `aria-live="polite"` (or `role="status"`) for success, progress, and result
  counts; use `role="alert"` for errors that block the user's current action.
- Set `aria-atomic="true"` when the whole message should be re-read on any change; leave
  it `false` (default) when only appended text should be spoken.
- Keep the region **in the DOM at all times**; toggle visibility with content, not by
  adding/removing the element. Do not hide it with `display:none` — hidden regions are
  not announced. Use a visually-hidden (clip) technique if it should be SR-only.
- Debounce rapid updates. Coalesce "1 result… 2 results…" into a single final
  "12 results" so the user hears the answer, not the process.
- Clear then set text when re-announcing the *same* string — identical content may not
  re-trigger. Set to empty, then on the next tick set the new message.
- For loading, announce start and end ("Loading results" → "12 results loaded"); do not
  leave the user in silence between them.

## Examples

**Good Example** — persistent region, populated after mount

```html
<!-- Rendered empty at page load so the browser is already watching it -->
<div id="status" role="status" aria-live="polite"></div>

<script>
  async function search(q) {
    const status = document.getElementById("status");
    status.textContent = "Searching…";           // polite: queued, not interrupting
    const results = await api.search(q);
    // Announce the final count, not each intermediate update
    status.textContent = `${results.length} results found`;
  }
</script>
```

**Bad Example** — region and text inserted together, wrong urgency

```html
<script>
  function showToast(msg) {
    const el = document.createElement("div");
    el.setAttribute("aria-live", "assertive"); // interrupts the user for a toast
    el.textContent = msg;                       // region + text added in one tick…
    document.body.appendChild(el);              // …so many SRs never announce it
  }
</script>
```

## Common Mistakes

- Creating the live element and its text in the same insertion — the change is missed
  because the region did not pre-exist in the accessibility tree.
- Using `assertive` for non-urgent status, interrupting whatever the user is reading.
- Hiding the region with `display:none` or `visibility:hidden`, which stops announcements.
- Firing an announcement per keystroke or per network chunk, flooding the user.
- Re-setting the region to the same string and expecting a re-announcement.
- Putting interactive controls inside a live region and expecting them to work — the
  region announces text; put buttons outside it.
- Stacking many live regions so multiple announcements collide and cancel each other.

## Production Tips

- Provide one app-level announcer utility (`announce(message, { assertive })`) backed by
  two persistent regions, one polite and one assertive. Every feature calls it, so
  timing and urgency rules live in one place.
- In automated tests, assert the region exists with the right role at mount and that its
  text updates — timing bugs do not show up in a static snapshot.
- Verify with a real screen reader (VoiceOver, NVDA); attribute presence does not prove
  the message was actually spoken.

## AI Review Checklist

- Does the live region exist in the DOM before its content is updated?
- Is `polite`/`role="status"` used for routine updates and `assertive`/`role="alert"`
  reserved for urgent errors?
- Is the region kept present and not hidden with `display:none`?
- Are rapid updates debounced into a single meaningful announcement?
- Is the announced payload short text, with no interactive controls inside?
- Is there a single reused announcer rather than a new element per message?

## Related

- `knowledge/accessibility/18-error-messages.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/06-screen-readers.md`
- `knowledge/accessibility/16-dialogs.md`
- `knowledge/accessibility/08-forms.md`

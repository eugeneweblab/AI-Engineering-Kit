---
id: accessibility/07-aria
topic: accessibility
slug: aria
title: "ARIA"
type: doc
order: 7
status: ready
tags: [accessibility, aria, aria-labelledby, role, aria-describedby, aria-expanded, getElementById, aria-checked]
related: [accessibility/03-semantic-html, accessibility/06-screen-readers, accessibility/05-focus-management, accessibility/19-live-regions, accessibility/16-dialogs]
when_to_use: "Read before adding any role, aria-* attribute, or building a custom widget that native HTML cannot express."
---
# ARIA

## Purpose

This document defines when and how to use ARIA (Accessible Rich Internet Applications) —
the `role`, `aria-*` state, and property attributes that patch information into the
[accessibility tree](06-screen-readers.md). It is written so an agent adds ARIA only where
it is needed, and never in a way that breaks the very users it targets.

ARIA changes what a screen reader announces; it changes **nothing** about behavior. It does
not add keyboard handling, focus, or click events. This asymmetry is the source of most ARIA
bugs: markup that *sounds* right but does not *work*.

## Why It Matters

ARIA is powerful and unguarded — you can overwrite an element's role, name, and state with a
single attribute, and the browser will not warn you. A wrong role tells a screen reader user
the element is something it is not; they act on that promise and hit a dead end. Studies of
real-world pages consistently show that pages *with* ARIA have *more* accessibility failures
than pages without, because ARIA is applied incorrectly. The first rule of ARIA is therefore
a rule about restraint.

## Core Principles

- **No ARIA is better than bad ARIA.** A wrong role or stale state is worse than none —
  it actively lies to the user. If you are unsure, use semantic HTML and stop.
- **Prefer native semantics.** If a native element (`<button>`, `<nav>`, `<select>`,
  `<dialog>`) does the job, use it; do not recreate it with `role` on a `<div>`.
- **ARIA does not implement behavior.** `role="button"` does not make Enter/Space fire a
  click, and `role="checkbox"` does not toggle. You must add keyboard handling yourself.
- **You own every state you declare.** If you set `aria-expanded`, `aria-checked`, or
  `aria-selected`, you must update it on every change. A stale state is a broken control.
- **Follow the authoring patterns.** The ARIA Authoring Practices Guide (APG) defines the
  required roles, states, and keys for each widget. Match a whole pattern, not one attribute.

## Best Practices

- Do not set a role that duplicates the element (`<button role="button">`) or contradicts it
  (`<a role="button">` without also adding button keyboard behavior).
- Name elements with the strongest available source: real text > `aria-labelledby` (points
  at visible text) > `aria-label` (invisible string). `aria-labelledby` overrides inner text.
- Use `aria-describedby` for supplementary help or error text, not for the primary name.
- Reserve `role="presentation"`/`aria-hidden="true"` for decorative content; never hide
  something focusable or something the user needs.
- For custom widgets, implement the full APG contract: roles, states, and the expected keys
  (arrows, Home/End, Escape) plus [focus management](05-focus-management.md).
- Announce dynamic text with a [live region](19-live-regions.md) (`aria-live`), not by
  toggling roles.
- Prefer native form validation and `aria-invalid`/`aria-describedby` over custom error
  plumbing; see [forms](08-forms.md).

## Examples

**Good Example** — a disclosure that keeps its declared state in sync

```html
<button type="button" aria-expanded="false" aria-controls="panel-1" id="btn-1">
  Shipping details
</button>
<div id="panel-1" role="region" aria-labelledby="btn-1" hidden>…</div>

<script>
  const btn = document.getElementById("btn-1");
  const panel = document.getElementById("panel-1");
  btn.addEventListener("click", () => {
    const open = btn.getAttribute("aria-expanded") === "true";
    btn.setAttribute("aria-expanded", String(!open)); // state updated every toggle
    panel.hidden = open;                               // visibility follows state
  });
</script>
```

**Bad Example** — a fake button that lies and does nothing

```html
<!-- role="button" promises button behavior but supplies none:
     not focusable (no tabindex), no Enter/Space handler, and aria-expanded
     is hard-coded "false" and never updated — a permanent lie about the state. -->
<div role="button" aria-expanded="false" onclick="togglePanel()">
  Shipping details
</div>
```

## Common Mistakes

- Adding `role` to a `<div>` instead of using the native element that already has that role.
- Declaring a state (`aria-expanded`, `aria-checked`) and never updating it on interaction.
- `role="button"`/`role="link"` with no `tabindex="0"` and no keyboard handler — announced
  as a control but unreachable and inert.
- Putting `aria-label` on a non-interactive element (`<div>`, `<span>`) where it is ignored.
- Pointing `aria-labelledby`/`aria-describedby` at an id that does not exist, yielding an
  empty name.
- Using `aria-hidden="true"` on the focused element or an ancestor of a focusable control.
- Redundant labeling that makes readers say the name twice (`<button aria-label="Close">Close</button>`).

## Production Tips

- Run [axe](21-axe.md) in CI — it catches invalid roles, orphaned `aria-*` ids, and required
  attributes missing from a role. It cannot judge whether a role is *correct* for the intent.
- When copying an APG widget, copy the entire keyboard and state table; partial adoption is a
  frequent regression source.
- Confirm every declared state audibly toggles in a real screen reader after each interaction.

## AI Review Checklist

- Could native HTML replace this ARIA? If yes, prefer it.
- Does each `role` match the element's real behavior, and is behavior actually implemented?
- Is every declared state (`aria-expanded`, `-checked`, `-selected`) updated on every change?
- Do `aria-labelledby`/`aria-describedby` reference existing ids that hold real text?
- Do custom widgets implement the full APG keyboard and focus contract?
- Is `aria-hidden` kept off focusable elements and their ancestors?

## Related

- `knowledge/accessibility/03-semantic-html.md`
- `knowledge/accessibility/06-screen-readers.md`
- `knowledge/accessibility/05-focus-management.md`
- `knowledge/accessibility/19-live-regions.md`
- `knowledge/accessibility/16-dialogs.md`

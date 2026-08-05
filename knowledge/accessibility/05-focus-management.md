---
id: accessibility/05-focus-management
topic: accessibility
slug: focus-management
title: "Focus Management"
type: doc
order: 5
status: ready
tags: [accessibility, focus-management]
related: [accessibility/04-keyboard-navigation, accessibility/16-dialogs, accessibility/19-live-regions, accessibility/07-aria, accessibility/06-screen-readers]
when_to_use: "Read before building modals, drawers, route transitions, or any UI that opens, closes, or replaces content dynamically."
---
# Focus Management

## Purpose

This document defines where keyboard focus must go, when to move it programmatically, and
how to keep it visible. Focus is the keyboard user's cursor: it is where the next
keystroke lands and, for screen-reader users, often what gets announced. In single-page
apps and dynamic UIs, focus does not manage itself — you must move it deliberately when
content appears, disappears, or is replaced.

## Why It Matters

When a modal opens but focus stays behind it, a keyboard user is tabbing through invisible
content beneath the overlay with no idea where they are. When a route changes but focus
stays on the clicked link, a screen-reader user hears nothing about the new page. When a
deleted row leaves focus on a detached element, focus silently resets to the top of the
document and context is lost. These are [Operable](02-pour-principles.md) failures that a
mouse user never experiences. Correct focus management is what makes a dynamic app usable
without a pointer.

## Core Principles

- **Focus follows the user's action.** Opening a dialog moves focus *into* it; closing it
  returns focus to the trigger. Deleting an item moves focus to a sensible neighbor. The
  user should never have to hunt for where focus went.
- **Trap focus inside modals, and only modals.** While a modal dialog is open, Tab and
  Shift+Tab cycle within it and the background is inert (`inert` attribute or
  `aria-hidden`). On close, restore focus to the element that opened it. See
  [dialogs](16-dialogs.md).
- **Never focus a non-visible or transient element as a dead end.** Move focus to
  something the user can see and act on; give a container `tabindex="-1"` if it has no
  natural focusable child.
- **Focus must always be visible.** A clearly visible focus indicator is required (WCAG
  2.4.7). Never remove outlines without an equal or better replacement.
- **Don't steal focus unexpectedly.** Move focus only in response to a user action, not on
  a timer or background event — jumping focus disorients and can trap typing.

## Best Practices

- Use `:focus-visible` to show a strong outline for keyboard users while suppressing it for
  mouse clicks — the best of both without hurting keyboard users.
- On client-side route change, move focus to the new page's `<h1>` (or a `tabindex="-1"`
  main container) and update the document title so screen-reader users know they navigated.
- Save the trigger element before opening an overlay and call `.focus()` on it after
  closing, so focus returns exactly where it left.
- Prefer the native `<dialog>` element with `showModal()`: it handles the focus trap,
  background inertness, and Escape-to-close for you.
- For a status update that should be heard but not stolen into, use a
  [live region](19-live-regions.md) rather than moving focus.

## Examples

**Good Example** — open and close a dialog with correct focus handling

```js
function openDialog(dialog, trigger) {
  dialog.__opener = trigger;      // remember where focus came from
  dialog.showModal();             // native: traps focus + makes background inert
  dialog.querySelector("[autofocus], button, input")?.focus(); // focus first control
}
function closeDialog(dialog) {
  dialog.close();
  dialog.__opener?.focus();       // restore focus to the trigger, not the page top
}
```

```css
/* Visible focus for keyboard users only; mouse clicks stay clean. */
:focus-visible { outline: 3px solid #2563eb; outline-offset: 2px; }
```

**Bad Example** — a modal that abandons focus

```js
function openDialog(el) {
  el.style.display = "block"; // shown visually only — focus stays behind it
  // No focus moved in, background still tabbable, Escape does nothing.
}
function closeDialog(el) {
  el.style.display = "none";  // focus is now on a hidden element → jumps to <body>
  // The user loses their place entirely and must Tab from the top.
}
```

And the outline was killed globally, so nobody can see focus at all:

```css
*:focus { outline: none; }
```

## Common Mistakes

- Opening a modal without moving focus into it, or without trapping focus, so the user
  tabs behind the overlay.
- Closing an overlay without restoring focus to the trigger, dumping focus to the top of
  the page.
- Removing focus outlines globally (`outline: none`) with no visible replacement.
- Focusing an element that is hidden or about to be removed, causing focus to silently
  reset.
- Not moving focus on SPA route changes, so keyboard and screen-reader users are unaware
  the page changed.
- Auto-focusing or stealing focus on background events (polling, ads), interrupting the
  user's typing.

## Production Tips

- Prefer platform primitives: native `<dialog>`, and the `inert` attribute to disable
  background regions, remove most manual focus-trap code and its bugs.
- Verify with a keyboard: open each overlay, confirm focus lands inside, Tab cycles within,
  Escape closes, and focus returns to the trigger.

## AI Review Checklist

- When a dialog/drawer opens, does focus move into it, trap within it, and make the
  background inert?
- On close, is focus restored to the element that opened it?
- Is focus always visible (`:focus-visible`), with no unreplaced `outline: none`?
- On SPA route changes, is focus moved to the new content and the title updated?
- Does focus never land on a hidden, detached, or transient element as a dead end?
- Is focus moved only in response to user action, never stolen by background events?

## Related

- `knowledge/accessibility/04-keyboard-navigation.md`
- `knowledge/accessibility/16-dialogs.md`
- `knowledge/accessibility/19-live-regions.md`
- `knowledge/accessibility/07-aria.md`
- `knowledge/accessibility/06-screen-readers.md`
